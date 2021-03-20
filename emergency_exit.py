import telegram
import configparser
import pyupbit
import pandas as pd
import time

config = configparser.ConfigParser()
config.read('./config.ini')
telgm_token = config['TELEGRAM']['TOKEN']
chat_id = config['TELEGRAM']['CHAT_ID']
bot = telegram.Bot(token = telgm_token)
access_key = config['UPBIT']['ACCESSKEY']
secret_key = config['UPBIT']['SECRETKEY']

from telegram.ext import Updater

upbit = pyupbit.Upbit(access_key, secret_key)


#cmd_handler_bot.py
from telegram.ext import Updater
from telegram.ext import CommandHandler
import os
import time
import subprocess

updater = Updater( token= telgm_token, use_context=True )
dispatcher = updater.dispatcher

def health_checker(update, context): 
    context.bot.send_message(chat_id=update.effective_chat.id, text="정상 동작중.")


def emergency_exit(update, context):    
    balances = pd.DataFrame(upbit.get_balances())
    balances['coin_code'] = 'KRW' + '-' + balances['currency']
    balances = balances.query('currency != "KRW"')

    for i in range(balances.shape[0]) : 
        try : 
            time.sleep(0.2)
            row = balances.iloc[i]
            coin_code = row['coin_code']
            balance = row['balance']
            ret = upbit.sell_market_order(coin_code, balance)
        except : 
            continue 
    
    context.bot.send_message(chat_id=update.effective_chat.id, text="비상탈출을 완료합니다.")
    

def buy_bot_start(update, context):
    if 'buy_pid.txt' in os.listdir():
        message = "구매봇이 이미 실행중입니다."    
    else:
        cmd = ["open", '-W', '-a', 'Terminal.app', "python", '--args', "Buy_Main.py"]
        process = subprocess.Popen(cmd, shell=False)
        with open('buy_pid.txt', 'w') as f:
            f.write(str(process.pid))
        message = "구매봇을 실행합니다."
    
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    
    
def buy_bot_stop(update, context):
    if 'buy_pid.txt' not in os.listdir():
        message = "실행중인 구매봇이 없습니다."
    else:
        with open('buy_pid.txt', 'r') as f:
            pid = f.read()
        os.system('taskkill /f /pid ' + pid)
        os.remove('buy_pid.txt')
        message = "구매봇을 종료합니다."
        
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

    
def sell_bot_start(update, context):
    if 'sell_pid.txt' in os.listdir():
        message = "판매봇이 이미 실행중입니다."    
    else:
        cmd = ["open", '-W', '-a', 'Terminal.app', "python", '--args', "Sell_Main.py"]
        process = subprocess.Popen(cmd, shell=True)
        with open('sell_pid.txt', 'w') as f:
            f.write(str(process.pid))
        message = "판매봇을 실행합니다."
    
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    
    
def sell_bot_stop(update, context):
    if 'sell_pid.txt' not in os.listdir():
        message = "실행중인 판매봇이 없습니다."
    else:
        with open('sell_pid.txt', 'r') as f:
            pid = f.read()
        os.system('taskkill /f /pid ' + pid)
        os.remove('sell_pid.txt')
        message = "판매봇을 종료합니다."
        
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)




exit_handler = CommandHandler('exit', emergency_exit)
check_handler = CommandHandler('check', health_checker)
buy_start_handler = CommandHandler('buystart', buy_bot_start)
buy_stop_handler = CommandHandler('buystop', buy_bot_stop)
sell_start_handler = CommandHandler('sellstart', sell_bot_start)
sell_stop_handler = CommandHandler('sellstop', sell_bot_stop)

dispatcher.add_handler(check_handler)
dispatcher.add_handler(exit_handler)
dispatcher.add_handler(buy_stop_handler)
dispatcher.add_handler(buy_stop_handler)
dispatcher.add_handler(sell_stop_handler)
dispatcher.add_handler(sell_stop_handler)
updater.start_polling()