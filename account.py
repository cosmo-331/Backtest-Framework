# -*- coding: utf-8 -*-
import datetime
import math
import pandas as pd
import FunctionsLib
class account(object):
    # data is a dictionary of dataframes whose indices are dates, 
    # keys are the stock IDs.
    def __init__(self, capital = 1000000):
        self.capital = capital
        self.holdings = dict()
        self.date = datetime.datetime(1900,1,1)
        self.order_history = list()
        self.data = dict()
        self.commission = 0
    
    def set_commission(self, x):
        self.commission = x
    
    def load_data(self,df,col):
        '''
        loads data into the account

        Parameters
        ----------
        df : DataFrame
            the processed data.
        col : str
            the column of stock IDs in df.

        Returns
        -------
        None.

        '''
        for stock in df[col]:
            self.data[stock] = df[df[col] == stock].drop(col,axis = 1)
    
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
        price = self.data[stock].loc[self.date]
        # if we don't have enough money, then buy the largest amount we can
        if price * amount > self.capital:
            amount = math.floor(self.capital/price/100)*100
        
        if stock in self.holdings.keys():
            # if we are selling more than we have, we will sell all of them
            if amount + self.holdings[stock]<0:
                amount = -self.holdings[stock]
            self.holdings[stock] = self.holdings[stock] + amount
            if self.holdings[stock] == 0:
                self.holdings.pop(stock)
        else:
            self.holdings[stock] = amount
            
        self.order_history.append({'date': self.date,
                                   'stock_ID': stock,
                                   'amount': amount,
                                   'price': price})
        self.capital = self.capital - price*amount - price*abs(amount)*self.commission
        
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
