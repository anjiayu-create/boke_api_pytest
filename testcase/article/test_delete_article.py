# -*- coding: utf-8 -*-
"""
@Time ： 2026/6/24 03:46
@Auth ： tianjiayu
"""
import pytest
from common.yaml_util import load_yaml_with_marks
from common.assert_util import AssertUtil


# 注意：第二个参数必须和YAML里的键名完全一致
delete_cases = load_yaml_with_marks("data/article_cases/article_delete_data.yaml", "delete_article_cases")

@pytest.mark.parametrize("case", delete_cases)
def test_delete_article(article_auth, temp_article_id, case):
    """
    删除文章接口全场景测试
    覆盖：参数校验（article_id为空/非数字/不存在）、鉴权异常、正向删除
    依赖：temp_article_id 先创建临时文章，保证有可用的article_id
    """
    # 1. 初始化默认配置
    assert_util = AssertUtil(case["case_name"])
    session,headers = article_auth

    # 2. 处理article_id（优先用测试数据，无则用临时文章ID）
    case_name = case["case_name"]
    article_id = case["article_id"]
    if article_id == "" and case_name != "异常-文章ID为空":
        article_id = temp_article_id  # 非空场景兜底用临时ID

    # 3. 构造删除参数
    delete_data = {}
    if article_id != "":  # 非空则添加article_id
        delete_data["article_id"] = article_id

    # 4. 发送POST删除请求
    res = session.post(
        url="/api/article/delete",
        headers=headers,
        json=delete_data,
    )

    # 6. 传入和业务码一致的HTTP状态码
    assert_util.assert_http_status_code(res, expected_code=case["expect_code"]) \
        .assert_business_code(expected_code=case["expect_code"]) \
        .assert_message(expected_msg=case["expect_msg"])
    # 正向场景额外校验删除结果（查询详情验证）
    if case_name == "正向-删除存在的文章ID":
        detail_response = session.get(f"/api/article/{article_id}", headers=headers)
        detail_assert = AssertUtil(f"{case_name}-删除结果验证")
        detail_assert.assert_http_status_code(detail_response, expected_code=400) \
            .assert_business_code(expected_code=400) \
            .assert_message(expected_msg="文章不存在或无权限访问")