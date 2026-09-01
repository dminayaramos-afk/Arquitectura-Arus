"""
ARUS
Virtual Laboratory
Workspace Model
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List
from uuid import uuid4


@dataclass
class Workspace:
    """
    Espacio de trabajo de un laboratorio.
    """

    name: str

    description: str = ""

    id: str = field(default_factory=lambda: str(uuid4()))

    created_at: datetime = field(default_factory=datetime.utcnow)

    updated_at: datetime = field(default_factory=datetime.utcnow)

    files: Dict[str, str] = field(default_factory=dict)

    folders: List[str] = field(default_factory=list)

    metadata: Dict[str, object] = field(default_factory=dict)

    tags: List[str] = field(default_factory=list)

    def touch(self):
        self.updated_at = datetime.utcnow()

    def add_file(self, filename: str, content: str = ""):
        self.files[filename] = content
        self.touch()

    def remove_file(self, filename: str):
        self.files.pop(filename, None)
        self.touch()

    def file_exists(self, filename: str) -> bool:
        return filename in self.files

    def add_folder(self, folder: str):
        if folder not in self.folders:
            self.folders.append(folder)
            self.touch()

    def remove_folder(self, folder: str):
        if folder in self.folders:
            self.folders.remove(folder)
            self.touch()

    def add_tag(self, tag: str):
        if tag not in self.tags:
            self.tags.append(tag)
            self.touch()

    def info(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "files": len(self.files),
            "folders": len(self.folders),
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
