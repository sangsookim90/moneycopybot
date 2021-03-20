import warnings
warnings.filterwarnings(action='ignore')

import configparser    
import matplotlib.pyplot as plt
import numpy as np
import pyupbit
import telegram
import time
import pandas as pd
from logic_lib.volatility_check import VolatilityChecker
import traceback
import matplotlib.gridspec as gridspec
import os
from mpl_finance import candlestick_ohlc

class MoneyCopyBot():
    
    def __init__(self) : 
        config = configparser.ConfigParser()
        config.read('./config.ini')
        access_key = config['UPBIT']['ACCESSKEY']
        secret_key = config['UPBIT']['SECRETKEY']
        telgm_token = config['TELEGRAM']['TOKEN']
        self.chat_id = config['TELEGRAM']['CHAT_ID']
        self.bot = telegram.Bot(token = telgm_token)
#         self.tickers = config['TICKERS']['NAMES'].split(',')
#         self.tickers = ['KRW-' + x for x in self.tickers]
        
        self.tickers = pyupbit.get_tickers('KRW')
#         self.tickers = ['KRW-BTC', 'KRW-ETH']
        
        self.tickers = [x for x in self.tickers if 'ADA' not in x ]
        self.max_buy_price = 20000.0
        self.max_sell_price = 20000.0
        self.upbit = pyupbit.Upbit(access_key, secret_key)
        self.vc = VolatilityChecker()
        self.tick = 3
        self.base = 0 
       
        
    def execute(self): 
        while True: 
            for coin_code in self.tickers:
                try : 
                    #print(coin_code)
                    self.buy_execute(coin_code)
                    #self.sell_execute(coin_code)
                except Exception as e : 
                    print(traceback.print_exc())
                    print(coin_code)
                    continue 
            time.sleep(240)
    
    def buy_execute(self, coin_code):
        time.sleep(0.1)
        data_days = pyupbit.get_ohlcv(coin_code, interval = 'day', count = 30)
        if self.vc.check_bollinger(data_days):
            data_minute = pyupbit.get_ohlcv(coin_code, interval="minute5", count= 30)  
            data_hours = pyupbit.get_ohlcv(coin_code, interval = 'minute60', count = 30)
            data_hours = self.vc.get_target_df_hours(data_hours, self.tick, self.base)
            
            
            if self.vc.check_buy_rsi(data_minute,rsi_jump=13): 
                ret = self.upbit.buy_market_order(coin_code, self.max_buy_price)
                if 'error' not in ret.keys() :
                    price = pyupbit.get_current_price(coin_code)
                    volume = self.max_buy_price/price
                    reason = 'rsi_buy_check'
                    self.send_message(price, None, coin_code, volume, None, 'buy', reason)
                    self.save_plotImage(data_minute, price)                    
                    self.bot.send_photo(chat_id=self.chat_id, photo = open(os.path.join(os.getcwd(), 'tmp_img', 'tmp.png'), 'rb' ))                
            
            
#             if self.vc.check_buy_point(data_minute, data_hours): 
#                 self.upbit.buy_market_order(coin_code, self.max_buy_price)
#                 price = pyupbit.get_current_price(coin_code)
#                 volume = self.max_buy_price/price
#                 reason = 'volatility_check'
#                 self.send_message(price, None, coin_code, volume, None, 'buy', reason)
#                 self.save_plotImage(data_minute, price)                    
#                 self.bot.send_photo(chat_id=self.chat_id, photo = open(os.path.join(os.getcwd(), 'tmp_img', 'tmp.png'), 'rb' ))


    def sell_execute(self, coin_code):
        ## 대충 파는 부분 -- 조회해서 있으면 판다. 
        balance = self.upbit.get_balance(ticker=coin_code)
        time.sleep(0.1)
        if balance > 0 : 
            data_minute = pyupbit.get_ohlcv(coin_code, interval="minute1", count= 30)  
            data_hours = pyupbit.get_ohlcv(coin_code, interval = 'minute60', count = 30)
            data_hours = self.vc.get_target_df_hours(data_hours, self.tick, self.base)
            current_price = pyupbit.get_current_price(coin_code)
            avg_buy_price = self.upbit.get_avg_buy_price(coin_code)
            
            benefit_ratio = (current_price - avg_buy_price)/avg_buy_price

            
            if self.vc.check_sell_rsi(data_minute,rsi_jump=13) and  benefit_ratio >= 1.01:
                ret = self.upbit.sell_market_order(coin_code, balance)
                if 'error' not in ret.keys() :
                    params = {}
                    params['COIN_CD'] = coin_code
                    params['PRICE'] = price
                    params['REASON'] = reason
                    params['GUBUN'] = 'SELL'
                    params['PROFIT'] = profit
                    params['AVG_BUY_PRICE'] = avg_buy_price
                    params['VOLUME'] = volume
        #             self.db.insert_buying_data(params)
                    reason = 'rsi_sell_check'
                    avg_buy_price = self.upbit.get_avg_buy_price(coin_code)
                    price =pyupbit.get_current_price(coin_code)
                    profit = (price - avg_buy_price) * balance
                    self.send_message(avg_buy_price, price, coin_code, balance, profit, 'sell', reason)
                    self.save_plotImage(data_minute, avg_buy_price)
                    self.bot.send_photo(chat_id=self.chat_id, photo = open(os.path.join(os.getcwd(), 'tmp_img', 'tmp.png'), 'rb' ))
        
            
            
            elif self.vc.check_extreme_down(data_minute) : 
                ret = self.upbit.sell_market_order(coin_code, balance)
                if 'error' not in ret.keys() :
                    params = {}
                    params['COIN_CD'] = coin_code
                    params['PRICE'] = price
                    params['REASON'] = reason
                    params['GUBUN'] = 'SELL'
                    params['PROFIT'] = profit
                    params['AVG_BUY_PRICE'] = avg_buy_price
                    params['VOLUME'] = volume
        #             self.db.insert_buying_data(params)
                    reason = 'extremedown_check'
                    avg_buy_price = self.upbit.get_avg_buy_price(coin_code)
                    price =pyupbit.get_current_price(coin_code)
                    profit = (price - avg_buy_price) * balance
                    self.send_message(avg_buy_price, price, coin_code, balance, profit, 'sell', reason)
                    self.save_plotImage(data_minute, avg_buy_price)
                    self.bot.send_photo(chat_id=self.chat_id, photo = open(os.path.join(os.getcwd(), 'tmp_img', 'tmp.png'), 'rb' ))
        
              
            
            
            
            
#             elif self.vc.check_sell_point(data_minute, self.tick, self.base) : 
#                 ret = self.upbit.sell_market_order(coin_code, balance)
#                 if 'error' not in ret.keys() :
#                     avg_buy_price = self.upbit.get_avg_buy_price(coin_code)
#                     price =pyupbit.get_current_price(coin_code)
#                     params = {}
#                     params['COIN_CD'] = coin_code
#                     params['PRICE'] = price
#                     params['REASON'] = reason
#                     params['GUBUN'] = 'SELL'
#                     params['PROFIT'] = profit
#                     params['AVG_BUY_PRICE'] = avg_buy_price
#                     params['VOLUME'] = volume
#         #             self.db.insert_buying_data(params)
#                     reason = 'volatility_check'

#                     profit = (price - avg_buy_price) * balance
#                     self.send_message(avg_buy_price, price, coin_code, balance, profit, 'sell', reason)
#                     self.save_plotImage(data_minute, avg_buy_price)
#                     self.bot.send_photo(chat_id=self.chat_id, photo = open(os.path.join(os.getcwd(), 'tmp_img', 'tmp.png'), 'rb' ))
        
        
    
    def save_plotImage(self, data, buy_price):
        
        os.makedirs(os.path.join(os.getcwd(), 'tmp_img'), exist_ok = True)
        
        fig = plt.figure(figsize=(8, 5))
        fig.set_facecolor('w')
        gs = gridspec.GridSpec(1, 1)
        axes = []
        axes.append(plt.subplot(gs[0]))
        axes[0].get_xaxis().set_visible(True)
        
        x = np.arange(len(data.index))
        ohlc = data[['open', 'high', 'low', 'close']].astype(int).values
        dohlc = np.hstack((np.reshape(x, (-1, 1)), ohlc))    
        
        candlestick_ohlc(axes[0],dohlc, width=0.5, colorup='r', colordown='b')

        plt.axhline(y = buy_price, color='g', linewidth = 2)
        plt.tight_layout()
        plt.savefig(os.path.join(os.getcwd(), 'tmp_img', 'tmp.png'), dpi = 100 )
    

    def send_message(self, avg_buy_price, sell_price, ticker, volumn, profit, mode, reason) : 
        
        if mode == 'sell':
            msg = '{0} \n'.format(mode)
            msg += 'ticker : {0} \n'.format(ticker)
            msg += 'avg_buy_price : {0} \n'.format(avg_buy_price)
            msg += 'sell_price : {0} \n'.format(sell_price)
            msg += 'volumn : {0} \n'.format(volumn)
            msg += 'profit : {0} \n'.format(profit)
            msg += 'reason : {0} \n'.format(reason)
            self.bot.sendMessage(chat_id =self.chat_id,  text=msg)
        
        elif mode =='buy' : 
            msg = '{0} \n'.format(mode)
            msg += 'ticker : {0} \n'.format(ticker)
            msg += 'buy_price : {0} \n'.format(avg_buy_price)
            msg += 'volumn : {0} \n'.format(volumn)
            msg += 'total_buy_price : {0} \n'.format(volumn*avg_buy_price)
            msg += 'reason : {0} \n'.format(reason)
            self.bot.sendMessage(chat_id =self.chat_id,  text=msg)

if __name__ == "__main__" :
    moneycopybot = MoneyCopyBot()
    moneycopybot.execute()



