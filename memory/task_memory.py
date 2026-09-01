"""
ARUS
Task Memory
"""

from __future__ import annotations

from database.database import Database
from database.memory_repository import MemoryRepository

_NAMESPACE = "tasks"


class MemoryTask:

    def __init__(
        self,
        name,
        arguments=None,
        status="pending",
        result=None,
    ):
        self.name = name
        self.arguments = arguments or {}
        self.status = status
        self.result = result

    def __eq__(self, other):
        if not isinstance(other, MemoryTask):
            return NotImplemented

        return (
            self.name == other.name
            and self.arguments == other.arguments
            and self.status == other.status
            and self.result == other.result
        )

    def __hash__(self):
        return hash(self.name)


class TaskMemory:

    def __init__(self, database=None):

        self.database = database or Database()
        self.repo = MemoryRepository(self.database)
        self.repo.create_table()

    def save(self, task_id: str, state: dict):

        self.repo.set(
            _NAMESPACE,
            task_id,
            state,
        )

    def get(self, task_id: str):

        state = self.repo.get(
            _NAMESPACE,
            task_id,
        )

        if state is None:
            return None

        return self._task(
            task_id,
            state,
        )

    def delete(self, task_id: str):

        self.repo.delete(
            _NAMESPACE,
            task_id,
        )

    def all(self):

        return self.repo.all(
            _NAMESPACE
        )

    def _task(self, task_id, state):

        return MemoryTask(
            name=task_id,
            arguments=state.get(
                "arguments",
                {}
            ),
            status=state.get(
                "status",
                "pending"
            ),
            result=state.get(
                "result"
            ),
        )

    def pending(self):

        return [
            self._task(task_id, state)
            for task_id, state in self.all().items()
            if state.get("status") == "pending"
        ]

    def complete(self, task, result):

        task.status = "done"
        task.result = result

        self.save(
            task.name,
            {
                "arguments": task.arguments,
                "status": task.status,
                "result": task.result,
            },
        )

        return task

    def completed(self):

        return [
            self._task(task_id, state)
            for task_id, state in self.all().items()
            if state.get("status") == "done"
        ]
