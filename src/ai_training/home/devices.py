from abc import ABC, abstractmethod
from typing import Any

class DeviceController(ABC):
    @abstractmethod
    def get_state(self) -> dict[str, Any]:
        ...
    @abstractmethod
    def set_light(self, room: str, on: bool) -> None:
        ...
    @abstractmethod
    def set_door_lock(self, door: str, locked: bool) -> None:
        ...
    @abstractmethod
    def set_temperature(self, celsius: float) -> None:
        ...

class SimulatedHome(DeviceController):
    def __init__(self) -> None:
        self._lights: dict[str, bool] = {
            "living_room" : False,
            "kitchen" : False,
            "bedroom" : False,
        }
        self._doors: dict[str, bool] = {
            "front": True,
            "back": True,
        }
        self._temperature = 22.0
        self.offline: set[str] = set()
    def get_state(self) -> dict[str, Any]:
        return{
            "lights": self._lights.copy(),
            "doors": self._doors.copy(),
            "temperature": self._temperature,
        }
    def set_light(self, room: str, on: bool) -> None:
        if f"light:{room}" in self.offline:
            raise ValueError(f"Device offline: light in '{room}")
        if room not in self._lights:
            raise ValueError(f"Unknown room '{room}'")
        self._lights[room] = on
    def set_door_lock(self, door: str, locked: bool) -> None:
        if door not in self._doors:
            raise ValueError(f"Unknown door '{door}'")
        self._doors[door] = locked
    def set_temperature(self, celsius: float) -> None:
        if not (10.0 <= celsius <= 30.0):
            raise ValueError(f"Temperature {celsius}°C is out of range (10 to 30).")
        self._temperature = float(celsius)