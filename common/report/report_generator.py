# -*- coding: utf-8 -*-
"""
@File : report_generator.py
@Auth ： tianjiayu
"""
import os
import zipfile
import subprocess
# ===================== 辅助函数 =====================
def generate_allure_report(ALLURE_RESULTS_DIR,ALLURE_REPORT_DIR):
    if not os.path.exists(ALLURE_RESULTS_DIR):
        return None
    try:
        subprocess.run(["allure", "generate", ALLURE_RESULTS_DIR, "-o", ALLURE_REPORT_DIR, "--clean"], check=True)
        return ALLURE_REPORT_DIR
    except:
        return None

def zip_dir(dir_path, zip_path):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(dir_path):
            for file in files:
                fp = os.path.join(root, file)
                zipf.write(fp, os.path.relpath(fp, os.path.dirname(dir_path)))
