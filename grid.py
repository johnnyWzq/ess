#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 30 00:06:06 2018

@author: zhiqiangwu
"""

import pandas as pd
import datetime

import file_process as fp

class Grid():
    
    def __init__(self, data_lens, **coe):
        
        col_list = []
        col_list.insert(0, 'price_coe')
        col_list.insert(0, 'bills')
        col_list.insert(0, 'grid') 
        col_list.insert(0, 'time')#增加时间列
        self.grid_data = pd.DataFrame(columns = col_list) #创建代表总电网侧的dataframe 
        self.col_list = col_list
        self.l_name = 'grid'
        self.load_ticks_max = data_lens
        self.grid_data['index'] = range(data_lens)
        self.grid_data = self.grid_data.set_index(['index'])
        self.grid_data = self.grid_data.fillna(0)
        self.grid_data['price_coe'] = [1] * data_lens
           
        #时间序列按采样周期赋值
        if data_lens <= 87600: #最高采样周期3600/h
            dlt = float(86400/data_lens)
            now_time = datetime.timedelta(seconds=1)
            tl = []
            for index in self.grid_data.index:
                tl.append(now_time)
                now_time = now_time + datetime.timedelta(seconds = dlt)
            
            self.grid_data['time'] = tl
            
        for c in coe:
            if c == 'cap':
                self.cap_nominal = coe[c]
            if c == 'phase':
                self.phase = coe[c]
            if c == 'volt':
                self.volt_nominal = coe[c]
            if c == 'price_coe':
                self.get_power_bills_data()
        
    def get_power_bills_data(self, **kwg):
        self.grid_data['price_coe'] = [1] * self.data_lens
        
    def draw(self):
        fp.draw_plot(self.grid_data, figure_output='program_output/gird.jpg', y_axis='grid')#,x_axis='cur')
            
'''test'''


def main():
    df = Grid(100, cap=1000, volt=380, phase=3)
    print(df.grid_data, df.cap_nominal, df.phase, df.volt_nominal)

if __name__ == '__main__':
    main()