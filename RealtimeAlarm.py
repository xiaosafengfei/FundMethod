import json, re, datetime
import requests
import pymysql

from FundMethod.model import FundsInfo, Values, CreateBandTable, QueryUnderTop, Hs300CompareMax

def RealtimeEstimateValue(fundCode):
    #   通过基金编码获取估值
    url = 'http://fundgz.1234567.com.cn/js/%s.js' % fundCode
    result = requests.get(url)  # 发送请求
    data = json.loads(re.match(".*?({.*}).*", result.text, re.S).group(1))   # 正则表达式，重点学习
    # print(data)
    return data
# RealtimeEstimateValue('001838')

def RealtimeData(fundCode):
    realtime_value = RealtimeEstimateValue(fundCode)['gsz']
    realtime_value = float(realtime_value)   # 格式化为浮点类型，便于下面运算
    year_top_value = max(Values(fundCode))
    under_top = (year_top_value - realtime_value) / year_top_value  # 以最高值为基准，实时估值比净值低于最高值多少
    update_time = RealtimeEstimateValue(fundCode)['gztime']
    create_time = datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")
    realtime_tuple = (fundCode, realtime_value, year_top_value, under_top, update_time,create_time)
    return realtime_tuple

# 创建波段实时表，把实时数据元组写入数据表
def WriteRealtimeData(fundCode):
    realtime_data = RealtimeData(fundCode)
    CreateBandTable()
    # 将列表内容写入数据库
    db = pymysql.connect(host='localhost',port=3216, user='root', passwd="Yibao@147", db="FundMethod",charset='utf8')
    cursor = db.cursor()
    try:
        # 执行SQL语句，插入多条数据,插入前先清空表
        table_name = 'band_realtime'
        cursor.execute("insert into {table_name} (fundcode, realtime_value, year_top_value, under_top, update_time, create_time) values(%s,%s,%s,%s,%s,%s)".format(table_name=table_name), realtime_data)
        # 提交数据
        db.commit()
    except:
        # 发生错误时回滚
        db.rollback()
    # 关闭数据库连接
    db.close()

def CompareMax(fundCode,fundName,First,Second,Third):
    under_top = QueryUnderTop(fundCode)
    alarm_time = datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")
    if First <= under_top < Second:
        print(alarm_time + '  ' + fundName + ': 低于top {under_top}应建仓2成,总仓位2成.'.format(under_top=under_top))
    elif Second <= under_top < Third:
        print(alarm_time + '  ' + fundName + ': 低于top {under_top}应继续加仓3成,总仓位5成.'.format(under_top=under_top))
    elif under_top >= Third:
        print(alarm_time + '  ' + fundName + ': 低于top {under_top}应继续加仓5成,总仓位满仓.'.format(under_top=under_top))
    else:
        print(alarm_time + '  ' + fundName + ': 低于top {under_top},少于第一次{First}不需要加仓'.format(under_top=under_top,First=First))

if __name__ == '__main__':
    funds_info = FundsInfo()
    for fund_info in funds_info:
        fundCode = fund_info['fundCode']
        fundName = fund_info['fundName']
        First = fund_info['First']
        Second = fund_info['Second']
        Third = fund_info['Third']
        WriteRealtimeData(fundCode)
        CompareMax(fundCode, fundName, First, Second, Third)

    # 沪深300指数年top比较
    Hs300CompareMax()
