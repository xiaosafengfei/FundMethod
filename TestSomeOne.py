import requests, re, math, os, time
from lxml import etree
from bs4 import BeautifulSoup
# from dateutil.relativedelta import relativedelta

f = 1.23456

print('%.4f' % f)
print('%.3f' % f)
print('%.2f' % f)

#
# date = datetime.now().strftime("%Y%m%d")
# print((date - relativedelta(years=1)).strftime('%Y%m%d'))
# print(date)

from datetime import datetime
from dateutil.relativedelta import relativedelta
# date = datetime.now().strftime("%Y-%m-%d")
# date_type = datetime.strptime(date, '%Y-%m-%d')
# date_yearago = (date_type - relativedelta(years=1)).strftime('%Y-%m-%d')



# a = 100
# b = math.ceil((a - 20) / 3)
# print(b)

# for value in range(2):
#     print(value)

# def ping_ip(ip):
#     output = os.popen('ping -n 1 %s'%ip).readlines()
#     for w in output:
#         if w.find('TTL')>=0:
#             print(ip)
# if __name__ == '__main__':
#     for num in range(1,255):
#         ip = '10.0.245.' + str(num)
#         ping_ip(ip)

# import tushare as ts
#
# code='hs300'
# b=ts.get_k_data(code, start='2021-01-01', end='2021-04-16')
#
# print(b)
# print(type(b))
# # for c in b:
# #     print(c)

# url = 'http://quote.eastmoney.com/zs000300.html'
