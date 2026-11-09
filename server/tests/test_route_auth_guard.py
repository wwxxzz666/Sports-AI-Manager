"""静态路由审计：防止新增端点忘记挂鉴权依赖。

这个测试不跑请求，直接遍历 FastAPI 的路由表检查 dependant 依赖。
它就是上一批 IDOR 修复的守门人 —— 以后再加端点，忘了写
Depends(get_current_user_id) 会立刻失败。
"""

import pytest

from api.v1 import agents, auth, health, motion, nutrition, ratings, reports, uploads, user

ALL_MODULES = (agents, auth, health, motion, nutrition, ratings, reports, uploads, user)

# 设计上就该公开的端点（路径, 方法）
# agents ""           -> 智能体市场列表，纯静态元数据
# auth /register /login -> 注册登录本身
PUBLIC_ENDPOINTS = {
    ("", "GET"),
    ("/register", "POST"),
    ("/login", "POST"),
}


def _route_key(route) -> tuple[str, str]:
    methods = sorted(m for m in route.methods if m not in {"HEAD", "OPTIONS"})
    return route.path, methods[0] if methods else ""


def _has_auth_dependency(route) -> bool:
    names = {getattr(d.call, "__name__", "") for d in route.dependant.dependencies}
    return "get_current_user_id" in names


def test_every_business_route_requires_auth():
    offenders = []
    for module in ALL_MODULES:
        for route in module.router.routes:
            key = _route_key(route)
            if key in PUBLIC_ENDPOINTS:
                continue
            if not _has_auth_dependency(route):
                offenders.append(f"{module.__name__}: {key[1]} {key[0] or '/'}")

    assert not offenders, (
        "以下端点缺少 get_current_user_id 鉴权依赖（若是故意公开，请加入 PUBLIC_ENDPOINTS）:\n  "
        + "\n  ".join(offenders)
    )


def test_public_whitelist_entries_still_exist():
    """白名单不能留过期条目，否则会掩盖真实的鉴权缺失。"""
    actual = {_route_key(r) for m in ALL_MODULES for r in m.router.routes}
    stale = PUBLIC_ENDPOINTS - actual
    assert not stale, f"PUBLIC_ENDPOINTS 里有已不存在的端点: {stale}"
