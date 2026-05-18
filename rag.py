from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings,ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS

from dotenv import load_dotenv
import os

load_dotenv()
llm=ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0.7,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# embedding model
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)


# split large text into chunks
def split_text(document_text):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=50
    )

    chunks = splitter.split_text(document_text)

    return chunks


# create embeddings
def create_embeddings(chunks):

    vectors = embeddings.embed_documents(chunks)

    return vectors


def create_vector_store(chunks):

    vector_store = FAISS.from_texts(
        chunks,
        embedding=embeddings
    )

    return vector_store


def retrieve_chunks(vector_store, query):

    docs = vector_store.similarity_search(
        query,
        k=1
    )

    return docs

def ask_question(vector_store, question):

    docs = retrieve_chunks(
        vector_store,
        question
    )

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    prompt = f"""
    Answer the question ONLY using the context below.

    Context:
    {context}

    Question:
    {question}

    If answer is not in context,
    say:
    "I could not find the answer in the document."
    """

    result = llm.invoke(prompt)

    return result.content[0]['text']