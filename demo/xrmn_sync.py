#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/10/7 11:02
# @Desc : xrmn.top - 同步版

import os
import time
import traceback

import requests
from lxml import html

ROOT_PATH = 'https://www.xrmn5.cc'
ROOT_PIC = 'https://t.xrmn5.cc'
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh,zh-CN;q=0.9',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
}
session = requests.Session()
file_dir = 'meinv/'


def seed_process(keyword, page_limit):
    search_url = f'{ROOT_PATH}/plus/search/index.asp?keyword={keyword}'
    try:
        parse_search_page(search_url, page_limit, 1)
    except Exception:
        traceback.print_exc()
    print('xrmn-search Finish!')


def parse_search_page(search_url, page_limit, page_no):
    """解析搜索列表页"""
    print('======== 开始下载第 %d 页 ========' % page_no)
    resp = session.get(search_url, headers=headers, timeout=10)
    resp.encoding = 'utf-8'  # 防止中文乱码
    ehtml = html.etree.HTML(resp.text)
    # 解析当前页（请求套图列表页）
    sousuos = ehtml.xpath("//div[@class='sousuo']")
    for sousuo in sousuos:
        detail_url = ROOT_PATH + sousuo.xpath("div[@class='title']/h2/a/@href")[0]
        parse_pics_page(detail_url, 1)
    # 判断翻页
    if page_no == 1:
        hrefs = ehtml.xpath("//div[@class='page']/a/@href")
        len_hrefs = len(hrefs)
        page_count = page_limit if len_hrefs >= page_limit else len_hrefs
        for i in range(1, page_count):
            more_search_url = f'{ROOT_PATH}/plus/search/index.asp{hrefs[i]}'
            parse_search_page(more_search_url, page_limit, i + 1)
            time.sleep(2)


def parse_pics_page(detail_url, page_no):
    """解析套图列表页"""
    resp = session.get(detail_url, headers=headers, timeout=10)
    resp.encoding = 'utf-8'  # 防止中文乱码
    ehtml = html.etree.HTML(resp.text)
    title_prefix = ehtml.xpath("//div[@class='item_title']/h1/text()")[0]
    update_date = ehtml.xpath("//div[@class='item_info']/div/span[2]/text()")[0]
    title = title_prefix + ' 更新时间：' + update_date
    # 解析当前页（保存图片）
    imgs = ehtml.xpath("//div[@class='content_left']/p/img/@src")
    for i in range(0, len(imgs)):
        real_path = str(imgs[i]).replace('uploadfile', 'UploadFile')  # 不替换则无法正常访问图片
        img_url = ROOT_PIC + real_path
        save2local(img_url, title, page_no, i)
        time.sleep(3)
    # 判断翻页
    if page_no == 1:
        pages = ehtml.xpath("//div[@class='page']/a/@href")
        for i in range(1, len(pages) - 1):
            more_detail_url = ROOT_PATH + pages[i]
            parse_pics_page(more_detail_url, i + 1)
            time.sleep(2)


def save2local(img_url, title, page_no, i):
    file_path = file_dir + title
    isExists = os.path.exists(file_path)
    if not isExists:  # 若目录不存在则创建
        os.makedirs(file_path)
        print(f"》》》 {file_path} 目录创建成功")
    else:
        print(f">>> 图片URL： {img_url}")
    resp = requests.get(img_url)
    with open(f'{file_path}/{page_no}_{i}.jpg', 'wb') as f:
        f.write(resp.content)


def call_xrmn(**kwargs):
    if kwargs.get('keyword') is not None:
        seed_process(kwargs['keyword'], kwargs['page_limit'])
    else:
        parse_pics_page(kwargs['detail_url'], 1)


if __name__ == '__main__':
    pass
    # call_xrmn(keyword='林星阑', page_limit=1)
    # call_xrmn(detail_url='https://www.xrmn5.cc/XiuRen/2021/20217151.html')
