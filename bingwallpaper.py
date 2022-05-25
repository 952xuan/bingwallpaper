# -*- coding:UTF-8 -*-
# 必应壁纸爬虫
# （妈耶爬错网站了，真必应网找机会另外写）
import time
import urllib
from bs4 import BeautifulSoup
from queue import Queue
from threading import Thread
import socket
import requests
from urllib import request
import os
import random

# UA池子
ua = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36",
      "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36",
      "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.17 Safari/537.36",
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36",
      "Mozilla/5.0 (X11; NetBSD) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36",
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36",
      "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
      "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
      "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
      "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
      "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
      "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
      "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
      "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
      "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
      "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
      "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
      "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
      "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
      "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
      "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
      "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:22.0) Gecko/20130328 Firefox/22.0",
      "Opera/9.80 (Windows NT 6.1; U; fi) Presto/2.7.62 Version/11.00",
      "Mozilla/5.0 (X11; CrOS i686 3912.101.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36",
      "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; Media Center PC 6.0; InfoPath.2; MS-RTC LM 8)",
      "Mozilla/5.0 (Windows; U; Windows NT 6.1; fr-FR) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27",
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2",
      ]

# 多线程
class DownloadBIZHI(Thread):

    def __init__(self, queue, path, proxy_pool_port):
        Thread.__init__(self)
        self.queue = queue
        self.path = path
        self.proxy_pool_port = proxy_pool_port
        if not os.path.exists(path):
            os.makedirs(path)

    def run(self):
        while True:
            url = self.queue.get()
            try:
                download(url, self.path, self.proxy_pool_port)
            finally:
                self.queue.task_done()

# 规范化命名
def ReNameTT(title):
    title = title.replace(' ', '-')
    title = title.replace('|', '')
    title = title.replace("['", '')
    title = title.replace("']", '')
    title = title.replace('["', '')
    title = title.replace('"]', '')
    title = title.replace('"', '')
    title = title.replace('\n', '')
    title = title.replace(':', '')
    title = title.replace('&', '')
    title = title.replace('nbps', '')
    title = title.replace('>', '')
    title = title.replace('<', '')
    title = title.replace('\\', '')
    title = title.replace('/', '')
    title = title.replace('h3', '')
    return str(title)

def get_proxy(proxy_pool_port):
    a = requests.get("http://127.0.0.1:"+str(proxy_pool_port)+"/get/").json()
    b = a.get("https")
    if not b:
        proxy = {"http": str(a.get("proxy"))}
    else:
        # proxy = {"https": str(a.get("proxy"))} request库用s有时报错但是把https当http又能直接用=-=
        proxy = {"http": str(a.get("proxy"))}
    return proxy

def delete_proxy(proxy):
    requests.get("http://127.0.0.1:11248/delete/?proxy={}".format(proxy))

def get_header(url):
    return {"user-agent": random.choice(ua),
            "Referrer":url}

# 网页连接
# def url_open(url,proxy_pool_port):
    # 写法2
    # header = get_header(url)
    # proxy = get_proxy(proxy_pool_port)
    # print("本次爬取使用代理：", proxy, '\n', "使用的header", str(header), '\n')
    # req = request.Request(url, headers=header)
    # proxyHandler = request.ProxyHandler(proxy)
    # opener = request.build_opener(proxyHandler)
    # response = opener.open(req)
    # socket.setdefaulttimeout(5)
    # # 读取响应文件
    # try:
    #     html = response.read().decode('utf-8')
    #     return html
    # except urllib.request.URLError as e:
    #     print(e)
    #     html = url_open(url)
    #     return html
    # except:
    #     html = url_open(url)
    #     return html

# 下载图片
def download(url,path,proxy_pool_port):
    header = get_header(url)
    proxy = get_proxy(proxy_pool_port)
    print("本次爬取使用代理：", proxy, '\n', "使用的header", str(header), '\n')
    response = requests.get(url=url, proxies=proxy, headers=header, timeout=10)
    try:
        if response.status_code == 200:
            html =response.text
    except:
        print("链接失败，进行重试")
        download(url,path,proxy_pool_port)
    soup = BeautifulSoup(html, 'lxml')
    # 写法2
    # soup = BeautifulSoup(url_open(url,proxy_pool_port), 'lxml')
    print("链接：" + url)

    img_list = soup.find_all('img', class_='progressive__img')
    img_name = soup.find_all('h3')
    # 每页下载到本地的路径（按页命名）
    F_path = str(path) + str(url).replace('https://bing.ioliu.cn/?p=', '')

    if not (os.path.isdir(F_path)):
        os.mkdir(F_path)

    if len(os.listdir(F_path)) == len(img_list):
        print("第" + str(url).replace('https://bing.ioliu.cn/?p=', '') + "页下载完毕")
        return None

    for i in range(0, len(img_list)):

        image = str(img_list[i].get('data-progressive')).replace('640x480', '1920x1080')
        # 不加注释就是原图 ， 加了就是1080p
        image = str(image).replace('http://h2.ioliu.cn/bing/','https://cn.bing.com/th?id=OHR.').replace('1920x1080.jpg?imageslim', 'UHD.jpg')

        title = ReNameTT(str(img_name[i]))

        try:
            lujing = str(F_path) + "\\" + str(title) + ".jpg"
            print("正在下载：", image)
            with open(lujing, 'wb') as f:
                time.sleep(1)
                img = requests.get(url=image,proxies=proxy,headers=header,timeout=5).content
                # 写法2
                # img = requests.get(image,proxies=get_proxy(proxy_pool_port)).content
                f.write(img)
                f.close()
            # daxiao = os.stat(lujing).st_size
            # if daxiao<524288 :
            #     os.remove(lujing)
            #     print("文件过小，疑似损坏")
            # else:
                print("图片"+title+"下载完成"+'\n'+"文件大小为："+ str((os.stat(lujing).st_size)/1048576)[0:3] +"MB")
        except OSError:
            download(url, path, proxy_pool_port)
            print('length  failed')
    download(url, path, proxy_pool_port)





if __name__ == '__main__':
    # print("输入起始页（前一次回车返回起点，后一次终点）")
    # num1 = int(input())
    # num2 = int(input())
    # print("开启线程数（为网站运营着想，建议不超过5）")
    # num3 = int(input())
    # print("redis的端口号")
    # num4 = str(input())

    # 构建所有的链接 共190页 原画质只有92页
    _url = "https://bing.ioliu.cn/?p={page}"
    # urls = [_url.format(page=page) for page in range(num1, num2)]
    urls = [_url.format(page=page) for page in range(1, 93)]

    proxy_pool_port = 11248

    queue = Queue()
    # 存储位置
    path = "C:\\Users\\Administrator\\Desktop\\新建文件夹\\测试\\"

    for x in range(3):
        worker = DownloadBIZHI(queue, path, proxy_pool_port)
        worker.daemon = True
        worker.start()

    for url in urls:
        queue.put(url)

    queue.join()

    # 补缺
    # xiazai = os.listdir(path)
    # numB = 0
    # weixiazai = {}
    # for j in range(0, len(urls)):
    #     c = 1
    #     b = int(urls[j].replace('https://bing.ioliu.cn/?p=', ''))
    #     for i in range(0, len(xiazai)):
    #         a = int(xiazai[i])
    #         if a == b:
    #             c = 0
    #             break
    #     if c == 1:
    #         weixiazai[numB] = str("https://bing.ioliu.cn/?p="+str(b))
    #         numB = numB + 1
    # urls = weixiazai

