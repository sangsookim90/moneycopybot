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
import datetime


class MoneyCopyBot():
    
    def __init__(self) : 
        self.config = configparser.ConfigParser()
        self.config.read('./config.ini')
        access_key = self.config['UPBIT']['ACCESSKEY']
        secret_key = self.config['UPBIT']['SECRETKEY']
        telgm_token = self.config['TELEGRAM']['TOKEN']
        self.chat_id = self.config['TELEGRAM']['CHAT_ID']
        self.bot = telegram.Bot(token = telgm_token)
        
        self.tickers = pyupbit.get_tickers('KRW')
        self.max_buy_price = 50000.0
        # self.max_sell_price = 50000.0
        self.upbit = pyupbit.Upbit(access_key, secret_key)
        self.vc = VolatilityChecker()
        self.tick = 3
        self.base = 0 
       

    def get_real_time_config(self, attr1, attr2): 
        self.config.read('./config.ini')
        return self.config[attr1][attr2]


    def execute(self): 
        while True:

            buy_mode = self.get_real_time_config('MODE', 'BUY')
            if buy_mode == '1' : 
                now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')                              
                tickers = self.get_tickers()
                print('{0} : buy_process '.format(now))
                for coin_code in tickers : 
                    try : 
                        self.buy_execute(coin_code)

                    except Exception as e : 
                        print(traceback.print_exc())
                        print(coin_code)
                        continue
                                     

            for _ in range(3) : 
                sell_mode = self.get_real_time_config('MODE', 'SELL')
                if sell_mode == '1' :
                    tickers = self.get_tickers()
                    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print('{0} : sell_process '.format(now))
                    for coin_code in tickers:
                        try : 
                            self.sell_execute(coin_code) 

                        except Exception as e : 
                            print(traceback.print_exc())
                            print(coin_code)
                            continue 
                time.sleep(60)


    def get_tickers(self):
        tickers = pyupbit.get_tickers('KRW')
        except_coins_config = self.get_real_time_config('TICKERS', 'NAMES')
        except_coins = ['KRW-{0}'.format(x) for x in except_coins_config.split(',') if len(x) > 0 ]
        tickers = [x for x in tickers if x not in except_coins]
        return tickers 
            
    
    def buy_execute(self, coin_code):
        data_days = pyupbit.get_ohlcv(coin_code, interval='day', count=30)
        time.sleep(0.2)

        if self.vc.check_bollinger(data_days):
            current_price = pyupbit.get_current_price(coin_code)
            avg_buy_price = self.upbit.get_avg_buy_price(coin_code)

            if abs(avg_buy_price-current_price) > 0.1 * avg_buy_price:
                data_minute3 = pyupbit.get_ohlcv(coin_code, interval='minute3', count=30)
                data_minute1 = pyupbit.get_ohlcv(coin_code, interval='minute1', count=30)
                data_hours = pyupbit.get_ohlcv(coin_code, interval='minute60', count=30)
                data_hours = self.vc.get_target_df_hours(data_hours, self.tick, self.base)
                
                rsi_3m = self.vc.check_buy_rsi(data_minute3, rsi_jump=14)
                rsi_1m = self.vc.check_buy_rsi(data_minute1, rsi_jump=14)
                if rsi_3m[-2] < 0.3 and rsi_3m[-1] > 0.3 and rsi_1m[-1] > 0.3: 
                    ret = self.upbit.buy_market_order(coin_code, self.max_buy_price)
                    if 'error' not in ret.keys():
                        volume = self.max_buy_price/current_price
                        reason = 'rsi_buy_check'
                        self.save_plotImage(data_minute3, current_price)
                        self.bot.send_photo(chat_id=self.chat_id, photo = open(os.path.join(os.getcwd(), 'tmp_img', 'tmp.png'), 'rb'))
                        self.send_message(current_price, None, coin_code, volume, None, 'buy', reason)
                        

    def sell_execute(self, coin_code):
        ## 대충 파는 부분 -- 조회해서 있으면 판다. 
        balance = self.upbit.get_balance(ticker=coin_code)
        time.sleep(0.2)

        if balance > 0 :
            data_minute3 = pyupbit.get_ohlcv(coin_code, interval='minute3', count=30)  
            data_minute1 = pyupbit.get_ohlcv(coin_code, interval='minute1', count=30)  
            data_hours = pyupbit.get_ohlcv(coin_code, interval='minute60', count=30)
            data_hours = self.vc.get_target_df_hours(data_hours, self.tick, self.base)

            current_price = pyupbit.get_current_price(coin_code)
            avg_buy_price = self.upbit.get_avg_buy_price(coin_code)
            benefit_ratio = (current_price - avg_buy_price) / avg_buy_price
            profit = (current_price - avg_buy_price) * balance
            
            rsi_3m = self.vc.check_sell_rsi(data_minute3, rsi_jump=14)
            rsi_1m = self.vc.check_sell_rsi(data_minute1, rsi_jump=14)
            if rsi_3m[-2] > 0.7 and rsi_3m[-1] < 0.7 and rsi_1m[-1] < 0.7 and benefit_ratio >= 0.03:
                ret = self.upbit.sell_market_order(coin_code, balance)
                if 'error' not in ret.keys():
                    reason = 'rsi_sell_check'
                    self.save_plotImage(data_minute3, avg_buy_price)
                    self.bot.send_photo(chat_id=self.chat_id, photo = open(os.path.join(os.getcwd(), 'tmp_img', 'tmp.png'), 'rb'))
                    self.send_message(avg_buy_price, current_price, coin_code, balance, profit, 'sell', reason)
                       
            elif self.vc.check_extreme_down(data_minute3):
                ret = self.upbit.sell_market_order(coin_code, balance)
                if 'error' not in ret.keys():
                    reason = 'extremedown_check'
                    self.save_plotImage(data_minute3, avg_buy_price)
                    self.bot.send_photo(chat_id=self.chat_id, photo = open(os.path.join(os.getcwd(), 'tmp_img', 'tmp.png'), 'rb'))
                    self.send_message(avg_buy_price, current_price, coin_code, balance, profit, 'sell', reason)
            
            elif benefit_ratio > 0.07 and rsi_3m[-1] < 0.6:
                ret = self.upbit.sell_market_order(coin_code, balance)
                if 'error' not in ret.keys() :
                    reason = 'standard margin'
                    self.save_plotImage(data_minute3, avg_buy_price)
                    self.bot.send_photo(chat_id=self.chat_id, photo = open(os.path.join(os.getcwd(), 'tmp_img', 'tmp.png'), 'rb'))
                    self.send_message(avg_buy_price, current_price, coin_code, balance, profit, 'sell', reason)


        
    
    def save_plotImage(self, data, buy_price):
        
        os.makedirs(os.path.join(os.getcwd(), 'tmp_img'), exist_ok=True)
        
        fig = plt.figure(figsize=(8, 5))
        fig.set_facecolor('w')
        gs = gridspec.GridSpec(1, 1)
        axes = []
        axes.append(plt.subplot(gs[0]))
        axes[0].get_xaxis().set_visible(True)
        
        x = np.arange(len(data.index))
        ohlc = data[['open', 'high', 'low', 'close']].astype(int).values
        dohlc = np.hstack((np.reshape(x, (-1, 1)), ohlc))    
        
        candlestick_ohlc(axes[0], dohlc, width=0.5, colorup='r', colordown='b')

        plt.axhline(y=buy_price, color='g', linewidth=2)
        plt.tight_layout()
        plt.savefig(os.path.join(os.getcwd(), 'tmp_img', 'tmp.png'), dpi = 100)
    

    def send_message(self, avg_buy_price, sell_price, ticker, volume, profit, mode, reason): 
        
        if mode == 'sell':
            msg = '{0} \n'.format(mode)
            msg += 'ticker : {0} \n'.format(ticker)
            msg += 'avg_buy_price : {0} \n'.format(avg_buy_price)
            msg += 'sell_price : {0} \n'.format(sell_price)
            msg += 'volume : {0} \n'.format(volume)
            msg += 'profit : {0} \n'.format(profit)
            msg += 'reason : {0} \n'.format(reason)
            self.bot.sendMessage(chat_id =self.chat_id, text=msg)
        
        elif mode =='buy' : 
            msg = '{0} \n'.format(mode)
            msg += 'ticker : {0} \n'.format(ticker)
            msg += 'buy_price : {0} \n'.format(avg_buy_price)
            msg += 'volume : {0} \n'.format(volume)
            msg += 'total_buy_price : {0} \n'.format(volume*avg_buy_price)
            msg += 'reason : {0} \n'.format(reason)
            self.bot.sendMessage(chat_id =self.chat_id, text=msg)

if __name__ == "__main__" :
    moneycopybot = MoneyCopyBot()
    moneycopybot.execute()