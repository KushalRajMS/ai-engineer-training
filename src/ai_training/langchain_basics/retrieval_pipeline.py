from ai_training.langchain_basics.ingestion import ingest_documents
from ai_training.langchain_basics.embeddings import make_embedder
from ai_training.langchain_basics.vector_store import create_vector_store, save_vector_store, make_retriever

def build_retrieval_pipeline(source_path, store_path, k=3):
    chunks= ingest_documents(source_path)
    embeder= make_embedder()
    vector_store= create_vector_store(chunks, embeder)
    save_vector_store(vector_store, store_path)
    return(make_retriever(vector_store, k=k))

def query_pipeline(retriever, question):
    results= retriever.invoke(question)
    contents= []
    for result in results:
        contents.append(result.page_content)
    return contents

if __name__ == "__main__":
    retriever= build_retrieval_pipeline(
        source_path= "data/inputs/",
        store_path= "artifacts/vector_store/",
        k=2
    )
    results= query_pipeline(retriever, "What is Python?")
    for r in results:
        print(r)
        print("---")