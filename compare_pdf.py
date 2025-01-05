import re
from tempfile import NamedTemporaryFile
from langchain.agents import Tool, AgentType, initialize_agent
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain_core.pydantic_v1 import BaseModel, Field

# Define the schema for document input
class DocumentInput(BaseModel):
    question: str = Field()

# Initialize the language model
llm = ChatOpenAI(model="gpt-4o-2024-05-13", temperature=0)

def process_pdf(uploaded_files):
    tools = []

    # Process each uploaded PDF file and create a retriever tool for each
    for uploaded_file in uploaded_files:
        with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_file_path = tmp_file.name

        # Load and split PDF content
        loader = PyPDFLoader(tmp_file_path)
        pages = loader.load_and_split()

        # Split text into chunks for embeddings
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
        docs = text_splitter.split_documents(pages)

        # Create embeddings and retriever
        embeddings = OpenAIEmbeddings()
        retriever = FAISS.from_documents(docs, embeddings).as_retriever()

        sanitized_name = re.sub(r'[^a-zA-Z0-9_-]', '_', uploaded_file.name)
        
        # Create a tool for each PDF file
        tools.append(
            Tool(
                args_schema=DocumentInput,
                name=sanitized_name,
                description=f"useful when you want to answer questions about {sanitized_name}",
                func=RetrievalQA.from_chain_type(llm=llm, retriever=retriever),
            )
        )

    # Initialize the agent with the tools created
    agent = initialize_agent(
        agent=AgentType.OPENAI_FUNCTIONS,
        tools=tools,
        llm=llm,
        verbose=True,
    )

    return agent

def ask_question(agent, question):
    # Use the agent to process the user's question and return the response
    result = agent({"input": question})
    return result["output"]
