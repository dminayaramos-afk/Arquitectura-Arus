"""
ARUS
Task Manager
"""

from __future__ import annotations

from brain.task import Task


class TaskManager:

    def __init__(self):

        self.tasks = []

    def add(
        self,
        task: Task,
    ):

        self.tasks.append(task)

    def next(self):

        for task in self.tasks:

            if task.status == "pending":
                return task

        return None

    def complete(
        self,
        task: Task,
        result,
    ):

        task.status = "done"
        task.result = result

    def pending(self):

        return [
            t
            for t in self.tasks
            if t.status == "pending"
        ]

    def completed(self):

        return [
            t
            for t in self.tasks
            if t.status == "done"
        ]

    def clear(self):

        self.tasks.clear()

    def execute_plan(
        self,
        tools,
    ):

        while True:

            task = self.next()

            if task is None:
                break

            try:

                result = tools.execute(
                    task.name,
                    **task.arguments,
                )

                self.complete(
                    task,
                    result,
                )

            except Exception as e:

                task.status = "error"
                task.result = str(e)

        return self.tasks

