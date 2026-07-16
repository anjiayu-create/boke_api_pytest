from requests import Response
from common.logger_util import info, error

class AssertUtil:
    def __init__(self, case_name: str):
        self.case_name = case_name
        self._last_response = None

    def assert_http_status_code(self, response: Response, expected_code: int = 200) -> "AssertUtil":
        self._last_response = response # 将response（类型是requests.Response)写入对象私有属性中
        actual_code = response.status_code
        try:
            assert actual_code == expected_code
            info(f"✅ 【{self.case_name}】HTTP状态码断言通过：预期={expected_code}，实际={actual_code}")
        except AssertionError:
            error(f"❌ 【{self.case_name}】HTTP状态码断言失败：预期={expected_code}，实际={actual_code}")
            raise
        return self

    def assert_business_code(self, response: Response = None, expected_code: int = 200) -> "AssertUtil":
        response = response or self._last_response
        self._last_response = response
        try:
            res_json = response.json()
            actual_code = res_json.get("code")
            assert actual_code == expected_code
            info(f"✅ 【{self.case_name}】业务码断言通过：预期={expected_code}，实际={actual_code}")
        except AssertionError:
            error(f"❌ 【{self.case_name}】业务码断言失败：预期={expected_code}，实际={actual_code}")
            raise
        except Exception as e:
            error(f"❌ 【{self.case_name}】业务码断言异常：JSON解析失败，错误={str(e)}，响应文本={response.text[:500]}")
            raise
        return self

    def assert_message(self, response: Response = None, expected_msg: str = "") -> "AssertUtil":
        response = response or self._last_response
        self._last_response = response
        try:
            res_json = response.json()
            actual_msg = res_json.get("msg")
            assert actual_msg == expected_msg
            info(f"✅ 【{self.case_name}】响应消息断言通过：预期={expected_msg}，实际={actual_msg}")
        except AssertionError:
            error(f"❌ 【{self.case_name}】响应消息断言失败：预期={expected_msg}，实际={actual_msg}")
            raise
        except Exception as e:
            error(f"❌ 【{self.case_name}】响应消息断言异常：JSON解析失败，错误={str(e)}，响应文本={response.text[:500]}")
            raise
        return self

    def assert_json_key_exists(self, response: Response = None, key: str = "") -> "AssertUtil":
        response = response or self._last_response
        self._last_response = response
        try:
            res_json = response.json()
            assert key in res_json
            info(f"✅ 【{self.case_name}】JSON根节点包含字段断言通过：字段={key}")
        except AssertionError:
            error(f"❌ 【{self.case_name}】JSON根节点包含字段断言失败：字段={key}不存在，响应体={res_json}")
            raise
        except Exception as e:
            error(f"❌ 【{self.case_name}】JSON根节点包含字段断言异常：JSON解析失败，错误={str(e)}，响应文本={response.text[:500]}")
            raise
        return self

    def assert_data_key_exists(self, response: Response = None, key: str = "") -> "AssertUtil":
        response = response or self._last_response
        self._last_response = response
        try:
            res_json = response.json()
            data = res_json.get("data", {})
            assert key in data
            info(f"✅ 【{self.case_name}】data字段包含字段断言通过：字段={key}")
        except AssertionError:
            error(f"❌ 【{self.case_name}】data字段包含字段断言失败：字段={key}不存在，data={data}")
            raise
        except Exception as e:
            error(f"❌ 【{self.case_name}】data字段包含字段断言异常：JSON解析失败，错误={str(e)}，响应文本={response.text[:500]}")
            raise
        return self

    def assert_data_value(self, response: Response = None, key: str = "", expected_value=None) -> "AssertUtil":
        response = response or self._last_response
        self._last_response = response
        try:
            res_json = response.json()
            data = res_json.get("data", {})
            actual_value = data.get(key)
            assert actual_value == expected_value
            info(f"✅ 【{self.case_name}】data字段值断言通过：字段={key}，预期={expected_value}，实际={actual_value}")
        except AssertionError:
            error(f"❌ 【{self.case_name}】data字段值断言失败：字段={key}，预期={expected_value}，实际={actual_value}")
            raise
        except Exception as e:
            error(f"❌ 【{self.case_name}】data字段值断言异常：JSON解析失败，错误={str(e)}，响应文本={response.text[:500]}")
            raise
        return self

    def assert_equal(self, actual_value, expected_value, desc: str = "值相等") -> "AssertUtil":
        try:
            assert actual_value == expected_value
            info(f"✅ 【{self.case_name}】{desc}断言通过：预期={expected_value}，实际={actual_value}")
        except AssertionError:
            error(f"❌ 【{self.case_name}】{desc}断言失败：预期={expected_value}，实际={actual_value}")
            raise
        return self

    def assert_string_startswith(self, actual_value: str, expected_prefix: str, desc: str = "字符串前缀") -> "AssertUtil":
        try:
            assert actual_value.startswith(expected_prefix)
            info(f"✅ 【{self.case_name}】{desc}断言通过：预期前缀={expected_prefix}，实际字符串={actual_value}")
        except AssertionError:
            error(f"❌ 【{self.case_name}】{desc}断言失败：预期前缀={expected_prefix}，实际字符串={actual_value}")
            raise
        return self

    def assert_greater_or_equal(self, actual_value: int, expected_min: int, desc: str = "数值大于等于") -> "AssertUtil":
        try:
            assert actual_value >= expected_min
            info(f"✅ 【{self.case_name}】{desc}断言通过：预期最小值={expected_min}，实际值={actual_value}")
        except AssertionError:
            error(f"❌ 【{self.case_name}】{desc}断言失败：预期最小值={expected_min}，实际值={actual_value}")
            raise
        return self