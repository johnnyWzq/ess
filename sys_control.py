#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 20:14:43 2018

@author: zhiqiangwu
"""

import data_preprocessing as dp

        
def loads_calc(sys_ticks, load_pre_data, l_name, load_regular):
    '''
    计算当前时刻值行的总负载值，并返回负载集
    使用方式：按指定的频率循环调用
    sys_ticks为系统运行至当前采样数,待计算行
    load_pre为当前时刻前的负载数据
    load_regular为负载调整指令集
    '''
    data = dp.data_single_row_add(sys_ticks, load_pre_data, l_name, load_regular)
    return data



'''test'''



def main():
    
    import pandas as pd

    df1 = pd.read_excel('data/blank.xls', index_col=0)
    df1.rename(columns={'power':'p1'}, inplace=True)
    
    df2 = pd.read_excel('data/model.xls', index_col=0)
    df2 = df2[['power']]
    df2 = dp.reset_index(df2, 10)
    p = 'power'
    df2 = dp.data_col_rename(df2, p, 'p'+str(2))#df2.rename(columns={'power':'p2'}, inplace=True)
    q = ['p1', 'p2']
    df1 = dp.data_merge(df1, df2, 'volt', q)
    df1 = loads_calc(12, df1, 'p1', [1,2])
    
    print(df1)

if __name__ == '__main__':
    main()