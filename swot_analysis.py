import streamlit as st  # This makes the window for our magic box.
from langchain.chains import MapReduceDocumentsChain, ReduceDocumentsChain, LLMChain, StuffDocumentsChain  # These are tools to read and summarize the book.
from langchain_text_splitters import CharacterTextSplitter  # This tool cuts the book into smaller pieces.
from langchain_core.prompts import PromptTemplate  # This helps us ask our smart friend the right questions.
from langchain_openai import ChatOpenAI  # This is our super smart friend.
from langchain_community.document_loaders import PyPDFLoader  # This helps our box read PDF files.
from tempfile import NamedTemporaryFile  # This helps our box save the book temporarily.

# This function does the magic work of reading and summarizing the book.
def generate_swot_analysis(uploaded_file):
    with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name
    
    loader = PyPDFLoader(file_path=tmp_file_path)
    docs = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = text_splitter.split_documents(docs)

    llm = ChatOpenAI(model="gpt-4o-2024-05-13", temperature=0)

    map_template = """The following is a set of documents:
    {docs}
    Based on this list of docs, please identify the strengths, weaknesses, opportunities, and threats.
    and create SWOT Analysis report only based on the given document. Use only information given in the document:"""
    map_prompt = PromptTemplate.from_template(map_template)
    map_chain = LLMChain(llm=llm, prompt=map_prompt)

    reduce_template = """The following is a set of SWOT analyses:
    {docs}
    Take these and distill them into a final, consolidated SWOT analysis in the form of a report.
    Consolidated SWOT Analysis report based on the given information only.:"""
    reduce_prompt = PromptTemplate.from_template(reduce_template)
    reduce_chain = LLMChain(llm=llm, prompt=reduce_prompt)
    combine_documents_chain = StuffDocumentsChain(
        llm_chain=reduce_chain, document_variable_name="docs"
    )
    reduce_documents_chain = ReduceDocumentsChain(
        combine_documents_chain=combine_documents_chain,
        collapse_documents_chain=combine_documents_chain,
        token_max=4000,
    )

    map_reduce_chain = MapReduceDocumentsChain(
        llm_chain=map_chain,
        reduce_documents_chain=reduce_documents_chain,
        document_variable_name="docs",
        return_intermediate_steps=False,
    )

    result = map_reduce_chain.invoke(split_docs)
    return result["output_text"]

# This is the window where we can interact with our magic box.
def main():
    st.title("FinBot-SWOT Analysis")

    # Instruction for users
    st.info(
    """
    **How to Use the PDF SWOT Analysis Generator:**
    
    1. **Upload a PDF**: Use the file uploader below to load your document.
    2. **Generate Analysis**: Once your document is uploaded, click the "Generate SWOT Analysis" button to start the analysis.
    3. **View Results**: The generated SWOT analysis based on the uploaded document will be displayed below.
    """)


    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
    if st.button("Generate SWOT Analysis"):
        if uploaded_file:
            with st.spinner("Generating SWOT analysis..."):
                swot_analysis = generate_swot_analysis(uploaded_file)
                st.write(swot_analysis)
        else:
            st.write("Please upload a PDF file.")

if __name__ == "__main__":
    main()
