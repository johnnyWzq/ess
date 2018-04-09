#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 25 13:41:14 2018

@author: zhiqiangwu
"""
import time
import numpy as np
import pandas as pd
import file_process as fp

from scipy.interpolate import lagrange #导入拉格朗日插值函数
import math

def preprocess_data(data, sys_settings, is_pro, col_sel=None, row_sel=None, 
                    v1=None, v2=None, v3=None,
                      c1=None, c2=None, c3=None):
    '''
    对数据文件进行预处理
    处理内容包括：
    1、获取电压、电流值
    2、根据电压电流值计算出功率
    3、选出一个周期对数值
    4、对数据进行清洗
    '''
    if is_pro == True:
        if col_sel and row_sel:
            data = data[data[col_sel]== row_sel]
    
        load_data = get_pvc_data(data, row_sel)
        
        load_data = sel_period(load_data)
            
        load_data = deal_abnormal_data(load_data, sys_settings.calc_para)
    else:
        load_data = data
        
    #补齐数据
    if len(load_data) < sys_settings.sample_interval:
        #利用插值补齐负载采样点
        load_data = complete_data(load_data, sys_settings.sample_interval, 
                                  sys_settings.calc_para)
    else:
        #过滤掉数据
        load_data = filter_data(load_data, sys_settings.sample_interval, 
                                  sys_settings.calc_para)
    return load_data

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
            fp.output_msg('Nan')
        else:
            power =  (data['volt'] * data['cur']) / 1000
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
        fp.output_msg("时间格式有误！")

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
    #计算要翻倍数据的次数
    num = math.log((sample_interval/len(data)), 2)
    a = [1, 2, 3, 4, 5, 6, 7, 8]
    if num in a:
        num = int(num)
    else:
        num = int(num) + 1
    if num < len(a): # 7200sample_interval
        data = insert_data(data, sel_col, num)
        if len(data) > sample_interval:#超出,删除超出的后面数据部分
            data = data[0:sample_interval]
    else:
        fp.output_msg("Error, the data is too big!")
    return data

def filter_data(data, sample_interval, sel_col):
    '''
    计算要压缩数据的次数
    但是为了不必要的程序开销，压缩后数据均会比目标大，大的部分直接去掉
    '''
    num = int(math.log((len(data)/sample_interval), 2))

    if num < 8: # 最多删减8次
        data = delete_data(data, sel_col, num)
        if len(data) > sample_interval:#超出,删除超出的后面数据部分
            data = data[0:sample_interval]
    else:
        fp.output_msg('the data is too small!')
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
            if  np.isnan(df0.values[j]): #如果为空即插值。
                df0[j] = ployinterp_column(df0, j, 2)
        df = df0.to_frame()
                
        return insert_data(df, sel_col, n-1)

def delete_data(data, sel_col, n):
    '''
    均匀删除数据,删除偶数行
    '''
    #确定数据行为偶数
    if int(len(data)/2) == 1:
        data0 = data[0:-1]
    else:
        data0 = data[:]
        
    if (n == 0):
        return data0
    else:
        #按偶数行删除
        l = list(range(0, len(data0), 2))
        data0 = data0.drop(l)
        data0['index'] = range(len(data0))
        data0 = data0.set_index(['index'])
    return delete_data(data0, sel_col, n-1)

def reset_index(data, ticks):
    '''重设index'''
    data['index'] = range(ticks, len(data)+ticks)
    data = data.set_index(['index'])
    return data

def data_col_rename(data, n, re):
    data0 = data[:]#防止修改原实参，进行切片复制
    data0.rename(columns={n:re}, inplace=True)
    return data0

def data_merge(df1, df2, **kwg):
    select = 0
    value = None
    for x in kwg:
        if x == 'col_name':
            col_name = kwg[x]
            if col_name in df1.columns:
                if df2.index[0] > 0:
                    value = df1.loc[0:df2.index[0]-1, [col_name]]
                df1 = df1.drop(col_name, 1)#删除指定列负载数据
        if x == 'col_list':
            col_list = kwg[x]
            select = 1
    result = pd.concat([df1, df2], axis=1)
    if select == 1:
        #留下col_list列表中的负载数据
        result = result[col_list]
    result = result.fillna(0)
    result.loc[0:df2.index[0]-1, [col_name]] = value
    return result

def data_del_col(ticks, df, col_name):
    df.loc[ticks:, [col_name]] = 0
    return df
    
def data_single_row_add(ticks, df, l_name):
    n = 0
    d_sum = 0.0
    #df0 = df[:].fillna(0)
    df0 = df.drop('time', 1)
    if ticks <= len(df0):
        for i in df0.iloc[ticks]:
            d_sum += i
            n += 1
        df0.loc[ticks, [l_name]] = d_sum
    df0['time'] = df['time']
    return df0
"""
def data_single_row_add(ticks, df, **kwg):
    n = 0
    d_sum = 0.0
    select0 = 0
    select1 = 0
    select2 = 0
    df0 = df[:]
    for x in kwg:
        if x == 'sum_name':
            sum_name = kwg[x]
        if x == 'del_col':
            del_col = kwg[x]
            df0 = df0.drop(del_col, 1)
            select0 = 1
        if x == 'regularlist':
            regularlist = kwg[x]
            select1 = 1
        if x == 'add_col':
            add_col = kwg[x]
            select2 = 1
    if ticks <= len(df0):
        if select1 == 1:
            for i in df0.iloc[ticks]:
                d_sum += i * float(regularlist[n])
                n += 1
        elif select2 == 1:
            df0 = df0[add_col]
            for i in df0.iloc[ticks]:
                d_sum += i
                n += 1
        df0.loc[ticks, [sum_name]] = d_sum
    if select0 ==1:
        df0[del_col] = df[del_col]
    return df0
"""
   
def dfs_col_add(ticks, data1, data2, add1_col, add2_col):
    s1 = data1.loc[ticks, [add1_col]]
    s2 =  data2.loc[ticks, [add2_col]]
    data1.loc[ticks, [add1_col]] = s1[0] + s2[0]
    return data1

def dfs_unit_limit(ticks, data, l_col, limit):
    s1 = data.loc[ticks, [l_col]]
    if s1[0] > limit:
        data.loc[ticks, [l_col]] = limit
    return data
    
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
        
        print(statistics)