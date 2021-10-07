#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/9/5 12:06
# @Desc :

# a = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
# b = []
# for i in a:
#     b.append(i + 1)
# print(a)
# print(b)

# a = [i + 1 for i in range(10)]
# print(a)

# sum = lambda x, y: x + y
# print(sum(2, 7))

a = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
add = map(lambda x: x + 1, a)
print(list(add))
