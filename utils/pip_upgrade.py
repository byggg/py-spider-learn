#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/8/20 23:12
# @Desc : 必须在所指定环境下执行

import os

result = os.popen('pip list -o')  # 执行系统命令，返回值为result
res = result.read()
data = res.split()
demo = []
for i in range(len(data)):
    demo.append(data[i])
for package in demo:
    os.system('pip install -U ' + package)
print("all update")
