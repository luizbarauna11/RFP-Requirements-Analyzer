from __future__ import annotations

from pathlib import Path

import pytest

from rfp_analyzer.config import Settings

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def rfp_text() -> str:
    return (FIXTURES / "rfp_ficticia_field_services.txt").read_text(encoding="utf-8")


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(_env_file=None, llm_enabled=False, llm_cache_enabled=False, llm_cache_dir=tmp_path / "cache")
