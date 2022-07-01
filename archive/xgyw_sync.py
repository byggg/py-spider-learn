#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/10/5 19:25
# @Desc : xgyw.top - 同步版

import os
import time
import traceback

import requests
from lxml import html

BASE_PATH = 'https://www.jpxgyw.vip'
BASE_PIC = 'https://t.jpxgyw.vip'
LOCAL_DIR = 'D:\\Picture\\Lure\\beauty\\'
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh,zh-CN;q=0.9',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
}
session = requests.Session()


def seed_process(keyword, page_limit):
    search_url = f'{BASE_PATH}/plus/search/index.asp?keyword={keyword}'
    try:
        parse_search_page(search_url, BASE_PATH, page_limit, 1)
    except Exception:
        traceback.print_exc()
    print('xgyw Finish!')


def parse_search_page(search_url, referer_url, page_limit, page_no):
    """解析搜索列表页"""
    print('======== 开始下载第 %d 页 ========' % page_no)
    headers['referer'] = referer_url.encode('utf-8').decode('latin1')  # 防止因含有中文而出现UnicodeEncodeError
    resp = session.get(search_url, headers=headers, timeout=10)
    resp.encoding = 'utf-8'  # 防止中文乱码
    ehtml = html.etree.HTML(resp.text)
    # 解析当前页（请求套图列表页）
    node_list = ehtml.xpath("//div[@class='node']/p/a")
    for i in range(1, len(node_list)):
        detail_url = BASE_PATH + node_list[i].xpath("@href")[0]
        parse_pics_page(detail_url, search_url, 1)
    # 判断翻页
    if page_no == 1:
        hrefs = ehtml.xpath("//div[@class='list']/div[@class='pagination']/ul/a/@href")
        len_hrefs = len(hrefs)
        page_count = page_limit if len_hrefs >= page_limit else len_hrefs
        for i in range(1, page_count):
            more_search_url = f'{BASE_PATH}/plus/search/index.asp{hrefs[i]}'
            parse_search_page(more_search_url, search_url, page_limit, i + 1)
            time.sleep(2)


def parse_pics_page(detail_url, referer_url, page_no):
    """解析套图列表页"""
    headers['referer'] = referer_url.encode('utf-8').decode('latin1')  # 防止因含有中文而出现UnicodeEncodeError
    resp = session.get(detail_url, headers=headers, timeout=10)
    resp.encoding = 'utf-8'  # 防止中文乱码
    ehtml = html.etree.HTML(resp.text)
    title_prefix = ehtml.xpath("//h1[@class='article-title']/text()")[0]
    update_date = ehtml.xpath("//div[@class='article-meta']/span/text()")[0]
    title = title_prefix + ' ' + update_date
    # 解析当前页（保存图片）
    imgs = ehtml.xpath("//article[@class='article-content']/p/img/@src")
    for i in range(0, len(imgs)):
        real_path = str(imgs[i]).replace('uploadfile', 'Uploadfile')  # 不替换则无法正常访问图片
        img_url = BASE_PIC + real_path
        save2local(img_url, title, page_no, i)
        time.sleep(3)
    # 判断翻页
    if page_no == 1:
        single_pages = ehtml.xpath("//div[@class='pagination']")[0]  # 存在2个pagination
        pages = single_pages.xpath("ul/a/@href")
        for i in range(1, len(pages) - 1):
            more_detail_url = BASE_PATH + pages[i]
            parse_pics_page(more_detail_url, detail_url, i + 1)
            time.sleep(2)


def save2local(img_url, title, page_no, i):
    file_path = LOCAL_DIR + title
    is_exists = os.path.exists(file_path)
    if not is_exists:  # 若目录不存在则创建
        os.makedirs(file_path)
        print(f"》》》 {file_path} 目录创建成功")
    else:
        print(f">>> 图片URL： {img_url}")
    headers['referer'] = BASE_PATH.encode('utf-8').decode('latin1')  # 防止因含有中文而出现UnicodeEncodeError
    resp = session.get(img_url, headers=headers, timeout=10)
    resp.encoding = 'utf-8'  # 防止中文乱码
    with open(f'{file_path}/{page_no}_{i}.jpg', 'wb') as f:
        f.write(resp.content)


def call_xgyw(**kwargs):
    if kwargs.get('keyword') is not None:
        seed_process(kwargs['keyword'], kwargs['page_limit'])
    else:
        parse_pics_page(kwargs['detail_url'], BASE_PATH, 1)


if __name__ == '__main__':
    pass
    # call_xgyw(keyword='可乐', page_limit=1)
    # call_xgyw(detail_url='https://www.jpxgyw.vip/Xiuren/Xiuren16158.html')
