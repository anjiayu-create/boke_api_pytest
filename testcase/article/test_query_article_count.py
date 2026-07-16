# -*- coding: utf-8 -*-
"""
@Time ： 2026/6/24 03:36
@Auth ： tianjiayu
"""
import pytest
from common.yaml_util import load_yaml_with_marks
from common.assert_util import AssertUtil


# 注意：第二个参数必须和YAML里的键名完全一致
count_cases = load_yaml_with_marks("data/article_cases/article_count_data.yaml", "count_article_cases")

@pytest.mark.parametrize("case", count_cases)
def test_query_article_count(article_auth, case):
    """
    查询当前用户已发布文章数量接口全场景测试
    覆盖：正向查询、Token缺失/过期、Session失效、Token与Session不匹配
    """
    # 1. 初始化默认配置
    assert_util = AssertUtil(case["case_name"])
    session,headers = article_auth

    # 3. 发送GET请求（无请求体）
    res = session.get(
        url="/api/article/count",
        headers=headers,
    )
    # 4. 传入和业务码一致的HTTP状态码
    assert_util.assert_http_status_code(res, expected_code=case["expect_code"]) \
        .assert_business_code(expected_code=case["expect_code"]) \
        .assert_message(expected_msg=case["expect_msg"])
    # 正向场景额外校验文章数量（可选）
    if case["case_name"] == "正向-查询自己的文章列表":
        count = assert_util._last_response.json()["data"]["articles"]["count"]
        assert_util.assert_greater_or_equal(count, 0, desc="文章数量应为非负数")
