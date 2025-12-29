Mistral RAG System

A lightweight Retrieval-Augmented Generation (RAG) application built with FastAPI and ChromaDB.
It allows you to upload documents, store them in a local vector database, and ask questions that are answered using Mistral AI.

-> Quick Start
1. Install Dependencies
pip install -r requirements.txt

2. Configure Environment
Create a .env file and add your Mistral API key:

MISTRAL_API_KEY=your_actual_mistral_api_key

You can get your key from: https://console.mistral.ai

3. Run the Application
Start the FastAPI backend:
uvicorn main:app --reload

Start the Streamlit frontend (if included):
streamlit run app.py

Then open your browser at http://localhost:8501.

-> Project Structure
rag-system/
│
├── app.py           # Streamlit frontend
├── main.py          # FastAPI backend
├── utils.py         # Helper functions
├── requirements.txt # Dependencies
├── .env.example     # Example environment variables
├── uploads/         # Uploaded documents
└── chroma_db/       # Vector database storage

-> Tech Stack

FastAPI – Backend API
ChromaDB – Local vector store
Mistral AI – LLM for answering questions
Streamlit – Simple web frontend

-> License
This project is open-source and available under the MIT License.