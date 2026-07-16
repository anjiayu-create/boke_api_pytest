# -*- coding: utf-8 -*-
"""
@File : test_result.py
@Auth ： tianjiayu
"""

# -*- coding: utf-8 -*-
"""
测试结果收集器
单例模式 + 线程锁，支持并行执行
所有逻辑和原始全局变量版完全兼容，仅做架构优化
"""
import threading
import time
from common.logger_util import debug, info, warning, error

class TestResultCollector:
    # 单例实例缓存
    _instance = None
    # 实例创建锁
    _instance_lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # 防止重复初始化
        if hasattr(self, "_initialized"):
            return
        self._initialized = True
        self.start_time = 0
        self.duration = 0
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.failed_cases = []
        # 数据操作锁
        self._data_lock = threading.Lock()

    def start(self):
        """测试启动：记录开始时间, 清空失败case列表"""
        self.start_time = time.time()
        self.failed_cases.clear()

    def add_result(self, report):
        """添加单条用例结果，线程安全"""
        if report.when != "call":
            return
        with self._data_lock:
            self.total += 1
            if report.passed:
                self.passed += 1
            elif report.failed:
                self.failed += 1
                case_name = report.nodeid.split("::")[-1]
                self.failed_cases.append(case_name)
            elif report.skipped:
                self.skipped += 1

    @property
    def calculate_duration(self):
        """计算执行总时长"""
        self.duration = round(time.time() - self.start_time, 2)
        return self.duration

    @property
    def pass_rate(self):
        """计算通过率"""
        if self.total == 0:
            return 0.0
        return round(self.passed / self.total * 100, 2)


# 全局单例实例，全项目共用
result_collector = TestResultCollector()