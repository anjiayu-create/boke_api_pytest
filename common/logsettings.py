# -*- coding: utf-8 -*-
"""
@Author: tianjiayu
@File: logsettings.py
@Adapted: 适配api_boke_pytest项目的日志配置
"""
import os
from datetime import datetime
# ===================== 1. 动态计算项目根目录和日志目录（适配项目） =====================
# 逻辑：当前文件在 common/ 下，往上找一级就是项目根目录
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 日志文件夹：项目根目录下的 logs/
log_dir = os.path.join(root_dir, "logs")
# 如果logs文件夹不存在，自动创建
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
# 日志文件名：按日期生成log
log_file_name = f"api_test_{datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.log"
# 完整的日志文件路径
log_file_path = os.path.join(log_dir, log_file_name)
# ===================== 2. LOGGING_DIC配置 =====================
LOGGING_DIC = {
    'version': 1.0,
    'disable_existing_loggers': False,
    # 日志格式（完全保留你的3种格式）
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(threadName)s:%(thread)d [%(name)s] %(levelname)s [%(pathname)s:%(lineno)d] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '%(asctime)s [%(name)s] %(levelname)s  %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'test': {
            'format': '%(asctime)s %(message)s',
        },
    },
    'filters': {},
    # 日志处理器（适配了filename路径，其他完全保留你的配置）
    'handlers': {
        'console_debug_handler': {
            'level': 'DEBUG',  # 日志处理的级别限制
            'class': 'logging.StreamHandler',  # 输出到终端
            'formatter': 'simple'  # 日志格式（用simple格式，控制台看起来简洁）
        },
        'file_info_handler': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件,日志轮转
            'filename': log_file_path,  # 【适配】动态生成的日志文件路径
            'maxBytes': 10 * 1024 * 1024,  # 日志大小字节
            'backupCount': 20,  # 日志文件保存数量限制
            'encoding': 'utf-8',
            'formatter': 'standard',  # 【适配】文件用standard格式，信息最全，方便复盘
        },
        'file_debug_handler': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',  # 保存到文件
            'filename': os.path.join(log_dir, 'test_debug.log'),  # 【适配】调试日志单独放
            'encoding': 'utf-8',
            'formatter': 'test',
        },
    },
    # 日志记录器（适配了我们的项目，新增api_test_logger）
    'loggers': {
        'logger1': {  # 导入时logging.getLogger时使用的app_name
            'handlers': ['console_debug_handler'],  # 日志分配到哪个handlers中
            'level': 'DEBUG',  # 日志记录的级别限制
            'propagate': False,  # 默认为True，向上（更高级别的logger）传递，设置为False即可，否则会一份日志向上层层传递传递给 root logger，导致同一条日志打印两次（一次是你的 logger，一次是 root）。
        },
        'logger2': {
            'handlers': ['console_debug_handler', 'file_debug_handler'],
            'level': 'INFO',
            'propagate': False,
        },
        # 项目专用的logger
        'api_test_logger': {
            'handlers': ['console_debug_handler', 'file_info_handler'],  # 同时输出到控制台和文件
            'level': 'DEBUG',  # 全局日志级别设为INFO
            'propagate': False,
        },
    }
}