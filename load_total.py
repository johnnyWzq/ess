#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 27 08:53:26 2018

@author: zhiqiangwu
"""

import pandas as pd
import datetime

class Loadtotal():
    
    def __init__(self, data_lens, col_num, l_name='Lo'):

        col_list = ['p'] * col_num
        for i in range(col_num):
            col_list[i] = 'p' + str(i+1)
        col_list.insert(0, l_name)
        col_list.insert(0, 'time')#增加时间列
        self.load_t = pd.DataFrame(columns = col_list) #创建代表总负载的dataframe 
        self.col_list = col_list
        self.l_name = l_name
        self.load_ticks_max = data_lens
        self.load_t['index'] = range(data_lens)
        self.load_t = self.load_t.set_index(['index'])
        self.load_t = self.load_t.fillna(0)
        
        #时间序列按采样周期赋值
        if data_lens <= 87600: #最高采样周期3600/h
            dlt = float(86400/data_lens)
            now_time = datetime.timedelta(seconds=1)
            tl = []
            for index in self.load_t.index:
                tl.append(now_time)
                now_time = now_time + datetime.timedelta(seconds = dlt)
            
            self.load_t['time'] = tl
'''   
    def initialize_dynamic_settings(self):
        """初始化系统变量设置"""

        self.charges_iswork = [0] * (self.chargers_num + 1)#第一位为总负载
        self.load_regular = [1] * (self.chargers_num + 1)
        
    def update_settings(self, num, state='on'):
        if state == 'on':
            self.charges_iswork[num] = 1
        elif state == 'off':
            self.charges_iswork[num] = 0
 '''           
            
'''test'''


def main():
    df = Loadtotal(100, 4)
    print(df.load_t)

if __name__ == '__main__':
    main()