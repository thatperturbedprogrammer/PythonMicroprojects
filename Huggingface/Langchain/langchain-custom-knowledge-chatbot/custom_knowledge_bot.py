import os
from dotenv import load_dotenv
from langchain_community.llms import HuggingFaceHub
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
import gradio as gr

load_dotenv()   # Load API key from .env file

# Fetch the API key
huggingface_api_key = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# Ensure the API key is set
if not huggingface_api_key:
    raise ValueError("Hugging Face API key is missing! Add it to your .env file.")
    
llm = HuggingFaceHub(
    repo_id="mistralai/Mistral-7B-v0.1",  # Public version of Mistral
    model_kwargs={"temperature": 0.7, "max_length": 200}
)

# Load documents from a text file
loader = TextLoader("data.txt")
documents = loader.load()

# Split long documents into smaller chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = splitter.split_documents(documents)

# Convert text into vector embeddings using a free model
embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Store the embeddings in FAISS
db = FAISS.from_documents(docs, embedding_function)
retriever = db.as_retriever()

qa_chain = RetrievalQA(llm=llm, retriever=retriever)

def chatbot(query):
     """Processes user queries and returns AI-generated responses."""
     return qa_chain.run(query)

interface = gr.Interface(
    fn=chatbot,
    inputs="text",
    outputs="text",
    title="Custom Knowledge Chatbot",
    description="Ask me anything based on the loaded knowledge!"
)

interface.launch()