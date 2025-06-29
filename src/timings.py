from typing import List

from src.graphics import RenderSettings


class TimeThreshold:

    def __init__(
            self,
            max_seconds_active: float,
    ):
        self.max_seconds_active = max_seconds_active
        self.active: bool = False
        self.blocked: bool = False
        self.last_activation: float = -1000.

    def activate(self, rs: RenderSettings):
        if not self.active and not self.blocked:
            self.active = True
            self.last_activation = rs.second

    def deactivate(self, rs: RenderSettings):
        self.active = False
        self.blocked = False

    def set_active(self, rs: RenderSettings, active: bool = True):
        if active:
            self.activate(rs)
        else:
            self.deactivate(rs)

    def step(self, rs: RenderSettings):
        if self.active:
            diff = rs.second - self.last_activation
            if diff >= self.max_seconds_active:
                self.active = False
                self.blocked = True

    def check_key_press(self, rs: RenderSettings, pressed: bool) -> bool:
        self.step(rs)
        self.set_active(rs, pressed)
        return self.active

class ValueScheduler:

    class Task:
        def __init__(self, value, seconds: float):
            self.value = value
            self.seconds = seconds
            self.time = None
            self.task_time = None

    def __init__(self, value):
        self.value = value
        self._tasks: List[ValueScheduler.Task] = []

    def schedule(self, value, seconds: float):
        self._tasks.append(self.Task(value, seconds))

    def step(self, rs: RenderSettings):
        new_max_time = None
        for task in self._tasks:
            if task.time is None:  # this task was newly added
                task.time = rs.second
                task.task_time = rs.second + task.seconds
                new_max_time = rs.second

        self._tasks.sort(key=lambda t: t.task_time)

        if new_max_time is not None:
            while self._tasks and self._tasks[0].time < new_max_time:
                self._tasks.pop(0)

        while self._tasks and self._tasks[0].task_time <= rs.second:
            self.value = self._tasks[0].value
            self._tasks.pop(0)

