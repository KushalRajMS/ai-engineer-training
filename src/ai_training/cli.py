import typer
import json
from pathlib import Path
from ai_training.chat.chatbot import ChatBot
from ai_training.providers.groq import GroqProvider
from ai_training.providers.mock import MockProvider
from ai_training.chat.profiles import PROMPT_PROFILES
from ai_training.pipeline.summarizer import Summarizer
from ai_training.pipeline.file_loader import FileLoader
from ai_training.pipeline.output_writer import OutputWriter
from ai_training.langchain_basics.rag import build_retrieval_pipeline, run_rag_with_sources
from ai_training.langchain_basics.chains import make_llm
from ai_training.langchain_basics.ingestion import ingest_documents
from ai_training.langchain_basics.embeddings import make_embedder
from ai_training.langchain_basics.vector_store import create_vector_store, save_vector_store, load_vector_store, make_retriever
from ai_training.config import ARTIFACTS_DIR
from typing import Optional

app = typer.Typer(help="Chat with a bot, Summarize a File, Process batch file summary report.")

def _make_provider(provider_name: str, model: Optional[str] = None):
    name = provider_name.strip().lower()
    if name == "groq":
        if model is None:
            return GroqProvider()
        return GroqProvider(model= model)
    elif name == "mock":
        return MockProvider()
    else:
        typer.echo(f"Unknown provider '{provider_name}'. Valid options: groq, mock.")
        raise typer.Exit(code=1)

@app.command(help="Chat with a bot.")
def bot(
    provider_name: str = typer.Option("groq", "--provider", help="Provider to use: groq or mock"),
    model: Optional[str] = typer.Option(None, "--model", help="Model name"),
    prompt_mode: str = typer.Option("default", "--prompt-mode", help="Provide your profile mode."),
    stream: bool = typer.Option(False, "--stream", help="Provider in stream mode.")
):
    prompt_mode = prompt_mode.strip().lower()
    if prompt_mode not in PROMPT_PROFILES:
        typer.echo(f"Unknown prompt mode '{prompt_mode}'. Valid: {list(PROMPT_PROFILES.keys())}. Using 'default'.")
        prompt_mode = 'default'

    provider = _make_provider(provider_name= provider_name, model= model)
    chat = ChatBot(provider= provider, profile= prompt_mode)
    while True:
        prompt = input("User: ")
        if prompt.lower() == "exit":
            break

        try:
          if stream:
            print("Assistant: ", end="", flush=True)
            for chunk in chat.stream_message(prompt=prompt):
                print(chunk, end="", flush=True)
            print()
          else: 
            print("Assistant: " + chat.send_message(prompt= prompt))
        except ValueError as error:
            print(f"Error: {error}")

@app.command(help="Summarize a File.")
def summarize_file(
    input_file: str = typer.Argument(..., help="Path of the text file to summarize."),
    provider_name: str = typer.Option("groq", "--provider", help="Provider to use: groq or mock."),
    model: Optional[str] = typer.Option(None, "--model", help="Provide model: model valid only for groq."),
    style: str = typer.Option("brief", "--style", help="Style provides brief, detailed, bullet points summary of file(s).")
):
    provider = _make_provider(provider_name= provider_name, model= model)
    summarize = Summarizer()
    file_loader = FileLoader()
    filepath = Path(input_file)
    content = file_loader.read_file_content(file_path= filepath)
    if content is None:
        print(f"{filepath} file doesnt exist or permission issue. Please check.")
        return None
    file_dict = {
        "filename": filepath.name,
        "content": content
    }
    response = summarize.summarize_file(file_dict= file_dict, provider= provider, style= style)
    json_form_response = json.dumps(response, indent=2)
    typer.echo(json_form_response)

@app.command(help="Batch file summary report.")
def batch(
    input_dir: str = typer.Argument(help="Folder/Directory Path for multiple files."),
    provider_name: str = typer.Option("groq", "--provider", help="Provider to use: groq or mock."),
    model: Optional[str] = typer.Option(None, "--model", help="Provide model: model valid only for groq."),
    output_dir: str = typer.Option(str(ARTIFACTS_DIR), "--output-dir", help="Summary files saving directory."),
    style: str = typer.Option("brief", "--style", help="Style provides brief, detailed, bullet points summary of file(s).")
    ):
    provider = _make_provider(provider_name= provider_name, model= model)
    file_loader = FileLoader()
    summarize = Summarizer()
    output_writer = OutputWriter()
    loaded_files = file_loader.load_text_files(directory_path= input_dir)
    summarized_files = summarize.summarize_batch(files= loaded_files, provider= provider, style=style)
    report_list = output_writer.save_batch_results(results= summarized_files, output_dir= output_dir)
    report = output_writer.build_batch_report(results= summarized_files, success_list= report_list)
    batch_response = {
        "report": report,
        "results": summarized_files
    }
    json_form_response = json.dumps(batch_response, indent=2)
    typer.echo(json_form_response)

@app.command(help="Ask a question againt your documents using RAG.")
def ask(
    question: str = typer.Argument(..., help="Question to ask."),
    source: str = typer.Option("data/inputs/", "--source", help="Document source path."),
    store: str = typer.Option("artifacts/vector_store/", "--store", help="Vector store path."),
    k: int = typer.Option(3, "--k", help="Number of chunks to retrieve.")
    ):
    if question.strip() == "":
        print("Question can not be blank or empty.")
        return None
    embedder= make_embedder()
    try:
        vector_store= load_vector_store(store, embedder)
    except Exception:
        print ("Vector store not found at {store}.\nRun: python -m ai_training.cli ingest --source <your_docs> --store artifacts/vector_store/")
        return None
    retriever= make_retriever(vector_store, k=k)
    llm= make_llm()
    result= run_rag_with_sources(retriever, question, llm)
    print("Answer:\n" + result["answer"] + "\n\nSources:")
    for source in result["sources"]:
        print(f"- {source['source']} (chunk {source['chunk_index']})")

@app.command(help= "Ingest documents and build vectore store.")
def ingest(
    source: str= typer.Option("data/inputs/", "--source", help= "Document source path."),
    store: str= typer.Option("artifacts/vector_store/", "--store", help= "Where to save vector store.")
    ):
    print(f"Loading documents from {source}...")
    chunks= ingest_documents(source)
    print(f"Loaded {len(chunks)} chunks.")
    embedder= make_embedder()
    print("Building vector store...")
    vector_store= create_vector_store(chunks, embedder)
    save_vector_store(vector_store, store)
    print(f"Vector store saved to {store}")

if __name__ == "__main__":
    app()
