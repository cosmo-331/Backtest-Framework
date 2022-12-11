# -*- coding: utf-8 -*-
import datetime
import math
import pandas as pd
import FunctionsLib
import matplotlib.pyplot as plt
class Account(object):
    
    def __init__(self):
        # the amount of cash in this account
        self.cash = 1000000
        # this is a dictionary whose keys are the stock_IDs of the stocks 
        # we own and the value is the number of shares
        self.holdings = dict()
        # the current date
        self.date = datetime.datetime(1900,1,1)
        # this is a list of tuples consisting of order information
        self.order_history = list()
        # data is a dictionary of dataframes whose indices are dates, and
        # keys are the stock IDs.
        self.data = dict()
        # 手续费
        self.commission = 0.002
        # the column name of stock_ID in self.data
        self.stock_col = 'stock_ID'
        # two lists consisting of the date and the corresponding capital of 
        # this account at that day.
        self.value_history = [[],[]]
    
    def set_cash(self, x):
        self.cash = x
    
    def set_commission(self, x):
        self.commission = x
    
    def load_data(self,df,col):
        '''
        loads data into the account. 

        Parameters
        ----------
        df : DataFrame
            the processed data. Note: the index of this dataframe must be date
            in datetime format
        col : str
            the column name of stock IDs in df.

        Returns
        -------
        None.

        '''
        self.data = dict()
        # split the dataframe by stock_ID and store them separately
        for stock in df[col]:
            self.data[stock] = df[df[col] == stock]
        # get the column name of stock_IDs
        self.stock_col = col
    
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
        # get the price of the stock by looking into self.data 
        price = self.data[stock]['close'].loc[self.date]
        # if we don't have enough cash, then buy the largest amount we can
        if price * amount + price*abs(amount)*self.commission > self.cash:
            amount = math.floor(self.cash/price/100)*100
        
        # if we own this stock, then we need to modify the number of shares we
        # own; if we do not own this stock, then set the number of shares to be
        # amount.
        if stock in self.holdings.keys():
            # if we are selling more than we have, we will sell all of them
            if amount + self.holdings[stock]<0:
                amount = -self.holdings[stock]
            # update the amount of the stock we hold
            self.holdings[stock] = self.holdings[stock] + amount
            # if we no longer hold this stock, then remove it from our portfolio
            if self.holdings[stock] == 0:
                self.holdings.pop(stock)
        else:
            # if we are selling something we don't have, then don't do anything
            if amount < 0:
                return
            self.holdings[stock] = amount
        
        # write the order information into the order history
        self.order_history.append({'date': self.date,
                                   'stock_ID': stock,
                                   'amount': amount,
                                   'price': price})
        # alter the amount of cash in this account
        self.cash = self.cash - price*amount - price*abs(amount)*self.commission
        
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
        # just order
        if stock in self.holdings.keys():
            self.order(stock, amount - self.holdings[stock])
        else:
            self.order(stock, amount)
            
    def get_history(self, stock_ID, attributes, start_date, end_date):
        '''
        get the data of one stock or a list of stocks during some period in the past (between 
        start_date and end_date, inclusive)
        
        Parameters
        ----------
        stock_ID: str or list
            the stock code of desired(can be multiple stocks)
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
            a pandas dataframe containing relevant data of the stock
            between start_date and end_date.

        '''
        # if the period is not in the past, then make end_date the previous day
        previous_day = FunctionsLib.timefromstr(FunctionsLib.last_trade_date(self.date))
        if end_date > previous_day:
            end_date = previous_day
        # if the query didn't ask for stock_ID, we will add them
        if self.stock_col not in attributes:
            attributes.append(self.stock_col)
        # if there is only one stock in the query, then just return the 
        # corresponding dataset
        if type(stock_ID) == str:
            return self.data[stock_ID][attributes].loc[start_date:end_date+datetime.timedelta(days = 1)]
        # if there is multiple stocks, then concatenate the dataframes
        # for each stock
        if type(stock_ID) == list:
            ans = self.data[stock_ID[0]][attributes].loc[start_date:end_date+datetime.timedelta(days = 1)]
            for i in range(1,len(stock_ID)):
                ans = pd.concat([ans, self.data[stock_ID[i]][attributes].loc[start_date: end_date+datetime.timedelta(days = 1)]])
            return ans
    def get_MA(self, days):
        '''
        add a moving average to the data

        Parameters
        ----------
        days : int
            number of days of the moving average.

        Returns
        -------
        None.

        '''
        col = 'MA'+str(days)
        # if we already have this moving average, don't do anything
        if col not in self.data[list(self.data.keys())[0]].columns:
            # we add the moving average to every stock
            for stock in self.data.keys():
                self.data[stock][col] = self.data[stock]['close'].rolling(days).mean()
    
    def get_total_value(self):
        '''
        get the total capital of the account

        Returns
        -------
        ans : int
            the total capital of the account.

        '''
        # we add the cash and the value of every stock we own
        ans = self.cash
        for stock in self.holdings.keys():
            #get the price from self.data
            price = self.data[stock]['close'].loc[self.date]
            ans = ans + price*self.holdings[stock]
        return ans
    
    def update_value_history(self):
        '''
        ask the account to update its value_history

        Returns
        -------
        None.

        '''
        # we get the total capital of the account and record it in value_history
        ans = self.get_total_value()
        self.value_history[0].append(self.date)
        self.value_history[1].append(ans)
        
    def plot_history(self):
        '''
        Plot the total capital of our trading account over time

        Returns
        -------
        None.

        '''
        # we plot the total capital over time by referring to value_history
        plt.plot(self.value_history[0], self.value_history[1])
        plt.xlabel('time')
        plt.ylabel('total_capital')
        plt.title('Earnings over time')
        
        
        
