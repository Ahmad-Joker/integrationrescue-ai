import os

import pytest

os.environ["IR_SKIP_DOTENV"] = "1"  # never load the developer's real .env (and API key) into tests

from integrationrescue.agent.orchestrator import IncidentService
from integrationrescue.agent.store import Store


@pytest.fixture(autouse=True)
def isolated_var(tmp_path, monkeypatch):
    monkeypatch.setenv("IR_VAR_DIR", str(tmp_path / "var"))
    monkeypatch.setenv("IR_PROVIDER", "deterministic")
    return tmp_path / "var"


@pytest.fixture
def svc(isolated_var):
    return IncidentService(Store())
