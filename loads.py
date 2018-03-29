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

    def __init__(self, sys_settings, load_num, load_type=4):

        '''负载类型

        '''
        if load_num <= sys_settings.chargers_num:
            self.load_type = load_type#标准模型中的负载类型
            self.state = False#负载还没有load_on, load_on为True
            self.load_num = load_num#负载编号
            self.sys_settings = sys_settings
            self.obj = True
            
            #读取数据文件
            self.load_data = fp.read_load_file(self.load_type, data_file)
            if data_file != 'data/loads_model.xls':
            #对数据进行预处理
                self.load_data = dp.preprocess_data(self.load_data, self.sys_settings,
                                    col_sel=filter_col, row_sel='010101030613001F')
            
        else:
            self.obj = None
            print("The number of loads is more than the system_setting! ")
            
        

    def loading(self, data_pre, sys_ticks, lt_col_list, 
                data_file='data/loads_model.xls', filter_col='BMS编号'):
        '''加载负载数据，并合并到load_pre
        默认为load.xls
        '''
        if self.obj == None:
            load_cur = data_pre
            print("The load's data has not loading because of the load model had not created!")
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
        load_cur = self.loads_on(data_pre, sys_ticks, lt_col_list)
        
        return load_cur #返回加载当前负载后的总负载表


    def loads_on(self, data_pre, sys_ticks, col_list):
        """
        计算当前加载的负载，放入load_pre中并返回
        sys_ticks为系统运行至当前采样数
        col_list为当前负载有效状态列表
        """
        if self.state == False:
            #在当前时刻为新的负载,可以加载，并更新state
            self.state = True
            #按当前时刻重设data的index，使得合并dataframe时行能对应
            self.load_data = dp.reset_index(self.load_data, sys_ticks)

            #按负载编号重命名数据calc_para列
            data = dp.data_col_rename(self.load_data, 
                               self.sys_settings.calc_para, 'p'+str(self.load_num))
            
            self.end_tick = sys_ticks + len(data) #负载失效时刻
            #与load_pre合并

            load_cur = dp.data_merge(data_pre, data,
                                    'p'+str(self.load_num),
                                    col_list)
            
            return load_cur
        else:
            print("The load's data has not loading because of the load is exist!")
            # 直接返回load_pre

            return data_pre
    
    def loads_off(self, data_pre):
        """
        找到负载对应列，置为0
        """
        #更新state
        self.state = False
        #self.load_pre.update_settings(self.load_num, 'off')
        load_cur = dp.data_del_col(data_pre, 'p'+str(self.load_num))

        return load_cur
    
    def loads_update(self, sys_ticks):
        if sys_ticks == self.end_tick:
            self.state = False
       #     self.load_pre.update_settings(self.load_num, 'off')
       # return self.load_pre.chargers_iswork
"""
test
"""
def main():
    

    from ess_settings import Settings
    
    import sys_control as sc

    from load_total import Loadtotal
    
    #file_input = 'data_temp/charging_data1.csv'  
    sys_settings = Settings() 
    
    ticks_max = sys_settings.sample_interval * 12 #24h
    
    
    load_total = Loadtotal(ticks_max, sys_settings.chargers_num) #创建代表总负载的dataframe  
    print(load_total.chargers_iswork)
    
    
    import link_list as ll
    
    loads_link = ll.LinkList()
    
    
    ticks_test1 = 1
    ticks_test2 = 50
    ticks_test3 = 200
    ticks_test4 = 400
    ticks_test6 = 800
    ticks_test5 = 1500
    for i in range(1, ticks_max):
        
        if i == ticks_test1:
            num = 1
            load = Loads(sys_settings, num)
            load_total.load_t = load.loading(load_total.load_t, ticks_test1, load_total.col_list)#, file_input)
           # if load.load_pre.chargers_iswork[load.load_num] == 1:
           #     load_total.chargers_iswork[load.load_num] == 1
            loads_link.append(load)
            print('sys_ticks = ' + str(i), load_total.chargers_iswork)
        if i == ticks_test2:
            num = 2
            load2 = Loads(sys_settings, num)
            load_total.load_t = load2.loading(load_total.load_t, ticks_test2, load_total.col_list)#, file_input)
            #if load2.load_pre.chargers_iswork[load2.load_num] == 1:
            #    load_total.chargers_iswork[load2.load_num] == 1
            loads_link.append(load2)
            print('sys_ticks = ' + str(i), load_total.chargers_iswork)
        if i == ticks_test3:
            num = 4
            load_test = Loads(sys_settings, num)
            load_total.load_t = load_test.loading(load_total.load_t, ticks_test3, load_total.col_list)#, file_input)
           # if load_test.load_pre.chargers_iswork[load_test.load_num] == 1:
            #    load_total.chargers_iswork[load_test.load_num] == 1
            loads_link.append(load_test)
            print('sys_ticks = ' + str(i), load_total.chargers_iswork)
        if i == ticks_test4:
            load_total.load_t = load.loading(load_total.load_t, ticks_test4, load_total.col_list)#, file_input)
            #if load.load_pre.chargers_iswork[load.load_num] == 1:
           #     load_total.chargers_iswork[load.load_num] == 1
            print('sys_ticks = ' + str(i), load_total.chargers_iswork)
        if i == ticks_test5:
            load_total.load_t = load.loading(load_total.load_t, ticks_test5, load_total.col_list)#, file_input)
            #if load.load_pre.chargers_iswork[load.load_num] == 1:
            #    load_total.chargers_iswork[load.load_num] == 1

            print('sys_ticks = ' + str(i), load_total.chargers_iswork)
        if i == ticks_test6:
            load8 = Loads(sys_settings, 8)
            load_total.load_t = load8.loading(load_total.load_t, ticks_test6, load_total.col_list)#, file_input)
            loads_link.append(load8)
            #if load8.load_pre.chargers_iswork[load8.load_num] == 1:
            #    load_total.chargers_iswork[load8.load_num] == 1
            print('sys_ticks = ' + str(i), load_total.chargers_iswork)
        
        
        load_total.load_t = sc.loads_calc(i, load_total.load_t,
                                     load_total.l_name, sys_settings.load_regular)

        ld = loads_link.head
        while ld != 0:
           ld.data.loads_update(i)
   #        t = ld.data.loads_update(i)
           ld = ld.next

     #   load_total.chargers_iswork = load2.loads_update(i)
      #  load_total.chargers_iswork = load_test.loads_update(i)
 
        if i == 120:
            load_total.load_t = load2.loads_off(load_total.load_t)
            print('sys_ticks = ' + str(i), load_total.chargers_iswork)
        i += 1
    fp.draw_plot(load_total.load_t, load_total.l_name, figure_output='data_load/load_total.jpg')
    fp.write_load_file(load_total.load_t, 'data_load/load_total.csv')
   # load_total.chargers_iswork = load.load_total.chargers_iswork

#    print(load.load_data)
#    print(sys_settings.chargers_iswork)
#    print(load_total.load_t)
"""    
    for ld in load_list:
        figure_output = 'data_load/load' + str(ld.load_num) + '.jpg'
        file_output = 'data_load/load' + str(ld.load_num) + '.csv'
        fp.draw_plot(ld.load_data, 'power', figure_output=figure_output)
        fp.write_load_file(ld.load_data, file_output)
 """   
 #   load_total.load_t.to_excel('data_temp/l_data.xls')

    
    
if __name__ == '__main__':
    main()