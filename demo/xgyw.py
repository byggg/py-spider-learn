#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/10/5 19:25
# @Desc : xgyw.top

import os
import time
import traceback

import requests
from lxml import html


class XgywSearch(object):
    """从搜索结果页开始"""

    def __init__(self):
        pass

    def seed_process(self, keyword, page_limit):
        search_url = 'https://www.jpxgmn.net/plus/search/index.asp?keyword=' + keyword
        search_referer = 'https://www.jpxgmn.net/'
        try:
            self.process_search_page(search_url, search_referer, page_limit, 1)
        except Exception:
            traceback.print_exc()
        print('xgyw search finished!')

    # 处理搜索列表页
    def process_search_page(self, search_url, referer_url, page_limit, page_no):
        print('======== 开始下载第 %d 页 ========' % page_no)
        resp = self.get_resp(search_url, referer_url)
        ehtml = html.etree.HTML(resp.text)
        # 解析当前页（请求详情页）
        node_list = ehtml.xpath("//div[@class='node']/div[@class='title']/h2/a")
        for i in range(8, len(node_list)):
            title_prefix = node_list[i].xpath("b/text()")
            update_date = ehtml.xpath("//div[@class='node']/div[@class='info']/span/text()")[i]
            title = '_'.join(title_prefix).strip() + ' 更新时间：' + update_date
            detail_url = 'https://www.jpxgmn.net' + node_list[i].xpath("@href")[0]
            self.process_pics_page(detail_url, search_url, title, 1)
            time.sleep(3)
        # 判断翻页
        if page_no == 1:
            hrefs = ehtml.xpath("//div[@class='list']/div[@class='pagination']/ul/a/@href")
            len_hrefs = len(hrefs)
            page_count = page_limit if len_hrefs >= page_limit else len_hrefs
            for i in range(1, page_count):
                more_search_url = 'https://www.jpxgmn.net/plus/search/index.asp' + hrefs[i]
                self.process_search_page(more_search_url, search_url, page_limit, i + 1)
                time.sleep(5)

    # 处理套图列表页
    def process_pics_page(self, detail_url, referer_url, title, page_no):
        resp = self.get_resp(detail_url, referer_url)
        ehtml = html.etree.HTML(resp.text)
        # 解析当前页（保存图片）
        imgs = ehtml.xpath("//article[@class='article-content']/p/img/@src")
        for i in range(0, len(imgs)):
            real_path = str(imgs[i]).replace('uploadfile', 'Uploadfile')  # 不替换则无法正常访问图片
            img_url = 'https://p.jpxgmn.net' + real_path
            self.save2local(img_url, title, page_no, i)
        # 判断翻页
        if page_no == 1:
            single_pages = ehtml.xpath("//div[@class='pagination']")[0]  # 存在2个pagination
            pages = single_pages.xpath("ul/a/@href")
            for i in range(1, len(pages) - 1):
                more_detail_url = 'https://www.jpxgmn.net' + pages[i]
                self.process_pics_page(more_detail_url, detail_url, title, i + 1)

    def get_resp(self, req_url, referer_url):
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
        return resp

    def save2local(self, img_url, title, page_no, i):
        file_dir = 'xgyw/' + title
        isExists = os.path.exists(file_dir)
        if not isExists:  # 若目录不存在则创建
            os.makedirs(file_dir)
            print(">>> %s 目录创建成功!" % file_dir)
        else:
            print(">>> %s 目录已经存在!" % file_dir)
        with open(file_dir + '/%d_%d.jpg' % (page_no, i), 'wb') as f:
            resp = self.get_resp(img_url, 'https://www.jpxgmn.net/')
            f.write(resp.content)


class XgywPics(object):
    """从套图列表页开始"""

    def __init__(self):
        pass

    def seed_process(self, detail_url):
        referer_url = 'https://www.jpxgmn.net/'
        try:
            self.process_pics_page(detail_url, referer_url, 1)
        except Exception:
            traceback.print_exc()
        print('xgyw pics finished!')

    # 处理套图列表页
    def process_pics_page(self, detail_url, referer_url, page_no):
        resp = self.get_resp(detail_url, referer_url)
        ehtml = html.etree.HTML(resp.text)
        title_prefix = ehtml.xpath("//h1[@class='article-title']/text()")[0]
        update_date = ehtml.xpath("//div[@class='article-meta']/span/text()")[0]
        title = title_prefix + ' ' + update_date
        # 解析当前页（保存图片）
        imgs = ehtml.xpath("//article[@class='article-content']/p/img/@src")
        for i in range(0, len(imgs)):
            real_path = str(imgs[i]).replace('uploadfile', 'Uploadfile')  # 不替换则无法正常访问图片
            img_url = 'https://p.jpxgmn.net' + real_path
            self.save2local(img_url, title, page_no, i)
        # 判断翻页
        if page_no == 1:
            single_pages = ehtml.xpath("//div[@class='pagination']")[0]  # 存在2个pagination
            pages = single_pages.xpath("ul/a/@href")
            for i in range(1, len(pages) - 1):
                more_detail_url = 'https://www.jpxgmn.net' + pages[i]
                self.process_pics_page(more_detail_url, detail_url, i + 1)
                time.sleep(3)

    def get_resp(self, req_url, referer_url):
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

    def save2local(self, img_url, title, page_no, i):
        file_dir = 'xgyw/' + title
        isExists = os.path.exists(file_dir)
        if not isExists:  # 若目录不存在则创建
            os.makedirs(file_dir)
            print(">>> %s 目录创建成功!" % file_dir)
        else:
            print(">>> %s 目录已经存在!" % file_dir)
        with open(file_dir + '/%d_%d.jpg' % (page_no, i), 'wb') as f:
            resp = self.get_resp(img_url, 'https://www.jpxgmn.net/')
            f.write(resp.content)


if __name__ == '__main__':
    # xgywSearch = XgywSearch()
    # xgywSearch.seed_process('过期米线线喵', 1)
    xgywPics = XgywPics()
    xgywPics.seed_process('https://www.jpxgmn.net/IMiss/IMiss19680.html')
