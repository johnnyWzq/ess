#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 24 12:13:52 2018

@author: zhiqiangwu
"""
import pandas as pd

import data_preprocessing as dp





class Loads():
    '''负载'''
    def __init__(self, sys_settings, load_pre, load_num, load_type=1):
        '''负载类型
        load_pre代表当前时刻前的负载数据集
        '''
        self.load_pre = load_pre
        if load_num <= sys_settings.chargers_num:
            self.load_type = load_type
            self.state = True
            self.load_num = load_num
            self.sys_settings = sys_settings
            
        else:
            self.state = False
            print("The number of loads is more than the system_setting! ")
            
        
    def loading(self, sys_ticks, lt_col_list, data_file='data/loads_model.xls'):
        '''加载负载数据，并合并到load_pre
        默认为load.xls
        '''
        if self.state == False:
            load_cur = self.load_pre.load_t
            return load_cur
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
                   data = pd.read_excel(data_file)#, index_col=0)
                   #读取负载数据，自动索引
                   #data = pd.read_excel(data_file)
                elif file_type == '.csv':
                    #只读取65535条数据
                    data = pd.read_csv(data_file,#index_col=0, 
                                                 nrows=65535, encoding='utf-8')
                    #对数据进行预处理
                    self.load_data = dp.preprocess_data(data, self.sys_settings,
                                col_sel='BMS编号', row_sel='010101030613001F')
                #print(self.load_data)
                else:
                    print("文件格式错误！")
                
                load_cur = self.loads_on(sys_ticks, lt_col_list)
            
                return load_cur #返回加载当前负载后的总负载表
        except:
            print("文件读取错误！")
            
    def loads_on(self, sys_ticks, col_list):
        """
        计算当前加载的负载，放入load_pre中并返回
        sys_ticks为系统运行至当前采样数
        
        """
        if self.sys_settings.charges_iswork[self.load_num] == 0:
            #在当前时刻为新的负载,可以加载，并更新sys
            self.sys_settings.update_settings(self.load_num, 'on')
            #按当前时刻重设data的index，使得合并dataframe时行能对应
            self.load_data = dp.reset_index(self.load_data, sys_ticks)

            #按负载编号重命名数据calc_para列
            data = dp.data_col_rename(self.load_data, 
                               self.sys_settings.calc_para, 'p'+str(self.load_num))
            #与load_pre合并
            load_cur = dp.data_merge(self.load_pre.load_t, data,
                                    'p'+str(self.load_num),
                                    col_list)
            self.load_pre.load_t = load_cur
            
            return load_cur
        else:
            # 直接返回load_pre
            return self.load_pre.load_t
    
    def loads_off(self):
        """
        找到负载对应列，置为0
        """
        #更新sys
        self.sys_settings.update_settings(self.load_num, 'off')
        load_cur = dp.data_del_col(self.load_pre.load_t, 'p'+str(self.load_num))

        return load_cur

"""
test
"""
def main():
    
    from data_preprocessing import Datadiscovery
    from ess_settings import Settings
    
    import sys_control as sc

    from load_total import Loadtotal
    
    
    sys_settings = Settings()
    print(sys_settings.charges_iswork)
    
    ticks_max = sys_settings.sample_interval * 24 #24h
    
    ticks_test = 10
    
    load_total = Loadtotal(ticks_max, sys_settings.chargers_num) #创建代表总负载的dataframe  
    
    file_input = 'data_temp/charging_data1.csv'
    file_output = 'data/charging_data.xls'

    
    try:
        load = Loads(sys_settings, load_total, 1)
        load_total.load_t = load.loading(ticks_test, load_total.col_list, file_input)
        load2 = Loads(sys_settings, load_total, 2)
        load_test = Loads(sys_settings, load_total, 4)
        load_total.load_t = load2.loading(ticks_test+10, load_total.col_list, file_input)
        load_total.load_t = load_test.loading(ticks_test+100, load_total.col_list, file_input)
    except:
        print("fail to load the load")
    
    
    for i in range(10, 1000):
        load_total.load_t = sc.loads_calc(ticks_test+i, load_total.load_t,
                                     load_total.l_name, sys_settings.load_regular)
        if i == 500:
            load_total.load_t = load2.loads_off()

    sys_settings.charges_iswork = load.sys_settings.charges_iswork
    
#    print(load.load_data)
    print(sys_settings.charges_iswork)
    print(load_total.load_t)
    load.load_data.to_excel(file_output)
    dd = Datadiscovery(load.load_data)
    dd.abnormal_check()
    
    figure_output = 'data/charging_data_' + 'L' + str(load.load_num) + '_'
    
    dd.draw_plot('line', 'power', figure_output)
    
 #   load_total.load_t.to_excel('data_temp/l_data.xls')
    cc = Datadiscovery(load_total.load_t)
    cc.draw_plot('line', load_total.l_name, 'data/charging_data_Lo')
    
if __name__ == '__main__':
    main()