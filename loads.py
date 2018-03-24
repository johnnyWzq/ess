#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 24 12:13:52 2018

@author: zhiqiangwu
"""
import pandas as pd

class Loads():
    '''负载'''
    def __init__(self, load_type=1):
        '''负载类型
        '''
        self.load_type = load_type
        
    def loading_loads(self, data_file='data/loads.xls'):
        '''加载负载数据
        默认为load.xls
        '''
        #判断文件类型
        file_type = data_file[-4:]

        try:
            if file_type == '.xls':
                #读取负载数据，第一列为索引     
                self.load_data = pd.read_excel(data_file, index_col=0)
            elif file_type == '.csv':
                self.load_data = pd.read_csv(data_file, index_col=0, 
                                             nrows=500000, encoding='utf-8')
                print(self.load_data)
            else:
                print("文件格式错误！")
                
            if data_file == 'data/loads.xls':
             #根据负载类型，选择默认负载数据
                if self.load_type == 1:
                    self.load_data['power'] = self.load_data['type1']
                elif self.load_type == 2:
                    self.load_data['power'] = self.load_data['type2']
                elif self.load_type == 3:
                    self.load_data['power'] = self.load_data['type3']
                else:
                    self.load_data['power'] = self.load_data['type4']
                self.load_data = self.load_data['power']
            else: 
                self.load_data = self.load_volt_cur(self.load_data, 
                                                    v1='volt', c1='cur')
                self.load_data['power'] = self.calc_power(self.load_data)
                #获得负载中对功率、电压和电流值
                self.load_data = self.load_data[['power', 'volt', 'cur']]
                
        except:
            print("文件读取有误!")
        
                
    def abnormal_check(self):
        '''对数据进行初步探索'''
        statistics = self.load_data.describe()
        
        statistics.loc['range'] = statistics.loc['max']-statistics.loc['min'] #极差
        statistics.loc['var'] = statistics.loc['std']/statistics.loc['mean'] #变异系数
        statistics.loc['dis'] = statistics.loc['75%']-statistics.loc['25%'] #四分位数间距
        
        print(statistics)
    
    def load_volt_cur(self, load_data, v1=None, v2=None, v3=None,
                      c1=None, c2=None, c3=None):
        """读取电压电流值"""
      
        if v2 and v3 and c2 and c3:
            data = self.load_data[[v1, v2, v3, c1, c2, c3]]
        else:
            data = self.load_data[[v1, c1]]
        return data
        
    def calc_power(self, load_data):
        '''根据电压电流计算功率'''
        power =  load_data['volt'] * load_data['cur']
        return power
'''
test
'''
def main():
    load = Loads(3)
    load.loading_loads('data1.csv')
    print(load.load_data)
 #   load.abnormal_check()
    
if __name__ == '__main__':
    main()