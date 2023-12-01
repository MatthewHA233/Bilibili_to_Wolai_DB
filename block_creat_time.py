
import requests
from datetime import datetime

WOLAI_DATABASE_ID = "tTnwmf7ki7X1uZnxF7wApD"
parent_block_id = "5fec7AhacDJ7nrZjhre4QV"
# 新加入的

def save_token_to_file(token):
    with open("700 功能性文件/wolai_token.md", "w") as file:
        file.write(token)

def read_token_from_file():
    try:
        with open("700 功能性文件/wolai_token.md", "r") as file:
            token = file.read().strip()
        return token
    except FileNotFoundError:
        return None

def is_token_valid(token):
    return token is not None and len(token) > 0

def get_or_load_token():
    token = read_token_from_file()
    if is_token_valid(token):
        return token
    else:
        token = get_wolai_token()
        if is_token_valid(token):
            save_token_to_file(token)
            return token
        else:
            print("Error: Failed to get a valid token.")
            return None

# 获取 WOLAI API Token
def get_wolai_token():
    url = "https://openapi.wolai.com/v1/token"
    headers = {"Content-Type": "application/json"}
    data = {
        "appId": "eR31BW2rHSvN2yuBT21TfA",
        "appSecret": "9c48661923600d198d308096c67fbfb8102c0389560590cc6e14ea58704a96ce"
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        token = response.json()["data"]["app_token"]
        return token
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def get_child_blocks(token, parent_block_id):
    url = f"https://openapi.wolai.com/v1/blocks/{parent_block_id}/children"
    headers = {
        "Content-Type": "application/json",
        "Authorization": token
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        child_blocks = response.json()["data"]
        return child_blocks
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def main():
    token = get_wolai_token()
    if token:
        print(f"Wolai Token: {token}")
        
        # 替换为您要获取的页面块 ID
        parent_block_id = "5fec7AhacDJ7nrZjhre4QV"
        child_blocks = get_child_blocks(token, parent_block_id)

        if child_blocks:
            print("Child blocks and their creation times:")
            for block in child_blocks:
                creation_time_unix = block["created_at"]
                creation_time = datetime.utcfromtimestamp(creation_time_unix // 1000).strftime('%Y-%m-%d')
                if block["content"]:
                    title = block["content"][0]["title"]
                else:
                    title = "No title"
                 # 修改标题获取方式
                print(f"Block ID: {block['id']}, Title: {title}, Creation Time: {creation_time}")

            print("\nPress any key to continue...")
            input()  # 等待按下任意键后继续执行

            # 在这里添加您希望在按下任意键后执行的后续代码

    else:
        print("Failed to get Wolai Token.")


if __name__ == "__main__":
    main()