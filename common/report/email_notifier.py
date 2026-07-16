# -*- coding: utf-8 -*-
"""
@File : email_notifiler.py
@Auth ： tianjiayu
"""
import os
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from common.logger_util import info, warning, error
from common.report.result_collector import result_collector
from common.report.report_generator import generate_allure_report, zip_dir


class EmailNotifier:
    def __init__(self,html_report_path: str,allure_results_dir: str,allure_report_dir: str,report_dir: str,run_time: str):
        self.html_report_path = html_report_path
        self.allure_results_dir = allure_results_dir
        self.allure_report_dir = allure_report_dir
        self.report_dir = report_dir
        self.run_time = run_time

        # 邮箱账号配置：从环境变量读取
        self.sender = os.getenv("EMAIL_SENDER")
        self.password = os.getenv("EMAIL_PASSWORD")
        self.receivers = os.getenv("EMAIL_RECEIVERS","").split(",")
        self.smtp_server = os.getenv("EMAIL_SMTP_SERVER")
        self.smtp_port = int(os.getenv("EMAIL_SMTP_PORT", 465))

    def send_email(self):
        """发送测试结果邮件，失败仅告警"""
        info("📧 调用 send_email 方法，准备发送邮件")
        if not all([self.sender, self.password, self.receivers, self.smtp_server]):
            warning("⚠️ 邮件配置不完整，跳过发送邮件通知")
            return
        try:
            # 状态判断+失败用例展示
            if result_collector.failed > 0:
                subject = f"❌ 测试失败_{self.run_time}"  # run_time传入的时间戳
                theme_color = "#f5222d"
                failed_html = "".join([f"<li>{case}</li>" for case in result_collector.failed_cases])
                failed_section = f"""
                <div style="background: #fff1f0; border-left: 4px solid #f5222d; padding: 16px; border-radius: 4px; margin: 16px 0;">
                    <h4 style="margin: 0 0 8px 0; color: #f5222d;">❌ 失败用例列表：</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #cf1322;">{failed_html}</ul>
                </div>
                """
            else:
                subject = f"✅ 测试成功_{self.run_time}"
                theme_color = "#52c41a"
                failed_section = ""

            html = f"""
            <h2 style="color: {theme_color};">{subject}</h2>
            <p>测试时间：{time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            <h3>测试结果：</h3>
            <p>总用例：{result_collector.total} | 通过：{result_collector.passed} | 失败：{result_collector.failed} | 跳过：{result_collector.skipped}</p>
            <p>通过率：{result_collector.pass_rate}% | 耗时：{result_collector.calculate_duration}秒</p>
            {failed_section}
            <hr>
            <p><strong>附件说明：</strong></p>
            <p>1. pytest-html报告：直接双击打开查看详细失败日志</p>
            <p>2. Allure报告：解压后执行 allure serve 目录名 查看交互式报告</p>
            """
            msg = MIMEMultipart()
            msg["From"] = self.sender
            msg["To"] = ",".join(self.receivers)
            msg["Subject"] = subject
            msg.attach(MIMEText(html, "html", "utf-8"))

            # 附件1：pytest-html报告（带时间戳）
            time.sleep(1)
            with open(self.html_report_path, "rb") as f:
                att = MIMEApplication(f.read())
                att.add_header("Content-Disposition", "attachment", filename=f"测试报告_{self.run_time}.html")
                msg.attach(att)

            # 附件2：Allure报告压缩包（带时间戳）
            allure_dir = generate_allure_report(self.allure_results_dir, self.allure_report_dir)
            if allure_dir:
                zip_p = os.path.join(self.report_dir, f"Allure报告_{self.run_time}.zip")  # 输出的allure压缩包路径
                zip_dir(allure_dir, zip_p)
                with open(zip_p, "rb") as f:
                    att2 = MIMEApplication(f.read())
                    att2.add_header("Content-Disposition", "attachment", filename=f"Allure报告_{self.run_time}.zip")
                    msg.attach(att2)
            # 连接服务器并发送
            server = smtplib.SMTP_SSL(os.getenv("EMAIL_SMTP_SERVER"), int(os.getenv("EMAIL_SMTP_PORT")))
            server.login(self.sender, self.password)
            server.sendmail(self.sender, self.receivers, msg.as_string())
            server.quit()
            info(f"✅ 邮件+报告发送成功")
        except Exception as e:
            warning(f"⚠️ 邮件通知发送失败：{str(e)}，不影响测试结果")



