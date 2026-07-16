# -*- coding: utf-8 -*-
"""
@File : feishu_send.py
@Auth ： tianjiayu
"""
import requests
from common.logger_util import info, warning
from common.report.result_collector import result_collector

class FeishuNotifier:
    def __init__(self,webhook_url):
        self.webhook_url = webhook_url

    def send_feishu(self):
        if not self.webhook_url:
            return
        try:
            if result_collector.failed > 0:
                color = "red"
                title = "❌ 测试执行失败"
                failed_text = "\n".join([f"• {case}" for case in result_collector.failed_cases])
            else:
                color = "green"
                title = "✅ 测试执行成功"
                failed_text = ""

            elements = [{
                "tag": "div",
                "text": {
                    "content": f"**测试结果**\n总用例：{result_collector.total}\n"
                               f"通过：{result_collector.passed}\n"
                               f"失败：{result_collector.failed}\n"
                               f"耗时：{result_collector.calculate_duration}秒\n"
                               f"通过率：{result_collector.pass_rate}%",
                    "tag": "lark_md"
                }
            }]

            if result_collector.failed > 0:
                elements.append({"tag": "hr"})
                elements.append({
                    "tag": "div",
                    "text": {"content": f"**❌ 失败用例列表：**\n{failed_text}", "tag": "lark_md"}
                })

            msg = {
                "msg_type": "interactive",
                "card": {
                    "config": {"wide_screen_mode": True},
                    "elements": elements,
                    "header": {"title": {"content": title, "tag": "plain_text"}, "template": color}
                }
            }
            requests.post(self.webhook_url, json=msg)
            info("✅ 飞书通知发送成功")
        except Exception as e:
            # 失败只告警，绝不抛出异常影响测试主流程
            warning(f"⚠️ 飞书通知发送失败：{str(e)}，不影响测试结果")

