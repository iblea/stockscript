from common import DATA_DIR
from common import API_KEY
from common import getKIURL, default_headers, auth_headers
import requests
import json
from datetime import datetime
from typing import Optional
from os.path import exists

requests.packages.urllib3.disable_warnings()




TOKEN_FILE: str = "token.json"
TOKEN_AUTH = { "token": "", "expire": datetime.strptime("1900-01-01 00:00:00", "%Y-%m-%d %H:%M:%S") }

token_file = "token.json"

def get_token(app_key: str = "", app_secret: str = "") -> str:
    global TOKEN_AUTH
    if TOKEN_AUTH["token"] == "":
        result = read_token()
        if result == False:
            TOKEN_AUTH = { "token": "", "expire": datetime.strptime("1900-01-01 00:00:00", "%Y-%m-%d %H:%M:%S") }

    if TOKEN_AUTH["expire"] <= datetime.now():
        print("Token expired. creating new token.")
        if create_access_token(app_key, app_secret) == False:
            return ""
        write_token()

    return TOKEN_AUTH["token"]

def read_token() -> bool:
    global TOKEN_AUTH
    TOKEN_PATH = DATA_DIR + TOKEN_FILE
    if exists(TOKEN_PATH) == False:
        print(f"Token file not found: {TOKEN_PATH}")
        return False

    try:
        with open(TOKEN_PATH, "r") as f:
            data = json.load(f)
            TOKEN_AUTH["token"] = data["token"]
            TOKEN_AUTH["expire"] = datetime.strptime(data["expire"], "%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"Error reading token file: {e}")
        return False
    return True

def write_token() -> bool:
    global TOKEN_AUTH
    TOKEN_PATH = DATA_DIR + TOKEN_FILE
    try:
        data = {
            "token": TOKEN_AUTH["token"],
            "expire": TOKEN_AUTH["expire"].strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(TOKEN_PATH, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error writing token file: {e}")
        return False
    return True

def create_access_token(app_key, app_secret) -> bool:
    """
    https://apiportal.koreainvestment.com/apiservice-apiservice?/oauth2/tokenP
    """

    "https://openapi.koreainvestment.com:9443"
    "/oauth2/tokenP"

    # requests.post()
    print("create auth")
    url = getKIURL(path="/oauth2/tokenP")
    headers = default_headers()
    body = {
        "grant_type": "client_credentials",
        "appkey": app_key,
        "appsecret": app_secret
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(body), verify=False)
        response.raise_for_status()  # HTTP 에러 발생 시 예외 발생

        token_data = response.json()
        # print(token_data)
        TOKEN_AUTH["token"] = token_data["access_token"]
        TOKEN_AUTH["expire"] = datetime.strptime(token_data["access_token_token_expired"], "%Y-%m-%d %H:%M:%S")
        print("Success to create access token, expire time: [{}]".format(token_data["access_token_token_expired"]))

    except requests.exceptions.RequestException as e:
        print(f"Failed to create access token: {e}")
        return False

    if write_token() == False:
        print("Failed to write token to file.. try to destroy token. [{}]".format(TOKEN_AUTH["access_token"]))
        destroy_access_token(app_key, app_secret, token_data["access_token"])
    return True

def destroy_access_token(app_key, app_secret, access_token) -> bool:
    """
    https://apiportal.koreainvestment.com/apiservice-apiservice?/oauth2/revokeP
    """

    url = getKIURL("/oauth2/revokeP")
    headers = default_headers()
    body = {
        "appkey": app_key,
        "appsecret": app_secret,
        "token": access_token
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(body), verify=False)
        response.raise_for_status()  # HTTP 에러 발생 시 예외 발생

        token_data = response.json()
        print(token_data)
        print("destroy token success: [{}]".format(access_token))
        return token_data
    except requests.exceptions.RequestException as e:
        print(f"Failed to destroy access token: {e}")
        return False
    return True

def get_hashkey(app_key, app_secret, access_token, body):
    """
    https://apiportal.koreainvestment.com/apiservice-apiservice?/uapi/hashkey
    """

    url = getKIURL("/uapi/hashkey")
    headers = auth_headers(app_key, app_secret, access_token)
    try:
        response = requests.post(url, headers=headers, data=json.dumps(body), verify=False)
        response.raise_for_status()  # HTTP 에러 발생 시 예외 발생

        hashkey_data = response.json()
        print(hashkey_data)
        return hashkey_data
    except requests.exceptions.RequestException as e:
        print(f"Failed to create hashkey: {e}")
        return None

    # requests.post()
    print("get hashkey")
    return "hashkey"


def websocket_key():
    """
    https://apiportal.koreainvestment.com/apiservice-apiservice?/oauth2/Approval
    """

    "https://openapi.koreainvestment.com:9443"
    "/oauth2/Approval"

    # requests.post()
    print("get websocket key")


if __name__ == "__main__":
    API_KEY.load_key_config()
    access_token = get_token(API_KEY.get_appkey(), API_KEY.get_appsecret())
    print("Access Token:", access_token)
    # destroy_access_token(app_key, app_secret, access_token)


