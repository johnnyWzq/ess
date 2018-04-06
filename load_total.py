#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 27 08:53:26 2018

@author: zhiqiangwu
"""

import pandas as pd
import datetime
import time
import link_list as ll

class Loadtotal():
    
    def __init__(self, data_lens, col_num, l_name='L0', input_mode='in'):

        col_list = ['p'] * col_num
        for i in range(col_num):
            col_list[i] = 'p' + str(i+1)
        col_list.insert(0, l_name)
        col_list.insert(0, 'time')#增加时间列
        self.load_t = pd.DataFrame(index = range(data_lens), columns = col_list) #创建代表总负载的dataframe 
        self.col_list = col_list
        self.l_name = l_name
        self.load_ticks_max = data_lens
        self.load_t = self.load_t.fillna(0)
        
        #时间序列按采样周期赋值
        if data_lens <= 87600: #最高采样周期3600/h
            dlt = int(86400/data_lens)
            now_time = datetime.timedelta(seconds=1)
            tl = []
            for index in self.load_t.index:
                #tl.append(now_time)
                now_time = now_time + datetime.timedelta(seconds = dlt)
                t = str(now_time)               
                if t.find('1 day') != -1:
                    t = t.lstrip('1 day,')
                tl.append(t)
            self.load_t['time'] = tl
         
        self.initialize_dynamic_settings(col_num)
        self.input_mode = input_mode
        
    def initialize_dynamic_settings(self, chargers_num):
        '''初始化系统变量设置'''
        self.loads_link = ll.LinkList()
        self.chargers_iswork = [0] * (chargers_num + 1)#第一位为总负载
    #    self.load_regular = [1] * (chargers_num + 1)
        
    def loads_state_update(self, num, state):
        if state == True:
            self.chargers_iswork[num] = 1
        elif state == False:
            self.chargers_iswork[num] = 0
            
    def loads_value_update(self, ticks, **load_value):
        """
        从外部接口获取负载值，更新当前时刻的负载值，并添加进负载表
        
        """
        if self.input_mode == 'out':
            i = 1
            for num in self.chargers_iswork:
                if num == 1:
                    self.load_t.loc[i, [self.col_list[i+1]]] = load_value[i]
            self.load_t.loc[ticks, [self.l_name]] = load_value[0]
        return 
        
            
'''test'''


def main():
    df = Loadtotal(100, 4)
    print(df.load_t)

if __name__ == '__main__':
    main()