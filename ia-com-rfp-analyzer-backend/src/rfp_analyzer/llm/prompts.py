"""Prompts versionados em YAML (padrão corporativo: nunca hardcoded no Python)."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from string import Template

import yaml


@dataclass(frozen=True)
class PromptTemplate:
    name: str
    version: str
    system: str
    user: Template

    def render(self, **kwargs: str) -> tuple[str, str]:
        return self.system, self.user.substitute(**kwargs)


@lru_cache
def load_prompt(prompts_dir: Path, name: str, version: str = "v1") -> PromptTemplate:
    data = yaml.safe_load((prompts_dir / f"{name}_{version}.yaml").read_text(encoding="utf-8"))
    return PromptTemplate(
        name=data["name"], version=str(data["version"]), system=data["system"], user=Template(data["user"])
    )
