from langchain.prompts import PromptTemplate

def template_forms(style: str = "brief") -> str:
    if style == "brief":
        return "Summarize the following text in 2-3 sentences:\n\n{content}"
    elif style == "detailed":
        return "Summarize the following text thorough and covering all the key points:\n\n{content}"
    elif style == "bullets":
        return "Summarize the following text in bullet points:\n\n{content}"
    return "Summarize the following text in 2-3 sentences:\n\n{content}"

def summary_template(style: str = "brief"):
    return PromptTemplate(
        input_variables=["content"],
        template= template_forms(style= style)
    )

def qa_template ():
    return PromptTemplate(
        input_variables=["context", "question"],
        template= "Use the following context to answer the question.\nContext: {context}\nQuestion: {question}\nAnswer: "
    )

def extraction_template():
    return PromptTemplate(
        input_variables= ["text", "fields"],
        template= "Extract the following fields from the text and return as JSON: {fields}\nText: {text}\nJSON: "
    )

if __name__ == "__main__":
    template = summary_template(style="bullets")
    print(template.format(content="Python and RAG and LLM"))
    template = qa_template()
    print(template.format(context= "We are discussing about Python Language", question= "Who invented python language?"))
    template = extraction_template()
    print(template.format(fields= "Date, Name, Amount", text= "David got 120 dollars on 18th July 2024."))