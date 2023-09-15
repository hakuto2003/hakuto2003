import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import Label, Entry, Button, Listbox, Scrollbar, OptionMenu, StringVar
import urllib.request,urllib.error
import urllib.parse
import bs4
import re
import time
import random

# 题目难度选项
difficulty_options =["暂无评定","入门", "普及-", "普及/提高−", "普及+/提高", "提高+/省选−", "省选/NOI−", "NOI/NOI+/CTSC"]

baseUrl = "https://www.luogu.com.cn/problem/P"
baseUrl2 = "https://www.luogu.com.cn/problem/solution/P"
savePath = r"D:\学习资料\软件工程\软工实践个人作业二\Problems\\"
savePath2 = r"D:\学习资料\软件工程\软工实践个人作业二\Solutions\\"

#创建GUI页面
def create_gui():
    root = tk.Tk()
    root.title("洛谷题目爬虫")

    # 添加筛选条件输入框
    Label(root, text="筛选条件：").grid(row=0, column=0, padx=10, pady=10)
    filter_condition = StringVar()
    difficulty_option_menu = OptionMenu(root, filter_condition, *difficulty_options)
    difficulty_option_menu.grid(row=0, column=1, padx=10, pady=10)
    
    # 添加开始题号和结束题号的输入框
    Label(root, text="开始题号：").grid(row=0, column=2, padx=10, pady=10)
    start_num_entry = Entry(root)
    start_num_entry.grid(row=0, column=3, padx=10, pady=10)
    
    Label(root, text="结束题号：").grid(row=0, column=4, padx=10, pady=10)
    end_num_entry = Entry(root)
    end_num_entry.grid(row=0, column=5, padx=10, pady=10)
    
    # 添加关键词输入框
    Label(root, text="关键词：").grid(row=0, column=6, padx=10, pady=10)
    keywords_entry = Entry(root)
    keywords_entry.grid(row=0, column=7, padx=10, pady=10)

    # 添加爬取按钮，使用columnspan参数来占据多列
    crawl_button = Button(root, text="开始爬取", command=lambda: start_crawling(result_listbox, start_num_entry.get(), end_num_entry.get()))
    crawl_button.grid(row=0, column=8, columnspan=2, padx=10, pady=10)

    # 添加结果显示列表框和滚动条
    result_listbox = Listbox(root, width=120, height=20)
    result_listbox.grid(row=1, column=0, columnspan=9, padx=10, pady=10)
    scrollbar = Scrollbar(root, command=result_listbox.yview)
    scrollbar.grid(row=1, column=9, sticky='ns')
    result_listbox.config(yscrollcommand=scrollbar.set)

    root.mainloop()


def getHTML(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 SLBrowser/8.0.1.4031 SLBChan/30',
        "Cookie":"__client_id=d37c778f331c80e3fdf878bd1148a61b8738d684; login_referer=https%3A%2F%2Fwww.luogu.com.cn%2Fproblem%2FP1000;_uid=1088889",
        "authority":"www.lougu.com.cn",
        "accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accpet-language":"zh-CN,zh;q=0.9",
        "cache-control":"max-age=0",
        "sec-ch-ua": " Not)A;Brand\";v=\"99\", \"Chromium\";v=\"8\"",
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
    }

    request = urllib.request.Request(url = url, headers = headers)
    response = urllib.request.urlopen(request)
    html = response.read().decode('utf-8')
    if str(html).find("Exception") == -1:        #洛谷中没找到该题目或无权查看的提示网页中会有该字样
        return html
    else:
        return "error"

def getMD(html):
    bs = bs4.BeautifulSoup(html,"html.parser")
    core = bs.select("article")[0]
    md = str(core)
    md = re.sub("<h1>","# ",md)
    md = re.sub("<h2>","## ",md)
    md = re.sub("<h3>","#### ",md)
    md = re.sub("</?[a-zA-Z]+[^<>]*>", "", md)
    return md

def Get_TJ_MD(html):
    soup = BeautifulSoup(html, "html.parser")
    encoded_content_element = soup.find('script')
    # 获取script标签中的内容
    encoded_content = encoded_content_element.text
    # print(encoded_content)
    # 定位第一个"的位置，从当前开始截取
    start = encoded_content.find('"')
    # 定位第二个"的后面一个位置，到那里结束截取
    end = encoded_content.find('"', start + 1)
    # 截取出题解的内容
    encoded_content = encoded_content[start + 1:end]
    # 对encoded_content进行decodeURIComponent解码为html源码
    decoded_content = urllib.parse.unquote(encoded_content)
    # 转为utf-8
    decoded_content = decoded_content.encode('utf-8').decode('unicode_escape')
    # 从第一个"content":"后面开始截取
    start = decoded_content.find('"content":"')
    # 从第一个'","type":"题解"'前面结束截取
    end = decoded_content.find('","type":"题解"')
    # 截取出题解的内容
    decoded_content = decoded_content[start + 11:end]
    # 将截取的内容返回
    return decoded_content


def Get_Problem_title(problemID, result_listbox):
    # 生成要访问的url
    url = 'https://www.luogu.com.cn/problem/P' + str(problemID)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 SLBrowser/8.0.1.4031 SLBChan/30'
    }
    # 创建请求
    r = requests.get(url, headers=headers)

    # 获取网页内容
    soup = BeautifulSoup(r.text, 'html.parser')

    # 获取题目标题
    title = soup.find('title').text
    # 将题目取到标题中-前的部分
    title = title.split('-')[0]
    # 将题目末尾空格去掉
    title = title.strip()

    # 结束函数
    return title

def saveData(data, savePath ,filename):
    cfilename = savePath + filename
    file = open(cfilename,"w",encoding="utf-8")
    for d in data:
        file.writelines(d)
    file.close()

def  start_crawling(result_listbox, start_num, end_num):
    start_num = int(start_num)
    end_num = int(end_num)
    print("计划爬取到P{}".format(end_num))
    result_listbox.insert(tk.END, "计划爬取到P{}".format(end_num) + '\n')
    for i in range(start_num, end_num + 1):
        title = Get_Problem_title(i, result_listbox)
        print("正在爬取P{}...".format(i))
        result_listbox.insert(tk.END, "正在爬取P{}...".format(i))
        html = getHTML(baseUrl + str(i))
        if html == "error":
            print("爬取失败，可能是不存在该题或无权查看")
            result_listbox.insert(tk.END, "爬取失败，可能是不存在该题或无权查看" + '\n')
        else:
            problemMD = getMD(html)
            print("爬取成功！正在保存...")
            result_listbox.insert(tk.END, "爬取成功！正在保存...")
            saveData(problemMD, savePath,"P"+str(i) + " " + str(title) + ".md")
            print("保存成功!")
            result_listbox.insert(tk.END, "保存成功 " + '\n')
            time.sleep(random.randint(1, 3))
        
        # 开始爬取题解
        print("正在爬取题解...")
        result_listbox.insert(tk.END, "正在爬取题解...\n")
        html = getHTML(baseUrl2 + str(i))
        if html == 'error':
            print("题解爬取失败！")
            result_listbox.insert(tk.END, "题解爬取失败！\n")
        else:
            print("已获取题解网页源码！")
            result_listbox.insert(tk.END, "已获取题解网页源码！\n")

            # 调用函数，传入html，获取题解MD文件
            solutionMD = Get_TJ_MD(html)
            print("获取题解MD文件成功！")
            result_listbox.insert(tk.END, "获取题解MD文件成功！\n")

            # 将题目编号-题目标题-题解作为文件名
            saveData(solutionMD, savePath2, "P"+str(i) + " " + str(title) + "-题解.md")
            print('题解爬取成功！')
            result_listbox.insert(tk.END, '题解爬取成功！\n')
            time.sleep(random.randint(1, 3))

    print("爬取完毕")
    result_listbox.insert(tk.END, "爬取完毕" + '\n')


if __name__ == '__main__':
    create_gui()

