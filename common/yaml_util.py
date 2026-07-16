import os
import yaml
import pytest

def load_yaml(file_path,max_memory_mb=200):
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(root_dir, file_path)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Yaml文件不存在：{full_path}")
    full_size_bytes = os.path.getsize(full_path) # 获取当前文件大小，单位bytes
    full_size_mb = full_size_bytes / 1024 / 1024 # 转换成MB
    if full_size_mb > max_memory_mb * 0.8:
        raise MemoryError(f"❌ 文件过大 ({full_size_mb:.2f}MB)，超过内存限制 ({max_memory_mb}MB)")
    with open(full_path, "r", encoding="utf-8",buffering=8192) as f:
        data = yaml.safe_load(f)
        return data

def load_yaml_with_marks(file_path, key):
    """
    ✅ 数据驱动标签核心函数
    输入：YAML文件路径 + 用例组键名
    输出：带标签的pytest.param列表
    """
    # 1. 加载原始YAML数据
    data = load_yaml(file_path)
    cases = data[key]
    processed_cases = []
    for case in cases:
        # 2. 取出并删除marks字段（用pop保证测试函数拿到的case和原来完全一致）
        case_marks = case.pop("marks", [])
        marks = []
        # 3. 把字符串标签转换成pytest标签对象
        for mark in case_marks:
            if mark == "skip":
                marks.append(pytest.mark.skip(reason="该功能暂未开发，待实现"))
            elif mark == "xfail":
                marks.append(pytest.mark.xfail(reason="已知bug，开发正在修复中"))
            else:
                # 动态获取pytest.mark.xxx对象
                marks.append(getattr(pytest.mark, mark))
        # 4. 把数据和标签绑定成pytest能识别的格式
        processed_cases.append(pytest.param(case, marks=marks))
    return processed_cases









