# -*- coding: utf-8 -*-
"""
@Time ： 2026/6/24 03:35
@Auth ： tianjiayu
"""
import pytest
from common.yaml_util import load_yaml_with_marks
from common.assert_util import AssertUtil

# 注意：第二个参数必须和YAML里的键名完全一致
update_cases = load_yaml_with_marks("data/article_cases/article_update_data.yaml", "update_article_cases")


@pytest.mark.parametrize("case", update_cases)
def test_update_article(article_auth,temp_article_id, case):
    """
    修改文章接口全场景测试
    覆盖：参数校验（标题/内容为空、长度异常）、article_id无效、鉴权异常、正向修改
    依赖：temp_article_id 先创建临时文章，保证有可用的article_id
    """
    # 1. 初始化默认配置
    assert_util = AssertUtil(case["case_name"])
    session, headers = article_auth

    # 2. 处理article_id（优先用测试数据，无则用临时文章ID）
    case_name = case["case_name"]
    article_id = case.get("article_id", temp_article_id)
    if article_id is None:
        article_id = temp_article_id  # 兜底用临时ID

    # 3. 构造修改参数（处理空值场景）
    update_data = {"article_id": article_id}
    if case["title"] != "":  # 非空则添加标题
        update_data["title"] = case["title"]
    if case["content"] != "":  # 非空则添加内容
        update_data["content"] = case["content"]

    # 5. 发送POST修改请求
    res = session.post(
        url="/api/article/update",
        headers=headers,
        json=update_data,
    )
    # 6. 传入和业务码一致的HTTP状态码
    assert_util.assert_http_status_code(res, expected_code=case["expect_code"]) \
        .assert_business_code(expected_code=case["expect_code"]) \
        .assert_message(expected_msg=case["expect_msg"])

    # 正向场景额外校验修改结果（查询详情验证）
    if case_name in ["正向-正常修改标题+内容", "正向-只修改标题", "正向-只修改内容"]:
        detail_response = session.get(f"/api/article/{article_id}", headers=headers)
        # 新建断言实例，区分主请求和验证请求
        detail_assert = AssertUtil(f"{case_name}-修改结果验证")
        detail_assert.assert_http_status_code(detail_response, expected_code=200) \
            .assert_business_code(expected_code=200) \
            .assert_message(expected_msg="查询成功")
        if case["title"] != "":
            detail_assert.assert_data_value(key="title", expected_value=case["title"])
        if case["content"] != "":
            detail_assert.assert_data_value(key="content", expected_value=case["content"])
