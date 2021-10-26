#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/8/20 16:30
# @Desc : 测试方法

import datetime
import json
import re
import time

from bs4 import BeautifulSoup
from lxml import html
from pyquery import PyQuery


# i = 3
# print("第 %d 次：" % i + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
# print(str(datetime.date.today() - datetime.timedelta(days=1)))

# print(int(time.time()))
#
# li = ['zh', 'li', 'sa', 'he', 'su', 'na']
# for i in range(len(li) - 1, -1, -1):
#     print(li[i])

def parse2json_lxml(content_source, rank_type):
    item_infos = []
    ehtml = html.etree.HTML(content_source)
    trs = ehtml.xpath("//tbody[@id='js-product-container']/tr")
    for tr in trs:
        rank_info = tr.xpath("//td/span[@class='rank rank1']/text()")
        if len(rank_info) == 2:
            rank = rank_info.split(' ')[0]
            trend_info = tr.xpath("//td/span[@class='rank rank1']/em/@class")
            if trend_info.endswith('up'):
                rank_trend = "上升 " + rank_info[1]
            elif trend_info.endswith('down'):
                rank_trend = "下降 " + rank_info[1]
            elif trend_info.endswith('new'):
                rank_trend = "新上榜 " + rank_info[1]
        media = tr.xpath("//td/div[@class='item-media']/a/img/@src")
        source_url = tr.xpath("//td/div[@class='item-title']/a/@href")
        title = tr.xpath("//td/div[@class='item-title']/a/span/text()")
        price_info = tr.xpath("//td/div[@class='item-title']/div[@class='price']/text()")
        infos = price_info.split(" ")
        if len(infos) == 2:
            price = infos[0] + infos[1]
        elif len(infos) == 3:
            price = infos[0] + infos[1]
            rank_tag = infos[2]
        cate_tag = tr.xpath("//td/span[@class='icon-industry']/text()")
        live_count = tr.xpath("//td")[3].text()
        if rank_type == '销售额最多':
            predictive_sales_volume = tr.xpath("//td")[4].text()
            predictive_sales = tr.xpath("td[@class='yellow']")[0].text()
        elif rank_type == '销量最多':
            predictive_sales_volume = tr.xpath("td[@class='yellow']")[0].text()
            predictive_sales = tr.xpath("//td")[5].text()
        detail_url = 'https://ks.feigua.cn/Member' + tr.xpath("td[@class='text-center']/a/@href")
        item_info = {'rank': rank, 'rank_trend': rank_trend, 'media': media, 'source_url': source_url, 'title': title, 'price': price, 'rank_tag': rank_tag, 'cate_tag': cate_tag,
                     'live_count': live_count, 'predictive_sales_volume': predictive_sales_volume, 'predictive_sales': predictive_sales, 'detail_url': detail_url}
        item_infos.append(item_info)
    return item_infos


def parse2json_pq(content_source, rank_type):
    item_infos = []
    doc = PyQuery(content_source)
    trs = doc('tbody#js-product-container tr')
    for tr in trs:
        rank_info = tr.find('td span.rank.rank1').text()
        if len(rank_info) == 2:
            rank = rank_info.split(' ')[0]
            trend_info = tr.find("td span.rank.rank1 em").attr('class')
            if trend_info.endswith('up'):
                rank_trend = "上升 " + rank_info[1]
            elif trend_info.endswith('down'):
                rank_trend = "下降 " + rank_info[1]
            elif trend_info.endswith('new'):
                rank_trend = "新上榜 " + rank_info[1]
        media = tr.find('td div.item-media a img').attr('src')
        source_url = tr.find('td div.item-title a').attr('href')
        title = tr.find('td div.item-title a span').text()
        price_info = tr.find('td div.item-title div.price').text()
        infos = price_info.split(" ")
        if len(infos) == 2:
            price = infos[0] + infos[1]
        elif len(infos) == 3:
            price = infos[0] + infos[1]
            rank_tag = infos[2]
        cate_tag = tr.find('td span.icon-industry').text()
        live_count = tr.find('td')[3].text()
        if rank_type == '销售额最多':
            predictive_sales_volume = tr.find('td')[4].text()
            predictive_sales = tr.find('td.yellow')[0].text()
        elif rank_type == '销量最多':
            predictive_sales_volume = tr.find('td.yellow')[0].text()
            predictive_sales = tr.find('td')[5].text()
        detail_url = 'https://ks.feigua.cn/Member' + tr.find('td.text-center a').attr('href')
        item_info = {'rank': rank, 'rank_trend': rank_trend, 'media': media, 'source_url': source_url, 'title': title, 'price': price, 'rank_tag': rank_tag, 'cate_tag': cate_tag,
                     'live_count': live_count, 'predictive_sales_volume': predictive_sales_volume, 'predictive_sales': predictive_sales, 'detail_url': detail_url}
        item_infos.append(item_info)
    return item_infos


def parse2json_bs4(content_source, rank_type):
    item_infos = []
    soup = BeautifulSoup(content_source, 'lxml')
    trs = soup.select('tbody#js-product-container tr')
    for tr in trs:
        rank_info = tr.select_one('td span.rank.rank1').get_text().strip().replace(' ', '').split('\n')
        rank = ''
        rank_trend = ''
        if len(rank_info) == 2:
            rank = int(rank_info[0])
            trend_infos = tr.select_one("td span.rank.rank1 em").attrs['class']
            trend_info = ''.join(trend_infos)
            if trend_info.endswith('up'):
                rank_trend = "上升 " + rank_info[1]
            elif trend_info.endswith('down'):
                rank_trend = "下降 " + rank_info[1]
            elif trend_info.endswith('new'):
                rank_trend = "新上榜 " + rank_info[1]
        media = tr.select_one('td div.item-media a img').attrs['src']
        source_url = tr.select_one('td div.item-title a').attrs['href']
        title = tr.select_one('td div.item-title a span').get_text()
        infos = tr.select_one('td div.item-title div.price').get_text().strip().replace(' ', '').split('\n')
        price = ''
        rank_tag = ''
        if len(infos) == 1:
            price = infos[0]
        else:
            price = infos[0]
            rank_tag = infos[len(infos) - 1]
        cate_tag = tr.select_one('td span.icon-industry').get_text()
        live_count = tr.select('td')[3].get_text()
        predictive_sales_volume = ''
        predictive_sales = ''
        if rank_type == '销售额最多':
            predictive_sales_volume = tr.select('td')[4].get_text()
            predictive_sales = tr.select('td.yellow')[0].get_text()
        elif rank_type == '销量最多':
            predictive_sales_volume = tr.select('td.yellow')[0].get_text()
            predictive_sales = tr.select('td')[5].get_text()
        detail_url = 'https://ks.feigua.cn/Member' + tr.select_one('td.text-center a').attrs['href']
        item_info = {'rank': rank, 'rank_trend': rank_trend, 'media': media, 'source_url': source_url, 'title': title, 'price': price, 'rank_tag': rank_tag, 'cate_tag': cate_tag,
                     'live_count': live_count, 'predictive_sales_volume': predictive_sales_volume, 'predictive_sales': predictive_sales, 'detail_url': detail_url}
        print(item_info)
        item_infos.append(item_info)
    return item_infos


def parse_txt2json():
    li = []
    with open('page_source.txt', 'r') as f:
        for line in f:
            li.append(line)
    result = ''.join(li)
    print('Read success!')
    regex = '.*?'
    trs = re.findall(regex, result, re.S)
    for tr in trs:
        if 'rank rank1' in tr:
            print(tr)


def gen_ids():
    li = []
    file_path = r'C:\Users\by\Desktop\author_id.txt'
    with open(file_path) as f:
        for line in f:
            li.append(line)
    result = '","'.join(li).replace('\n', '')
    print(result)


if __name__ == '__main__':
    # content_source = """"""
    # parse2json_bs4(content_source, '销售额最多')
    gen_ids()
