# -*- coding: utf-8 -*-
import datetime
import math
import pandas as pd
from . import FunctionsLib
class account(object):
    # data is historical stock data whose index is dates
    data = pd.DataFrame({})
    def __init__(self, capital = 1000000):
        self.capital = capital
        self.holdings = dict()
        self.date = datetime.datetime(1900,1,1)
        
    def order(self, stock, amount):
        '''
        Buy or sell a certain stock with this account
        
        Parameters
        ----------
        stock : str
            ID of the stock.
        amount : int
            number of shares of the stock ordered.
            is positive if we are buying;
            negative if we are selling
        
        Returns
        -------
        None.
        
        '''
        #get the price of the stock, can be improved to be more efficient
        price = self.data[self.data['stock_ID'] == stock].loc[self.date]
        # if we don't have enough money, then buy the largest amount we can
        if price * amount > self.capital:
            amount = math.floor(self.capital/price)
        
        if stock in self.holdings.keys():
            # if we are selling more than we have, we will sell all of them
            if amount + self.holdings[stock]<0:
                amount = - self.holdings[stock]
            self.holdings[stock] = self.holdings[stock] + amount
        else:
            self.holdings[stock] = amount
            
        self.capital = self.capital - price*amount
        
    def order_to(self, stock, amount):
        '''
        Buy or sell a certain stock with this account to a certain amount

        Parameters
        ----------
        stock : str
            ID for the stock.
        amount : int
            the number of share we want to end up with.

        Returns
        -------
        None.

        '''
        self.order(stock, amount - self.holdings[stock])
            
    def get_history(self, attributes, start_date, end_date):
        '''
        get the data during some period in the past (between start_date and 
        end_date, inclusive)
        
        Parameters
        ----------
        attributes : list
            a list of strings containing the columns wanted.
        start_date : datetime
            the beginning date of the query, can't be earlier than 20000101
            (or the date entered in FunctionsLib).
        end_date : datetime
            the end date of the query.

        Returns
        -------
        pandas DataFrame
            a pandas dataframe containing the attributes columns 
            between start_date and end_date.

        '''
        # if the period is not in the past, then make end_date the previous day
        previous_day = FunctionsLib.last_trade_date(self.date)
        if end_date > previous_day:
            end_date = previous_day
        return self.data[attributes].loc[start_date:end_date]