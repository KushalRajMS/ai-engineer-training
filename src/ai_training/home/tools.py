from langchain_core.tools import tool
from ai_training.home.devices import DeviceController, SimulatedHome
from typing import Any

home: DeviceController = SimulatedHome()

def is_risky(tool_name: str, args: dict) -> bool:
    """Only unlocking a door is risky. Loocking is safe."""
    if tool_name == "set_door_lock":
        return args.get("locked") is False
    return False

@tool
def set_light(room: str, on: bool) -> dict[str, Any]:
    """Turn the light on or off in a specific room."""
    try:
        home.set_light(room, on)
        state= "on" if on else "off"
        return{
            "tool_name": "set_light",
            "result": f"Light in '{room}' turned '{state}'.",
            "success": True,
        }
    except ValueError as e:
        return{
            "tool_name": "set_light",
            "result": str(e),
            "success": False,
        }

@tool
def set_door_lock(door: str, locked: bool) -> dict[str, Any]:
    """Lock or unlock a specific door in a home."""
    try:
        home.set_door_lock(door, locked)
        state= "locked" if locked else "unlocked"
        return{
            "tool_name": "set_door_lock",
            "result": f"The '{door}' door is now {state}.",
            "success": True,
        }
    except ValueError as e:
        return{
            "tool_name": "set_door_lock",
            "result": str(e),
            "success": False,
        }

@tool
def set_temperature(celsius: float) -> dict[str, Any]:
    """Set the home thermostat temperature in degrees Celsius (valid range: 10 to 30)."""
    try:
        home.set_temperature(celsius=celsius)
        return {
            "tool_name": "set_temperature",
            "result": f"Thermostat set to {celsius}°C.",
            "success": True,
        }
    except ValueError as e:
        return {
            "tool_name": "set_temperature",
            "result": str(e),
            "success": False,
        }

@tool
def get_home_state() -> dict[str, Any]:
    """Retrieve the current state of all lights, door locks, and the thermostat."""
    state = home.get_state()
    return {
        "tool_name": "get_home_state",
        "result": state,
        "success": True,
    }

if __name__ == "__main__":
    print("1. Turning on kitchen light:")
    print(set_light.invoke({"room": "kitchen", "on": True}))

    print("\n2. Unlocking front door:")
    print(set_door_lock.invoke({"door": "front", "locked": False}))

    print("\n3. Setting temperature to 25°C:")
    print(set_temperature.invoke({"celsius": 25.0}))

    print("\n4. Current home state:")
    print(get_home_state.invoke({}))

    print("\n5. Testing invalid temperature (90°C):")
    bad_temp = set_temperature.invoke({"celsius": 90.0})
    print(bad_temp)

    print("\n6. Testing unknown room ('garage'):")
    bad_room = set_light.invoke({"room": "garage", "on": True})
    print(bad_room)