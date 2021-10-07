#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/10/5 19:25
# @Desc : 精品美女吧（jpmnb.com）

import requests
from lxml import html


def main_schedule(keyword, page_limit):
    init_path = 'https://www.jpxgmn.top/plus/search/index.asp?keyword=%s'
    init_url = init_path % keyword
    init_referer = 'https://www.jpxgmn.top/'
    resp = get_resp_text(init_url, init_referer)

    # 判断翻页
    more_path = 'https://www.jpxgmn.top/plus/search/index.asp?keyword=%s&searchtype=title&p=%d'
    paginations = ehtml.xpath("//div[@class='pagination']/ul/a")
    # paginations = ehtml.xpath("//div[@class='pagination']/ul/a/@href")
    for p in paginations:
        if type(p) is int and int(p) <= page_limit:
            more_url = more_path % (keyword, p)
            resp = get_resp_text(more_url, init_referer)


def get_resp_text(req_url, referer_url):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh,zh-CN;q=0.9',
        'referer': referer_url,
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    }
    session = requests.Session()
    resp = session.get(req_url, headers=headers)
    return resp.text


# 处理搜索列表页
def process_index_page(resp, source_url):
    ehtml = html.etree.HTML(resp.text)
    node_list = ehtml.xpath("//div[@class='node']/div[@class='title']/h2/a")
    # print(node_list)
    for node in node_list:
        # print(node)
        title = node.xpath("b/text()")
        node_url = node.xpath("@href")
        if title and node_url:
            full_title = '_'.join(title)
            node_url = 'https://www.jpxgmn.top/' + node_url[0]
            print(full_title + '\t' + node_url, sep='\n')
            resp = get_resp_text(node_url, source_url)
        else:
            print('pics_list_error: ' + source_url)


# 处理套图列表页
def process_detail_page():
    pass


if __name__ == '__main__':
    main_schedule('唐安琪', 5)
