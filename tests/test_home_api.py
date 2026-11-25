import pytest
from fastapi.testclient import TestClient

from ai_training.api.main import app
from ai_training.home import agent as agent_module
from ai_training.home import audit, tools
from ai_training.home.devices import SimulatedHome

client = TestClient(app)
HEADERS = {"X-API-Key": "test-key"}


class FakeSettings:
    home_api_key = "test-key"
    audit_db_path = ""


@pytest.fixture(autouse=True)
def isolate(monkeypatch, tmp_path):
    fake = FakeSettings()
    fake.audit_db_path = str(tmp_path / "audit.db")
    monkeypatch.setattr("ai_training.home.api.get_settings", lambda: fake)
    monkeypatch.setattr("ai_training.home.audit.get_settings", lambda: fake)
    monkeypatch.setattr(tools, "home", SimulatedHome())
    monkeypatch.setattr(agent_module, "_agents", {})
    monkeypatch.setattr(
        agent_module, "create_tool_calling_agent", lambda llm, t, p: None
    )
    monkeypatch.setattr(agent_module, "AgentExecutor", lambda **kw: None)
    monkeypatch.setattr(agent_module, "make_llm", lambda: None)


def test_missing_key_returns_401():
    r = client.post("/home/command", json={"session_id": "a", "text": "hi"})
    assert r.status_code == 401


def test_wrong_key_returns_401():
    r = client.get("/home/state", headers={"X-API-Key": "nope"})
    assert r.status_code == 401


def test_state_with_key():
    r = client.get("/home/state", headers=HEADERS)
    assert r.status_code == 200
    assert "lights" in r.json()


@pytest.mark.parametrize("body", [
    {"session_id": "a", "text": "   "},
    {"session_id": "   ", "text": "hi"},
    {"session_id": "a"},
])
def test_blank_or_missing_fields_return_422(body):
    r = client.post("/home/command", json=body, headers=HEADERS)
    assert r.status_code == 422


def test_audit_limit_validated():
    assert client.get("/home/audit?limit=0", headers=HEADERS).status_code == 422
    assert client.get("/home/audit?limit=501", headers=HEADERS).status_code == 422


def test_agent_failure_returns_502(monkeypatch):
    class Boom:
        def handle(self, text):
            raise RuntimeError("llm down")

    monkeypatch.setattr("ai_training.home.api.get_agent", lambda sid: Boom())
    r = client.post("/home/command", json={"session_id": "a", "text": "hi"}, headers=HEADERS)
    assert r.status_code == 502


def test_session_b_cannot_confirm_session_a():
    a = agent_module.get_agent("A")
    b = agent_module.get_agent("B")
    guarded = next(t for t in a.guarded_tools if t.name == "set_door_lock")
    guarded.invoke({"door": "front", "locked": False})
    assert a.pending is not None
    assert b.pending is None
    b.executor = type("E", (), {"invoke": lambda self, d: {"output": "ok"}})()
    b.handle("yes")
    assert tools.home.get_state()["doors"]["front"] is True
    assert a.pending is not None


def test_same_session_gets_same_agent():
    assert agent_module.get_agent("x") is agent_module.get_agent("x")


def test_safe_tool_runs_exactly_once():
    calls = []
    real = tools.home.set_light

    def counting(room, on):
        calls.append(room)
        real(room, on)

    tools.home.set_light = counting
    a = agent_module.get_agent("once")
    guarded = next(t for t in a.guarded_tools if t.name == "set_light")
    guarded.invoke({"room": "kitchen", "on": True})
    assert calls == ["kitchen"]


def test_audit_records_blocked_then_confirmed():
    a = agent_module.get_agent("audit")
    guarded = next(t for t in a.guarded_tools if t.name == "set_door_lock")
    guarded.invoke({"door": "front", "locked": False})
    a.handle("yes")
    rows = audit.get_log()
    assert [r["success"] for r in rows] == [1, 0]
    assert all(r["session_id"] == "audit" for r in rows)


def test_offline_device_reports_failure_others_still_work():
    tools.home.offline.add("light:bedroom")
    bad = tools.set_light.invoke({"room": "bedroom", "on": True})
    good = tools.set_light.invoke({"room": "kitchen", "on": True})
    assert bad["success"] is False
    assert "offline" in bad["result"].lower()
    assert good["success"] is True
    assert tools.home.get_state()["lights"]["kitchen"] is True