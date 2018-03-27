#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 25 13:41:14 2018

@author: zhiqiangwu
"""
import time

import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import lagrange #导入拉格朗日插值函数
import math

def preprocess_data(data, sys_settings, col_sel=None, row_sel=None, 
                    v1=None, v2=None, v3=None,
                      c1=None, c2=None, c3=None):
    '''
    对外部对数据文件进行预处理
    处理内容包括：
    1、获取电压、电流值
    2、根据电压电流值计算出功率
    3、选出一个周期对数值
    4、对数据进行清洗
    '''
    if col_sel and row_sel:
        data = data[data[col_sel]== row_sel]

    load_data = get_pvc_data(data, row_sel)
    
    load_data = sel_period(load_data)
        
    load_data = deal_abnormal_data(load_data, sys_settings.calc_para)
    
    return load_data
'''   
 #补齐数据
    if len(load_data) < sys_settings.sample_interval:
        #利用插值补齐负载采样点
        load_data = complete_data(load_data, sys_settings.sample_interval, 
                                  data_key)
'''    
 #   return load_data

def get_pvc_data(data, row_sel=None):

#    load_data = load_volt_cur(data, v1='volt', c1='cur')
    data['power'] = calc_power(data, v1='volt', c1='cur')
    #获得负载中对功率、电压和电流值
    data = data[['time', 'power', 'volt', 'cur']]

    return data
      
def load_volt_cur(data, v1=None, v2=None, v3=None,
                      c1=None, c2=None, c3=None):
        """读取电压电流值"""
      
        if v2 and v3 and c2 and c3:
            load_data = data[['time', v1, v2, v3, c1, c2, c3]]
        else:
            load_data = data['time', [v1, c1]]
        return load_data
        
def calc_power(data, v1=None, v2=None, v3=None,
                      c1=None, c2=None, c3=None):
        '''根据电压电流计算功率'''
        if v2 and v3 and c2 and c3:
            print('Nan')
        else:
            power =  data['volt'] * data['cur']
        return power

def sel_period(data, index_col='time', interval=10, d_clip=2):
    '''
    选择一个周期对数据切片，
    时间间隔大于10分钟认为新对周期
    '''
    data = data.set_index([index_col])#将time设为index
    
    index = data.index[0]
    index_pre = index
    try:
        t_obj = time.strptime(index, "%Y/%m/%d %H:%M")
        t_stamp_pre = time.mktime(t_obj)
        index_list = [index]
        time_interval = 60 * interval
        #将字符串转换为时间戳并计算得到按时间划分对index
        for index in data.index:
            
            t_obj = time.strptime(index, "%Y/%m/%d %H:%M")
            t_stamp = time.mktime(t_obj)
            if (t_stamp - t_stamp_pre ) >= time_interval:
                index_list.append(index_pre)
                index_list.append(index)
            t_stamp_pre = t_stamp
            index_pre = index
    except:
        print("时间格式有误！")

    #选择第2个数据片
    d_clip %= 2 
    data_clip = data[index_list[2+d_clip]:index_list[3+d_clip]]

    return data_clip


def deal_abnormal_data(data, sel_col='power'):
    '''
    处理power对异常数值
    删除空值，并采用拉格朗日插值
    '''
    #过滤异常值，将高出正常值其变为空值，低于0置于0
    data[sel_col][data[sel_col] > 300000] = None
    data[sel_col][data[sel_col] < 0] = 0 
    #因为时间有重复，重设索引
    #data.reset_index() #无效？
    data['index'] = range(len(data))
    data = data.set_index(['index'])
    #逐个元素判断是否需要插值
    for j in range(len(data)):
        if (data[sel_col].isnull())[j]: #如果为空即插值。
            data[sel_col][j] = ployinterp_column(data[sel_col], j, 3)
    return data

def ployinterp_column(s, n, k=5):
    '''
    自定义列向量插值函数
    s为列向量，n为被插值的位置，k为取前后的数据个数，默认为5
    '''
    y = s[list(range(n-k, n)) + list(range(n+1, n+1+k))] #取数
    y = y[y.notnull()] #剔除空值
    return lagrange(y.index, list(y))(n) #插值并返回插值结果

def complete_data(data, sample_interval, sel_col):
    '''
    均匀补齐数据
    '''
            
            
    return data
def insert_data(data, sel_col, n):
    '''
    利用递归方式，采用拉格朗日方法均匀插入值
    '''
    data0 = data[:]
    if (n == 0):
        return data0
    else:
        data0['index'] = range(0, 2*len(data0), 2)      
        data0 = data0.set_index(['index'])
    
        df = pd.DataFrame(columns = [sel_col]) #创建代表总负载的dataframe 
        df['index'] = range(2*len(data0))
        df = df.set_index(['index'])
        
        df = pd.concat([data0, df], axis=1)
        #留下del_col列表中的数据
        df = df[sel_col]
    
       # s0 = result.loc[[0]]
        for i in range(2):
            s0 = df.iloc[:,i] #取指定列
            if s0[0] != None:
                df0 = s0
                break
    
        for j in range(len(df0)):
            if df0.values[j] > 120: #如果为空即插值。
                df0[j] = ployinterp_column(df0, j, 2)
        df = df0.to_frame()
                
        return insert_data(df, sel_col, n-1)
    
def del_data(data, sample_interval, sel_col):
    None

def reset_index(data, ticks):
    '''重设index'''
    data['index'] = range(ticks, len(data)+ticks)
    data = data.set_index(['index'])
    return data

def data_col_rename(data, n, re):
    data0 = data[:]#防止修改原实参，进行切片复制
    data0.rename(columns={n:re}, inplace=True)
    return data0

def data_merge(df1, df2, col_name, col_list):
    if col_name in df1.columns:
        df1 = df1.drop(col_name, 1)#删除指定列负载数据
    result = pd.concat([df1, df2], axis=1)
    #留下col_list列表中的负载数据
    result = result[col_list]
    result = result.fillna(0)
    return result

def data_del_col(df, col_name):
    df[col_name] = 0
    return df
    
def data_single_row_add(ticks, df, l_name, regularlist):
    n = 0
    d_sum = 0.0
    for i in df.iloc[ticks]:
        d_sum += i * float(regularlist[n])
        n += 1
    df.loc[ticks, [l_name]] = d_sum
    return df
    
class Datadiscovery():
    """对数据做简单探索"""
    
    def __init__(self, data=None):
        """定义数据探索值"""
        self.data = data

        
    def load_csv_flie(self, csv_file, limit=None):
        """
        加载csv文件，
        limit：读取文件行数
        """
        self.data = pd.read_csv(csv_file, nrows=limit)
    
    def load_xls_fils(self, xls_file, col=None):
        self.data = pd.read_excel(xls_file, index_col=col)
   #     data = pd.read_excel(xls_file, index_col=col)
        
    def abnormal_check(self):

        statistics = self.data.describe()
        
        statistics.loc['range'] = statistics.loc['max']-statistics.loc['min'] #极差
        statistics.loc['var'] = statistics.loc['std']/statistics.loc['mean'] #变异系数
        statistics.loc['dis'] = statistics.loc['75%']-statistics.loc['25%'] #四分位数间距
        
        #print(statistics)
        
        
    def draw_plot(self, commont_kinds, col, figure_output):
        data = self.data[col].copy()
        data.sort_values(ascending = False)
        
        plt.rcParams['font.sans-serif'] = ['SimHei'] #用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False #用来正常显示负号
        
        plt.figure()
        data.plot(kind = commont_kinds)
        unit = {'power':'kW', 'volt':'V', 'cur':'A', 'Lo':'kW'}
        plt.ylabel(col + '(' + unit[col] + ')')
#        data.plot(style = '-o', linewidth = 2)
        
        plt.savefig(figure_output + col +'.jpg', dpi=100)
        plt.show()