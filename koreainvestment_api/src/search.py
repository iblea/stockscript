
import requests
requests.packages.urllib3.disable_warnings()

from common import API_KEY, DOMAIN
from common import auth_headers
from authlib import get_token


PATH = "/uapi/overseas-futureoption/v1/quotations/inquire-price"

def 해외선물종목현재가(access_token, app_key, app_secret, stock_code):
    """
    https://apiportal.koreainvestment.com/apiservice-apiservice?/uapi/overseas-futureoption/v1/quotations/inquire-price
    """
    TR_ID = "HHDFC55010000"
    headers = auth_headers(app_key, app_secret, access_token)
    headers.update({
        "tr_id": TR_ID,                             # TR ID
        "custtype": "P",                            # 고객 구분 (P: 개인, C: 기업)

    })

    url = DOMAIN + PATH + f"?SRS_CD={stock_code}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(data)
        if data['rt_cd'] == '0':
            print("success!")
            return data
        else:
            print(f"Error: {data['rt_cd']} - {data['msg']}")
            return None
    else:
        print(f"HTTP Error: {response.status_code}")
        print(f"Response: {response.text}")
        return None



API_KEY.load_key_config()

access_token= get_token()
app_key= API_KEY.get_appkey()
app_secret= API_KEY.get_appsecret()

해외선물종목현재가(access_token, app_key, app_secret, "MNQM25")
해외선물종목현재가(access_token, app_key, app_secret, "MESM25")
# 해외선물종목현재가(access_token, app_key, app_secret, "MGCM25")

