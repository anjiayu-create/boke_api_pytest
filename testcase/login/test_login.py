# -*- coding: utf-8 -*-
"""
@Author: tianjiayu
@File: test_login.py
"""
import pytest
from common.yaml_util import load_yaml_with_marks
from common.assert_util import AssertUtil

# 2. 添加模块级公共标签
pytestmark = [
    pytest.mark.login,
    pytest.mark.regression,
]
# 3. 加载登录用例
login_data = load_yaml_with_marks("data/login_cases/login_data.yaml", "login_cases")

#4. 加载测试逻辑开始测试
@pytest.mark.parametrize("case", login_data)
def test_login(valid_admin_session, case):
    """登录接口-参数化数据驱动，覆盖正常/异常所有场景"""
    # 1. 初始化断言工具（必须第一步，传入用例名称）
    assert_util = AssertUtil(case["case_name"])
    # 2. 发送请求
    response = valid_admin_session.post(
        "/api/login",
        json={"username": case["username"], "password": case["password"]}
    )
    # 3. 统一分层断言（替换所有原生assert）
    assert_util.assert_http_status_code(response, expected_code=case["expect_code"]) \
        .assert_business_code(response, case["expect_code"]) \
        .assert_message(response, case["expect_msg"])

    # 4. 正向场景额外断言数据结构（替换原始的issubset）
    if case["expect_code"] == 200:
        assert_util.assert_data_key_exists(response, "token") \
            .assert_data_key_exists(response, "user_id") \
            .assert_data_key_exists(response, "username")





