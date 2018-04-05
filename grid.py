#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 30 00:06:06 2018

@author: zhiqiangwu
"""

import pandas as pd
import datetime
import time

import file_process as fp

class Grid():
    
    def __init__(self, data_lens, **kwg):
        
        col_list = []
        col_list.insert(0, 'price_coe')
      #  col_list.insert(0, 'bills')
      #  col_list.insert(0, 'G0') 
        col_list.insert(0, 'time')#增加时间列
        self.grid_data = pd.DataFrame(index=range(data_lens), columns = col_list) #创建代表总电网侧的dataframe 
        self.col_list = col_list
        self.l_name = 'G0'
        self.load_ticks_max = data_lens
       # self.grid_data = self.grid_data.fillna(0)
        self.grid_data['price_coe'] = [1] * data_lens
        #变压器设置
        self.trans_cap = 350 #kw
        self.trans_rate = 0.8
        self.cap_limit = self.trans_cap * self.trans_rate       
        self.xtg = True #是否允许电网回馈

        #时间序列按采样周期赋值
        if data_lens <= 87600: #最高采样周期3600/h
            dlt = int(86400/data_lens)
            now_time = datetime.timedelta(seconds=1)
            tl = []
            self.time_list = []
            for index in self.grid_data.index:
                tl.append(now_time)
                now_time = now_time + datetime.timedelta(seconds = dlt)
                t = str(now_time)               
                if t.find('1 day') != -1:
                    t = t.lstrip('1 day,')
                t=time.strptime(t,'%H:%M:%S')            
                self.time_list.append(t)
            self.grid_data['time'] = tl
            
        for x in kwg:
            if x == 'cap':
                self.cap_nominal = kwg[x]
            if x == 'phase':
                self.phase = kwg[x]
            if x == 'volt':
                self.volt_nominal = kwg[x]
            if x == 'price':
                self.get_power_price_data(kwg[x])
        
    def get_power_price_data(self, price_data):
        """
        外部读取电价数据，暂要求表列名为‘price’，并且有h:m:s格式对时间列
        """
        i = 0
        j = 0
        index_list = []
        for time1 in self.time_list:
            time0 = price_data.loc[j, ['time']]
            time0 = time0[0]
            time0 = time.strptime(time0, '%H:%M:%S')
            if time1 > time0:
                index_list.append(i)
                j += 1
                if j >= len(price_data):
                    break
            i += 1 
        i = 0
        lens = len(index_list) - 1    
        for price in price_data['price']:
            if i >= lens:
                self.grid_data.loc[index_list[i]:, ['price_coe']] = price
                break
            self.grid_data.loc[index_list[i]:index_list[i+1], ['price_coe']] = price 
            i += 1
        price = self.grid_data.loc[len(self.grid_data)-1, ['price_coe']]
        self.grid_data.loc[0:index_list[0], ['price_coe']] = price[0]
        #self.grid_data['price_coe'] = prices
        
    def draw(self):
        fp.draw_plot(self.grid_data, figure_output='program_output/gird.jpg',
                     y_axis=self.l_name)#,x_axis='cur')
            
'''test'''


def main():
    p = fp.read_load_file(0,'data/price.xls')
    df = Grid(100, price = p, cap=1000, volt=380, phase=3)
    print(df.grid_data, df.cap_nominal, df.phase, df.volt_nominal)

if __name__ == '__main__':
    main()