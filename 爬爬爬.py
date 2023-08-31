import requests
import re
import csv
import json
import emoji
import tkinter as tk
from tkinter import messagebox

global data, oid
data = []
page = 1
oid = ""


def get_oid():  # 输入视频链接拿到oid
    video_url = entry.get()
    print("video_url:", video_url)
    response = requests.get(video_url)
    content = response.text
    # print("content",content)

    # 匹配&oid=开头，数字结尾
    pattern = re.compile(r'&oid=\d+')
    # 匹配数字
    oid = pattern.findall(content)
    # 去掉&oid=
    oid = oid[0][5:]

    get_data(oid, page)
    print(oid)
    return oid


def get_data(oid, page):  # 获取评论区，翻页
    print("oid", oid)
    while True:
        success = get_comments(oid, page)  # 调用方法
        page += 1
        if get_comments(oid, page) == 0:
            break


def get_comments(oid, page):
    # url = f"https://api.bilibili.com/x/v2/reply/main?mode=3&oid={video_id}&pagination_str=%7B%22offset%22:%22%22%7D&plat=1&seek_rpid=&type=1"  # 替换上面的URL中的song_id为你想要爬取评论的歌曲ID
    url = f"https://api.bilibili.com/x/v2/reply"  # https://api.bilibili.com/x/v2/reply?type=1&oid={video_id}&pn=100

    # 配置请求头，伪装成浏览器
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    }
    # 参数
    params = {
        'type': 1,
        'oid': oid,
        'pn': page,
    }

    # 发起HTTP请求获取网页内容,请求方式可以是get、post等
    response = requests.get(url, headers=headers, params=params)
    print(response.text)  # 打印源数据
    json_data = json.loads(response.text)

    if json_data['data']['replies'] is not None:
        for item in json_data['data']['replies']:
            uname = item['member']['uname']
            sex = item['member']['sex']
            content = item['content']['message']
            processed_content = emoji.demojize(content)
            # print(uname, sex, processed_content)
            data.append({'昵称': uname, '性别': sex, '评论内容': processed_content})

        print('第{}页爬取完成'.format(page))

        save_to_csv(data)  # 调用方法将数据写入csv文件
        return 1
    else:
        print('爬完了')
        return 0


def save_to_csv(data):  # 保存excel文件
    filename = '评论区.csv'

    with open(filename, 'a', newline='', encoding='utf-8') as f:
        fieldnames = ['昵称', '性别', '评论内容']
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(data)


def main():
    get_oid()
    messagebox.showinfo('提示', '爬取完成')


root = tk.Tk()
frame = tk.Frame(root)
frame.pack(pady=10, anchor="center")
root.geometry("400x300")
root.title('B站视频评论爬取')
label = tk.Label(root, text="Hello, World! by cls")
button = tk.Button(root, text="开始!", command=main)
entry = tk.Entry(root)
label2 = tk.Label(root, text="输入B站链接")
label.pack(ipady='50')
label2.pack()
entry.pack(ipadx='50',pady='10')
button.pack(pady='10')
root.mainloop()

print('数据爬取完成！')
