import requests

# 假设这是你的headers字典
headers = {
    'referer': 'https://space.bilibili.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0',
    'cookie': 'SESSDATA=5e90b00d%2C1694782634%2Cc7a51%2A32'
}

# 打印检查headers
print("Headers being sent:")
print(headers)

# 发送请求到一个测试URL
test_url = 'https://httpbin.org/headers'
try:
    response = requests.get(test_url, headers=headers)
    print("Response received:")
    print(response.json())  # httpbin.org返回了你发送的headers，这样可以进行验证
except Exception as e:
    print("Error during the request:", e)


