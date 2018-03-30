# -*- coding: utf-8 -*-
"""
Created on Fri Mar 30 14:50:16 2018

@author: wuzhiqiang
"""
import pandas as pd
import scipy.signal

import file_process as fp
import data_preprocessing as dp
import sys_control as sc

class FittingDevice():
    
    def __init__(self, data_lens):
        
        self.fitting = False
        col_list = []
        col_list.insert(0, 'Ebxn')
        col_list.insert(0, 'price_coe')
        col_list.insert(0, 'bills')
        col_list.insert(0, 'Gn') 
   #     col_list.insert(0, 'time')#增加时间列
        self.data = pd.DataFrame(columns = col_list) #创建代表拟合器输出的dataframe 
        self.col_list = col_list
        self.g_name = col_list[0]
        self.e_name = col_list[3]
        self.load_ticks_max = data_lens
        self.data['index'] = range(data_lens)
        self.data = self.data.set_index(['index'])
        self.data = self.data.fillna(0)
        self.data['price_coe'] = [1] * data_lens
 
    def input_conditon(self, **kwg):
        for x in kwg:
            if x == 'sys_s':
                sys_s = kwg[x]
                self.cap_limit = sys_s.cap_limit
            if x == 'ebx':
                ebx = kwg[x]
                self.ebx = ebx
            if x == 'price':
                self.data['price_coe'] = kwg[x]
        

    def set_targe(self, targe):
        self.targe = targe
            
    def fitting(self, data, col_name):
        l0 = data[:]
        l0 = l0[[col_name]]
        if self.targe == 'day_cost':
            g0 = self.day_cost_algorithm(self, l0)
            self.data[self.col_list] = g0[self.col_list]
            
    def day_cost_algorithm(self, data):
        """
        进行计算，并将计算结果分别放入self.data的Gn，L0,En,bills中
        """
        df = dp.data_merge(self.data, data) #将表合并到df中
        #计算L0和*price, 先计算能量，对l0积分，然后在乘以price，因为price是系数，
       # 经过公式变化L0和*price等效于L0*price
        '''
        cost0 = 0
        c = df['L0'] * df['price_coe']
        for i in c:
            cost0 += i
        print('the original cost is :' + str(cost0))
        '''
        c = df['L0']
        d = df['price_coe']
        e = scipy.signal.convolve(c, d)
        print(e)
        return df
        
        
        
    def draw(self):
        fp.draw_plot(self.data, figure_output='program_output/gird.jpg',
                     y_axis=self.l_name)#,x_axis='cur')
            
'''test'''


def main():
    df = FittingDevice(250)
    df0 = pd.read_excel('data/model.xls', index_col=0)
    df0 = df0.fillna(0)
    p = df0['price_coe']
    l = df0['L0']
    df.input_conditon(ebx=2, price=p)
    df.set_targe('day_cost')
    df.day_cost_algorithm(l)
    print(df.data)
    print(df.ebx, df.price, df.targe)

if __name__ == '__main__':
    main()