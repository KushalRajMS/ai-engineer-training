from ai_training.config import APP_CONFIG
from langchain_huggingface import HuggingFaceEmbeddings
from ai_training.langchain_basics.ingestion import ingest_documents

def make_embedder(model= APP_CONFIG["embed_model"]):
    return HuggingFaceEmbeddings(model_name= model)

def embed_query(embedder, query):
    return embedder.embed_query(query)

def embed_chunks(embedder, chunks):
    vectors= []
    for chunk in chunks:
        vectors.append(embedder.embed_query(chunk.page_content))
    return vectors

if __name__ == "__main__":
    embedder= make_embedder()
    print(embed_query(embedder= embedder, query= "What is artificial intelligence?"))
    chunks= ingest_documents(source_path= "data/inputs/ai_overview.txt")
    print(len(embed_chunks(embedder= embedder, chunks= chunks)))