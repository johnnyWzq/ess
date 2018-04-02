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
    data = dp.data_single_row_add(sys_ticks, load_pre_data, 
                                          l_name, load_regular)
    return data

def grid_calc(sys_ticks, grid_data, load_data, **kwg):
    '''
    计算当前时刻值行的电网侧输出功率值，并计算截止到当前时刻合计的电费
    使用方式：按指定的频率循环调用
    sys_ticks为系统运行至当前采样数,待计算行

    '''
    for x in kwg:
        if x == 'add1_col':
            add1_col = kwg[x] #被计算量，当前代表电网功率的grid
        if x == 'add2_col':
            add2_col = kwg[x]
        if x == 'sys_s':
            sys_settings = kwg[x]
    grid_data = dp.dfs_col_add(sys_ticks, grid_data, load_data, add1_col, add2_col)
    grid_data = grid_limit(sys_ticks, grid_data, limit_col=add1_col, sys_s=sys_settings)
    return grid_data


def grid_limit(sys_ticks, grid_data, **kwg):
    """
    考虑配电侧参数限制，在根据负载计算出来的grid_data基础上进行处理
    """
    for x in kwg:
        if x == 'sys_s':
            sys_s = kwg[x]
            grid_cap = sys_s.cap_limit
        if x == 'limit_col':
            limit_col = kwg[x]
    return (dp.dfs_unit_limit(sys_ticks, grid_data, limit_col, grid_cap))

def day_cost_algorithm(data1, data2):
    """
    进行计算，并将计算结果分别放入data1，data2的第一列
    """


'''test'''



def main():
    
    import pandas as pd

    df1 = pd.read_excel('data/blank.xls', index_col=0)
    df1.rename(columns={'power':'grid'}, inplace=True)
    
    df2 = pd.read_excel('data/model.xls', index_col=0)
    df2 = df2[['power']]
   # df2 = dp.reset_index(df2, 10)
    p = 'power'
    df2 = dp.data_col_rename(df2, p, 'p'+str(2))#df2.rename(columns={'power':'p2'}, inplace=True)
    df2 = df2[0:19]
    q = ['p1', 'p2']
   # df1 = dp.data_merge(df1, df2, 'volt', q)
    df1 = grid_calc(12, df1, df2)
    
    print(df1)

if __name__ == '__main__':
    main()