from pathlib import Path
from ai_training.langchain_basics.loaders import load_text, load_directory, load_pdf
from ai_training.langchain_basics.splitters import split_documents, enrich_chunk_metadata

def ingest_documents(source_path, chunk_size= 500, chunk_overlap= 50, doc_id= None):
    source = Path(source_path)
    if source.is_file():
        if str(source.suffix) == ".txt":
            docs= load_text(source_path)
        elif str(source.suffix) == ".pdf":
            docs= load_pdf(source_path)
    elif source.is_dir():
        docs= load_directory(source_path, extension="**/*.txt")
    chunks= split_documents(docs= docs, chunk_size= chunk_size, chunk_overlap= chunk_overlap)
    chunks= enrich_chunk_metadata(chunks= chunks, doc_id= doc_id)
    return chunks

if __name__ == "__main__":
    chunks= ingest_documents(source_path="data/inputs/ai_overview.txt")
    print(chunks)
    chunks= ingest_documents(source_path="data/inputs/")
    print(chunks)