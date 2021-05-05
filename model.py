from datetime import datetime
from dateutil.relativedelta import relativedelta
import re, json, math
import requests
import pymysql
from bs4 import BeautifulSoup

def FundsInfo():
    dict_jungong = {'fundCode':'010364', 'fundName':'鹏华空天军工指数(LOF)C', 'First':0.20, 'Second':0.26, 'Third':0.30}
    dict_bandaoti = {'fundCode':'320007', 'fundName':'诺安成长混合', 'First':0.20, 'Second':0.26, 'Third':0.30}
    dict_xinnengyuan = {'fundCode': '003834', 'fundName': '华夏能源革新股票', 'First': 0.18, 'Second': 0.22, 'Third': 0.25}
    dict_huangjin = {'fundCode': '002207', 'fundName': '前海开源金银珠宝混合C', 'First': 0.18, 'Second': 0.22, 'Third': 0.25}
    dict_yiliao = {'fundCode': '009163', 'fundName': '广发医疗保健股票C', 'First': 0.18, 'Second': 0.22, 'Third': 0.25}
    dict_spyl = {'fundCode': '660012', 'fundName': '农银汇理消费主题混合A', 'First': 0.15, 'Second': 0.18, 'Third': 0.20}
    dict_yiyao = {'fundCode': '161726', 'fundName': '招商国证生物医药指数(LOF)', 'First': 0.15, 'Second': 0.18, 'Third': 0.20}
    dict_nongye = {'fundCode': '005106', 'fundName': '银华农业产业股票发起式', 'First': 0.15, 'Second': 0.18, 'Third': 0.20}
    FundsInfo = [dict_jungong, dict_bandaoti, dict_xinnengyuan, dict_huangjin, dict_yiliao,  dict_spyl, dict_yiyao, dict_nongye]
    return FundsInfo

'''
获取首页历史净值详情，获取最近20条净值和总页数
'''
def GetPageValue(fundCode,pageIndex=1):
    url = 'http://api.fund.eastmoney.com/f10/lsjz'
    # 参数化访问链接，以dict方式存储
    params = {
        'callback': 'jQuery18307633215694564663_1548321266367',
        'fundCode': fundCode,
        'pageIndex': pageIndex,
        'pageSize': 20,
    }
    # 存储cookie内容
    cookie = 'EMFUND1=null; EMFUND2=null; EMFUND3=null; EMFUND4=null; EMFUND5=null; EMFUND6=null; EMFUND7=null; EMFUND8=null; EMFUND0=null; EMFUND9=01-24 17:11:50@#$%u957F%u4FE1%u5229%u5E7F%u6DF7%u5408A@%23%24519961; st_pvi=27838598767214; st_si=11887649835514'
    # 装饰头文件
    headers = {
        'Cookie': cookie,
        'Host': 'api.fund.eastmoney.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        'Referer': 'http://fundf10.eastmoney.com/jjjz_%s.html' % fundCode,
    }
    try:
        r = requests.get(url=url, headers=headers, params=params)  # 发送请求,可以获取基金历史净值总条数
        if r.status_code == 200:
            page_value = re.findall('\((.*?)\)', r.text)[0]     # 提取首页净值信息dict,重点学习find
            return page_value
        return None
    except RecursionError:
        return None

''' 获取历史净值总页数，每页默认20条'''
def PageCount(fundCode):
    page_value = GetPageValue(fundCode,pageIndex=1)
    if page_value is not None:
        total_count = json.loads(page_value)['TotalCount']  # 获取TotalCount历史净值总条数
        page_count = math.ceil(total_count / 20 - 1)   #最后一页不足20条，下面循环是以每页20条为基准所以去掉最后一页减1
        return page_count
    return None

def GetTotalVaule(fundCode):
    page_count = PageCount(fundCode)
    page = 0
    total_value_list = []
    # 把每一页的20天净值添加到列表中
    while page < page_count:
        page += 1
        page_value = GetPageValue(fundCode, pageIndex=page)
        page_LSJZList = json.loads(page_value)['Data']['LSJZList']  # 获取历史净值数据,json数据转换学习
        for value in range(20):   #倒序排，把最近的值放最前面,19为每页20条净值
            day_dict = page_LSJZList[value]  #某一天净值字典
            day_tuple = (fundCode,day_dict['FSRQ'],day_dict['DWJZ'],day_dict['LJJZ'],day_dict['JZZZL'],day_dict['SGZT'],day_dict['SHZT'])
            total_value_list.append(day_tuple)   #把这一页的20天净值添加到列表中
    return total_value_list

def CreateHisTable(fundCode):
    table_name = 'fund_his_' + fundCode
    # 打开数据库连接,参数1:主机名或IP；参数2：用户名；参数3：密码；参数4：数据库名称
    db = pymysql.connect(host='localhost',port=3216, user='root', passwd="Yibao@147", db="FundMethod",charset='utf8')
    # 使用cursor()方法创建一个游标对象cursor
    cursor = db.cursor()
    # 使用预处理语句创建表
    sql = """
    CREATE TABLE IF NOT EXISTS {table} (
    id int NOT NULL AUTO_INCREMENT,
    FCODE varchar(10) NOT NULL COMMENT '基金代码',
    FSRQ date DEFAULT NULL COMMENT '基金日期',
    DWJZ decimal(10,4) DEFAULT NULL COMMENT '单位净值',
    LJJZ decimal(10,4) DEFAULT NULL COMMENT '累计净值',
    JZZZL varchar(20) DEFAULT NULL COMMENT '日增长率',
    SGZT varchar(20) DEFAULT NULL COMMENT '申购状态',
    SHZT varchar(20) DEFAULT NULL COMMENT '赎回状态',
    PRIMARY KEY (id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='基金历史数据表';
    """.format(table=table_name)
    # 使用execute()方法执行SQL查询
    cursor.execute(sql)
    db.commit()
    # 关闭数据库连接
    db.close()

# 查询某只基金最近区间（天数可自己定义默认180天约3个季度，目的是某些基金单位净值会突然下调）历史净值
def Values(fundCode,Days=180):
    table = 'fund_his_' + fundCode
    # 打开数据库连接,参数1:主机名或IP；参数2：用户名；参数3：密码；参数4：数据库名称
    db = pymysql.connect(host='localhost', port=3216, user='root', passwd="Yibao@147", db="FundMethod", charset='utf8')
    # 使用cursor()方法创建一个游标对象cursor
    cursor = db.cursor()
    try:
        # 查询
        selectSql = 'select FSRQ,DWJZ from {table} order by FSRQ desc limit {Days};'.format(table=table, Days=Days)
        selectData = cursor.execute(selectSql)
        results = cursor.fetchall()
        values = []
        for row in results:
            dwjz = float(row[1])
            values.append(dwjz)
    except:
        print("Error: unable to fetch data")
    db.close()
    return values

# 存数据库(实时数据-14:00-15:00每隔五分钟获取一次实时净值)
def CreateBandTable():
    table_name = 'band_realtime'
    # 打开数据库连接,参数1:主机名或IP；参数2：用户名；参数3：密码；参数4：数据库名称
    db = pymysql.connect(host='localhost',port=3216, user='root', passwd="Yibao@147", db="FundMethod",charset='utf8')
    # 使用cursor()方法创建一个游标对象cursor
    cursor = db.cursor()
    # 使用预处理语句创建表
    sql = """
    CREATE TABLE IF NOT EXISTS {table_name} (
    id INT NOT NULL AUTO_INCREMENT,
    fundcode VARCHAR(10) NOT NULL COMMENT '基金代码',
    realtime_value DECIMAL(10,4) DEFAULT NULL COMMENT '实时净值',
    year_top_value DECIMAL(10,4) DEFAULT NULL COMMENT '最近一年的最高值',
    under_top DECIMAL(10,2) DEFAULT NULL COMMENT '低于最高值多少比例',
    update_time DATETIME DEFAULT null COMMENT '估值更新时间',
    create_time DATETIME DEFAULT null COMMENT '数据写入时间',
    PRIMARY KEY (id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='基金实时数据表';
    """.format(table_name=table_name)

    # 使用execute()方法执行SQL语句
    cursor.execute(sql)
    db.commit()
    # 关闭数据库连接
    db.close()

#查询最近一条更新（实时）under_top低于最高值比例
def QueryUnderTop(fundCode):
    table_name = 'band_realtime'
    db = pymysql.connect(host='localhost',port=3216, user='root', passwd="Yibao@147", db="FundMethod",charset='utf8')
    cursor = db.cursor()
    sql = 'select under_top from band_realtime where fundcode = {fundCode} order by id desc limit 1;'.format(fundCode=fundCode)
    select_data = cursor.execute(sql)
    result = cursor.fetchall()
    query_under_top = result[0][0]
    query_under_top = float(query_under_top)
    db.commit()
    db.close()
    return query_under_top

def Hs300RealtimePrice():
    url = 'http://hq.sinajs.cn/rn=1618795512520&list=s_sz399300'
    result = requests.get(url)
    html = result.text
    hs300_realtime_price = re.findall('[0-9]{4}[\.][0-9]{2}', html)
    hs300_realtime_price = float(hs300_realtime_price[0])
    return hs300_realtime_price

def Hs300Max():
    #   通过基金编码获取估值
    date_now = datetime.now().strftime("%Y-%m-%d")
    date_type = datetime.strptime(date_now, '%Y-%m-%d')
    date_yearago = (date_type - relativedelta(years=1)).strftime('%Y-%m-%d')
    url = 'http://app.finance.ifeng.com/hq/stock_daily.php?code=sz399300&begin_day={date_yearago}&end_day={date_now}'.format(date_yearago=date_yearago,date_now=date_now)
    result = requests.get(url) # 发送请求
    html = result.text
    soup = BeautifulSoup(html, features='lxml')
    divs = soup.findAll('div',{'class': 'tab01'})
    hs300_data = []
    for div in divs:
        rows = div.findAll('tr')
        for row in rows:
            td = row.findAll('td')
            if td:
                # td0 = str(td[0])   #收盘时间
                td4 = str(td[4])    #收盘价格
                # date = re.findall("\d{4}[\-]\d{2}[\-]\d{2}", td0)
                # date = date[0]
                closing_price = re.findall("\d+[\.]\d*", td4)
                closing_price = closing_price[0]
                # hs300_data_tuple = (date,closing_price)
                hs300_data.append(closing_price)
    hs300_max = float(max(hs300_data))
    return hs300_max

def Hs300UnderTop():
    hs300_realtime_price = Hs300RealtimePrice()
    hs300_max = Hs300Max()
    hs300_under_top = (hs300_max - hs300_realtime_price) / hs300_max
    hs300_under_top = round(hs300_under_top, 2)
    return hs300_under_top

def Hs300CompareMax():
    hs300_under_top = Hs300UnderTop()
    alarm_time = datetime.now().strftime("%y-%m-%d %H:%M:%S")
    if 0.1 <= hs300_under_top < 0.15:
        print(alarm_time + '  ' + '沪深300指数低于年top {hs300_under_top}混合基金应加仓10%,总加仓位10%.'.format(hs300_under_top=hs300_under_top))
    elif 0.15 <= hs300_under_top < 0.2:
        print(alarm_time + '  ' + '沪深300指数低于年top {hs300_under_top}混合基金应加仓15%,总加仓位25%.'.format(hs300_under_top=hs300_under_top))
    elif 0.2 <= hs300_under_top < 0.25:
        print(alarm_time + '  ' + '沪深300指数低于年top {hs300_under_top}混合基金应加仓20%,总加仓位45%.'.format(hs300_under_top=hs300_under_top))
    elif 0.25 <= hs300_under_top < 0.3:
        print(alarm_time + '  ' + '沪深300指数低于年top {hs300_under_top}混合基金应加仓25%,总加仓位70%.'.format(hs300_under_top=hs300_under_top))
    elif  hs300_under_top >= 0.3:
        print(alarm_time + '  ' + '沪深300指数低于年top {hs300_under_top}混合基金应加仓30%,总加仓位满仓.'.format(hs300_under_top=hs300_under_top))
    else:
        print(alarm_time + '  ' + '沪深300指数低于年top {under_top},少于0.1不需要加仓'.format(under_top=under_top))
