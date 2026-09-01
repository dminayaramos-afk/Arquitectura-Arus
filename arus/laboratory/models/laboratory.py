"""
ARUS
Virtual Laboratory
Laboratory Model
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from .status import LaboratoryStatus


@dataclass
class Laboratory:
    name: str
    description: str = ""

    id: str = field(default_factory=lambda: str(uuid4()))

    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    status: LaboratoryStatus = LaboratoryStatus.CREATED

    workspaces: Dict[str, object] = field(default_factory=dict)
    experiments: List[str] = field(default_factory=list)
    metadata: Dict[str, object] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    owner: Optional[str] = None
    version: str = "1.0"

    def touch(self):
        self.updated_at = datetime.utcnow()

    def initialize(self):
        self.status = LaboratoryStatus.INITIALIZING
        self.touch()

    def ready(self):
        self.status = LaboratoryStatus.READY
        self.touch()

    def start(self):
        self.status = LaboratoryStatus.RUNNING
        self.touch()

    def pause(self):
        self.status = LaboratoryStatus.PAUSED
        self.touch()

    def finish(self):
        self.status = LaboratoryStatus.FINISHED
        self.touch()

    def archive(self):
        self.status = LaboratoryStatus.ARCHIVED
        self.touch()

    def delete(self):
        self.status = LaboratoryStatus.DELETED
        self.touch()

    def add_workspace(self, workspace):
        self.workspaces[workspace.name] = workspace
        self.touch()

    def remove_workspace(self, name):
        self.workspaces.pop(name, None)
        self.touch()

    def workspace_exists(self, name):
        return name in self.workspaces

    def get_workspace(self, name):
        return self.workspaces.get(name)

    def add_experiment(self, experiment):
        self.experiments.append(experiment)
        self.touch()

    def add_tag(self, tag):
        if tag not in self.tags:
            self.tags.append(tag)
            self.touch()

    def info(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "owner": self.owner,
            "version": self.version,
            "workspaces": len(self.workspaces),
            "experiments": len(self.experiments),
            "tags": self.tags,
            "metadata": self.metadata,
        }
