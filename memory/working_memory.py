"""
ARUS
Working Memory
"""

class WorkingMemory:

    def __init__(self, limit=50):
        self.limit = limit
        self.messages = []

    def add(self, role, content):
        self.messages.append({
            "role": role,
            "content": content
        })
        self.trim()

    def trim(self):
        if len(self.messages) > self.limit:
            self.messages = self.messages[-self.limit:]

    def history(self):
        return list(self.messages)

    def clear(self):
        self.messages.clear()
