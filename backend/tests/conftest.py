"""Test konfigürasyonu — app import edilmeden ÖNCE test DB'sine geçir."""
import os
import pathlib

# Ayrı test veritabanı (app import'undan önce set edilmeli)
_TEST_DB = pathlib.Path(__file__).parent / "test_aday.db"
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{_TEST_DB.as_posix()}"
# OpenAI key gerekmesin (FakeLLM kullanılacak; yine de Settings zorunlu alan istiyor)
os.environ.setdefault("OPENAI_API_KEY", "sk-test-fake")

import pytest


@pytest.fixture(scope="session", autouse=True)
def _cleanup_test_db():
    yield
    try:
        _TEST_DB.unlink(missing_ok=True)
    except PermissionError:
        pass
