# -*- coding: utf-8 -*-
"""
@File : conftest.py
@Auth ： tianjiayu
"""
import pytest
from datetime import datetime, timedelta, UTC
from common.logger_util import debug, info, warning, error

# 1、准备工作：创建测试文章、删除测试文章（保证测试文章在使用后会被删除）
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
        error("临时文章创建失败")
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

# 2. 使用钩子函数目录级自动打标签（核心：替代每个文件的 pytestmark）
def pytest_collection_modifyitems(items):
    for item in items:
        item.add_marker(pytest.mark.article)
        item.add_marker(pytest.mark.regression)

# 3.将if判断鉴权场景搬进来
@pytest.fixture(scope="function")
def article_auth(request,valid_admin_session,real_invalid_session,admin_token,normal_token,invalid_token):
    """
    文章接口统一鉴权场景构造器（基于case_name判断，零数据改动版）
    自动读取当前用例的case_name，返回组装好的 (session对象, 请求头字典)
    逻辑与原测试文件中的鉴权分支100%一致
    """
    # 1. 自动从当前用例的参数中读取 case 数据，提取 case_name
    case_data = {}
    if hasattr(request.node, "callspec") and "case" in request.node.callspec.params:
        case_data = request.node.callspec.params["case"]
    case_name = case_data.get("case_name", "")

    # 2. 初始化默认配置（管理员正常场景）
    session = valid_admin_session
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 3. 鉴权场景判断 —— 和原来每个文件里的逻辑逐字对应，完全复刻
    if case_name == "鉴权异常-Token缺失":
        headers.pop("Authorization")
    elif case_name == "鉴权异常-Token格式错误":
        headers["Authorization"] = "invalid_token_123456"
    elif case_name == "鉴权异常-Token已过期":
        headers["Authorization"] = f"Bearer {invalid_token}"
    elif case_name == "鉴权异常-Session已失效":
        session = real_invalid_session
    elif case_name == "鉴权异常-Token与Session不匹配":
        headers["Authorization"] = f"Bearer {normal_token}"

    # 日志：方便排查，不影响业务逻辑
    info(f"🔐 当前用例：{case_name}，鉴权配置已自动加载")
    # 4. 返回组装好的结果，测试函数直接解包使用
    return session, headers

@pytest.fixture(scope="function")
def resolved_article_id(request, temp_article_id):
    """
    统一解析当前用例的 article_id
    自动根据 case_name 判断：正向/鉴权场景返回临时文章ID，参数异常场景返回用例自定义ID
    逻辑与原测试文件中的判断完全一致
    """
    # 读取用例名称（和 article_auth 相同的读取方式）
    case_data = {}
    if hasattr(request.node, "callspec") and "case" in request.node.callspec.params:
        case_data = request.node.callspec.params["case"]
    case_name = case_data.get("case_name", "")

    # 需要使用临时ID的场景集合（和原代码判断条件完全对应）
    use_temp_id_scenes = {
        "正向-查询存在的文章ID",
        "鉴权异常-Token缺失",
        "鉴权异常-Token已过期",
        "鉴权异常-Session已失效",
        "鉴权异常-Token与Session不匹配"
    }
    # 判断并返回最终ID
    if case_name in use_temp_id_scenes:
        return temp_article_id
    else:
        return case_data.get("article_id")