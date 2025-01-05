import streamlit as st
from compare_pdf import process_pdf, ask_question
from rag_pdf import run_rag_app
from swot_analysis import main as gen_main  # Import the new module

def main():
    st.set_page_config(page_title="FinBot: Your Financial Analyst 📄", page_icon=":books:", layout="wide")

    st.title("FinBot: Your Financial Analyst 📄")

    st.sidebar.title("Navigation")
    app_mode = st.sidebar.radio("Go to", ["Generate SWOT Analysis", "RAG for PDF", "Compare two PDFs"])

    if app_mode == "Compare two PDFs":
        st.header("FinBot-Compare PDFs")

        # Info box for guidance
        st.info(
            """
            **Guide to Using the PDF Comparison Tool:**

            1. **Upload PDF Files**: Use the file uploader below to upload two PDF files for analysis.
            2. **Enter Your Question**: Once your files are uploaded, type a question in the input box to explore differences or similarities between the documents.
            3. **Submit and View Results**: Click "Submit" to receive insights based on the content of the uploaded documents.
            """
        )

        # File uploader for PDF documents
        uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

        # Only process the PDF files once and store the agent in session state
        if uploaded_files:
            if "agent" not in st.session_state:
                st.session_state.agent = process_pdf(uploaded_files)

            # Input for user question
            user_question = st.text_input("Your question:")

            if st.button("Submit"):
                if user_question:
                    # Pass the question to the agent and get the response
                    result = ask_question(st.session_state.agent, user_question)
                    st.write(result)
                else:
                    st.write("Please enter a question.")
        else:
            st.write("Please upload PDF files to get started.")

    elif app_mode == "RAG for PDF":
        st.header("FinBot-RAG")
        run_rag_app(configured=True)

    elif app_mode == "Generate SWOT Analysis":
        gen_main()  # Call the main function from swot_analysis.py

if __name__ == "__main__":
    main()
