import os
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader
from langchain_mistralai import MistralAIEmbeddings, ChatMistralAI
from dotenv import load_dotenv
import uuid

try:
    from langchain_community.document_loaders import UnstructuredImageLoader
    IMAGE_SUPPORT = True
except ImportError:
    IMAGE_SUPPORT = False

try:
    from langchain_community.document_loaders import UnstructuredPowerPointLoader
    PPTX_SUPPORT = True
except ImportError:
    PPTX_SUPPORT = False

load_dotenv()

mistral_api_key = os.getenv("MISTRAL_API_KEY")
embedding_model = MistralAIEmbeddings(api_key=mistral_api_key)
llm = ChatMistralAI(api_key=mistral_api_key)


def get_chroma_client():
    """Initialize and return ChromaDB client"""
    client = chromadb.PersistentClient(path="./chroma_db")
    return client


def extract_text_from_file(file_path: str):
    ext = os.path.splitext(file_path)[-1].lower()

    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext == ".docx":
        loader = Docx2txtLoader(file_path)
    elif ext == ".pptx":
        if not PPTX_SUPPORT:
            raise ValueError(
                "PowerPoint support not installed. Install with: pip install python-pptx unstructured"
            )
        loader = UnstructuredPowerPointLoader(file_path)
    elif ext in [".jpg", ".jpeg", ".png"]:
        if not IMAGE_SUPPORT:
            raise ValueError(
                "Image support not installed. Install with: pip install pillow unstructured"
            )
        loader = UnstructuredImageLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    return loader.load()


def process_and_embed(file_path: str):
    documents = extract_text_from_file(file_path)

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)

    texts = [chunk.page_content for chunk in chunks]
    vectors = embedding_model.embed_documents(texts)

    embedded_chunks = [
        {
            "text": chunk.page_content,
            "metadata": chunk.metadata,
            "embedding": vectors[i],
        }
        for i, chunk in enumerate(chunks)
    ]

    return embedded_chunks


def save_to_chromadb(embedded_chunks, client, collection_name="documents"):
    """Save embedded chunks to ChromaDB"""
    try:
        collection = client.get_collection(name=collection_name)
    except:
        collection = client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    ids = [str(uuid.uuid4()) for _ in embedded_chunks]
    documents = [chunk["text"] for chunk in embedded_chunks]
    embeddings = [chunk["embedding"] for chunk in embedded_chunks]
    metadatas = []

    for chunk in embedded_chunks:
        metadata = chunk["metadata"]
        if not isinstance(metadata, dict):
            metadata = {"source": str(metadata)}

        metadata = {k: str(v) for k, v in metadata.items()}
        metadatas.append(metadata)

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )

    return collection


def answer_query(query: str, client, collection_name="documents", top_k: int = 5):
    """Query ChromaDB and generate answer using LLM"""
    try:
        collection = client.get_collection(name=collection_name)
    except:
        return "No documents found. Please upload documents first."

    query_vector = embedding_model.embed_query(query)

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k
    )

    if not results["documents"] or not results["documents"][0]:
        return "No relevant context found."

    context = "\n\n".join(results["documents"][0])

    prompt = f"Answer the following question using the context below:\n\nContext:\n{context}\n\nQuestion: {query}"
    response = llm.invoke(prompt)
    return response.content.replace("\n", " ").strip()


def get_supported_formats():
    """Return list of supported file formats"""
    formats = ["pdf", "docx"]
    if PPTX_SUPPORT:
        formats.append("pptx")
    if IMAGE_SUPPORT:
        formats.extend(["jpg", "jpeg", "png"])
    return formats