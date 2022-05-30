#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/10/9 19:54
# @Desc : 古诗文网（https://www.gushiwen.cn）

import time

import pymongo
import requests
from pyquery import PyQuery


class GswwRecommend:
    """推荐页"""

    def __init__(self):
        self.gsww_util = GswwUtil()

    def seed_process(self, recommend_url):
        resp = self.get_resp(recommend_url)
        self.parse_resp_html(resp, self.gsww_util)

    def get_resp(self, req_url):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            # 'accept-encoding': 'gzip, deflate, br', # 导致响应乱码
            'accept-language': 'zh,zh-CN;q=0.9',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
        }
        session = requests.Session()
        # session.keep_alive = False
        # session.adapters.DEFAULT_RETRIES = 5
        resp = session.get(req_url, headers=headers, timeout=10)
        resp.encoding = 'utf-8'
        return resp

    def parse_resp_html(self, resp, gsww_util):
        doc = PyQuery(resp.text)
        current_page = doc('label#temppage').text()
        print('==== 第 %s 页 ====' % current_page)
        # 解析当前页
        sons_list = doc('div.main3 div.left div.sons').items()
        # print(len(sons_list))
        for sons in sons_list:
            # gsw = {}
            if sons('div.contImg'):
                cont_img = sons.find('div.contImg')
                img = cont_img.find('div.info').text()
                img_url = cont_img.find('img').attr('src')
                shiju = cont_img.find('div.jucount a').text()
                shiju_url = cont_img.find('div.jucount a').attr('href')
                source = cont_img.find('div.sourceimg a').text()
                source_url = cont_img.find('div.sourceimg a').attr('href')
                gsw = {'img': img, 'img_url': img_url, 'shiju': shiju, 'shiju_url': shiju_url, 'source': source,
                       'source_url': source_url}
            elif sons('div.cont div.yizhu'):
                cont = sons.find('div.cont')
                poem_title = cont.find('p a b').text()
                poem_url = cont.find('p a:nth-child(1)').attr('href')
                author = cont.find('p.source a:nth-child(1)').text()
                author_url = cont.find('p.source a:nth-child(1)').attr('href')
                dynasty = cont.find('p.source a:nth-child(2)').text()
                dynasty_url = cont.find("p.source a:nth-child(2)").attr('href')
                contson = cont.find('div.contson').text()
                gsw = {'poem_title': poem_title, 'poem_url': poem_url, 'author': author, 'author_url': author_url,
                       'dynasty': dynasty, 'dynasty_url': dynasty_url, 'contson': contson}
            elif sons('div.cont div.changshi'):
                cont = sons.find('div.cont')
                is_common = cont.find('div.changshi').text()
                list_td = []
                tds = cont.find('td').items()  # 采用层级标签反而无法获得可遍历的generator
                for td in tds:
                    list_td.append(td.text().strip())
                changshi_title = ''.join(list_td)
                changshi_cont = cont.find('div.changshicont').text()
                gsw = {'is_common': is_common, 'changshi_title': changshi_title, 'changshi_cont': changshi_cont}
            else:
                li_mingju = []
                conts = sons.find('div.cont').items()
                for cont in conts:
                    # a:nth-child(n) 选择属于其父元素的第n个子元素的每个元素
                    mingju = cont.find('a:nth-child(1)').text()
                    mingju_url = cont.find('a:nth-child(1)').attr('href')
                    source = cont.find('a:nth-child(3)').text()
                    source_url = cont.find('a:nth-child(3)').attr('href')
                    single_gsw = {'mingju': mingju, 'mingju_url': mingju_url, 'source': source,
                                  'source_url': source_url}
                    li_mingju.append(single_gsw)
                gsw = {'mingju_list': li_mingju}
            print(gsw)
            # gsww_util.save2mongo('test', 'gsw_recommend', gsw)
        # 判断翻页
        next_page = doc('a#amore').attr('href')
        if next_page:
            time.sleep(3)
            more_resp = self.get_resp(next_page)
            self.parse_resp_html(more_resp, gsww_util)


class GswwUtil:
    def __init__(self):
        pass

    def save2mongo(self, db_name, collection_name, item):
        client = pymongo.MongoClient(host='localhost', port=27017)
        db = client[db_name]
        collection = db[collection_name]
        result = collection.insert_one(item)
        # print(result.inserted_id)
        print(result)


if __name__ == '__main__':
    gsww_recommend = GswwRecommend()
    gsww_recommend.seed_process('https://www.gushiwen.cn')
