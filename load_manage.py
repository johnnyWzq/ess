#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 20:14:43 2018

@author: zhiqiangwu
"""
import data_preprocessing as dp

def loads_work(sys_ticks, sys_settings, load_pre, load, load_regular):
    """
    计算负载当前时刻值，放入load_pre中并返回
    sys_ticks为系统运行至当前采样数
    load_pre为当前时刻前的负载数据集
    load为当前时刻加载的负载
    load_regular为负载调整指令集
    """
    if sys_settings.charges_iswork[load.load_num - 1] == 0:
        #在当前时刻为新的负载,可以加载，并更新sys
        sys_settings.charges_iswork[load.load_num -1 ] = 1
        #按当前时刻重设data的index，使得合并dataframe时行能对应
        load_data = dp.reset_index(sys_ticks, load.load_data)
        #按负载编号重命名数据calc_para列
        load_data = dp.data_col_rename(load_data, 
                               sys_settings.calc_para, 'p'+str(load.load_num))
        #与load_pre合并
    

    #更新load_pre后返回
    return 
