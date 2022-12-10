# -*- coding: utf-8 -*-
"""
Created on Wed Nov  9 14:59:50 2022
Quant Research Libary
@author: kailei
"""
#初始化接口

import pandas as pd
import numpy as np
import tushare as ts
import matplotlib.pyplot as plt
import datetime
import time
import re
ts.set_token('99858a63ddbc39334d2e61af5aa19f5ac5f5da5a2c109262ed68a092') #token如果失效，需要登陆Tushare官网刷新后更改
pro = ts.pro_api() 

# #def false_positive(security, trade_date):
    
    
#     """
#     判断某天是否出现假阳线，当天收盘价>开盘价，但低于前一天收盘价；
#     主力诱惑行为，后期下跌概率较大

#     security : 股票代码
#     trade_date : 交易日

#     """
#     df = pro.daily(ts_code = security, trade_date = trade_date)
    
#     if (df['close'] > df['open']) & (df['change'] < 0):
    

     
    
    
    
start_date = '20221102'
end_date = '20221108'
data = pro.daily(ts_code = '605398.SH', start_date = start_date, end_date = end_date).sort_values(by = 'trade_date') #start_date = str(int(end_date) - 6)
data = data.reset_index(drop = True) #重排index

# 计算当天的涨跌额，并判断该日阳线或者阴线
# 涨停一字板
data['today_change'] = data['close'] - data['open']
data['is_positive'] = np.sign(data['today_change']) 
data['is_positive'] = data['is_positive'].map({1:'+', -1:'-'})
data.loc[(data['today_change'] == 0)  & (data['pct_chg'] > 0), 'is_positive'] = '+'
data.loc[(data['today_change'] == 0)  & (data['pct_chg'] < 0), 'is_positive'] = '-'

print(data.iloc[0,:])
# 计算成交量变化
data['volume_change'] = data['vol'].diff(periods = 1)


up_down = ','.join(list(data['is_positive'])).replace(',', '')

for i in re.finditer(r'[+][-][+]', up_down): # 查找是否两阳夹一阴，并返回第一根阳线所在位置
    if i:
        # i.start会返回所有的+-+位置，我们只获取最新的
        pos_new_positive = i.start() #获得最新的两阳夹一阴形态，并识别不了+-+-+中的第二个+-+（待解决）
        
    

str1 ='20220930' 
str2 ='20211102'
date1=datetime.datetime.strptime(str1[0:10], '%Y%m%d')
date2=datetime.datetime.strptime(str2[0:10], '%Y%m%d')
num =(date1-date2).days


















