"""Scenario framework: each scenario builds a fresh, isolated incident environment.

Ground truth (``hidden``) is stored for the evaluator only; it is never exposed
to agent tools, prompts, file names or incident identifiers.
"""

from __future__ import annotations

import random
import shutil
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..paths import TEMPLATES_DIR
from ..simulators.world import World


@dataclass
class ScenarioInstance:
    family: str
    variant: str
    world_path: Path
    repo_dir: Path
    ticket: dict[str, Any]
    # Business contract the independent verifier checks (derived from billing, not from the agent).
    contract: dict[str, Any]
    # Evaluation-only ground truth.
    hidden: dict[str, Any] = field(default_factory=dict)

    @property
    def world(self) -> World:
        return World(self.world_path)


SetupFn = Callable[[Path, random.Random, str], ScenarioInstance]


@dataclass
class ScenarioFamily:
    name: str
    description: str
    variants: list[str]
    heldout_variants: list[str]
    setup: SetupFn


REGISTRY: dict[str, ScenarioFamily] = {}


def register(family: ScenarioFamily) -> ScenarioFamily:
    REGISTRY[family.name] = family
    return family


def copy_template_repo(dest: Path, template: str = "entitlement_sync") -> Path:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(TEMPLATES_DIR / template, dest,
                    ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    return dest


FIRST = ["Lena", "Omar", "Priya", "Mateo", "Yuki", "Amara", "Jonas", "Sofia", "Karim", "Ines"]
LAST = ["Hart", "Rahman", "Okafor", "Silva", "Tanaka", "Novak", "Haddad", "Berg", "Moreau", "Quinn"]
TENANTS = ["northwind", "bluefin", "kestrel", "lumen", "orchid", "tidewater", "zephyr", "cobalt"]


def fictional_person(rng: random.Random, domain: str) -> tuple[str, str]:
    first, last = rng.choice(FIRST), rng.choice(LAST)
    return f"{first} {last}", f"{first.lower()}.{last.lower()}{rng.randint(10, 99)}@{domain}.example"
