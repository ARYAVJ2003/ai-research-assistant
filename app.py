import streamlit as st

from graph import build_graph
from pdf_generator import create_pdf
from upload_pdf import extract_pdf_text,extract_txt_text

# build app
if "app_graph" not in st.session_state:

    st.session_state.app_graph = build_graph()

app_graph = st.session_state.app_graph

# title
st.title("AI Research Assistant")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = "user1"
 
if "all_messages" not in st.session_state:
    st.session_state.all_messages = {}
# user input
if "processing" not in st.session_state:
    st.session_state.processing = False


uploaded_file = st.file_uploader(
    "Upload PDF or TXT",
    type=["pdf", "txt"]
)
document_text = ""

if uploaded_file:

    if uploaded_file.type == "application/pdf":

        document_text = extract_pdf_text(
            uploaded_file
        )

    elif uploaded_file.type == "text/plain":

        document_text = extract_txt_text(
            uploaded_file
        )

    st.success("File uploaded successfully")

    if st.button("Summarize Document"):

     with st.spinner("Analyzing document..."):

        result = app_graph.invoke(
            {
                "input": f"Summarize this document:\n{document_text}"
            },
            config={
                "configurable": {
                    "thread_id": st.session_state.thread_id
                }
            }
        )

     st.write(result["output"])
# session memory

# sidebar
with st.sidebar:

    st.header("Settings")

    if st.button("Clear Chat"):

        st.session_state.all_messages[
        st.session_state.thread_id
    ] = []

    # new backend memory thread
    #st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

    thread_id = st.text_input(
        "Thread ID",
        value=st.session_state.thread_id
    )

    st.session_state.thread_id = thread_id
    if st.session_state.thread_id not in st.session_state.all_messages:

        st.session_state.all_messages[
        st.session_state.thread_id
    ] = []
    
    messages = st.session_state.all_messages[
    st.session_state.thread_id
]

#user_input = st.chat_input("Ask something...")
user_input= st.chat_input("Say something", disabled=st.session_state.processing)

    
# show old messages
for msg in messages:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# new message
if user_input:

    st.session_state.processing = True

    # save user message
    messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    # loading spinner
    with st.spinner("Thinking..."):

        result = app_graph.invoke(
            {
                "input": user_input
            },
            config={
                "configurable": {
                    "thread_id": st.session_state.thread_id
                }
            }
        )

        ai_output = result["output"]
        pdf_path=create_pdf(result["output"])

    # save ai response
    messages.append(
        {
            "role": "assistant",
            "content": ai_output
        }
    )

    st.session_state.processing = False

    with st.chat_message("assistant"):
        st.markdown(ai_output)  

    with open(pdf_path, "rb") as file:

     st.download_button(
        label="Download PDF",
        data=file,
        file_name="research_report.pdf",
        mime="application/pdf"
     )