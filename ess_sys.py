#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  7 09:30:44 2018

@author: zhiqiangwu
"""
import data_preprocessing as dp
import file_process as fp
from ess_settings import Settings
import sys_control as sc
from loads import Loads
from load_total import Loadtotal
from grid import Grid
from energy_box import Energybox
from fitting_device import FittingDevice

def main():
    

    
    file_input = 'data_temp/charging_data1.csv'  
    sys_settings = Settings() 
    
    ticks_max = sys_settings.sample_interval * 8 #24h
    
    grid0 = Grid(ticks_max) #创建电网侧负荷对象，仅考虑配电参数限制
    
    grid0.get_power_price_data(fp.read_load_file(0,'data/price.xls'))

    load_total = Loadtotal(ticks_max, sys_settings.chargers_num) #创建代表总负载的dataframe
    
    ebox = Energybox(sys_settings.sample_interval)
    
    fitting = FittingDevice(ebox, grid0, ticks_max)
    fitting.set_settings(targe='normal',
                      load_regular_enable=True,
                      lte=False)
    grid0.xtg = True
    print("sys_ticks init:"+str(load_total.chargers_iswork))
    
    
    
    ticks_test1 = 200
    ticks_test2 = 220
    ticks_test3 = 600
    ticks_test4 = 510
    ticks_test6 = 800
    ticks_test5 = 1500
    ticks_test7 = 600
    for i in range(1, ticks_max):
        if (load_total.input_mode == 'in'):
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
            if i == ticks_test3:
                num = 4
                load_test = Loads(sys_settings, num)
                load_test.loading(load_total, ticks_test3)#, file_input)
               # if load_test.load_pre.chargers_iswork[load_test.load_num] == 1:
                #    load_total.chargers_iswork[load_test.load_num] == 1
                #loads_link.append(load_test)
                print('sys_ticks = ' + str(i), load_total.chargers_iswork)
            if i == ticks_test4:
                load.loading(load_total, ticks_test4)#, file_input)
                #if load.load_pre.chargers_iswork[load.load_num] == 1:
               #     load_total.chargers_iswork[load.load_num] == 1
                print('sys_ticks = ' + str(i), load_total.chargers_iswork)
            if i == ticks_test5:
                load9.loading(load_total, ticks_test5)#, file_input)
                #if load.load_pre.chargers_iswork[load.load_num] == 1:
                #    load_total.chargers_iswork[load.load_num] == 1
    
                print('sys_ticks = ' + str(i), load_total.chargers_iswork)
            if i == ticks_test6:
                load8 = Loads(sys_settings, 8)
                load8.loading(load_total, ticks_test6)#, file_input)
                #loads_link.append(load8)
                #if load8.load_pre.chargers_iswork[load8.load_num] == 1:
                #    load_total.chargers_iswork[load8.load_num] == 1
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
            if i == 310:
                load2.loads_off(load_total, i)
                print('sys_ticks = ' + str(i), load_total.chargers_iswork)
                
            ld = load_total.loads_link.head
            while ld != 0:
               ld.data.loads_update(load_total, i)
               ld = ld.next
        
        load_total.loads_value_update(i)
        load_total.load_t = sc.loads_calc(i, load_total.load_t, load_total.l_name)
        load_total.load_t_bk = sc.loads_calc(i, load_total.load_t_bk, load_total.l_name)
        """
        grid0.grid_data = sc.grid_calc(i, grid0, load_total.load_t,
                                      add1_col=grid0.l_name, add2_col=load_total.l_name,
                                      sys_s=sys_settings)
        """
        load_t = load_total.load_t.loc[i, [load_total.l_name]]
        load_t = load_t[0]

        fitting.sys_fitting(i, ebox, load_t, load_total)
        sc.loads_regular(i, load_total, ticks_max)
        i += 1

    load_origin = fitting.data['load_origin']
    load_origin = load_origin[load_origin.notnull()]
    load_origin = list(load_origin)
    load_regular = fitting.data['load_regular']
    load_regular = load_regular[load_regular.notnull()]
    load_regular = list(load_regular)
    bill_origin= fitting.data['bills_origin']
    bill_origin = bill_origin[bill_origin.notnull()]
    bill_origin = list(bill_origin)
    bill_regular= fitting.data['bills_regular']
    bill_regular = bill_regular[bill_regular.notnull()]
    bill_regular = list(bill_regular)
    g_regular = fitting.data[fitting.g_name]
    g_regular = g_regular[g_regular.notnull()]
    grid_regular = list(g_regular)
    ebx_power = fitting.data['fit_power']
    ebx_power = ebx_power[ebx_power.notnull()]
    ebx_power = list(ebx_power)
    ebx_energy = fitting.data['SOE']
    ebx_energy = ebx_energy[ebx_energy.notnull()]
    ebx_energy = list(ebx_energy)
    
    x_axis = list(g_regular.index)
    x_axis_len = len(load_total.load_t)

    '''
    fp.draw_power_plot(load_total.load_t.index, True, figure_output='program_output/load_total.jpg',
                       y_axis=list(load_total.load_t[load_total.l_name]), x_axis=list(load_total.load_t.index),
                       cap=grid0.cap_limit)
    fp.draw_power_plot(fitting.data.index, True, figure_output='program_output/fitting.jpg',
                       y_axis=grid_regular, x_axis=x_axis, 
                       cap=grid0.cap_limit)
    fp.draw_power_plot_double(True, figure_output='program_output/fitting2.jpg',
                       x1_axis=list(load_total.load_t.index), y1_axis=list(load_total.load_t[load_total.l_name]),
                       y2_axis=grid_regular, x2_axis=x_axis, 
                       cap=grid0.cap_limit)
    '''
    figure_output = 'program_output/power-%s-%s'%(fitting.targe,str(fitting.load_regular_enable))
    fp.draw_all(grid0.cap_limit, load_origin, grid_regular, load_origin, load_regular,
             bill_origin, bill_regular, ebx_power, ebx_energy,
             x_axis, x_axis_len, True, figure_output+'.jpg')
    fp.write_file(load_total.load_t, 'program_output/load_total.xls')
    fp.write_file(load_total.load_t_bk, 'program_output/load_total_bk.xls')
    fp.write_file(fitting.data, figure_output+'.xls')
    b = fitting.data['bills_regular']
    b = b[b.notnull()]
    print(sum(b))
    #grid0.draw()
    
if __name__ == '__main__':
    main()