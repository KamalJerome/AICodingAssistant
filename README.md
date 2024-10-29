# 🤖 AI Coding Assistant

An intelligent assistant designed to simplify programming by offering real-time help on coding queries, giving precise answers, and generating code snippets to boost productivity. This assistant uses a hybrid Retrieval-Augmented Generation (RAG) model to analyze code files (`.py`, `.c`, `.cpp`, etc.) and answer questions based on the code content.

## Key Features

- ✅ **Code-based Answers**: Provides context-aware responses by examining and understanding the code in your files.
- ❓ **Programming-Specific Q&A**: Restricted to only programming-related questions, delivering expert responses on various programming languages.
- 📜 **Embedded RAG Model**: Integrates a hybrid RAG model for storing and retrieving detailed programming knowledge from custom file inputs.
- 🔍 **Advanced Search and Recall**: Uses Redis for efficient data retrieval and OpenAI embeddings for relevance ranking.
- 🧩 **Interactive Console**: Simple and interactive user interface powered by Streamlit for ease of use.

## Technologies Used

- 🤖 OpenAI's `gpt-4o` for natural language understanding and response generation.
- ⚙️ `text-embedding-3-small` for code and query embeddings.
- 🧩 **Streamlit** for the front-end interface.
- 📅 **Redis** for quick, indexed access to knowledge base entries.
- 🐍 **Python** for core application logic.

## Getting Started

AI Coding Assistant has been deployed here: https://aicodingassistant.streamlit.app/

**HOW TO USE:**

1. Upload Code Files: Load your code files to initialize the assistant’s knowledge base.
2. Ask Programming Questions: Type a coding question related to your files or general programming.
3. Receive Code-Specific Answers: The assistant will respond with context-based answers, code snippets, or explanations, drawing information from the loaded code files.

## Demo Video
[![Watch the video](https://img.youtube.com/vi/DcS94kOBI4U/maxresdefault.jpg)](https://youtu.be/DcS94kOBI4U)

### [Watch this video on YouTube](https://youtu.be/DcS94kOBI4U)

## Creators
V Kamal Jerome | Shakthireka Karthikeyan | Kopika M | Deepesh Raj AY | Ashirvad Janardanan V
