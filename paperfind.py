# 修改 三项超参数 获取不同的会议论文
# 输出格式：内容为：论文名 链接 作者的csv文件，文件名：年份-关键词1-关键词2-。。。-关键词n.csv
import re
import threading
import requests
import pandas
import time
import tqdm
import os

init_urls = "https://aclanthology.coli.uni-saarland.de/events"  # 初始化链接，不可修改
years = [2016, 2017, 2018]  # 获取列表内时间的论文，可修改.ps:某些年份某些会议未举办，所以不会输出结果
names = ["emnlp", "acl"]  # 获取列表内会议的论文，可修改
keywords_ = ["relation extraction"]  # 论文只要满足含有任意一个关键词就被选择，可修改


# 勾造某个年份的url列表
def concat_url(init_url, name_list, year):
    return [init_url + "/" + name + "-" + str(year) for name in name_list]


# 获取某个url的页面及会议信息
def get_page(url):
    try:
        r = requests.get(url)
        page = r.text
        print(r.status_code)
        return page, str(url).split("events/")[1]
    except Exception as err:
        print(url, ":", err)


# 清理得到的paper的title
def clean(string):
    return " ".join("".join(string.strip("&#39;").strip('&#39;" ').split("\n")).split()).strip().lower()


# 解析得到的页面
def get_parser(page, confer, keywords):
    pattern = re.compile(r'<a href="(http://aclweb\.org/anthology/[\w\W]*?)">[\w\W]*?Open PDF of ([\s\S]*?)width')
    p_list = re.findall(pattern, page)
    result_list = []
    for p in p_list:
        cw = clean(p[1])
        for kw in keywords:
            if cw.find(kw) != -1:
                t = cw.replace(":", "")
                result_list.append((p[0], confer, cw))
                download(p[0], confer, t)
                break
    return result_list


# 下载pdf
def download(url, confer, name):
    base_folder = "downloads/"
    next_folder = base_folder + str(confer)
    folder = os.path.exists(base_folder)
    if not folder:
        os.makedirs("downloads/")
    sub_f = os.path.exists(next_folder)
    if not sub_f:
        os.makedirs(next_folder)
    r = requests.get(url)
    with open(next_folder + "/" + str(name) + ".pdf", "wb") as f:
        f.write(r.content)


# 构造线程类，加快速度
class Threads(threading.Thread):

    def __init__(self, url_list, kws, year):
        threading.Thread.__init__(self)
        self.name = str(year) + "-" + "-".join(kws)
        self.url_list = url_list
        self.keywords = kws

    def run(self):
        results = []
        for link in self.url_list:
            try:
                page, confer = get_page(link)
                temp_result = get_parser(page, confer, self.keywords)
                results += temp_result
                print(confer, "get parsered")
            except Exception as error:
                print(error)
        df = pandas.DataFrame(results, columns=["link", "conference", "title"])
        df.to_csv(self.name + ".csv")


if __name__ == '__main__':
    # 开始时间标记
    s = time.time()

    # 构造url列表，列表元素为列表，表示某个年份的url列表
    url_list_list = []
    for year_item in years:
        url_list_list.append(concat_url(init_urls, names, year_item))

    # 构造线程列表
    thread_list = [Threads(url_list_list[i], keywords_, years[i]) for i in range(len(years))]

    print("------threading list have been created------")

    # 开始线程
    for th in thread_list:
        th.start()
    # 等待所有线程完成
    for index in tqdm.trange(len(thread_list)):
        thread_list[index].join()
        print()
    # 结束时间
    e = time.time()

    print("The cost time is:", e-s)




