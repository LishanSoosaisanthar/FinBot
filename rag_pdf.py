import os
import tempfile
import streamlit as st
from langchain.document_loaders import PyPDFLoader
from dotenv import load_dotenv

from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS

from web_template import css, bot_template, user_template

llm = ChatOpenAI(model="gpt-4o-2024-05-13", temperature=0)

### Contextualize question ###
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

### Answer question ###
system_prompt = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, say that you "
    "don't know."
    "\n\n"
    "{context}"
)
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

### Statefully manage chat history ###
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

def create_retriever_from_pdf(file_bytes):
    # Save the PDF file bytes to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(file_bytes)
        tmp_file_path = tmp_file.name
    
    loader = PyPDFLoader(file_path=tmp_file_path)
    data = loader.load()
    
    # Clean up the temporary file
    os.remove(tmp_file_path)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
    docs = text_splitter.split_documents(data)

    for i, doc in enumerate(docs):
        doc.metadata['page'] = i

    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(documents=docs, embedding=embeddings)
    retriever = vectorstore.as_retriever()
    return retriever

def create_conversational_rag_chain(llm, retriever):
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    
    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )
    
    return conversational_rag_chain

def process_query(query_text):
    response = st.session_state.conversation.invoke(
        {"input": query_text, "chat_history": st.session_state.chat_history},
        config={"configurable": {"session_id": "unique_session_id"}}
    )
    st.session_state.chat_history.append({"question": query_text, "answer": response["answer"]})
    
    # Display the entire chat history
    for message in st.session_state.chat_history:
        st.write(user_template.replace("{{MSG}}", message["question"]), unsafe_allow_html=True)
        st.write(bot_template.replace("{{MSG}}", message["answer"]), unsafe_allow_html=True)

def run_rag_app(configured=False):
    load_dotenv()

    if not configured:
        st.set_page_config(page_title="Chat with PDFs", page_icon=":books:", layout="wide")
    st.image("baasha.jpg")

    st.write(css, unsafe_allow_html=True)

    st.header("Hi, I am FinBot")
      # Add instructions for using the RAG component
    st.info(
    """
    **How to Use the RAG PDF ChatBot:**
    
    1. **Upload a PDF**: Use the sidebar to upload your PDF document.
    2. **Run the Analysis**: After uploading, click **Run**. FinBot will begin processing the document.
    3. **Ask Questions**: Once processing is complete, type any question about the PDF content in the text box below. FinBot will analyze the document and provide a concise, relevant answer.
    4. **View Chat History**: Every question and response is recorded in the chat, allowing you to review previous interactions. FinBot remembers the context of your conversation, enabling it to build on prior questions and responses, making the experience similar to conducting a conversation with a human assistant.
    """)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    with st.sidebar:
        st.subheader("PDF documents")
        uploaded_file = st.file_uploader("Upload your PDF file", type=["pdf"], accept_multiple_files=False)
        if st.button("Run"):
            if uploaded_file:
                with st.spinner("Processing..."):
                    pdf_bytes = uploaded_file.read()
                    retriever = create_retriever_from_pdf(pdf_bytes)
                    
                    # Create a conversational RAG chain
                    st.session_state.conversation = create_conversational_rag_chain(llm, retriever)
                    
                    # Initialize conversation history
                    st.session_state.chat_history = []

    if st.session_state.conversation:
        query = st.text_input("How can I help you today?")
        if query:
            process_query(query)

if __name__ == "__main__":
    run_rag_app()
