from os.path import dirname, abspath

ABSOLUTE_DIR: str = dirname(dirname(abspath(__file__))) + "/"
DATA_DIR: str = ABSOLUTE_DIR + "data/"
CONF_DIR: str = ABSOLUTE_DIR + "conf/"
# DATA_DIR: str = dirname(abspath(__file__)) + "/data/"

DOMAIN = "https://openapi.koreainvestment.com:9443"

def getKIURL(path: str, query: str = "") -> str:
    """Korea Investment API URL 생성 함수
    URL을 생성하는 함수
    :param path: API 경로
    :param query: 쿼리 문자열
    :return: 완전한 URL
    """

    url = f"{DOMAIN}{path}"
    if not query:
        return url
    return f"{url}?{query}"


def default_headers() -> dict[str, str]:
    headers = {
        "content-type": "application/json; charset=utf-8",
    }
    return headers

def auth_headers(app_key: str, app_secret: str, access_token: str) -> dict[str, str]:
    headers: dict[str, str] = default_headers()
    headers.update({
        "appkey": app_key,
        "appsecret": app_secret,
        "authorization": f"Bearer {access_token}",
    })
    return headers



def remove_quotes(value: str) -> str:
    """
    문자열에서 따옴표 제거
    :param value: 따옴표가 포함된 문자열
    :return: 따옴표가 제거된 문자열
    """
    if len(value) >= 2:
        if (value[0] == '"' and value[-1] == '"') or (value[0] == "'" and value[-1] == "'"):
            return value[1:-1]
    return value

class APIKeys:

    def __init__(self):
        self.app_key: str = ""
        self.app_secret: str = ""

    def get_appkey(self) -> str:
        return self.app_key

    def get_appsecret(self) -> str:
        return self.app_secret

    def load_key_config(self) -> True:
        """
        conf/key.conf 파일에서 APP_KEY, APP_SECRET 값을 읽어 반환
        """
        conf_path: str = CONF_DIR + "key.conf"
        try:
            with open(conf_path, "r") as f:
                for line in f:
                    line: str = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("APP_KEY"):
                        key: str = remove_quotes(line.split("=", 1)[1].strip())
                        self.app_key = key
                        continue
                    if line.startswith("APP_SECRET"):
                        secret: str = remove_quotes(line.split("=", 1)[1].strip())
                        self.app_secret = secret
                        continue
        except Exception as e:
            print(f"key.conf 읽기 실패: {e}")
        if self.app_key == "" or self.app_secret == "":
            print("key.conf 파일에 APP_KEY 또는 APP_SECRET이 없습니다.")
            return False
        return True

API_KEY: APIKeys = APIKeys()

# Example usage:
# API_KEY.load_key_config()
# print("API_KEY.app_key: ", API_KEY.app_key)
# print("API_KEY.app_secret: ", API_KEY.app_secret)
