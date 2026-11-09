"""pytest 公共配置。

注意：必须在 import 任何 server 模块之前设置环境变量，
因为 db/session.py 在模块导入时就根据 settings.DATABASE_URL 建 engine。
"""

import os
import pathlib
import sys

_SERVER_DIR = pathlib.Path(__file__).resolve().parents[1]
_TMP_DB_DIR = pathlib.Path(__file__).resolve().parent / "_tmp"

os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{(_TMP_DB_DIR / 'test.db').as_posix()}"
os.environ["DEBUG"] = "false"
os.environ["ALLOW_ANONYMOUS_USER"] = "false"
os.environ["LLM_API_KEY"] = ""

_TMP_DB_DIR.mkdir(exist_ok=True)

if str(_SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(_SERVER_DIR))

import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402

from config import settings  # noqa: E402
from db.session import Base, engine  # noqa: E402
from main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _create_schema():
    """建表一次即可，测试之间用数据隔离而不是重建 schema。"""
    import asyncio

    async def _run():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(_run())
    yield


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def auth_headers():
    """生成任意用户的合法 token。"""
    from core.security import create_access_token

    def _make(user_id: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {create_access_token(user_id)}"}

    return _make


@pytest.fixture
def strict_auth(monkeypatch):
    """确保被测用例跑在"必须认证"模式下。"""
    monkeypatch.setattr(settings, "ALLOW_ANONYMOUS_USER", False)
    return settings


@pytest.fixture
def anonymous_auth(monkeypatch):
    """模拟本地开发模式：未认证回落到 dev-user。"""
    monkeypatch.setattr(settings, "ALLOW_ANONYMOUS_USER", True)
    return settings
