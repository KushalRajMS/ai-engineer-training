from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor
from ai_training.langchain_basics.chains import make_llm
from ai_training.langchain_basics.tools import get_tool_registry

def build_agent_prompt():
    return ChatPromptTemplate([("system", "You are a helpful assistant with access to tools."),("human", "{input}"), MessagesPlaceholder(variable_name="agent_scratchpad")])

def build_agent(llm, tools):
    agent= create_tool_calling_agent(llm, tools, build_agent_prompt())
    return AgentExecutor(agent= agent, tools= tools, verbose=True, handle_parsing_errors= True, max_iterations= 3)

def run_agent(executor, question):
    result= executor.invoke({"input": question})
    return result["output"]

if __name__ == "__main__":
    llm = make_llm()
    tools = get_tool_registry()
    executor = build_agent(llm, tools)

    print(run_agent(executor, "How many words are in this text: Python is a great language"))
    print(run_agent(executor, "Give me a preview of this text: " + "word " * 50))
    print(run_agent(executor, "Divide 10 by 2"))
    print(run_agent(executor, "Divide 10 by 0"))