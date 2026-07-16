import requests
from requests import Response
from common.logger_util import info, error, warning
from common.yaml_util import load_yaml


class HttpClient:
    def __init__(self):
        """初始化方法：创建Session、加载环境配置、设置默认headers"""
        env_config = load_yaml("config/env.yaml")
        active_env = env_config["active_env"]
        self.base_url = env_config[active_env]["url"]
        self.timeout = env_config[active_env]["timeout"]
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json"
        })

    def __del__(self):
        """析构方法：对象销毁时自动关闭Session，释放TCP连接"""
        if hasattr(self, "session") and self.session is not None:
            self.session.close()

    def __build_url(self, path: str) -> str:
        """内部方法：自动拼接base_url和接口路径"""
        if path.startswith("/"):
            path = path[1:]
        full_url = f"{self.base_url}/{path}"
        return full_url

    def __log_request(self, method: str, url: str, **kwargs):
        """内部方法：记录请求的全量日志"""
        info(f"📤 发送请求：{method.upper()} {url}")
        if "json" in kwargs:
            info(f"📤 请求参数（JSON）：{kwargs['json']}")
        if "params" in kwargs:
            info(f"📤 请求参数（Query）：{kwargs['params']}")
        if "headers" in kwargs:
            safe_headers = {k: v for k, v in kwargs["headers"].items() if k.lower() != "authorization"}
            info(f"📤 请求头：{safe_headers}")

    def __log_response(self, response: Response):
        """内部方法：记录响应的全量日志"""
        info(f"📥 收到响应：HTTP状态码 {response.status_code}")
        try:
            res_json = response.json()
            info(f"📥 响应体（JSON）：{res_json}")
        except requests.exceptions.JSONDecodeError:
            info(f"📥 响应体（Text）：{response.text[:500]}")  # 截断长文本避免日志爆炸

    def request(self, method: str, path: str = None, url: str = None, **kwargs) -> Response:
        """
        通用请求方法，同时支持 path（相对路径）和 url（相对路径）参数
        完全兼容 requests.Session.request 的所有参数
        """
        # ✅ 核心兼容逻辑：优先用 path，没有则用 url
        request_path = path or url
        if not request_path:
            raise ValueError("必须传入 path 或 url 参数（二选一）")
        full_url = self.__build_url(request_path)
        timeout = kwargs.pop("timeout", self.timeout)
        self.__log_request(method, full_url, **kwargs)
        try:
            response = self.session.request(
                method=method,
                url=full_url,
                timeout=timeout,
                **kwargs
            )
            self.__log_response(response)
            if response.status_code >= 400:
                warning(f"⚠️ HTTP状态码异常：{response.status_code}")
            return response
        except requests.exceptions.RequestException as e:
            error(f"❌ 请求失败！错误详情：{str(e)}")
            raise

    # ===================== 快捷方法（同时支持 path 和 url 参数） =====================
    def get(self, path: str = None, url: str = None, **kwargs) -> Response:
        return self.request("get", path=path, url=url, **kwargs)

    def post(self, path: str = None, url: str = None, **kwargs) -> Response:
        return self.request("post", path=path, url=url, **kwargs)

    def put(self, path: str = None, url: str = None, **kwargs) -> Response:
        return self.request("put", path=path, url=url, **kwargs)

    def delete(self, path: str = None, url: str = None, **kwargs) -> Response:
        return self.request("delete", path=path, url=url, **kwargs)