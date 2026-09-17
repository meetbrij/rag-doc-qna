# Conversational RAG Document Q&A with History (Groq & Llama)

A Conversational RAG (Retrieval-Augmented Generation) application built with Streamlit and LangChain that allows users to upload multiple PDFs and query them via Groq's Llama models. Featuring chat history retention and history-aware document retrieval, it ensures contextually accurate answers directly sourced from your files.

## 🚀 Features
- **Multi-File Uploads:** Drag and drop multiple PDF documents simultaneously right from the UI.
- **Context-Aware Memory:** Remembers historical conversational context so you can ask natural follow-up questions.
- **Open-Source Local Embeddings:** Completely eliminates dependency on paid OpenAI APIs by processing vector spaces locally via HuggingFace's `all-MiniLM-L6-v2`.
- **Lightning-Fast Generation:** Backed by Groq's ultra-low latency compute engine running `llama-3.1-8b-instant`.
- **Transparency:** Expandable citation sections showing exact source chunks pulled from your documents during similarity lookups.

## 🛠️ Tech Stack
- **Framework:** [Streamlit](https://streamlit.io)
- **Orchestration:** [LangChain](https://www.langchain.com/)
- **LLM Engine:** [Groq Cloud (Llama 3.1 8B)](https://groq.com)
- **Embeddings:** [HuggingFace (Sentence Transformers)](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- **Vector Store:** [FAISS (Facebook AI Similarity Search)](https://github.com)

## 📋 Prerequisites
Before setting up, make sure you have:
- Python 3.9 or higher installed.
- A **Groq API Key** (Get one for free from the [Groq Console](https://groq.com)).

## ⚙️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com
   cd YOUR_REPO_NAME
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate

   # On Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Environment Variables:**
   Create a `.env` file in the root directory of your project and paste your Groq API key:
   ```env
   GROQ_API_KEY=your_actual_groq_api_key_here
   ```

## 🖥️ Running the Application

Launch the app with Streamlit:
```bash
streamlit run app.py
```

## 💡 How to Use
1. Upload one or more PDF files via the sidebar/uploader tool.
2. Click the **"Process & Embed Documents"** button to parse the PDFs and initialize the local FAISS vector database.
3. Type a query based on the uploaded contents inside the input prompt box.
4. Review responses alongside their matched source text snippets within the collapsible layout expander.