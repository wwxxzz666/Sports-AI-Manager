"""启动配置校验与资源生命周期测试。"""

import asyncio

import pytest

from config import settings
from llm import factory


# ---------------- validate_settings ----------------

UNSAFE = [
    "",
    "dev-secret-change-in-production",
    "change-me-to-a-random-string",
]


@pytest.mark.parametrize("secret", UNSAFE)
def test_production_rejects_default_jwt_secret(monkeypatch, secret):
    from main import validate_settings

    monkeypatch.setattr(settings, "DEBUG", False)
    monkeypatch.setattr(settings, "JWT_SECRET", secret)

    with pytest.raises(RuntimeError) as exc:
        validate_settings()
    assert "JWT_SECRET" in str(exc.value)


def test_production_accepts_custom_jwt_secret(monkeypatch):
    from main import validate_settings

    monkeypatch.setattr(settings, "DEBUG", False)
    monkeypatch.setattr(settings, "JWT_SECRET", "a-real-random-secret")
    monkeypatch.setattr(settings, "ALLOW_ANONYMOUS_USER", False)

    validate_settings()  # 不应抛错


def test_debug_mode_skips_validation(monkeypatch):
    from main import validate_settings

    monkeypatch.setattr(settings, "DEBUG", True)
    monkeypatch.setattr(settings, "JWT_SECRET", "dev-secret-change-in-production")

    validate_settings()


def test_production_warns_when_anonymous_user_left_on(monkeypatch, caplog):
    from main import validate_settings

    monkeypatch.setattr(settings, "DEBUG", False)
    monkeypatch.setattr(settings, "JWT_SECRET", "a-real-random-secret")
    monkeypatch.setattr(settings, "ALLOW_ANONYMOUS_USER", True)

    with caplog.at_level("ERROR"):
        validate_settings()

    assert any("ALLOW_ANONYMOUS_USER" in r.message for r in caplog.records)


# ---------------- close_llm ----------------

def test_close_llm_is_noop_without_instance():
    factory.reset_llm()
    asyncio.run(factory.close_llm())  # 不应抛错


def test_close_llm_closes_and_clears_singleton(monkeypatch):
    factory.reset_llm()
    client = factory.get_llm()
    closed = {"v": False}

    async def _close():
        closed["v"] = True

    monkeypatch.setattr(client, "close", _close)

    asyncio.run(factory.close_llm())

    assert closed["v"] is True, "close() 没有被调用（httpx 连接池会泄漏）"
    # 单例应被清空，下次 get_llm() 会重建
    assert factory._llm_instance is None
