# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 10:44:46 2018

@author: wuzhiqiang
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
from matplotlib.gridspec import GridSpec

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

def write_file(data, data_file='data_load/loads.csv'):
    
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
def draw_plot(data, is_save=False, figure_output='data_load/loads.jpg', **col):
    unit = {'power':'kW', 'volt':'V', 'cur':'A', 'L0':'kW', 'G0':'kW', 'time':''}
    axis = []
    for c in col:
        axis.append(col[c])
        
    y_axis = data[axis[0]].copy()
    y_axis.sort_values(ascending = False)
        
    plt.rcParams['font.sans-serif'] = ['SimHei'] #用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False #用来正常显示负号
    
    plt.figure()
    
    xy = len(axis)
    if xy == 1:
        plt.plot(y_axis)
        plt.ylabel(axis[0] + '(' + unit[axis[0]] + ')')
    else:
        x_axis = data[axis[1]].copy()
        plt.plot(x_axis, y_axis)
        plt.xlabel(axis[1] + '(' + unit[axis[1]] + ')')
  
    
    
    if is_save == True:
        plt.savefig(figure_output, dpi=128)
    plt.show()
    
def draw_power_plot(ticks, is_save=False, figure_output='program_output/powr1.jpg', **kwg):

    x_axis = ticks
    for x in kwg:
        if x == 'cap':
            cap = kwg[x]
            y_cap = np.linspace(cap, cap, len(ticks))
            plt.plot(ticks, y_cap, '--', linewidth=2, label='配电容量')
        if x == 'y_axis':                                     
            y_axis = kwg[x]
        if x == 'x_axis':
            x_axis = kwg[x]
            plt.plot(x_axis, y_axis, label='负载功率')
    plt.rcParams['font.sans-serif'] = ['SimHei'] #用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False #用来正常显示负号

    plt.xlabel('时间轴') 
    plt.ylabel('功率(kW)')
    plt.title("功率图")
    plt.legend(loc='upper right')
    plt.ylim(0, np.max(y_axis)+20)
    plt.xlim(0, len(ticks))
    plt.grid(linestyle=':') #开启网格
    if is_save == True:
        plt.savefig(figure_output, dpi=128)
    plt.show()
    
def draw_power_plot_double(is_save=False, figure_output='program_output/power2.jpg', **kwg):

    for x in kwg:
        if x == 'cap':
            cap = kwg[x]
        if x == 'y1_axis':                                     
            y1_axis = kwg[x]
        if x == 'y2_axis':
            y2_axis = kwg[x]
        if x == 'x2_axis':
            x2_axis = kwg[x]
        if x == 'x1_axis':
            x1_axis = kwg[x]
            
    
    plt.rcParams['font.sans-serif'] = ['SimHei'] #用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False #用来正常显示负号
    
    fig = plt.figure(1,figsize=(8,8))
    fig.suptitle('电力功率曲线', fontsize=14, fontweight='bold')
    
    #plt.subplot(211, facecolor='LightGray')
    ax1 = fig.add_subplot(211, facecolor='k')
    ax1.plot(x1_axis, y1_axis, 'greenyellow', linewidth=2, label='负载功率')
    y_cap = np.linspace(cap, cap, len(x1_axis))
    ax1.plot(x1_axis, y_cap, 'r--', linewidth=1, label='配电容量')
    ax1.set_ylim(0, np.max(y1_axis)+20)
    ax1.set_xlim(0, len(x1_axis))
    ax1.grid(linestyle=':') #开启网格
    ax1.legend(loc='upper right')
    ax1.set_ylabel('功率(kW)')
    ax1.set_title('原电力功率曲线')
    
    ax2 = fig.add_subplot(212, facecolor='k', alpha=0.5)
    ax2.plot(x2_axis, y2_axis, 'greenyellow', linewidth=2, label='负载功率')
    y_cap = np.linspace(cap, cap, len(x2_axis))
    ax2.plot(x2_axis, y_cap, 'r--', linewidth=1, label='配电容量')
    ax2.set_ylim(0, np.max(y1_axis)+20)
    ax2.set_xlim(0, len(x1_axis))
    ax2.grid(linestyle=':') #开启网格
    ax2.legend(loc='upper right')
    ax2.set_xlabel('时间轴') 
    ax2.set_ylabel('功率(kW)')
    ax2.set_title('调整后电力功率曲线')  
    ax2.legend(loc='upper right')
    """
    hours = mdates.HourLocator()
    minutes = mdates.MinuteLocator()
    hoursFmt = mdates.DateFormatter('%H:%M')
    # format the ticks
    ax1.xaxis.set_major_locator(hours)
    ax1.xaxis.set_major_formatter(hoursFmt)
    #ax1.xaxis.set_minor_locator(minutes)
    ax1.format_xdata = mdates.DateFormatter('%H:%M')
    fig.autofmt_xdate()
    """
    if is_save == True:
        plt.savefig(figure_output, dpi=128)
    plt.show()

def make_ticklabels_invisible(fig):
    for i, ax in enumerate(fig.axes):
        ax.text(0.5, 0.5, "ax%d" % (i+1), va="center", ha="center")
        ax.tick_params(labelbottom=False, labelleft=False)
        
def draw_all(cap, grid_origin, grid_regular, load_origin, load_regular,
             bill_origin, bill_regular, ebx_power, ebx_energy,
             x_axis, x_axis_len,
             is_save=False, figure_output='program_output/power_all.jpg'):

    plt.rcParams['font.sans-serif'] = [u'SimHei'] #用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False #用来正常显示负号
    plt.figure(edgecolor='k', figsize=(20, 15))
    
    gs = GridSpec(2, 5)
    
    ax1 = plt.subplot(gs[0, 0:2], facecolor='#383737')
    ax2 = plt.subplot(gs[1, 0:2], facecolor='#383737')
    ax3 = plt.subplot(gs[0, 2:4], facecolor='#383737')
    ax4 = plt.subplot(gs[1, 2:4], facecolor='#383737')
    ax5 = plt.subplot(gs[0, -1], facecolor='#383737')
    ax6 = plt.subplot(gs[1, -1], facecolor='#383737')
    
    ax1.plot(x_axis, grid_origin, color='greenyellow', alpha=1,linewidth=1, label='电力负荷')
    y_cap = np.linspace(cap, cap, len(x_axis))
    ax1.plot(x_axis, y_cap, 'r--', linewidth=1.2, label='配电容量')
    '''
    ax1.annotate('配电容量', xy=(2, 1), xytext=(3, 4),
            arrowprops=dict(facecolor='black', shrink=0.05))
    '''
    ax1.set_ylim(0, np.max(grid_origin)+20)
    ax1.set_xlim(0, x_axis_len)
    ax1.grid(linestyle=':') #开启网格
    ax1.legend(loc='upper right')
    ax1.set_ylabel('功率(kW)')
    ax1.set_title('原电力功率曲线')
    
    ax2.plot(x_axis, grid_regular, color='greenyellow', alpha=1, linewidth=1, label='电力负荷')
    y_cap = np.linspace(cap, cap, len(x_axis))
    ax2.plot(x_axis, y_cap, color='r', linestyle='--', linewidth=1.2, label='配电容量')
    ax2.set_ylim(0, np.max(grid_origin)+20)
    ax2.set_xlim(0, x_axis_len)
    ax2.grid(linestyle=':') #开启网格
    ax2.legend(loc='upper right')
    ax2.set_xlabel('时间轴') 
    ax2.set_ylabel('功率(kW)')
    ax2.set_title('调整后电力功率曲线')  
    '''
    x = np.arange(0.0, 2, 0.01)
    load_regular = np.sin(2*np.pi*x)
    load_origin = 1.2*np.sin(4*np.pi*x)
    '''
    ax3.plot(x_axis, load_origin, color='dodgerblue', label='原负载')
    ax3.plot(x_axis, load_regular, color='silver', label='调整后负载')
    #ax3.fill_between(x_axis, load_regular, load_origin, facecolor='silver', where=load_regular>=load_origin, interpolate=True, alpha=0.5,)
    #ax3.fill_between(x_axis, load_regular, load_origin, facecolor='dodgerblue', where=load_origin>load_regular, interpolate=True, alpha=0.3)
    ax3.set_ylim(0, np.max(load_origin)+20)
    ax3.set_xlim(0, x_axis_len)
    ax3.grid(linestyle=':')
    ax3.legend(loc='upper right')
    ax3.set_xlabel('时间轴') 
    ax3.set_ylabel('功率(kW)')
    ax3.set_title('负载功率曲线')  

    ax4.plot(x_axis, ebx_power, 'greenyellow', alpha=1, linewidth=0.6, label='储能装置输出功率')
    ax4.fill_between(x_axis, 0, ebx_energy, color='green', alpha=0.85, label='储能装置输出功率储能装置剩余容量')
    ax4.set_ylim(0-np.max(ebx_power), np.max(ebx_power)*1.5)
    ax4.set_xlim(0, x_axis_len)
    ax4.grid(linestyle=':')
    ax4.legend(loc='upper right')
    ax4.set_xlabel('时间轴') 
    ax4.set_ylabel('功率(kW)')
    ax4.set_title('储能装置工作曲线')
    
    bills_o = sum(bill_origin)
    bills_r = sum(bill_regular)

    ax5.fill_between(x_axis, 0, bill_origin, color='gold', alpha=0.85)#color='slateblue')
    ax5.set_ylim(0, np.max(bill_origin)+5)
    ax5.set_xlim(0, x_axis_len)
    ax5.set_xlabel('时间轴') 
    ax5.set_ylabel('电费(元)')
    ax5.grid(linestyle=':')
    text = '原电费合计: %.2f（元）'%bills_o
    ax5.set_title(text)  
    
    ax6.fill_between(x_axis, 0, bill_regular, color='gold', alpha=0.85)#color='slateblue')
    ax6.set_ylim(0, np.max(bill_origin)+5)
    ax6.set_xlim(0, x_axis_len)
    ax6.grid(linestyle=':')
    ax6.set_xlabel('时间轴') 
    ax6.set_ylabel('电费(元)')
    text = '调整后电费合计: %.2f(元)'%bills_r
    ax6.set_title(text)  
    
    if is_save == True:
        plt.savefig(figure_output, dpi=128)
    plt.show()
    
def deal_err(msg):
    print(msg)
    
def output_msg(msg):
    print(msg
          )
'''
test
'''

def main():
    data = read_load_file(1, 'data_temp/charging_data1.csv')
    draw_plot(data, figure_output='data_load/loads.jpg', y_axis='volt')#,x_axis='cur')

if __name__ == '__main__':
    main()
