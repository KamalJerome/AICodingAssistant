import json
import streamlit as st
import redis
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationEntityMemory
from langchain.memory.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import key

# Initialize Redis client with Upstash URL and token
redis_url = 'rediss://endless-bengal-21596.upstash.io'
redis_token = 'AVRcAAIjcDE2NTkxNGYxODcxYjg0ZjM0YWRjOTgxZTM3ZjRlMjhiZHAxMA'
redis_client = redis.from_url(redis_url, password=redis_token)

#OpenAI API
apiKey = key.API_KEY

st.set_page_config(page_title="AI Coding Assistant")

# Initialize the classifier LLM
classifier_llm = ChatOpenAI(api_key=apiKey)

#Check if question is programming related
def is_programming_related(query):
    prompt_template = PromptTemplate(input_variables=["query"],
                                     template="""
        Decide if the following question is programming-related or not. Respond with "Yes" if it is programming-related, or "No" if it is not.

        Question: {query}
        """)
    prompt = prompt_template.format(query=query)

    # Run the prompt through the LLM
    response = classifier_llm(prompt)
    # Access the content of the response directly
    response_text = response.content.strip()  # Assuming response is an AIMessage

    return response_text.lower() == "yes"

#Load Chats
def load_chat(chat_name):
    chat_data = redis_client.get(chat_name)
    if chat_data:
        data = json.loads(chat_data)
        entity_memory = ConversationEntityMemory(
            llm=ChatOpenAI(api_key=apiKey), k=data.get('k', 50))
        for i in range(len(data["past"])):
            entity_memory.save_context({"input": data["past"][i]},
                                       {"output": data["generated"][i]})
        return {
            "generated": data["generated"],
            "past": data["past"],
            "entity_memory": entity_memory
        }
    return {
        "generated": [],
        "past": [],
        "entity_memory":
        ConversationEntityMemory(llm=ChatOpenAI(api_key=apiKey), k=50)
    }

#Save Chats
def save_chat(chat_name, chat_data):
    serializable_data = {
        "generated": chat_data["generated"],
        "past": chat_data["past"],
        "k": chat_data["entity_memory"].k
    }
    redis_client.set(chat_name, json.dumps(serializable_data))


if "current_chat" not in st.session_state:
    st.session_state.current_chat = None
if "input_text" not in st.session_state:
    st.session_state.input_text = ""
if "uploaded_code" not in st.session_state:
    st.session_state.uploaded_code = ""

#Create new Chats
def create_new_chat():
    new_chat_name = f"Chat {len(list(redis_client.keys())) + 1}"
    chat_data = {
        "generated": [],
        "past": [],
        "entity_memory":
        ConversationEntityMemory(llm=ChatOpenAI(api_key=apiKey), k=50)
    }
    save_chat(new_chat_name, chat_data)
    st.session_state.current_chat = new_chat_name
    st.session_state.input_text = ""

#Switch between Chats
def switch_chat(chat_name):
    st.session_state.current_chat = chat_name
    st.session_state.input_text = ""

#Input prompt processing
def process_input():
    user_input = st.session_state.input_text
    uploaded_code = st.session_state.uploaded_code

    if user_input:
        if is_programming_related(user_input):
            current_chat = load_chat(st.session_state.current_chat)
            llm = ChatOpenAI(api_key=apiKey)
            Conversation = ConversationChain(
                llm=llm,
                prompt=ENTITY_MEMORY_CONVERSATION_TEMPLATE,
                memory=current_chat["entity_memory"])

            # Process uploaded code files
            if uploaded_code:
                raw_text = get_code_text(uploaded_code)
                text_chunks = get_text_chunks(raw_text)
                embeddings = OpenAIEmbeddings(model="text-embedding-3-small",
                                              openai_api_key=apiKey)
                vector_store = FAISS.from_texts(text_chunks,
                                                embedding=embeddings)
                vector_store.save_local("faiss_index")

                # Perform similarity search with user input
                docs = vector_store.similarity_search(user_input)
                response = Conversation.run(input=user_input + "\n\n" +
                                            str(docs))
            else:
                response = Conversation.run(input=user_input)

            current_chat["past"].append(user_input)
            current_chat["generated"].append(response)

            save_chat(st.session_state.current_chat, current_chat)
        else:
            st.write(
                "_This assistant only answers programming-related questions. Please ask a question related to programming._"
            )

        st.session_state.input_text = ""


def get_code_text(code_docs):
    text = ""
    for code in code_docs:
        text += code.read().decode(
            'utf-8')  # Assuming the code files are text-based
    return text


def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,
                                                   chunk_overlap=100)
    chunks = text_splitter.split_text(text)
    return chunks


# Sidebar with chat options
with st.sidebar:
    st.caption("Made with ❤️ by Kamal, Reka, Kopika, Deepesh & Ashir")
    st.title("Chats")
    if st.button("Create New Chat"):
        create_new_chat()

    for chat_name in redis_client.keys():
        if st.button(chat_name.decode("utf-8")):
            st.session_state.current_chat = chat_name.decode("utf-8")
            st.session_state.input_text = ""

# Main UI for chat interface
if st.session_state.current_chat:
    st.title(f"🤖 AI Coding Assistant")
    st.markdown(f"{st.session_state.current_chat}")

    # Display conversation history in a scrollable container
    current_chat = load_chat(st.session_state.current_chat)
    st.subheader("Conversation")
    with st.container():
        if current_chat["generated"]:
            for i in range(len(current_chat["generated"])):
                user_message = st.chat_message("user")
                ai_message = st.chat_message("assistant")
                user_message.write(f" {current_chat['past'][i]}")
                ai_message.write(f" {current_chat['generated'][i]}")
        else:
            st.write("_No conversation history yet._")

    # Input field with text input at the top and file uploader below
    st.text_input("your input",
                  value=st.session_state.input_text,
                  key="input_text",
                  placeholder="Ask a question related to programming...",
                  label_visibility="hidden",
                  on_change=process_input)

    # Add some space if needed
    st.write("")

    # File uploader below the input field
    uploaded_code = st.file_uploader(
        "Upload Code Files",
        type=["py", "c", "cpp", "java", "html", "css", "js"],
        accept_multiple_files=True,
        key="uploaded_code")

else:
    st.title("🤖 AI Coding Assistant")
    st.write("Please create or select a chat from the sidebar.")