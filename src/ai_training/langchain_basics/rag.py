from langchain.prompts import PromptTemplate
from ai_training.langchain_basics.retrieval_pipeline import build_retrieval_pipeline
from ai_training.langchain_basics.chains import make_llm
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

def build_rag_prompt():
    template= ("Use the following context to answer the question.\nIf the answer is not in the context, say \"I don\'t know.\"\n\nContext:\n{context}\n\nQuestion: {question}\n\nAnswer:")
    return PromptTemplate(
        input_variables=["context", "question"],
        template= template
    )

def format_context(chunks):
    content= ""
    for chunk in chunks:
        content += chunk.page_content + "\n\n"
    return content

def run_rag(retriever, question, llm):
    chunks= retriever.invoke(question)
    context= format_context(chunks)
    prompt= build_rag_prompt().format(context= context, question=question)
    result= llm.invoke(prompt)
    return result.content

def extract_sources(chunks):
    source= []
    for chunk in chunks:
        source.append(
            {
                "source": chunk.metadata.get("source", "unknown"),
                "chunk_index": chunk.metadata.get("chunk_index", "unknown")
            }
        )
    return source

def run_rag_with_sources(retriever, question, llm):
    chunks= retriever.invoke(question)
    context= format_context(chunks)
    prompt= build_rag_prompt().format(context= context, question= question)
    result= llm.invoke(prompt)
    return{
        "answer": result.content,
        "sources": extract_sources(chunks)
    }

def build_rag_chain(retriever, llm):
    return (
        {"context": retriever | RunnableLambda(format_context), "question": RunnablePassthrough()}
        | build_rag_prompt()
        | llm
    )

if __name__ == "__main__":
    retriever= build_retrieval_pipeline(
        source_path="data/inputs/",
        store_path="artifacts/vector_store/",
        k=2
    )
    llm= make_llm()
    rag_chain= build_rag_chain(retriever, llm)
    result= rag_chain.invoke("What is Python?")
    print(result.content)