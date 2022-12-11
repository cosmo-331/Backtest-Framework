# -*- coding: utf-8 -*-
"""
Created on Sun Dec 11 11:13:59 2022

@author: Thinkpad
"""
import tushare as ts
import pandas as pd
import FunctionsLib as FL
from account import Account
from datetime import datetime
ts.set_token('99858a63ddbc39334d2e61af5aa19f5ac5f5da5a2c109262ed68a092') #token如果失效，需要登陆Tushare官网刷新后更改
pro = ts.pro_api()

def run(account, preprocess, loop, start_date, end_date):
    '''
    run the backtest and then plot the earnings over time

    Parameters
    ----------
    account : Account object
        the account used for the backtest.
    preprocess : Function object
        the init function that will be run for once before the backtest.
    loop : Function object
        the execution function for our strategy that will be run every 
        trade day.
    start_date : datetime
        the beginnning date.
    end_date : datetime
        the ending date.

    Returns
    -------
    None.

    '''
    preprocess(account)
    account.date = start_date
    while(account.date<end_date):
        loop(account)
        account.update_value_history()
        account.date = FL.timefromstr(FL.next_trade_date(account.date))
    account.plot_history()

def init(account):
    '''
    the init function that will be used in the run function.
    typically this includes loading data, setting the factors used for the 
    strategy, etc. When loading data, we need to make the index to be the
    dates in datetime format.
    
    Parameters
    ----------
    account : Account object
        the account we wish to run backtest on.

    Returns
    -------
    None.

    '''
    #get data
    df = pro.daily(ts_code = '002952.SZ', 
                   start_date = '20190511',
                   end_date = '20220501')
    # transform the index into the desired format
    df.index = df['trade_date'].apply(FL.timefromstr).values
    # we want the dates to be in ascending order
    df = df.sort_index(ascending = True)
    account.load_data(df, 'ts_code')
    account.set_commission(0)
    # if we need any extra factors, it's a good idea to get them into the data
    # at the init function. 
    account.get_MA(5)
    account.get_MA(20)
    #print(account.data)
    
def handle_data(account):
    '''
    The looped function that will be used in the run function
    typically this includes getting a stock list, a history of those stocks,
    and buying or selling with account.order or account.order_to when we see
    some signal.

    Parameters
    ----------
    account : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    '''
    # getting a stock list
    stock_list = ['002952.SZ']
    # get the range of the history we want
    today = FL.timefromstr(FL.last_trade_date(account.date))
    previous_day = FL.timefromstr(FL.previous_trade_date(today))
    
    # loop over every stock and get the history or get the history as a whole
    # both are supported in this framework
    for stock in stock_list:
        # get_history of the previous two days
        df = account.get_history(stock_ID = stock, 
                                 attributes = ['MA5', 'MA20'], 
                                 start_date = previous_day, 
                                 end_date = today)
        if len(df) == 0:
            continue
        MA5_before = df['MA5'].iloc[0]
        MA5_now = df['MA5'].iloc[-1]
        MA20_before = df['MA20'].iloc[0]
        MA20_now = df['MA20'].iloc[-1]
        # make transactions if we see a certain behavior
        if(MA5_before<MA20_before) & (MA5_now>MA20_now):
            account.order(stock, 100000)
        if(MA5_before>MA20_before) & (MA5_now<MA20_now):
            account.order_to(stock,0)
if __name__ == '__main__':
    backtest = Account()
    run(account = backtest, 
        preprocess = init, 
        loop = handle_data, 
        start_date = datetime(2018,12,11),
        end_date = datetime(2022,3,1))
