from langchain.text_splitter import RecursiveCharacterTextSplitter
from ai_training.langchain_basics.loaders import load_text
from pathlib import Path

def split_documents(docs, chunk_size, chunk_overlap):
    splitter= RecursiveCharacterTextSplitter(chunk_size= chunk_size, chunk_overlap= chunk_overlap)
    chunks= splitter.split_documents(docs)
    return chunks

def get_chunk_stats(chunks):
    len_chunk= []
    for chunk in chunks:
        len_chunk.append(len(chunk.page_content))
    total_chunks= len(len_chunk)
    avg_chunk_size= int(sum(len_chunk) / total_chunks) if total_chunks > 0 else 0
    min_chunk_size= min(len_chunk) if total_chunks > 0 else 0
    max_chunk_size= max(len_chunk) if total_chunks > 0 else 0

    return{
        "total_chunks": total_chunks,
        "avg_chunk_size": avg_chunk_size,
        "min_chunk_size": min_chunk_size,
        "max_chunk_size": max_chunk_size,
    }

def enrich_chunk_metadata(chunks, doc_id):
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"]= i
        chunk.metadata["chunk_size"]= len(chunk.page_content)

        if doc_id is not None:
            chunk.metadata["doc_id"]= doc_id
        else:
            source_file= chunk.metadata.get("source", "Unknown_Source.txt")
            chunk.metadata["doc_id"]= Path(source_file).name
    return chunks

if __name__ == "__main__":
    docs= load_text(file_path= "data/inputs/ai_overview.txt")
    chunks= split_documents(docs= docs, chunk_size= 100, chunk_overlap= 20)
    chunks= enrich_chunk_metadata(chunks=chunks, doc_id="ai_overview")
    print(get_chunk_stats(chunks=chunks))
    print(chunks[0].page_content)
    print(chunks[0].metadata)
    chunks= split_documents(docs= docs, chunk_size= 500, chunk_overlap= 20)
    print(get_chunk_stats(chunks=chunks))
    print(chunks[0].page_content)