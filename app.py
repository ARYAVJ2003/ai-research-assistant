import streamlit as st

from graph import build_graph
from pdf_generator import create_pdf
from upload_pdf import extract_pdf_text,extract_txt_text
from rag import (
    split_text,
    create_vector_store,
    ask_question
)

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
if "chat_sessions" not in st.session_state:

    st.session_state.chat_sessions = [
        "Chat 1"
    ]
if "thread_documents" not in st.session_state:
    st.session_state.thread_documents = {}
    
if "thread_vectorstores" not in st.session_state:
    st.session_state.thread_vectorstores = {}
# user input
if "processing" not in st.session_state:
    st.session_state.processing = False
if "last_pdf" not in st.session_state:
    st.session_state.last_pdf = None

if st.session_state.thread_id not in st.session_state.thread_documents:
    st.session_state.thread_documents[
        st.session_state.thread_id
    ] = ""

document_text = st.session_state.thread_documents[
    st.session_state.thread_id
]


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

    st.subheader("Chats")

    for chat in st.session_state.chat_sessions:

      label = chat

      if chat == st.session_state.thread_id:
        label = f"➡️ {chat}"

      if st.button(label):

         st.session_state.thread_id = chat

         st.rerun()
      
    if st.button("+ New Chat"):

     new_chat = f"Chat {len(st.session_state.chat_sessions) + 1}"

     st.session_state.chat_sessions.append(
        new_chat
    )

     st.session_state.thread_id = new_chat

     st.session_state.all_messages[
        new_chat
    ] = []

     st.rerun()
  
    if st.session_state.thread_id not in st.session_state.all_messages:

         st.session_state.all_messages[
         st.session_state.thread_id
    ] = []
    
messages = st.session_state.all_messages[
    st.session_state.thread_id
]


    
# show old messages
for msg in messages:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
#st.subheader("📄 Document Tools")
with st.expander("📄 Document Tools"):
    uploaded_file = st.file_uploader(
        "Upload PDF or TXT",
        type=["pdf", "txt"],
        key=f"uploader_{st.session_state.thread_id}"

    )
    if uploaded_file:

        if uploaded_file.type == "application/pdf":

            document_text = extract_pdf_text(
                uploaded_file
            )

            st.session_state.thread_documents[
        st.session_state.thread_id
    ] = document_text
            chunks = split_text(document_text)

            vector_store = create_vector_store(chunks)

            st.session_state.thread_vectorstores[
        st.session_state.thread_id
    ] = vector_store

        elif uploaded_file.type == "text/plain":

            document_text = extract_txt_text(
                uploaded_file
            )
            chunks = split_text(document_text)

            vector_store = create_vector_store(chunks)

            st.session_state.thread_vectorstores[
        st.session_state.thread_id
    ] = vector_store
            st.session_state.thread_documents[
        st.session_state.thread_id
    ] = document_text

        st.success("File uploaded successfully")
        document_question = st.text_input(
        "Ask question about document"
    )
        col1, col2 = st.columns(2)  
        with col1:
        
            summarize_clicked = st.button(
                "Summarize Document"
            )
            if summarize_clicked:
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
                
                messages.append(
                {
                    "role": "user",
                    "content": "Summarize uploaded document"
                }
            )

                messages.append(
                {
                    "role": "assistant",
                    "content": result["output"]
                }

            )
                st.session_state.last_pdf = create_pdf(
    result["output"]
)
                st.rerun()
                #st.write(result["output"])
    # session memory
    
        
        with col2:

            ask_clicked = st.button(
                "Ask Document"
            )  
            if ask_clicked:
                if document_question:

                    vector_store = st.session_state.thread_vectorstores.get(
                    st.session_state.thread_id
                )
                else:
                    st.warning("ask question")  
                    st.stop()

                if vector_store:

                    with st.spinner("Searching document..."):
                        conversation_history = ""

                        for msg in messages[-6:]:

                         conversation_history += (
                    f"{msg['role']}: {msg['content']}\n")

                        full_question = f"""
            Conversation History:
            {conversation_history}

            Current Question:
            {document_question}
            """
                
                        answer = ask_question(
                            vector_store,
                            full_question
                        )

                    #st.write(answer)
                        messages.append(
                {
                    "role": "user",
                    "content": document_question
                }
            )

                        messages.append(
                {
                    "role": "assistant",
                    "content":answer
                }
            ) 
                        st.session_state.last_pdf = create_pdf(
    answer
)
                        st.rerun()

                else:

                    st.warning("Upload a document first")
#user_input = st.chat_input("Ask something...")


# new message
user_input= st.chat_input("Say something", disabled=st.session_state.processing)
if user_input:

    st.session_state.processing = True

    # save user message
    messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    #with st.chat_message("user"):
      #  st.markdown(user_input)

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
        st.session_state.last_pdf = create_pdf(
    result["output"]
)

    # save ai response
    messages.append(
        {
            "role": "assistant",
            "content": ai_output
        }
    )
    st.session_state.processing = False

    st.rerun()
   
    #with st.chat_message("assistant"):
      #  st.markdown(ai_output)  

if st.session_state.last_pdf:

     with open(
        st.session_state.last_pdf,
        "rb"
    ) as file:

      st.download_button(
        label="Download PDF",
        data=file,
        file_name="research_report.pdf",
        mime="application/pdf"
     )