"""鉴权相关回归测试。

历史问题：get_current_user_id 在 token 无效时直接 return "dev-user"，
导致全站 19 处依赖关系全部放行，任何人可读写同一份数据。

注意 GET /api/v1/agents（智能体市场列表）本身是公开端点，
不带鉴权依赖，所以这里用真正受保护的端点做探针。
"""

# 受保护端点探针：(method, path, 需要的 body)
PROTECTED = [
    ("GET", "/api/v1/agents/food-calories/history", None),
    ("POST", "/api/v1/agents/food-calories/chat", {"message": "hi"}),
    ("GET", "/api/v1/user/profile", None),
]


async def test_no_token_is_rejected(client, strict_auth):
    """无 token 请求受保护接口必须 401。"""
    for method, path, body in PROTECTED:
        resp = await client.request(method, path, json=body)
        assert resp.status_code == 401, f"{method} {path} 期望 401，实际 {resp.status_code}"


async def test_invalid_token_is_rejected(client, strict_auth):
    """伪造 token 必须 401，不能回落成 dev-user。"""
    for method, path, body in PROTECTED:
        resp = await client.request(
            method, path, json=body, headers={"Authorization": "Bearer not-a-real-token"}
        )
        assert resp.status_code == 401, f"{method} {path} 期望 401，实际 {resp.status_code}"


async def test_valid_token_is_accepted(client, strict_auth, auth_headers):
    """合法 token 应正常返回。"""
    resp = await client.get("/api/v1/agents", headers=auth_headers("user-a"))
    assert resp.status_code == 200
    assert resp.json()["code"] == 0


async def test_anonymous_mode_only_when_explicitly_enabled(client, anonymous_auth):
    """显式打开 ALLOW_ANONYMOUS_USER 时才允许匿名（仅本地开发）。"""
    resp = await client.get("/api/v1/agents/food-calories/history")
    assert resp.status_code == 200
