#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/10/7 11:02
# @Desc : xrmn.top (以搜索页为入口)

import os
import time
import traceback

import requests
from lxml import html


def process_search_page(search_url, page_limit, page_no):
    print('======== 开始下载第 %d 页 ========' % page_no)
    resp = get_resp(search_url)
    ehtml = html.etree.HTML(resp.text)
    # 解析当前页（请求详情页）
    sousuos = ehtml.xpath("//div[@class='sousuo']")
    for sousuo in sousuos:
        title_prefix = sousuo.xpath("div[@class='title']/h2/a/span/text()")
        title = ''.join(title_prefix).strip()
        detail_url = 'https://www.xrmn5.com' + sousuo.xpath("div[@class='title']/h2/a/@href")[0]
        process_detail_page(detail_url, title, 1)
        time.sleep(3)
    # 判断翻页
    if page_no == 1:
        hrefs = ehtml.xpath("//div[@class='page']/a/@href")
        len_hrefs = len(hrefs)
        page_count = page_limit if len_hrefs >= page_limit else len_hrefs
        for i in range(1, page_count):
            more_search_url = 'https://www.xrmn5.com/plus/search/index.asp' + hrefs[i]
            process_search_page(more_search_url, page_limit, i + 1)
            time.sleep(5)


def process_detail_page(detail_url, title, page_no):
    resp = get_resp(detail_url)
    ehtml = html.etree.HTML(resp.text)
    # 解析当前页（保存图片）
    imgs = ehtml.xpath("//div[@class='content_left']/p/img/@src")
    for i in range(0, len(imgs)):
        img_url = 'https://pic.xrmn5.com' + imgs[i]
        save2local(img_url, title, page_no, i)
    # 判断翻页
    if page_no == 1:
        pages = ehtml.xpath("//div[@class='page']/a/@href")
        for i in range(1, len(pages) - 1):
            more_detail_url = 'https://www.xrmn5.com' + pages[i]
            process_detail_page(more_detail_url, title, i + 1)


def get_resp(req_url):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh,zh-CN;q=0.9',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    }
    session = requests.Session()
    resp = session.get(req_url, headers=headers, timeout=10)
    return resp


def save2local(img_url, title, page_no, i):
    file_dir = 'xrmn/' + title
    isExists = os.path.exists(file_dir)
    if not isExists:  # 若目录不存在则创建
        os.makedirs(file_dir)
        print(">>> %s 目录创建成功!" % file_dir)
    else:
        print(">>> %s 目录已经存在!" % file_dir)
    with open(file_dir + '/%d_%d.jpg' % (page_no, i), 'wb') as f:
        resp = requests.get(img_url)
        f.write(resp.content)


def main(keyword, page_limit):
    search_url = 'https://www.xrmn5.com/plus/search/index.asp?keyword=' + keyword
    try:
        process_search_page(search_url, page_limit, 1)
    except Exception:
        traceback.print_exc()
    print('crawl finished!')


if __name__ == '__main__':
    main('安然', 1)
