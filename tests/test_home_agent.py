import pytest
from ai_training.home import tools
from ai_training.home.agent import HomeAgent
from ai_training.home.devices import SimulatedHome


class NoToolLLM:
    """Stand-in LLM. HomeAgent only passes it to create_tool_calling_agent,
    which we patch out, so it is never called."""


@pytest.fixture(autouse=True)
def fresh_home(monkeypatch):
    monkeypatch.setattr(tools, "home", SimulatedHome())


@pytest.fixture
def agent(monkeypatch):
    monkeypatch.setattr(
        "ai_training.home.agent.create_tool_calling_agent", lambda llm, t, p: None
    )
    monkeypatch.setattr(
        "ai_training.home.agent.AgentExecutor", lambda **kwargs: None
    )
    return HomeAgent(llm=NoToolLLM())


def guarded(agent, name):
    return next(t for t in agent.guarded_tools if t.name == name)


def test_risky_call_does_not_run_and_sets_pending(agent):
    result = guarded(agent, "set_door_lock").invoke({"door": "front", "locked": False})
    assert result["needs_confirmation"] is True
    assert tools.home.get_state()["doors"]["front"] is True
    assert agent.pending["args"] == {"door": "front", "locked": False}


def test_safe_call_runs_immediately(agent):
    result = guarded(agent, "set_door_lock").invoke({"door": "front", "locked": True})
    assert result["success"] is True
    assert agent.pending is None


def test_yes_runs_pending_action(agent):
    guarded(agent, "set_door_lock").invoke({"door": "front", "locked": False})
    out = agent.handle("yes")
    assert out["needs_confirmation"] is False
    assert tools.home.get_state()["doors"]["front"] is False
    assert agent.pending is None


def test_no_cancels_and_door_stays_locked(agent):
    guarded(agent, "set_door_lock").invoke({"door": "back", "locked": False})
    out = agent.handle("no")
    assert out["reply"] == "Cancelled."
    assert tools.home.get_state()["doors"]["back"] is True
    assert agent.pending is None


@pytest.mark.parametrize("text", ["maybe", "hold on", "turn on the light"])
def test_ambiguous_reply_keeps_pending_and_never_runs(agent, text):
    guarded(agent, "set_door_lock").invoke({"door": "front", "locked": False})
    out = agent.handle(text)
    assert out["needs_confirmation"] is True
    assert agent.pending is not None
    assert tools.home.get_state()["doors"]["front"] is True


def test_pending_expires(agent, monkeypatch):
    guarded(agent, "set_door_lock").invoke({"door": "front", "locked": False})
    agent._pending_at -= 61
    agent._expire_pending()
    assert agent.pending is None


def test_expired_pending_cannot_be_confirmed(agent):
    guarded(agent, "set_door_lock").invoke({"door": "front", "locked": False})
    agent._pending_at -= 61
    agent.executor = type("E", (), {"invoke": lambda self, d: {"output": "ok"}})()
    agent.handle("yes")
    assert tools.home.get_state()["doors"]["front"] is True


def test_guarded_tools_keep_name_and_description(agent):
    names = {t.name for t in agent.guarded_tools}
    assert names == {"set_light", "set_door_lock", "set_temperature", "get_home_state"}
    assert all(t.description for t in agent.guarded_tools)


def test_is_risky():
    assert tools.is_risky("set_door_lock", {"door": "front", "locked": False}) is True
    assert tools.is_risky("set_door_lock", {"door": "front", "locked": True}) is False
    assert tools.is_risky("set_light", {"room": "kitchen", "on": True}) is False