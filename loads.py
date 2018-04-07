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
            
        else:
            self.obj = None
            fp.output_msg("The number of loads is more than the system_setting! ")
            
        

    def loading(self, load_total, sys_ticks, 
                data_file='data/loads_model.xls', filter_col='BMS编号'):
        '''加载负载数据，并合并到load_pre
        默认为load.xls
        '''
        if self.obj == None:
            fp.output_msg(
                "The load's data has not loading because of the load model had not created!")
        #读取数据文件
        self.load_data = fp.read_load_file(self.load_type, data_file)
        if data_file == 'data/loads_model.xls':
            data_d = False
        else:
            data_d = True
        #对数据进行预处理
        self.load_data = dp.preprocess_data(self.load_data, self.sys_settings,
                                data_d, col_sel=filter_col, row_sel='010101030613001F')
        self.loads_on(load_total, sys_ticks)


    def loads_on(self, load_total, sys_ticks):
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
            load_cur = load_total.load_t[:]           
            load_total.load_t = dp.data_merge(load_cur, data,
                    col_name='p'+str(self.load_num), col_list=load_total.col_list)
            load_total.loads_link.append(self)
            load_total.loads_state_update(self.load_num, self.state)
            fp.output_msg('sys_ticks = ' + str(sys_ticks) + ' The load' 
                          + str(self.load_num) + ' is on.')
        else:
            fp.output_msg('sys_ticks = ' + str(sys_ticks)
            + " The load's data has not loading because of the load already exists!")
    
    def loads_off(self, load_total, sys_ticks):
        """
        找到负载对应列，置为0
        """
        #更新state
        self.state = False
        #self.load_pre.update_settings(self.load_num, 'off')
        load_total.load_t = dp.data_del_col(load_total.load_t, 'p'+str(self.load_num))
        load_total.loads_link.delete(load_total.loads_link.index(self))
        load_total.loads_state_update(self.load_num, self.state)
        fp.output_msg('sys_ticks = ' + str(sys_ticks) + " The load" + str(self.load_num) + " is off.")
        
    def loads_update(self,load_total, sys_ticks):
        if sys_ticks == self.end_tick:
            self.loads_off(load_total, sys_ticks)

"""
test
"""
def main():
    

    from ess_settings import Settings
    
    sys_settings = Settings() 
    
    ticks_max = sys_settings.sample_interval * 8 #24h

    load_total = Loadtotal(ticks_max, sys_settings.chargers_num) #创建代表总负载的dataframe

    
    print("sys_ticks init:"+str(load_total.chargers_iswork))
    
    
    
    ticks_test1 = 1
    ticks_test2 = 100
    ticks_test7 = 300
    for i in range(1, ticks_max):
            if i == ticks_test1:
                num = 1
                load = Loads(sys_settings, num)
                load.loading(load_total, ticks_test1)#, file_input)
               # if load.load_pre.chargers_iswork[load.load_num] == 1:
               #     load_total.chargers_iswork[load.load_num] == 1
               # loads_link.append(load)
                print('sys_ticks = ' + str(i), load_total.chargers_iswork)
            if i == ticks_test2:
                num = 2
                load2 = Loads(sys_settings, num)
                load2.loading(load_total, ticks_test2)#, file_input)
                #if load2.load_pre.chargers_iswork[load2.load_num] == 1:
                #    load_total.chargers_iswork[load2.load_num] == 1
                #loads_link.append(load2)
                print('sys_ticks = ' + str(i), load_total.chargers_iswork)
            if i == ticks_test7:
                num, num1, num2 = 3,6,9
                load3 = Loads(sys_settings, num)
                load3.loading(load_total, ticks_test7)#, file_input)
                load6 = Loads(sys_settings, num1)
                load6.loading(load_total, ticks_test7)
                load9 = Loads(sys_settings, num2)
                load9.loading(load_total, ticks_test7)
                print('sys_ticks = ' + str(i), load_total.chargers_iswork)
            if i == 120:
                load2.loads_off(load_total, i)
                print('sys_ticks = ' + str(i), load_total.chargers_iswork)
                
            ld = load_total.loads_link.head
            while ld != 0:
               ld.data.loads_update(load_total, i)
               ld = ld.next
        

    
if __name__ == '__main__':
    main()