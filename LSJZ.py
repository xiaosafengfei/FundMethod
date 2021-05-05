import requests
import re
import json
import math

import pymysql

from FundMethod.model import FundsInfo, GetPageValue, PageCount, GetTotalVaule, CreateHisTable

def WriteHisData(fundCode):
    total_value_list = GetTotalVaule(fundCode)
    CreateHisTable(fundCode)
    # 将列表内容写入数据库
    db = pymysql.connect(host='localhost',port=3216, user='root', passwd="Yibao@147", db="FundMethod",charset='utf8')
    cursor = db.cursor()
    try:
        # 执行SQL语句，插入多条数据,插入前先清空表
        valueTable='fund_his_' + fundCode
        cursor.execute("delete from {valueTable}".format(valueTable=valueTable))
        cursor.executemany("insert into {valueTable} (FCODE, FSRQ, DWJZ, LJJZ, JZZZL, SGZT, SHZT) values(%s,%s,%s,%s,%s,%s,%s)".format(valueTable=valueTable), total_value_list)
        # 提交数据
        db.commit()
    except:
        # 发生错误时回滚
        db.rollback()
    # 关闭数据库连接
    db.close()

if __name__ == '__main__':
    funds_info = FundsInfo()
    for fund_info in funds_info:
        fundCode = fund_info['fundCode']
        fundName = fund_info['fundName']
        WriteHisData(fundCode)
        print(fundName + '历史净值数据写入mysql完成')