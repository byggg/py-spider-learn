#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/10/5 19:25
# @Desc : xgyw.top - 同步版

import os
import random
import time
import traceback

import requests
from lxml import html

ROOT_PATH = 'https://www.jpxgyw.vip'
ROOT_PIC = 'https://p.jpxgyw.vip'


def seed_process(keyword, page_limit):
    search_url = f'{ROOT_PATH}/plus/search/index.asp?keyword={keyword}'
    try:
        parse_search_page(search_url, ROOT_PATH, page_limit, 1)
    except Exception:
        traceback.print_exc()
    print('xgyw Finish!')


def parse_search_page(search_url, referer_url, page_limit, page_no):
    """解析搜索列表页"""
    print('======== 开始下载第 %d 页 ========' % page_no)
    resp = get_resp(search_url, referer_url)
    ehtml = html.etree.HTML(resp.text)
    # 解析当前页（请求详情页）
    node_list = ehtml.xpath("//div[@class='node']/p/a")
    for i in range(1, len(node_list)):
        detail_url = ROOT_PATH + node_list[i].xpath("@href")[0]
        parse_pics_page(detail_url, search_url, 1)
        time.sleep(random.randint(2, 4))
    # 判断翻页
    if page_no == 1:
        hrefs = ehtml.xpath("//div[@class='list']/div[@class='pagination']/ul/a/@href")
        len_hrefs = len(hrefs)
        page_count = page_limit if len_hrefs >= page_limit else len_hrefs
        for i in range(1, page_count):
            more_search_url = f'{ROOT_PATH}/plus/search/index.asp{hrefs[i]}'
            parse_search_page(more_search_url, search_url, page_limit, i + 1)
            time.sleep(random.randint(4, 6))


def get_resp(req_url, referer_url):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh,zh-CN;q=0.9',
        'referer': referer_url.encode('utf-8').decode('latin1'),  # 防止因含有中文而出现UnicodeEncodeError
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    }
    session = requests.Session()
    resp = session.get(req_url, headers=headers, timeout=10)
    resp.encoding = 'utf-8'  # 防止中文乱码
    return resp


def parse_pics_page(detail_url, referer_url, page_no):
    """解析套图列表页"""
    resp = get_resp(detail_url, referer_url)
    ehtml = html.etree.HTML(resp.text)
    title_prefix = ehtml.xpath("//h1[@class='article-title']/text()")[0]
    update_date = ehtml.xpath("//div[@class='article-meta']/span/text()")[0]
    title = title_prefix + ' ' + update_date
    # 解析当前页（保存图片）
    imgs = ehtml.xpath("//article[@class='article-content']/p/img/@src")
    for i in range(0, len(imgs)):
        real_path = str(imgs[i]).replace('uploadfile', 'Uploadfile')  # 不替换则无法正常访问图片
        img_url = ROOT_PIC + real_path
        save2local(img_url, title, page_no, i)
    # 判断翻页
    if page_no == 1:
        single_pages = ehtml.xpath("//div[@class='pagination']")[0]  # 存在2个pagination
        pages = single_pages.xpath("ul/a/@href")
        for i in range(1, len(pages) - 1):
            more_detail_url = ROOT_PATH + pages[i]
            parse_pics_page(more_detail_url, detail_url, i + 1)
            time.sleep(random.randint(2, 4))


def save2local(img_url, title, page_no, i):
    file_dir = 'meinv/' + title
    is_exists = os.path.exists(file_dir)
    if not is_exists:  # 若目录不存在则创建
        os.makedirs(file_dir)
        print(f">>> {file_dir} 目录创建成功")
    else:
        print(f">>> {file_dir} 目录已存在")
    with open(f'{file_dir}/{page_no}_{i}.jpg', 'wb') as f:
        resp = get_resp(img_url, ROOT_PATH)
        f.write(resp.content)


def call_xgyw(**kwargs):
    if kwargs.get('keyword') is not None:
        seed_process(kwargs['keyword'], kwargs['page_limit'])
    else:
        parse_pics_page(kwargs['detail_url'], ROOT_PATH, 1)


if __name__ == '__main__':
    pass
    # call_xgyw(keyword='可乐', page_limit=1)
    # call_xgyw(detail_url='https://www.jpxgyw.vip/Xiuren/Xiuren16158.html')