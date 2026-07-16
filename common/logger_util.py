# -*- coding: utf-8 -*-
"""
@Author: tianjiayu
@File: logger_util.py
"""

import logging.config
from common.logsettings import LOGGING_DIC  # 导入日志配置

# ===================== 1. 用dictConfig加载你的LOGGING_DIC配置 =====================
# 这是核心：完全定义的格式、处理器、记录器来初始化logging
logging.config.dictConfig(LOGGING_DIC)
# ===================== 2. 获取项目专用的logger（对应logsettings.py里的api_test_logger） =====================
logger = logging.getLogger("api_test_logger")

# ===================== 3. 封装快捷调用方法（和之前一样，简化使用） =====================
def debug(msg: str):
    """调试级日志，开发时用"""
    logger.debug(msg)

def info(msg: str):
    """信息级日志，正常业务流程用"""
    logger.info(msg)

def warning(msg: str):
    """警告级日志，不影响用例执行，但需要关注"""
    logger.warning(msg)

def error(msg: str):
    """错误级日志，用例执行失败用"""
    logger.error(msg)

def critical(msg: str):
    """严重错误级日志，项目启动失败用"""
    logger.critical(msg)