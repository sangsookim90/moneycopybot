import telegram
import configparser
import pyupbit
import pandas as pd
import time
from telegram.ext import Updater
from telegram.ext import CommandHandler
import os
import subprocess



class TelegramControlBot():
    
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('./config.ini')
        telgm_token = self.config['TELEGRAM']['TOKEN']
        chat_id = self.config['TELEGRAM']['CHAT_ID']
        access_key = self.config['UPBIT']['ACCESSKEY']
        secret_key = self.config['UPBIT']['SECRETKEY']

        self.upbit = pyupbit.Upbit(access_key, secret_key)
        self.updater = Updater( token= telgm_token, use_context=True )
        self.dispatcher = self.updater.dispatcher
        
        
        self.add_handler('exit', self.emergency_exit)
        self.add_handler('check', self.health_checker)
        self.add_handler('start', self.bot_start)
        self.add_handler('stop', self.bot_stop)
        self.add_handler('except', self.except_coin)
        self.add_handler('checkexcept', self.check_except_coin)
        self.add_handler('buyon', self.buy_on)
        self.add_handler('sellon', self.sell_on)
        self.add_handler('buyoff', self.buy_off)
        self.add_handler('selloff', self.sell_off)
        

    def execute(self): 
        self.updater.start_polling()
        
        
    def add_handler(self, command, function):
        com_handler = CommandHandler(command, function)
        self.dispatcher.add_handler(com_handler)
    
    def change_config_attr(self, attr_nm1, attr_nm2, value):
        self.config.read('./config.ini')
        self.config.set(attr_nm1, attr_nm2, value)  
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)
        
    
    def buy_on(self, update, context):
        self.change_config_attr('MODE', 'BUY', '1')
        context.bot.send_message(chat_id=update.effective_chat.id, text="buy_process를 작동합니다.")
    
    def buy_off(self, update, context):
        self.change_config_attr('MODE', 'BUY', '0')
        context.bot.send_message(chat_id=update.effective_chat.id, text="buy_process를 중지합니다.")
    
    def sell_on(self, update, context):
        self.change_config_attr('MODE', 'SELL', '1')
        context.bot.send_message(chat_id=update.effective_chat.id, text="sell_process를 작동합니다.")
    
    def sell_off(self, update, context):
        self.change_config_attr('MODE', 'SELL', '0')
        context.bot.send_message(chat_id=update.effective_chat.id, text="sell_process를 중지합니다.")
        
        
        
        
    def health_checker(self, update, context): 
        
        self.config.read('./config.ini')
        main_on = 'on' if 'pid.txt' in os.listdir() else 'off' 
        buy_on = 'on' if self.config['MODE']['BUY'] == '1' else 'off'
        sell_on = 'on' if self.config['MODE']['SELL'] == '1' else 'off'
        message = 'main_process : {0}, buy : {1}, sell : {2}'.format(main_on, buy_on, sell_on)
        context.bot.send_message(chat_id=update.effective_chat.id, text= message)


    def emergency_exit(self, update, context):    
        balances = pd.DataFrame(self.upbit.get_balances())
        balances['coin_code'] = 'KRW' + '-' + balances['currency']
        balances = balances.query('currency != "KRW"')

        for i in range(balances.shape[0]) : 
            try : 
                time.sleep(0.2)
                row = balances.iloc[i]
                coin_code = row['coin_code']
                balance = row['balance']
                ret = self.upbit.sell_market_order(coin_code, balance)
            except : 
                continue 

        context.bot.send_message(chat_id=update.effective_chat.id, text="비상탈출을 완료합니다.")


    def bot_start(self, update, context):
        if 'pid.txt' in os.listdir():
            message = "봇이 이미 실행중입니다."    
        else:
            cmd = [ "python3", "bot_execute.py"]
            #cmd = ["python3",  "Buy_Main.py"]
            process = subprocess.Popen(cmd, shell=False)
            with open('pid.txt', 'w') as f:
                f.write(str(process.pid))
            message = "봇을 실행합니다."

        context.bot.send_message(chat_id=update.effective_chat.id, text=message)


    def bot_stop(self, update, context):
        if 'pid.txt' not in os.listdir():
            message = "실행중인 봇이 없습니다."
        else:
            with open('pid.txt', 'r') as f:
                pid = f.read()
            os.system('kill -9 ' + pid)
            os.remove('pid.txt')
            message = "봇을 종료합니다."

        context.bot.send_message(chat_id=update.effective_chat.id, text=message)



    def except_coin(self, update, context):

        self.config.read('./config.ini')
        except_coins = [ x for x in self.config['TICKERS']['NAMES'].split(',')   if len(x) > 0 ]
        target_coin = context.args[0].upper()

        if 'KRW-'+target_coin in pyupbit.get_tickers('KRW'): 

            if target_coin in except_coins : 
                except_coins.remove(target_coin)
                message = "{} 거래를 재개합니다.".format(target_coin)

            else : 
                except_coins.append(target_coin)
                message = "{} 거래를 중지합니다.".format(target_coin)
                
            self.change_config_attr('TICKERS', 'NAMES', ','.join(except_coins) )

        else:
            message = "코인 코드명이 잘못되었습니다."

        context.bot.send_message(chat_id=update.effective_chat.id, text=message)


    def check_except_coin(self, update, context):
        self.config.read('./config.ini')
        except_coin_list = [ x for x in self.config['TICKERS']['NAMES'].split(',')   if len(x) > 0 ]
        if len(except_coin_list) != 0:
            except_coin_list = [coin for coin in except_coin_list]
            message = "{} 거래 중지 코인 목록입니다.".format(except_coin_list)
        else:
            message = "거래 중지 코인 목록이 없습니다."

        context.bot.send_message(chat_id=update.effective_chat.id, text=message)

if __name__ == "__main__" :
    telegram_control_bol = TelegramControlBot()
    telegram_control_bol.execute()
