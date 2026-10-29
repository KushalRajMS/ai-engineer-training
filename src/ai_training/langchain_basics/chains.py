from langchain_groq import ChatGroq
from ai_training.langchain_basics.prompts import extraction_template, qa_template, summary_template
from ai_training.pipeline.summarizer import Summarizer
from ai_training.chat.chatbot import chat_once
from ai_training.providers.groq import GroqProvider
from ai_training.config import APP_CONFIG

def make_llm():
    return ChatGroq(model= APP_CONFIG["model"], api_key= APP_CONFIG["api_key"], temperature= APP_CONFIG["temperature"])

def run_summary_chain(content, style):
    llm= make_llm()
    prompt_template= summary_template(style= style)
    chain= prompt_template | llm
    result = chain.invoke({"content": content})
    return result.content

def run_qa_chain(context, question):
    llm= make_llm()
    prompt_template= qa_template()
    chain= prompt_template | llm
    result = chain.invoke({"context": context, "question": question})
    return result.content

def run_extraction_chain(text, fields):
    llm = make_llm()
    prompt_template= extraction_template()
    chain= prompt_template | llm
    result= chain.invoke({"text": text, "fields": fields})
    return result.content

if __name__ == "__main__":
    content= "Python is a high-level programming language known for its simple and readable syntax. It is widely used in web development, data science, automation, and artificial intelligence."
    print("=== LangChain Chain ===")
    print(run_summary_chain(content= content, style= "brief"))

    print("\n=== Existing Summarizer ===")
    prompt= Summarizer().build_summary_prompt(content= content, style= "brief")
    response, _ = chat_once(prompt= prompt, provider=GroqProvider())
    print(response)