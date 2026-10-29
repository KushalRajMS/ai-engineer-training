from langchain_community.vectorstores import FAISS
from ai_training.langchain_basics.ingestion import ingest_documents
from ai_training.langchain_basics.embeddings import make_embedder

def create_vector_store(chunks, embedder):
    return FAISS.from_documents(chunks, embedder)

def save_vector_store(vector_store, path):
    vector_store.save_local(path)

def load_vector_store(path, embedder):
    return FAISS.load_local(path, embedder, allow_dangerous_deserialization=True)

def search(vector_store, query, k=3):
    return vector_store.similarity_search(query, k)

def make_retriever(vector_store, k=3):
    return vector_store.as_retriever(search_kwargs={"k": k})

def search_with_scores(vector_store, query, k=3):
    return vector_store.similarity_search_with_score(query, k=k)

if __name__ == "__main__":
    chunks= ingest_documents(source_path="data/inputs/")
    embedder= make_embedder()
    loaded_vector= load_vector_store("artifacts/vector_store/", embedder)
    retriever= make_retriever(loaded_vector, k=2)
    print(retriever.invoke("What is Python?"))
    result= search_with_scores(loaded_vector, "What is Python?")
    # print(result)
    print(result[0][0].page_content)
    print(result[0][1])