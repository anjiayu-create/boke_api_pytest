# -*- coding: utf-8 -*-
"""
@Time ： 2026/6/24 03:35
@Auth ： tianjiayu
"""
import pytest
from common.yaml_util import load_yaml_with_marks
from common.assert_util import AssertUtil


# 注意：第二个参数必须和YAML里的键名完全一致
create_cases = load_yaml_with_marks("data/article_cases/article_create_data.yaml", "create_article_cases")

@pytest.mark.parametrize("case", create_cases)
def test_create_article(article_auth,admin_token,valid_admin_session, case):
    """
    发布文章接口全场景测试
    覆盖：参数校验、Token缺失/格式错误/过期、Session失效、Token与Session不匹配
    """
    # 1. 初始化：默认使用管理员Session和有效Token
    assert_util = AssertUtil(case["case_name"])
    article_id = None
    session,headers = article_auth
    try:
        # 3. 发送请求（接口路径按项目适配）
        response = session.post(
            url="/api/article/create",
            headers=headers,
            json={"title": case["title"], "content": case["content"]},
        )
        # 4. 传入和业务码一致的HTTP状态码
        assert_util.assert_http_status_code(response, expected_code=case["expect_code"]) \
            .assert_business_code(expected_code=case["expect_code"]) \
            .assert_message(expected_msg=case["expect_msg"])
        # 5. 正向场景额外断言（对应核心断言3）
        if case["expect_code"] == 200:
            assert_util.assert_data_key_exists(key="article_id")
            # 提取article_id用于后续清理
            article_id = assert_util._last_response.json()["data"]["article_id"]
    finally:
        if article_id is not None:
            try:
                # 清理时使用有效鉴权（避免因测试场景的无效鉴权导致删除失败）
                clean_headers = {"Authorization": f"Bearer {admin_token}"}
                # 使用管理员有效Session删除文章
                delete_res = valid_admin_session.post(
                    url="/api/article/delete",
                    headers=clean_headers,
                    json={"article_id": article_id},
                )
                # 清理操作单独断言，用独立的AssertUtil实例
                clean_assert = AssertUtil(f"{case['case_name']}-临时文章清理")
                clean_assert.assert_http_status_code(delete_res, expected_code=200) \
                    .assert_business_code(expected_code=200)
            except Exception as e:
                raise AssertionError(f"❌ 临时文章 {article_id} 清理失败：{str(e)}") from e
