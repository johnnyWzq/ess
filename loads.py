#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 24 12:13:52 2018

@author: zhiqiangwu
"""
import pandas as pd
from data_preprocessing import Datadiscovery
import data_preprocessing as dp
from ess_settings import Settings


class Loads():
    '''负载'''
    def __init__(self, sys_settings, load_type=1):
        '''负载类型
        '''
        self.load_type = load_type
        self.sys_settings = sys_settings
        
    def loading_loads(self, data_file='data/loads_model.xls'):
        '''加载负载数据
        默认为load.xls
        '''
        #判断文件类型
        file_type = data_file[-4:]

        try:
            #如果是预设的数据
            if data_file == 'data/loads_model.xls':
                self.load_data = pd.read_excel(data_file, index_col=0)
             #根据负载类型，选择默认负载数据
                if self.load_type == 1:
                    self.load_data['power'] = self.load_data['type1']
                elif self.load_type == 2:
                    self.load_data['power'] = self.load_data['type2']
                elif self.load_type == 3:
                    self.load_data['power'] = self.load_data['type3']
                else:
                    self.load_data['power'] = self.load_data['type4']
                self.load_data = self.load_data[['power']]
            else: 
                #加载数据文件，并进行预处理
            
                if file_type == '.xls':
                   #读取负载数据，第一列为索引     
                   data = pd.read_excel(data_file, index_col=0)
                   #读取负载数据，自动索引
                   #data = pd.read_excel(data_file)
                elif file_type == '.csv':
                    #只读取65535条数据
                    data = pd.read_csv(data_file,index_col=0, 
                                                 nrows=65535, encoding='utf-8')
                    #对数据进行预处理
                    self.load_data = dp.preprocess_data(data, self.sys_settings,
                                col_sel='BMS编号', row_sel='010101030613001F')
                #print(self.load_data)
                else:
                    print("文件格式错误！")
        except:
            print("文件读取错误！")
'''            
def loads_calc(sys_ticks, load_pre, load_list, load_regular):
    """
    计算负载当前时刻值，并返回
    sys_ticks为系统运行至当前采样数
    load_pre为当前时刻前的负载数据
    load_regular为负载调整指令集
    """
    i = 0
    for load in load_list:
        #将列表里的负载当前时刻的数据进行相加
        load_data[i++] = load.load_data['power']
 '''       
'''
test
'''
def main():

    sys_settings = Settings()
    load = Loads(sys_settings)
    file_input = 'data_temp/charging_data1.csv'
    file_output = 'data/charging_data.xls'
    figure_output = 'data/charging_data_'
    load.loading_loads(file_input)
    print(load.load_data)
    load.load_data.to_excel(file_output)
    dd = Datadiscovery(load.load_data)
    dd.abnormal_check()

    dd.draw_plot('line', u'power', figure_output)
    
'''
    for i in range(len(common_kinds)):
        dd.draw_plot(common_kinds[i], u'power')
'''
  #  dd.draw_plot('line', u'power')
    
if __name__ == '__main__':
    main()