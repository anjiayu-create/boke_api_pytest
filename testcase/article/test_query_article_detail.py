# -*- coding: utf-8 -*-
"""
@Time ： 2026/6/24 03:36
@Auth ： tianjiayu
"""
import pytest
from common.yaml_util import load_yaml_with_marks
from common.assert_util import AssertUtil


# 注意：第二个参数必须和YAML里的键名完全一致
query_cases = load_yaml_with_marks("data/article_cases/article_detail_data.yaml", "query_article_cases")

@pytest.mark.parametrize("case", query_cases)
def test_query_article_detail(article_auth,resolved_article_id, case):
    """
    查询单篇文章详情接口全场景测试
    覆盖：参数校验（非数字/负数/不存在）、鉴权异常、正向查询
    依赖：temp_article_id 先创建临时文章，保证有可用的article_id
    """
    # 1. 初始化默认配置
    assert_util = AssertUtil(case["case_name"])
    session,headers = article_auth
    article_id  = resolved_article_id

    # 4. 拼接路径参数，发送GET请求
    res = session.get(url=f"/api/article/{article_id}", headers=headers)
    # 5. 修复：传入和业务码一致的HTTP状态码
    assert_util.assert_http_status_code(res, expected_code=case["expect_code"]) \
        .assert_business_code(expected_code=case["expect_code"]) \
        .assert_message(expected_msg=case["expect_msg"])
    # 正向场景额外校验文章详情
    if case["case_name"] == "正向-查询存在的文章ID":
        assert_util.assert_data_value(key="id", expected_value=int(resolved_article_id))
        title = assert_util._last_response.json()["data"]["title"]
        assert_util.assert_string_startswith(title, "临时测试文章_", desc="文章标题前缀验证")
