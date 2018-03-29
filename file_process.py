# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 10:44:46 2018

@author: wuzhiqiang
"""

import pandas as pd
import matplotlib.pyplot as plt

def read_load_file(load_type, data_file='data/loads_model.xls', rows_num=65535):
    '''读取负载数据文件
    支持xls和csv格式，默认读取数据65535条
    返回dataframe
    '''
    #如果是预设的数据
    if data_file == 'data/loads_model.xls':
        try:
            data = pd.read_excel(data_file, index_col=0)
        except:
            deal_err('文件读取失败！')
            return None
        #根据负载类型，选择默认负载数据
        if load_type == 1:
            data['power'] = data['type1']
        elif load_type == 2:
            data['power'] = data['type2']
        elif load_type == 3:
            data['power'] = data['type3']
        else:
            data['power'] = data['type4']
            
        data = data[['power']]
    else: 
        
        #加载数据文件
        try:
            file_type = data_file[-4:]
            if file_type == '.xls':
               #读取负载数据，第一列为索引     
               data = pd.read_excel(data_file)#, index_col=0)
               #读取负载数据，自动索引
               #data = pd.read_excel(data_file)
            elif file_type == '.csv':
                #只读取65535条数据
                data = pd.read_csv(data_file,#index_col=0, 
                                                 nrows=rows_num, encoding='utf-8')
            else:
                deal_err('文件格式不支持!')
        except:
            deal_err('文件读取失败！')
            return None

    return data

def write_load_file(data, data_file='data_load/loads.csv'):
    
    file_type = data_file[-4:]
    try:
        if file_type == '.csv':
            data.to_csv(data_file)
        elif file_type == '.xls':
            data.to_excel(data_file)
        else:
            deal_err('文件格式有误！')
    except:
        deal_err('文件保存失败！')
'''
def draw_plot(data, commont_kinds, x_col, col_name, figure_output='data_load/loads.jpg'):

    data = data[col_name].copy()
    data.sort_values(ascending = False)
    
    plt.rcParams['font.sans-serif'] = ['SimHei'] #用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False #用来正常显示负号
    
    plt.figure()
    data.plot(kind = commont_kinds)
    unit = {'power':'kW', 'volt':'V', 'cur':'A', 'Lo':'kW'}
    plt.ylabel(col_name + '(' + unit[col_name] + ')')
#        data.plot(style = '-o', linewidth = 2)
    
    plt.savefig(figure_output, dpi=100)
    plt.show()       
    
 '''
def draw_plot(data, y_col, x_col=None, figure_output='data_load/loads.jpg'):
    unit = {'power':'kW', 'volt':'V', 'cur':'A', 'Lo':'kW', 'time':''}
    y_axis = data[y_col].copy()
    y_axis.sort_values(ascending = False)
        
    plt.rcParams['font.sans-serif'] = ['SimHei'] #用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False #用来正常显示负号
    
    plt.figure()
    
    if x_col == None:
        plt.plot(y_axis)
    else:
        x_axis = data[x_col].copy()
        plt.plot(x_axis, y_axis)
        plt.xlabel(x_col + '(' + unit[x_col] + ')')
    
    plt.ylabel(y_col + '(' + unit[y_col] + ')')
    
    
    plt.savefig(figure_output, dpi=128)
    plt.show()
    
    
def deal_err(msg):
    print('msg')
    
    
'''
test
'''

def main():
    data = read_load_file(1, 'data_temp/charging_data1.csv')
    draw_plot(data, 'volt','cur', figure_output='data_load/loads.jpg')
    
if __name__ == '__main__':
    main()