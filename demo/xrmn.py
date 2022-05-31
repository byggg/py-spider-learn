#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/10/7 11:02
# @Desc : xrmn.top

import os
import time
import traceback

import requests
from lxml import html

ROOT_PATH = 'https://www.xrmn5.cc'
ROOT_PIC = 'https://t.xrmn5.cc'


class XrmnSearch:
    """从搜索结果页开始"""

    def __init__(self):
        self.xrmn_util = XrmnUtil()

    def seed_process(self, keyword, page_limit):
        search_url = f'{ROOT_PATH}/plus/search/index.asp?keyword={keyword}'
        try:
            self.process_search_page(search_url, page_limit, 1)
        except Exception:
            traceback.print_exc()
        print('xrmn-search Finish!')

    # 处理搜索列表页
    def process_search_page(self, search_url, page_limit, page_no):
        print('======== 开始下载第 %d 页 ========' % page_no)
        resp = self.xrmn_util.get_resp(search_url)
        ehtml = html.etree.HTML(resp.text)
        # 解析当前页（请求详情页）
        sousuos = ehtml.xpath("//div[@class='sousuo']")
        for sousuo in sousuos:
            title_prefix = sousuo.xpath("div[@class='title']/h2/a/span/text()")
            title = ''.join(title_prefix).strip()
            detail_url = ROOT_PATH + sousuo.xpath("div[@class='title']/h2/a/@href")[0]
            self.process_pics_page(detail_url, title, 1)
            time.sleep(5)
        # 判断翻页
        if page_no == 1:
            hrefs = ehtml.xpath("//div[@class='page']/a/@href")
            len_hrefs = len(hrefs)
            page_count = page_limit if len_hrefs >= page_limit else len_hrefs
            for i in range(1, page_count):
                more_search_url = f'{ROOT_PATH}/plus/search/index.asp{hrefs[i]}'
                self.process_search_page(more_search_url, page_limit, i + 1)
                time.sleep(5)

    # 处理套图列表页
    def process_pics_page(self, detail_url, title, page_no):
        resp = self.xrmn_util.get_resp(detail_url)
        ehtml = html.etree.HTML(resp.text)
        # 解析当前页（保存图片）
        imgs = ehtml.xpath("//div[@class='content_left']/p/img/@src")
        for i in range(0, len(imgs)):
            real_path = str(imgs[i]).replace('uploadfile', 'UploadFile')  # 不替换则无法正常访问图片
            img_url = ROOT_PIC + real_path
            self.xrmn_util.save2local(img_url, title, page_no, i)
        # 判断翻页
        if page_no == 1:
            pages = ehtml.xpath("//div[@class='page']/a/@href")
            for i in range(1, len(pages) - 1):
                more_detail_url = ROOT_PATH + pages[i]
                self.process_pics_page(more_detail_url, title, i + 1)


class XrmnPics:
    """从套图列表页开始"""

    def __init__(self):
        self.xrmn_util = XrmnUtil()

    def seed_process(self, detail_url):
        try:
            self.process_pics_page(detail_url, 1)
        except Exception:
            traceback.print_exc()
        print('xrmn-pics Finish!')

    # 处理套图列表页
    def process_pics_page(self, detail_url, page_no):
        resp = self.xrmn_util.get_resp(detail_url)
        ehtml = html.etree.HTML(resp.text)
        title_prefix = ehtml.xpath("//div[@class='item_title']/h1/text()")[0]
        update_date = ehtml.xpath("//div[@class='item_info']/div/span[2]/text()")[0]
        title = title_prefix + ' 更新时间：' + update_date
        # 解析当前页（保存图片）
        imgs = ehtml.xpath("//div[@class='content_left']/p/img/@src")
        for i in range(0, len(imgs)):
            real_path = str(imgs[i]).replace('uploadfile', 'UploadFile')  # 不替换则无法正常访问图片
            img_url = ROOT_PIC + real_path
            self.xrmn_util.save2local(img_url, title, page_no, i)
        # 判断翻页
        if page_no == 1:
            pages = ehtml.xpath("//div[@class='page']/a/@href")
            for i in range(1, len(pages) - 1):
                more_detail_url = ROOT_PATH + pages[i]
                self.process_pics_page(more_detail_url, i + 1)
                time.sleep(5)


class XrmnUtil:
    """公共方法类"""

    def __init__(self):
        pass

    def get_resp(self, req_url):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh,zh-CN;q=0.9',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
        }
        session = requests.Session()
        resp = session.get(req_url, headers=headers, timeout=10)
        resp.encoding = 'utf-8'  # 防止中文乱码
        return resp

    def save2local(self, img_url, title, page_no, i):
        file_dir = 'meinv/' + title
        isExists = os.path.exists(file_dir)
        if not isExists:  # 若目录不存在则创建
            os.makedirs(file_dir)
            print(f">>> {file_dir} 目录创建成功")
        else:
            print(f">>> {file_dir} 目录已存在")
        with open(f'{file_dir}/{page_no}_{i}.jpg', 'wb') as f:
            resp = requests.get(img_url)
            f.write(resp.content)


def call_xrmn(**kwargs):
    if kwargs.get('keyword') is not None:
        xrmn_search = XrmnSearch()
        xrmn_search.seed_process(kwargs['keyword'], kwargs['page_limit'])
    else:
        xrmn_pics = XrmnPics()
        xrmn_pics.seed_process(kwargs['detail_url'])


if __name__ == '__main__':
    pass
    # call_xrmn(keyword='林星阑', page_limit=1)
    # call_xrmn(detail_url='https://www.xrmn5.cc/XiuRen/2021/20217151.html')
