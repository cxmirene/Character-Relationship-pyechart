import jieba
import jieba.analyse
import numpy as np
import time
import pandas
from pyecharts import options as opts
from pyecharts.charts import Graph
from pyecharts.charts import Bar

class People():
    def __init__(self):
        self.people = {}
        self.relationship = {}
        self.episode = []
        self.origin = {}

    def stopword(self):
        stop_words=[]
        with open('stopwords.txt','r',encoding='UTF-8') as f:
            for line in f:
                stop_words.append(line.strip('\n'))
        # print(stop_words)
        return stop_words

    def get_origin(self):
        df = pandas.read_excel('replace.xlsx')
        df.name = df['name']
        df.replace_name = df['replace_name']
        self.origin = df.set_index('name')['replace_name'].to_dict()
        # print(self.origin)

    def get_people(self):
        start = time.time()
        stop_words = self.stopword()
        people = {}
        # with open('people_content.txt','r',encoding="UTF-8") as f:
        with open('hlm_content.txt','r',encoding="UTF-8") as f:
            for line in f:
                part = jieba.analyse.extract_tags(line, allowPOS=('nr',))   # 只能从人名中选取
                part_ = []
                for name in part:
                    if name in stop_words:                        # 去停用词
                        continue
                    if name in list(self.origin.keys()):          # 替代词
                        name = self.origin[name]
                    if name in list(people.keys()):          # 如果该人已经存在于字典中，则其出现次数加一
                        people[name]+=1
                    else:
                        people[name]=1
                    part_.append(name)
                print(part_)
                self.episode.append(part_)           # 每一段的内容存入episode列表中
        for key, value in people.items():
            if value>=10:
                self.people[key] = value
        end = time.time()
        print(self.people)
        process = round(end-start,2)
        print("运行时间为："+str(process))

        import heapq
        length = min(len(list(self.people.keys())), 20)
        max = map(list(self.people.values()).index, heapq.nlargest(length, list(self.people.values())))
        max = list(max)
        people_20 = {}
        for m in max:
            people_20[list(self.people.keys())[m]] = list(self.people.values())[m]
        bar = (
            Bar(init_opts=opts.InitOpts(width="1200px", height="600px"))
            .add_xaxis(list(people_20.keys()))
            .add_yaxis("人物", list(people_20.values()))
            .set_global_opts(title_opts=opts.TitleOpts(title="人物出场次数"))
        )
        bar.render('人物出场次数.html')
        print("******************************************************")

    def get_realtionship(self):
        people_name = list(self.people.keys())                          # 获取过滤后的所有人名
        relationship = {}                                               # “共现”字典
        for e in self.episode:                                          # 读取每一段剧情梗概的人名列表
            for name1 in e:                                             # 对于每一个人名创建对应的子字典
                if name1 not in people_name:
                    continue
                if name1 not in list(relationship.keys()):              # 创建
                    relationship.setdefault(name1, {})
                for name2 in e:                                         # 遍历人名
                    if name2 not in people_name:                        # 因为剧情梗概的人名列表中没有进行根据出现次数过滤的操作
                        continue
                    if name1==name2:                                    # 同一个人
                        continue
                    else:
                        if name2 in list(relationship[name1].keys()):   # 出现在同一段，次数加一
                            relationship[name1][name2] += 1
                        else:
                            relationship[name1].setdefault(name2, 1)
        for key, key_value in relationship.items():
            self.relationship.setdefault(key, {})
            for key2, value in key_value.items():
                if value>=5:                                            # 将那些出现在同一段次数小于5的进行过滤
                    self.relationship[key][key2] = value
        print(self.relationship)

    def draw(self):
        nodes_data = []
        sort_people = sorted(self.people.items(), key=lambda item:item[1], reverse=True)
        for key, value in sort_people:
            nodes_data.append(opts.GraphNode(name=key, symbol_size=value/80))           # 节点出现次数
        links_data = []
        for key, key_value in self.relationship.items():
            for key2, value in key_value.items():
                links_data.append(opts.GraphLink(source=key, target=key2, value=value)) # 节点之间权值
        c = Graph(init_opts=opts.InitOpts(width="1200px", height="800px"))# 调用类
        c.add(
            "",
            nodes_data,                     # 关系图节点数据项列表
            links_data,                     # 关系图节点间关系数据项列表
            layout="circular",
            repulsion=800,                 # 节点之间的斥力因子
            edge_length=100,                # 边的两个节点之间的距离
            linestyle_opts=opts.LineStyleOpts(curve=0.3),    # 关系边的公用线条样式
            label_opts=opts.LabelOpts(position="right"),
        )
        c.set_global_opts(
            title_opts=opts.TitleOpts(title="人物图谱")
        )
        c.render("人物图谱.html")


people = People()
people.get_origin()
people.get_people()
people.get_realtionship()
people.draw()
