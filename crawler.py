import argparse
import os
import time

import pandas
import requests
from bs4 import BeautifulSoup

class Crawler():
    def __init__(self,args):

        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}

        self.start_page = args.start_page                       # 起始页
        self.end_page = args.end_page                           # 截止页
        self.url = 'http://www.juqingba.cn/neidijuqing/59486'              # url
        

    def get_page(self): 
        for page in range(self.start_page, self.end_page+1):
            if page==1:
                url = self.url+'.html'
            else:
                url = self.url+'_'+str(page)+'.html'

            print(url)
            try:
                self.req = requests.get(url, headers=self.headers)
                self.req.encoding = 'gbk'
                print(self.req.status_code)
                if self.req.status_code == 200:                     # 状态码为200时进行解析
                    self.decode(self.req.content)
            except Exception as e:
                print("出现错误")
                print(e)

    def decode(self, html):

        soup = BeautifulSoup(html, "html.parser")
        end = False
        for content in soup.find_all('p'):
            if end:
                break
            if "剧情吧原创剧情" in content.getText():            # 剧情吧原创剧情向后是无用内容
                index = content.getText().index("剧情吧原创剧情")
                content_ = content.getText()[:index-1]
            else:
                content_ = content.getText()
            with open('content.txt',"a") as file:   # 将梗概写入文档
                file.write(content_ +"\n")
            if "weibo" in content.getText():                    # 出现weibo字段表示结束
                end = True


parser = argparse.ArgumentParser()
parser.add_argument("-s","--start_page",type=int,default=1,help="起始页")
parser.add_argument("-e","--end_page",type=int,default=26,help="终止页")
args = parser.parse_args()

crawler = Crawler(args)
crawler.get_page()
# crawler.result()
# crawler.write()
# crawler.data_analysis()
