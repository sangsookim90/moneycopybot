import pandas as pd 
import numpy as np

class Valid_Checker(): 
    def __init__(self): 
        pass
    
    ### 장기로 Trend up
    def check_trend_up(self, df, up_trend_ratio = 1.02):
        boolean = df['close'].iloc[-1] > df['close'].iloc[0] * up_trend_ratio
        return boolean 
    
    ### 극소값에서 산다.
    def check_local_minimum_point(self, df, window_size = 0, downsize = 3, upsize = 1): 
        if window_size == 0 : 
            df['target_col'] = df['close']
        else : 
            df['target_col'] = df['close'].rolling(window=window_size).mean() 
        df = df.dropna(axis = 0)
        start_idx = -downsize-upsize-1
        boolean = True
        ### Down Stream
        for i in range(0, downsize-1): 
            boolean = boolean and (df['target_col'].iloc[start_idx+(i+1) ] < df['target_col'].iloc[start_idx + i])
        boolean = boolean and (df['target_col'].iloc[-upsize-1] * 1.005 < df['target_col'].iloc[-upsize-2])
        ### Up Stream
        for i in range(0, upsize):
            boolean = boolean and (df['target_col'].iloc[-upsize+i] > df['target_col'].iloc[-upsize+i-1])
        return boolean 
            
        
        
    ### 극대값에서 판다. 익절한다.
    def check_down_point_short(self, df, avg_buy_price, window_size=0, downsize=3, ikjeol_ratio = 1.03):
        if window_size == 0 : 
            df['target_col'] = df['close']
        else : 
            df['target_col'] = df['close'].rolling(window=window_size).mean() 
        df = df.dropna(axis = 0)
        boolean = True
        
        boolean = boolean and (df['target_col'].iloc[-5] < df['target_col'].iloc[-4])
        boolean = boolean and (df['target_col'].iloc[-4] > df['target_col'].iloc[-3])
        boolean = boolean and (df['target_col'].iloc[-2] > df['target_col'].iloc[-3])
        boolean = boolean and (df['target_col'].iloc[-1] > df['target_col'].iloc[-2])
        
        boolean = boolean and (df['target_col'].iloc[-1] > avg_buy_price*ikjeol_ratio)
        return boolean 
    
    
    ### 손해가 얼만큼 이상 났을 때 판다 .
    def check_loss_limit(self, df, avg_buy_price, loss_ratio=0.90):    
        return df['close'].iloc[-1] < avg_buy_price * loss_ratio
        
    
    ### 이득이 얼만큼 이상 났을 때 판다. 
    def check_benefit_limit(self, df, avg_buy_price, benefit_limit = 1.12): 
        return df['close'].iloc[-1] > avg_buy_price*benefit_limit
    
    
    def check_mid_term_trend(self, df, up_trend_ratio = 1.01) : 
        boolean = df['close'].iloc[-1] > df['close'].iloc[24] * up_trend_ratio
        return boolean
    
        
        
    def check_oscilator_up(self, df, windows = [12,5,3]):
        df['ma{0}'.format(windows[0])] = None
        df['ma{0}'.format(windows[0])] = df['close'].rolling(window = windows[0]).mean()
        
        df['ma{0}'.format(windows[1])] = None
        df['ma{0}'.format(windows[1])] = df['close'].rolling(window = windows[1]).mean()
        
        df['MACD']= df['ma{0}'.format(windows[1])]-df['ma{0}'.format(windows[0])]
        df['SIGNAL']= df['MACD'].rolling(window=windows[2]).mean() 
        df['Oscillator'] = df['MACD'] - df['SIGNAL']
        
        
        ### 0보다 크면 상승국면이니깐 파는 시기 - 극대점일 때 팔거임
        ### 0보다 작으면 하강국면이니까 사는 시기 - 극소점일 때 살거임
        
        boolean = df['Oscillator'].iloc[-1] > 0 
        
        return boolean
        
        
    def check_oscilator_diff(self, df, windows = [12,5,3]):
        df['ma{0}'.format(windows[0])] = None
        df['ma{0}'.format(windows[0])] = df['close'].rolling(window = windows[0]).mean()
        
        df['ma{0}'.format(windows[1])] = None
        df['ma{0}'.format(windows[1])] = df['close'].rolling(window = windows[1]).mean()
        
        df['MACD']= df['ma{0}'.format(windows[1])]-df['ma{0}'.format(windows[0])]
        df['SIGNAL']= df['MACD'].rolling(window=windows[2]).mean() 
        df['Oscillator'] = df['MACD'] - df['SIGNAL']
        
        
        ### 0보다 크면 상승국면이니깐 파는 시기 - 극대점일 때 팔거임
        ### 0보다 작으면 하강국면이니까 사는 시기 - 극소점일 때 살거임
    
        boolean = (df['Oscillator'].iloc[-1] - df['Oscillator'].iloc[-2]) > 0 
        
        return boolean

    
    def get_di(self, df, window = 10):
        df['PDM'] = 0
        df['MDM'] = 0
        df['TR'] = 0
        for i in range(1,df.shape[0]) : 
            tdVar = df.iloc[i]['high'] - df.iloc[i-1]['low']
            ydVar = df.iloc[i-1]['high'] - df.iloc[i-1]['low']
            upMove = df.iloc[i]['high'] - df.iloc[i-1]['high']
            downMove = df.iloc[i-1]['low'] - df.iloc[i]['low']


            if upMove > downMove and upMove > 0 : 
                df['PDM'].iloc[i] = upMove
            else : 
                df['PDM'].iloc[i] = 0 

            if downMove > upMove and downMove > 0 : 
                df['MDM'].iloc[i] = downMove 
            else : 
                df['MDM'].iloc[i] = 0

            tr = max(abs(df.iloc[i]['high'] - df.iloc[i]['low']), abs(df.iloc[i]['high'] - df.iloc[i-1]['close']), abs(df.iloc[i]['low'] - df.iloc[i-1]['close']))        
            df['TR'].iloc[i] = tr


        df['PDM_MA_{0}'.format(window)] = df['PDM'].rolling(window = window).mean()
        df['MDM_MA_{0}'.format(window)] = df['MDM'].rolling(window = window).mean()
        df['TR_MA_{0}'.format(window)] = df['TR'].rolling(window = window).mean()

        df['PDI'] = df['PDM_MA_{0}'.format(window)] / df['TR_MA_{0}'.format(window)]
        df['MDI'] = df['MDM_MA_{0}'.format(window)] / df['TR_MA_{0}'.format(window)]
        df['ADX'] = np.abs(df['PDI'] - df['MDI']) / (df['PDI'] + df['MDI'])

        return df

    
    def check_adx_up(self, df, window = 10, adx_th_lower = 0.3, adx_th_higher = 0.5):
        data = self.get_di(df, window) 
        boolean = (data['ADX'].iloc[-1] > data['ADX'].iloc[-3]) 
        boolean = boolean and  (data['MDI'].iloc[-1] < data['PDI'].iloc[-1]) 
        boolean = boolean and (data['ADX'].iloc[-1] > adx_th_lower) 
        boolean = boolean and (data['ADX'].iloc[-1] < adx_th_higher)
        
        return boolean 
    
    
    
    
    
    
    def check_band_center_up(self,df) : 
        df['ma20'] = df['close'].rolling(window=20).mean() 
        diff_1 = df['ma20'].iloc[-1]- df['ma20'].iloc[-6]
        diff_2 =  df['ma20'].iloc[-6] - df['ma20'].iloc[-11]
        df['ma30']= df['close'].rolling(window=30).mean() 
        boolean = (diff_1 > diff_2) and (df['ma30'].iloc[-1] - df['ma30'].iloc[-2] > 0)
        return boolean 
    
    
    
    def check_extreme_up(self, df ):
        
        window = 10
        df['ewm{0}'.format(window)] = None
        df['ewm{0}'.format(window)] = df.ewm(span = window,adjust=False).mean()
        boolean = df['ewm10'].iloc[-2] * 2  < df['close'].iloc[-1]
        return boolean
    
    ### 단기 변동성 돌파 전략(래리 윌리엄스, Larry R. Williams)
    def check_wiliams_buy():
        
        
        return
    def check_wiliams_sell():
        return 
        