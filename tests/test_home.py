import pytest
from ai_training.home import tools
from ai_training.home.devices import SimulatedHome


@pytest.fixture(autouse=True)
def fresh_home(monkeypatch):
    monkeypatch.setattr(tools, "home", SimulatedHome())


def test_set_light_on():
    r = tools.set_light.invoke({"room": "kitchen", "on": True})
    assert r["success"] is True
    assert tools.home.get_state()["lights"]["kitchen"] is True


def test_set_light_unknown_room():
    r = tools.set_light.invoke({"room": "garage", "on": True})
    assert r["success"] is False
    assert "garage" in r["result"]


def test_unlock_door():
    r = tools.set_door_lock.invoke({"door": "front", "locked": False})
    assert r["success"] is True
    assert tools.home.get_state()["doors"]["front"] is False


def test_unknown_door():
    r = tools.set_door_lock.invoke({"door": "garage", "locked": False})
    assert r["success"] is False


def test_temperature_valid():
    r = tools.set_temperature.invoke({"celsius": 25.0})
    assert r["success"] is True
    assert tools.home.get_state()["temperature"] == 25.0


@pytest.mark.parametrize("value", [9.9, 30.1, 90.0])
def test_temperature_out_of_range(value):
    r = tools.set_temperature.invoke({"celsius": value})
    assert r["success"] is False
    assert tools.home.get_state()["temperature"] == 22.0


def test_get_home_state():
    r = tools.get_home_state.invoke({})
    assert r["success"] is True
    assert set(r["result"]) == {"lights", "doors", "temperature"}


def test_state_is_a_copy():
    state = tools.home.get_state()
    state["lights"]["kitchen"] = True
    assert tools.home.get_state()["lights"]["kitchen"] is False