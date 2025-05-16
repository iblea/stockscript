
# pip3 install requests

import requests
import zipfile
import io

import os

from common import DATA_DIR


requests.packages.urllib3.disable_warnings()

columns = ['종목코드', '서버자동주문 가능 종목 여부', '서버자동주문 TWAP 가능 종목 여부', '서버자동 경제지표 주문 가능 종목 여부',
                    '필러', '종목한글명', '거래소코드 (ISAM KEY 1)', '품목코드 (ISAM KEY 2)', '품목종류', '출력 소수점', '계산 소수점',
                    '틱사이즈', '틱가치', '계약크기', '가격표시진법', '환산승수', '최다월물여부 0:원월물 1:최다월물',
                    '최근월물여부 0:원월물 1:최근월물', '스프레드여부', '스프레드기준종목 LEG1 여부', '서브 거래소 코드']

def download_file():
    print("Downloading...")

    file_content = None
    try:
        response = requests.get('https://new.real.download.dws.co.kr/common/master/ffcode.mst.zip', verify=False)
        print(response.status_code)
        if response.status_code != 200:
            raise Exception(f"Failed to request data, status code: {response.status_code}")

        z = zipfile.ZipFile(io.BytesIO(response.content))
        file_content = z.read('ffcode.mst')
        print(file_content)

        with open('ffcode.mst', 'wb') as f:
            f.write(file_content)
        print("File saved successfully.")

    except Exception as e:
        print("Error in download_file:", e)
        file_content = None

    return file_content



file_content = None

FFCODE_MST_FILE = DATA_DIR + 'ffcode.mst'

if os.path.exists(FFCODE_MST_FILE):
    print("Find ffcode.mst")
    with open(FFCODE_MST_FILE, 'rb') as f:
        file_content = f.read()
else:
    print("File not found, downloading...")
    file_content = download_file()


if file_content is None:
    print("Failed to download or read the file.")
    from sys import exit
    exit(1)

# 적절한 인코딩을 찾는 함수
def try_decode(binary_data):
    encodings = ['utf-8', 'cp949', 'euc-kr', 'latin1']

    for encoding in encodings:
        try:
            return binary_data.decode(encoding), encoding
        except UnicodeDecodeError:
            continue

    # 모든 인코딩 시도 실패시 latin1은 어떤 바이트 시퀀스든 디코딩 가능
    # (단, 한글이 깨질 수 있음)
    return binary_data.decode('latin1'), 'latin1'

print("Converting")
file_content, used_encoding = try_decode(file_content)
print("Converted!!")
print("encoding:", used_encoding)

lst = [ columns ]
# print(file_content)

contents = file_content.splitlines()
for row in contents:
    a = row[:32]              # 종목코드
    b = row[32:33].rstrip()   # 서버자동주문 가능 종목 여부
    c = row[33:34].rstrip()   # 서버자동주문 TWAP 가능 종목 여부
    d = row[34:35]            # 서버자동 경제지표 주문 가능 종목 여부
    e = row[35:82].rstrip()   # 필러
    f = row[82:107].rstrip()  # 종목한글명
    g = row[-92:-82]          # 거래소코드 (ISAM KEY 1)
    h = row[-82:-72].rstrip() # 품목코드 (ISAM KEY 2)
    i = row[-72:-69].rstrip() # 품목종류
    j = row[-69:-64]          # 출력 소수점
    k = row[-64:-59].rstrip() # 계산 소수점
    l = row[-59:-45].rstrip() # 틱사이즈
    m = row[-45:-31]          # 틱가치
    n = row[-31:-21].rstrip() # 계약크기
    o = row[-21:-17].rstrip() # 가격표시진법
    p = row[-17:-7]          # 환산승수
    q = row[-7:-6].rstrip() # 최다월물여부 0:원월물 1:최다월물
    r = row[-6:-5].rstrip() # 최근월물여부 0:원월물 1:최근월물
    s = row[-5:-4].rstrip() # 스프레드여부
    t = row[-4:-3].rstrip() # 스프레드기준종목 LEG1 여부 Y/N
    u = row[-3:].rstrip() # 서브 거래소 코드

    lst.append([a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u])

print("\nDone, count:", len(lst) - 1)
# print(lst)
print(lst[0])
print(lst[1])


