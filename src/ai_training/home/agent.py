import time
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import StructuredTool
from ai_training.home import tools as home_tools
from ai_training.home.tools import is_risky
from ai_training.langchain_basics.chains import make_llm
import threading
from ai_training.home import audit

YES = {"yes", "y", "confirm", "ok", "okay"}
NO = {"no", "n", "cancel"}
PENDING_TTL_SECONDS = 60

REAL_TOOLS = [
    home_tools.set_light,
    home_tools.set_door_lock,
    home_tools.set_temperature,
    home_tools.get_home_state,
]


def build_agent_prompt():
    return ChatPromptTemplate([
        ("system",
         "You control a home using tools. Always use a tool to perform an action; "
         "never claim you did something without calling a tool. Do not guess device "
         "state: call get_home_state if you are unsure. If a tool says confirmation "
         "is required, ask the user to confirm and do NOT try again."),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])


class HomeAgent:
    def __init__(self, llm=None, session_id="default"):
        self.pending = None
        self._pending_at = 0.0
        self._real = {t.name: t for t in REAL_TOOLS}
        self.guarded_tools = [self._guard(t) for t in REAL_TOOLS]
        self.session_id = session_id
        llm = llm or make_llm()
        agent = create_tool_calling_agent(llm, self.guarded_tools, build_agent_prompt())
        self.executor = AgentExecutor(
            agent=agent, tools=self.guarded_tools, verbose=False,
            handle_parsing_errors=True, max_iterations=5,
        )

    def _run(self, tool_name, args):
        return self._real[tool_name].invoke(args)

    def _guard(self, real_tool):
        name = real_tool.name

        def guarded(**kwargs):
            if is_risky(name, kwargs):
                self.pending = {"tool_name": name, "args": kwargs}
                self._pending_at = time.monotonic()
                blocked = {
                    "tool_name": name,
                    "result": "Confirmation required from the user.",
                    "success": False,
                    "needs_confirmation": True,
                }
                audit.record(self.session_id, name, kwargs, blocked)
                return blocked
            try:
                result = self._run(name, kwargs)
            except Exception as e:
                result = {"tool_name": name, "result": str(e), "success": False}
            audit.record(self.session_id, name, kwargs, result)
            return result
        return StructuredTool.from_function(
            func=guarded,
            name=name,
            description=real_tool.description,
            args_schema=real_tool.args_schema,
        )

    def _expire_pending(self):
        if self.pending and time.monotonic() - self._pending_at > PENDING_TTL_SECONDS:
            self.pending = None

    def handle(self, text: str) -> dict:
        self._expire_pending()
        answer = text.strip().lower().rstrip(".!")

        if self.pending:
            if answer in YES:
                pending, self.pending = self.pending, None
                try:
                    result = self._run(pending["tool_name"], pending["args"])
                except Exception as e:
                    result = {"tool_name": pending["tool_name"], "result": str(e), "success": False}
                audit.record(self.session_id, pending["tool_name"], pending["args"], result)
                return {"reply": result["result"], "needs_confirmation": False}
            if answer in NO:
                self.pending = None
                return {"reply": "Cancelled.", "needs_confirmation": False}
            return {"reply": "Please answer yes or no.", "needs_confirmation": True}

        output = self.executor.invoke({"input": text})["output"]
        return {"reply": output, "needs_confirmation": self.pending is not None}

_agents: dict[str, HomeAgent] = {}
_lock = threading.Lock()

def get_agent(session_id: str) -> HomeAgent:
    with _lock:
        if session_id not in _agents:
            _agents[session_id] = HomeAgent(session_id=session_id)
        return _agents[session_id]

if __name__ == "__main__":
    agent = HomeAgent()
    for message in [
        "Turn on the kitchen light",
        "Lock the front door",
        "Unlock the front door",
        "yes",
        "Set the temperature to 90",
        "Unlock the back door",
        "no",
        "What is the state of the home?",
    ]:
        print(f"> {message}")
        print(agent.handle(message), "\n")