#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/10/5 19:25
# @Desc : xgyw.top (以详情页为入口)

import os
import time
import traceback

import requests
from lxml import html


# 处理套图列表页
def process_detail_page(detail_url, referer_url, page_no):
    resp = get_resp(detail_url, referer_url)
    ehtml = html.etree.HTML(resp.text)
    title_prefix = ehtml.xpath("//h1[@class='article-title']/text()")[0]
    update_date = ehtml.xpath("//div[@class='article-meta']/span/text()")[0]
    title = title_prefix + ' ' + update_date
    # 解析当前页（保存图片）
    imgs = ehtml.xpath("//article[@class='article-content']/p/img/@src")
    for i in range(0, len(imgs)):
        real_path = str(imgs[i]).replace('uploadfile', 'Uploadfile')  # 不替换则无法正常访问图片
        img_url = 'https://p.jpxgmn.top' + real_path
        save2local(img_url, title, page_no, i)
    # 判断翻页
    if page_no == 1:
        single_pages = ehtml.xpath("//div[@class='pagination']")[0]  # 存在2个pagination
        pages = single_pages.xpath("ul/a/@href")
        for i in range(1, len(pages) - 1):
            more_detail_url = 'https://www.jpxgmn.top' + pages[i]
            process_detail_page(more_detail_url, detail_url, i + 1)
            time.sleep(3)


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


def save2local(img_url, title, page_no, i):
    file_dir = 'xgyw/' + title
    isExists = os.path.exists(file_dir)
    if not isExists:  # 若目录不存在则创建
        os.makedirs(file_dir)
        print(">>> %s 目录创建成功!" % file_dir)
    else:
        print(">>> %s 目录已经存在!" % file_dir)
    with open(file_dir + '/%d_%d.jpg' % (page_no, i), 'wb') as f:
        resp = get_resp(img_url, 'https://www.jpxgmn.top/')
        f.write(resp.content)


if __name__ == '__main__':
    detail_url = 'https://www.jpxgmn.top/IMiss/IMiss18199.html'
    referer_url = 'https://www.jpxgmn.top/'
    try:
        process_detail_page(detail_url, referer_url, 1)
    except Exception:
        traceback.print_exc()
    print('crawl finished!')
