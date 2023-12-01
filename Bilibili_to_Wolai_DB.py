import os
import requests
import json
import re
from pprint import pprint
from datetime import datetime

# 2.2版本新增input

WOLAI_DATABASE_ID = "tTnwmf7ki7X1uZnxF7wApD"

# 读取cookies
script_dir = os.path.dirname(os.path.abspath(__file__))
cookie_file_path = os.path.join(script_dir, "700 功能性文件", "cookies.md")

cookie = open(cookie_file_path, 'r', encoding="utf-8").read()

headers = {
    'referer': 'https://space.bilibili.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0',
    'cookie': cookie
}
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

# 新建 WOLAI 数据表格行
def create_wolai_row(token, title, collected_time):
    url = f"https://openapi.wolai.com/v1/databases/{WOLAI_DATABASE_ID}/rows"
    headers = {
        "Content-Type": "application/json",
        "Authorization": token
    }

    data = {
      "rows": [{
        "标题": title,
        "收藏日期": collected_time
      }]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        print(f"Row created successfully for video: {title}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

# 获取收藏夹信息（这里测试出问题是cookie输入错了）
def get_id(name):
    url = 'https://api.bilibili.com/x/web-interface/nav'
    try:
        response = requests.get(url=url, headers=headers)
        response.raise_for_status()  # 这会在HTTP请求错误时抛出异常
        json_data = response.json()
        print(json_data)  # 打印看看返回的数据结构
        mid = json_data['data']['mid']
        return mid
    except requests.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # 打印HTTP错误信息
    except KeyError as err:
        print(f'KeyError: {err}')  # 打印KeyError信息
        print(json_data)  # 打印返回的JSON数据以便调试

    mid = json_data['data']['mid']
    url = 'https://api.bilibili.com/x/v3/fav/folder/created/list-all?up_mid={}&jsonp=jsonp'.format(mid)
    json_data = json.loads(requests.get(url=url, headers=headers).text)
    favorites_list = json_data['data']['list']
    f = {}
    for i in favorites_list:
        id_ = i['id']
        title = re.sub('([^\u4e00-\u9fa5a-zA-Z])', '', i['title']).replace('/','-')
        count = i['media_count']
        f[title] = [id_, count]
    return f

def get_favorite_videos(favorite_id):
    url = 'https://api.bilibili.com/x/v3/fav/resource/list?media_id={}&pn=1&ps=20&keyword=&order=mtime&type=0&tid=0&platform=web&jsonp=jsonp'.format(favorite_id)
    response = requests.get(url=url, headers=headers)
    json_data = json.loads(response.text)
    count = json_data['data']['info']['media_count']
    num_page = int(count/20)+1

    video_list = []

    for i in range(num_page):
        url = 'https://api.bilibili.com/x/v3/fav/resource/list?media_id={}&pn={}&ps=20&keyword=&order=mtime&type=0&tid=0&platform=web&jsonp=jsonp'.format(favorite_id, i+1)
        response = requests.get(url=url, headers=headers)
        json_data = json.loads(response.text)
        medias = json_data['data'].get('medias')

        if medias is None:
            print(f"Error: 'medias' is None. json_data: {json_data}")
            continue

        for media in medias:
            title = media['title']
            collected_time_unix = media['fav_time']
            collected_time = datetime.utcfromtimestamp(collected_time_unix).strftime('%Y-%m-%d')
            link = f'https://www.bilibili.com/video/{media["bvid"]}'
            video_info = {'title': title, 'collected_time': collected_time, 'link': link}
            video_list.append(video_info)

    return video_list


def get_table_info(token, row_limit):
    url = f"https://openapi.wolai.com/v1/databases/{WOLAI_DATABASE_ID}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": token
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        json_data = response.json()
        column_order = json_data["data"]["column_order"]
        rows = json_data["data"]["rows"]

        title_id_dict = {}
        for row in rows:
            page_id = row["page_id"]
            title = row["data"]["标题"]["value"]
            title_id_dict[title] = page_id
        
        return title_id_dict
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def create_embed_block(token, parent_id, title, video_dict):
    url = "https://openapi.wolai.com/v1/blocks"
    headers = {
        "Content-Type": "application/json",
        "Authorization": token
    }
    
    # 根据视频标题查找对应的链接
    link = None
    for video in video_dict:
        if video["title"] == title:
            link = video["link"]
            break

    # 如果找不到链接，打印错误信息
    if link is None:
        print(f"Error: Link not found for video: {title}")
        return
    
    data = {
        "parent_id": parent_id,
        "blocks": [
            {
                "type": "embed",
                "original_link": link
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"Embed block created successfully for video: {title}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

# 主程序
def main():
    # 获取收藏夹名字为 "默认收藏夹" 的视频信息
    favorite_name = "默认收藏夹"
    favorites = get_id(favorite_name)
    favorite_id = favorites[favorite_name][0]
    favorite_videos = get_favorite_videos(favorite_id)

    # 获取 WOLAI API Token
    token = get_or_load_token()
    if token:
        print(f"Wolai Token: {token}")

        # 获取用户输入的视频收藏数量
        row_limit = int(input("需要收藏多少个视频？"))

        # 根据收藏夹中的视频信息创建 WOLAI 数据表格行
        row_created = 0
        for video in favorite_videos:
            if row_created < row_limit:
                title = video["title"]
                collected_time = video["collected_time"]
                create_wolai_row(token, title, collected_time)
                row_created += 1
            else:
                break

        # 获取数据表格信息
        title_id_dict = get_table_info(token, row_limit)


        # 根据标题和块 ID 一一对应，生成 embed_block
        for video_title, parent_id in title_id_dict.items():
            create_embed_block(token, parent_id, video_title, favorite_videos)

    else:
        print("Failed to get Wolai Token.")

if __name__ == "__main__":
    main()