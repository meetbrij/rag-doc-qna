import streamlit as st 
import os 
import tempfile
import time
from dotenv import load_dotenv 

from langchain_groq import ChatGroq 
from langchain_huggingface import HuggingFaceEmbeddings # <--- Free, local embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.chains.combine_documents import create_stuff_documents_chain 
from langchain_classic.chains import create_retrieval_chain, create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder 
from langchain_community.chat_message_histories import ChatMessageHistory 
from langchain_core.chat_history import BaseChatMessageHistory 
from langchain_core.runnables.history import RunnableWithMessageHistory 
from langchain_community.vectorstores import FAISS 
from langchain_community.document_loaders import PyPDFLoader

load_dotenv() 

## Cleaned up: Only checking for Groq API key now
if not os.getenv("GROQ_API_KEY"):
    st.warning("Please ensure GROQ_API_KEY is configured in your environment or .env file.")

os.environ['GROQ_API_KEY'] = os.getenv("GROQ_API_KEY", "") 
groq_api_key = os.getenv("GROQ_API_KEY") 

llm = ChatGroq(groq_api_key=groq_api_key, model_name="openai/gpt-oss-20b")

## Langsmith Tracking
os.environ["LANGCHAIN_API_KEY"]=os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_PROJECT"]="RAG DOC QNA"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = ChatMessageHistory()

if "vectors" not in st.session_state:
    st.session_state.vectors = None

st.title("RAG Document Q-n-A With History (Groq & Llama)")

uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)

if st.button("Process & Embed Documents"):
    if uploaded_files:
        all_docs = []
        
        # 1. Start the loading spinner animation
        with st.spinner("Parsing PDFs and generating vector embeddings. Please wait..."):
            with tempfile.TemporaryDirectory() as temp_dir:
                for uploaded_file in uploaded_files:
                    temp_filepath = os.path.join(temp_dir, uploaded_file.name)
                    with open(temp_filepath, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    loader = PyPDFLoader(temp_filepath)
                    all_docs.extend(loader.load())
                
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200) 
                final_documents = text_splitter.split_documents(all_docs) 
                
                embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
                st.session_state.vectors = FAISS.from_documents(final_documents, embeddings)
        
        # 2. Once the 'with' block completes, the spinner hides and this success message appears
        st.success("Vector Database is ready! You can now type your queries below.")
    else:
        st.error("Please upload at least one PDF file first.")

user_prompt = st.text_input("Enter your query from the research paper:")

if user_prompt:
    if st.session_state.vectors is None:
        st.error("Please upload files and click the 'Process & Embed Documents' button before submitting queries.")
    else:
        retriever = st.session_state.vectors.as_retriever()

        contextualize_q_system_prompt = (
            "Given a chat history and the latest user question "
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, "
            "just reformulate it if needed and otherwise return it as is."
        )
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        
        history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)

        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, say that you don't know. Use five sentences maximum and keep the answer concise.\n\n<context>\n{context}\n</context>"),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        
        document_chain = create_stuff_documents_chain(llm, qa_prompt)
        retrieval_chain = create_retrieval_chain(history_aware_retriever, document_chain)

        def get_session_history(session_id: str) -> BaseChatMessageHistory:
            return st.session_state.chat_history

        conversational_rag_chain = RunnableWithMessageHistory(
            retrieval_chain,
            get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )

        start = time.process_time()
        response = conversational_rag_chain.invoke(
            {"input": user_prompt},
            config={"configurable": {"session_id": "streamlit_session"}}
        )
        
        print(f"Response time: {time.process_time() - start}")
        
        st.subheader("Answer:")
        st.write(response['answer'])

        with st.expander("Document similarity Source Chunks"):
            for i, doc in enumerate(response['context']):
                st.write(f"**Chunk {i+1}:** Source: {os.path.basename(doc.metadata.get('source', 'Unknown'))}")
                st.write(doc.page_content)
                st.write('------------------------')