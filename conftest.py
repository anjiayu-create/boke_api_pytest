# -*- coding: utf-8 -*-
"""
@Author: tianjiayu
@File: conftest.py
"""
import requests
import pytest
import jwt
import os
import time
from datetime import datetime, timedelta, UTC
from dotenv import load_dotenv
from common.yaml_util import load_yaml
from common.http_client import HttpClient
from common.logger_util import debug, info, warning, error
from common.report.result_collector import result_collector
from common.report.feishu_send import FeishuNotifier
from common.report.email_notifier import EmailNotifier

# ===================== 全局配置（统一时间戳，所有文件共用） =====================
_RUN_TIME = time.strftime('%Y%m%d_%H%M%S')
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(ROOT_DIR, "report")
PYTEST_HTML_REPORT = os.path.join(REPORT_DIR, "pytest_html", f"测试报告_{_RUN_TIME}.html")
ALLURE_RESULTS_DIR = os.path.join(REPORT_DIR, "allure-results")
ALLURE_REPORT_DIR = os.path.join(REPORT_DIR, "allure-report")

#加载内存中的配置信息
load_dotenv(dotenv_path=os.path.join(ROOT_DIR, ".env"))
FEISHU_WEBHOOK = os.getenv("FEISHU_WEBHOOK")

# 动态配置pytest-html：自动带时间戳+强制自包含模式
def pytest_configure(config):
    config.option.htmlpath = PYTEST_HTML_REPORT
    config.option.self_contained_html = True

# ===================== 原有Fixture（保留，不修改用例） =====================

@pytest.fixture(scope="module")
def admin_user():
    return load_yaml("config/user.yaml")["admin"]

@pytest.fixture(scope="module")
def normal_user():
    return load_yaml("config/user.yaml")["normal_user"]

@pytest.fixture(scope="module")
def valid_admin_session(admin_user):
    """生成管理员的有效Session"""
    client = HttpClient()
    client.post("/api/login",
        json={"username": admin_user["username"], "password": admin_user["password"]})
    info("✅ [Fixture] 管理员登录态初始化完成")  # 【新增】
    yield client # 返回类的对象，此时已经登陆成功，返回了管理员的session
    info("♻️ [Fixture] 管理员登录态生命周期结束")  # 【新增】


@pytest.fixture(scope="module")
def valid_normal_session(normal_user):
    """普通人员登陆session"""
    client = HttpClient() # 【变】
    client.post( # 【变】
        "/api/login",
        json={"username": normal_user["username"], "password": normal_user["password"]}
    )
    info("✅ [Fixture] 普通人员登录态初始化完成")  # 【新增】
    yield client
    info("♻️ [Fixture] 普通人员登录态生命周期结束")

@pytest.fixture(scope="function")
def admin_token(valid_admin_session, admin_user):
    """提取管理员的有效Token（核心适配点）"""
    res = valid_admin_session.post(
        "/api/login",
        json={"username": admin_user["username"], "password": admin_user["password"]}
    )
    res_json = res.json()
    if "data" in res_json and "token" in res_json["data"]:
        token = res_json["data"]["token"]
        info("✅ [Fixture] 成功提取管理员的有效Token ")
    else:
        return "登陆接口返回有问题"
    return token


@pytest.fixture(scope="function")
def real_invalid_session(admin_user):
    """生成真实失效的Session（登录后登出）"""
    info("🔧 [Fixture] 开始制造：真实失效 Session（登录后登出）")
    client = HttpClient() # 【变2】
    # 【核心不变】业务逻辑1：登录
    info("🔧 [Fixture] 步骤 1/2：执行登录")
    login_resp = client.post( # 【变3】
        "/api/login",
        json={"username": admin_user["username"], "password": admin_user["password"]}
    )
    login_json = login_resp.json()
    # 拿到当前这个client登录生成的局部token，不用外部admin_token
    local_token = login_json["data"]["token"]
    # 【核心不变】业务逻辑2：登出（核心逻辑完全保留！）
    info("🔧 [Fixture] 步骤 2/2：执行登出，制造失效态")
    client.post( # 【变4】
        "/api/logout",
        # 【变5】只需要传业务相关的 Token，Content-Type 自动带
        headers={"Authorization": f"Bearer {local_token}"}
    )
    info("✅ [Fixture] 真实失效 Session 制造完成")
    yield client # 【变6】


@pytest.fixture(scope="module")
def normal_token(normal_user):
    """提取普通用户的有效Token（同管理员Token提取逻辑）"""
    client = HttpClient()
    res = client.post(  # 【变】
        "/api/login",
        json={"username": normal_user["username"], "password": normal_user["password"]}
    )
    # 【核心不变】下面提取 token 的逻辑，一个字都不用改！
    res_json = res.json()
    if "data" in res_json and "token" in res_json["data"]:
        token = res_json["data"]["token"]
        info("✅ [Fixture] 成功提取普通用户的有效Token ")
    else:
        return "登陆接口返回有问题"
    return token

# 构造真实的过期token
@pytest.fixture(scope="module")
def jwt_config():
    """
    测试项目中配置被测系统（api_base）的JWT参数
    需与api_base/config.py中的配置完全一致
    """
    return {
        "secret_key": "jwt_secret_654321",  # 替换api_base实际的JWT_SECRET_KEY
        "algorithm": "HS256"  # 被测系统默认的加密算法
    }

@pytest.fixture(scope="module")
def admin_api_user():
    """
    测试项目中配置被测系统（api_base）的管理员信息
    需与api_base的预设管理员（users.json/config.py）一致
    """
    return {
        "id": 1,  # api_base管理员固定ID
        "username": "admin"  # api_base管理员固定用户名
    }

# ========== 第二步：构造真实过期Token ==========
@pytest.fixture(scope="module")
def invalid_token(jwt_config, admin_api_user):
    """
    生成真实过期的JWT Token（完全复刻被测系统构造逻辑，仅修改exp为过去时间）
    核心：exp字段设为1小时前，后端会判定为“Token已过期”
    """
    # 构造JWT载荷（和被测系统api_base后端生成Token的载荷完全一致）
    payload = {
        "user_id": admin_api_user["id"],  # 匹配api_base的user_id字段（管理员ID=1）
        "username": admin_api_user["username"],  # 匹配api_base的username字段（admin）
        "exp": datetime.now(UTC) - timedelta(hours=1)  # 过期时间：1小时前（已过期），UTC时区
    }
    # 用被测系统的JWT密钥+算法生成过期Token（100%匹配api_base的生成逻辑）
    invalid_token = jwt.encode(
        payload,
        jwt_config["secret_key"],  # api_base的JWT密钥
        algorithm=jwt_config["algorithm"]  # api_base的加密算法（HS256）  # 等价于 algorithm="HS256"
    )
    return invalid_token

# 准备工作：创建测试文章、删除测试文章（保证测试文章在使用后会被删除）
@pytest.fixture(scope="function")
def temp_article_id(valid_admin_session, admin_token):
    headers = {
        "Authorization": f"Bearer {admin_token}"
    }
    # 【适配点】若创建文章需要额外参数（如category_id），补充到create_data中
    create_data = {
        "title": f"临时测试文章_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}",
        "content": "临时测试内容，用于接口测试数据隔离"
    }
    info("🔧 [Fixture] 开始创建：临时测试文章")
    res = valid_admin_session.post(
        "/api/article/create",
        headers=headers,
        json=create_data
    )
    res_json = res.json()
    art_id = None
    if "data" in res_json and "article_id" in res_json["data"]:
        art_id = res_json["data"]["article_id"]
        info(f"✅ [Fixture] 临时文章创建成功，ID: {art_id}")  # 【新增】
    else:
        error(f"❌ 创建临时文章失败，响应：{res_json}")
        raise Exception("创建文章接口失败，无法生成临时ID")
    yield art_id
    #删除创建好的文章
    info(f"🗑️ [Fixture] 开始清理：临时文章 ID: {art_id}")  # 【新增】
    try:
        valid_admin_session.post(
            "/api/article/delete",
            headers=headers,
            json={"article_id": art_id}
        )
        info(f"✅ [Fixture] 临时文章 ID: {art_id} 清理成功")  # 【新增】
    except Exception as e:
        print(f"\n⚠️ 临时文章{art_id}删除失败：{str(e)}，请手动清理")

# ===================== 测试统计+失败用例收集 =====================
def pytest_sessionstart(session):
    result_collector.start()

def pytest_runtest_logreport(report):
    result_collector.add_result(report)

# ===================== 最终通知入口（所有文件写完后触发） =====================
def pytest_unconfigure(config):
    info("🔔 pytest_unconfigure 钩子被触发了")
    # 飞书通知
    if FEISHU_WEBHOOK:
        FeishuNotifier(FEISHU_WEBHOOK).send_feishu()
    # 邮件通知
    if os.getenv("EMAIL_SENDER"):
        EmailNotifier(
            html_report_path=PYTEST_HTML_REPORT,
            allure_results_dir=ALLURE_RESULTS_DIR,
            allure_report_dir=ALLURE_REPORT_DIR,
            report_dir=REPORT_DIR,
            run_time=_RUN_TIME
        ).send_email()



