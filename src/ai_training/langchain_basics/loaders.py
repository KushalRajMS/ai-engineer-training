from langchain_community.document_loaders import TextLoader, PyPDFLoader, DirectoryLoader

def load_text(file_path: str) -> list:
    try:
        loader= TextLoader(file_path= file_path)
        docs = loader.load()
        return docs
    except ValueError:
        return []

def load_pdf(file_path: str) -> list:
    try:
        loader= PyPDFLoader(file_path= file_path)
        docs= loader.load()
        return docs
    except ValueError:
        return []

def load_directory(dir_path: str, extension: list[str]) -> list:
    loader_map= {
        ".txt": TextLoader,
        ".pdf": PyPDFLoader,
    }
    all_docs= []
    for pattern in extension:
        ext= f".{pattern.split('.')[-1]}"
        loader= loader_map.get(ext)
        try:
            dir_loader= DirectoryLoader(path= dir_path, glob= pattern, loader_cls= loader)
            docs= dir_loader.load()
            all_docs.extend(docs)
        except (ValueError, Exception):
            continue
    return all_docs

if __name__ == "__main__":
    text= load_text(file_path= "data/inputs/ai_overview.txt")
    print(text)
    dir_load= load_directory(dir_path= "data/inputs/", extension= "**/*.txt")
    print(dir_load)