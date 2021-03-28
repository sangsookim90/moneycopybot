import numpy as np
import pandas as pd


class VolatilityChecker():
    def __init__(self): 
        pass
    

    def check_buy_point(self, df_minute, df_hours):
        df_minute['ma3'] = df_minute['close'].rolling(window=3).mean()
        cur_price = df_minute.iloc[-1]['ma3']
        buy_price = df_hours.loc[df_hours.index <= df_minute.index[-1], 'buy_price'].iloc[-1]
        if cur_price > buy_price : 
            return True
        return False
    

    def get_target_df_hours(self, df_hours, tick, base):
        hour_targets = [base + x for x in range(0, 25-base, tick)]
        df_hours['buy_price'] = None
        for i in range(df_hours.shape[0]): 
            df_hours['buy_price'].iloc[i] = (df_hours['high'].iloc[i-tick:i, ].max() - df_hours['low'].iloc[i-tick:i].min())/2 + df_hours['open'].iloc[i]    
        return df_hours.loc[df_hours.index.hour.isin(hour_targets), :].dropna(axis = 0)
    
    
    def check_sell_point(self, df_minute, tick, base):
        hour_targets = [base + x for x in range(0, 25-base, tick)]
        if df_minute.index.hour[-1] in hour_targets and df_minute.index.minute[-1] == 0 : 
            return True
        return False
    

    def check_extreme_down(self, df_minute): 
        return (df_minute.iloc[-1]['close'] - df_minute.iloc[-2]['close']) / df_minute.iloc[-2]['close'] < -0.1
        

    ### rsi 출력은 임시조치, 수정 예정
    def check_buy_rsi(self, df_minute, rsi_jump=14, lower_limit=0.3):
        df_minute['diff'] = None
        for i in range(1, df_minute.shape[0]) :
            df_minute['diff'].iloc[i] = df_minute['close'].iloc[i] - df_minute['close'].iloc[i-1] 
        df_minute['RSI'] = None
        for i in range(1+rsi_jump, df_minute.shape[0]) :
            diff = df_minute['diff'].iloc[i+1-rsi_jump:i+1]
            df_minute['RSI'].iloc[i] = np.sum(np.where(diff > 0, diff, 0) ) / np.sum(np.abs(diff))
#         return (df_minute['RSI'].iloc[-1] > lower_limit) and (df_minute['RSI'].iloc[-2] < lower_limit)
        return df_minute['RSI']
    
    
    def check_sell_rsi(self, df_minute, rsi_jump=14, upper_limit=0.7):  
        df_minute['diff'] = None
        for i in range(1, df_minute.shape[0]) :
            df_minute['diff'].iloc[i] = df_minute['close'].iloc[i] - df_minute['close'].iloc[i-1] 
        df_minute['RSI'] = None
        for i in range(1+rsi_jump, df_minute.shape[0]) :
            diff = df_minute['diff'].iloc[i+1-rsi_jump:i+1]
            df_minute['RSI'].iloc[i] = np.sum(np.where(diff > 0, diff, 0) ) / np.sum(np.abs(diff))
        
#         boolean = df_minute['RSI'].iloc[-2] > upper_limit 
#         boolean = boolean and  df_minute['RSI'].iloc[-2] >= df_minute['RSI'].iloc[-3] 
#         boolean = boolean and df_minute['RSI'].iloc[-1] <= df_minute['RSI'].iloc[-2] 
#         return boolean
#         print([df_minute['RSI'].iloc[-1], df_minute['RSI'].iloc[-2]])
#         return (df_minute['RSI'].iloc[-1] < upper_limit) and (df_minute['RSI'].iloc[-2] > upper_limit)
        return df_minute['RSI']


    def check_bollinger(self, df_days):
        b_window = 20
        rolling_frame = df_days['close'].rolling(b_window)
        df_days['bollinger_mid'] = rolling_frame.mean()
        df_days['bollinger_upper'] = rolling_frame.mean() + 2 * rolling_frame.std()
        df_days['bollinger_lower'] = rolling_frame.mean() - 2 * rolling_frame.std()

        boolean = (df_days['close'].iloc[-1] < df_days['bollinger_upper'].iloc[-1])
        boolean = boolean and (df_days['close'].iloc[-2] < df_days['bollinger_upper'].iloc[-2])
        
        return boolean 