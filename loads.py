#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 24 12:13:52 2018

@author: zhiqiangwu
"""

import data_preprocessing as dp

import file_process as fp




class Loads():
    '''负载'''
    def __init__(self, sys_settings, load_pre, load_num, load_type=4):
        '''负载类型
        load_pre代表当前时刻前的负载数据集
        '''
        self.load_pre = load_pre
        if load_num <= sys_settings.chargers_num:
            self.load_type = load_type#标准模型中的负载类型
            self.state = True#负载置为有效
            self.load_num = load_num#负载编号
            self.sys_settings = sys_settings
            
        else:
            self.state = False
            print("The number of loads is more than the system_setting! ")
            
        
    def loading(self, sys_ticks, lt_col_list, 
                data_file='data/loads_model.xls', filter_col='BMS编号'):
        '''加载负载数据，并合并到load_pre
        默认为load.xls
        '''
        if self.state == False:
            self.state = True #当前对象允许下一次调用时可以加载数据
            load_cur = self.load_pre.load_t
            return load_cur
        #读取数据文件
        self.load_data = fp.read_load_file(self.load_type, data_file)
        if data_file == 'data/loads_model.xls':
            data_d = False
        else:
            data_d = True
        #对数据进行预处理
        self.load_data = dp.preprocess_data(self.load_data, self.sys_settings,
                                data_d, col_sel=filter_col, row_sel='010101030613001F')
        load_cur = self.loads_on(sys_ticks, lt_col_list)
        
        return load_cur #返回加载当前负载后的总负载表


    def loads_on(self, sys_ticks, col_list):
        """
        计算当前加载的负载，放入load_pre中并返回
        sys_ticks为系统运行至当前采样数
        
        """
        if self.load_pre.chargers_iswork[self.load_num] == 0:
            #在当前时刻为新的负载,可以加载，并更新sys
            self.load_pre.update_settings(self.load_num, 'on')
            #按当前时刻重设data的index，使得合并dataframe时行能对应
            self.load_data = dp.reset_index(self.load_data, sys_ticks)

            #按负载编号重命名数据calc_para列
            data = dp.data_col_rename(self.load_data, 
                               self.sys_settings.calc_para, 'p'+str(self.load_num))
            
            self.end_tick = sys_ticks + len(data) #负载失效时刻
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
        self.load_pre.update_settings(self.load_num, 'off')
        load_cur = dp.data_del_col(self.load_pre.load_t, 'p'+str(self.load_num))

        return load_cur
    
    def loads_update(self, sys_ticks):
        if sys_ticks == self.end_tick:
            self.load_pre.update_settings(self.load_num, 'off')
        return self.load_pre.chargers_iswork
"""
test
"""
def main():
    

    from ess_settings import Settings
    
    import sys_control as sc

    from load_total import Loadtotal
    
    
    sys_settings = Settings()
    
    
    ticks_max = sys_settings.sample_interval * 12 #24h
    
    ticks_test1 = 1
    ticks_test2 = 50
    ticks_test3 = 200
    ticks_test4 = 400
    
    load_total = Loadtotal(ticks_max, sys_settings.chargers_num) #创建代表总负载的dataframe  
    print(load_total.chargers_iswork)
    
    file_input = 'data_temp/charging_data1.csv'

    load_list = []
    
    for i in range(1, ticks_max):
        
        try:
            if i == ticks_test1:
                load = Loads(sys_settings, load_total, 1)
                load_total.load_t = load.loading(ticks_test1, load_total.col_list)#, file_input)
                if load.load_pre.chargers_iswork[load.load_num] == 1:
                    load_total.chargers_iswork[load.load_num] == 1
                load_list.append(load)
            
            if i == ticks_test2:
                load2 = Loads(sys_settings, load_total, 2)
                load_total.load_t = load2.loading(ticks_test2, load_total.col_list)#, file_input)
                if load2.load_pre.chargers_iswork[load2.load_num] == 1:
                    load_total.chargers_iswork[load2.load_num] == 1
                    load_list.append(load2)
            
            if i == ticks_test3:
                load_test = Loads(sys_settings, load_total, 4)
                load_total.load_t = load_test.loading(ticks_test3, load_total.col_list)#, file_input)
                if load_test.load_pre.chargers_iswork[load_test.load_num] == 1:
                    load_total.chargers_iswork[load_test.load_num] == 1
                    load_list.append(load_test)
                    
            if i == ticks_test4:
                load_total.load_t = load.loading(ticks_test4, load_total.col_list)#, file_input)
                if load.load_pre.chargers_iswork[load.load_num] == 1:
                    load_total.chargers_iswork[load.load_num] == 1
                load_list.append(load)
        except:
            print("fail to load the load")
        
        
        
        load_total.load_t = sc.loads_calc(i, load_total.load_t,
                                     load_total.l_name, sys_settings.load_regular)
    #    for load in load_list:
        load_total.chargers_iswork = load.loads_update(i)
     #   load_total.chargers_iswork = load2.loads_update(i)
      #  load_total.chargers_iswork = load_test.loads_update(i)
 
        if i == 120:
            load_total.load_t = load2.loads_off()
        i += 1
   # load_total.chargers_iswork = load.load_total.chargers_iswork
    
#    print(load.load_data)
#    print(sys_settings.chargers_iswork)
#    print(load_total.load_t)
    
    for ld in load_list:
        figure_output = 'data_load/load' + str(ld.load_num) + '.jpg'
        file_output = 'data_load/load' + str(ld.load_num) + '.csv'
        fp.draw_plot(ld.load_data, 'power', figure_output=figure_output)
        fp.write_load_file(ld.load_data, file_output)
    
 #   load_total.load_t.to_excel('data_temp/l_data.xls')

    fp.draw_plot(load_total.load_t, load_total.l_name, figure_output='data_load/load_total.jpg')
    fp.write_load_file(load_total.load_t, 'data_load/load_total.csv')
    
if __name__ == '__main__':
    main()