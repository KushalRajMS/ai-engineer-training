from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever
from ai_training.langchain_basics.retrieval_pipeline import build_retrieval_pipeline
from ai_training.langchain_basics.chains import make_llm
from langchain_core.messages import HumanMessage, AIMessage
from ai_training.langchain_basics.rag import format_context, extract_sources, build_rag_prompt

def build_contextualize_prompt():
    return ChatPromptTemplate([
        ('system', "Given a chat history and the latest user question, reformulate it as a standalone question. If no reformulation needed, return as is."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ])

def build_memory_retriever(retriever, llm):
    return create_history_aware_retriever(llm, retriever, build_contextualize_prompt())

def run_conversation_rag(memory_retriever, llm, questions):
    chat_history= []
    conversation_dict= []
    for question in questions:
        chunks= memory_retriever.invoke({"input": question, "chat_history": chat_history})
        context= format_context(chunks)
        prompt= build_rag_prompt().format(context= context, question= question)
        result= llm.invoke(prompt)
        answer= result.content
        chat_history.append(HumanMessage(question))
        chat_history.append(AIMessage(answer))
        conversation_dict.append({
            "question": question,
            "answer": answer,
            "sources": extract_sources(chunks)
        })
    return conversation_dict


if __name__ == "__main__":
    retriever = build_retrieval_pipeline("data/inputs/", "artifacts/vector_store/", k=2)
    llm = make_llm()
    memory_retriever = build_memory_retriever(retriever, llm)

    chat_history = []
    result = memory_retriever.invoke({"input": "What is Python?", "chat_history": chat_history})
    questions = [
        "What is Python?",
        "What is it used for?",
        "What is AI?"
    ]
    results = run_conversation_rag(memory_retriever, llm, questions)
    for r in results:
        print(f"Q: {r['question']}")
        print(f"A: {r['answer']}")
        print(f"Sources: {r['sources']}")
        print("---")