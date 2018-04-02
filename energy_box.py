# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 14:49:10 2018

@author: wuzhiqiang
"""

class Energybox():
    '''
    定义储能电池系统
    '''
    def __init__(self, sys_settings):
        '''
        初始化
        '''
        self.bat_type = 'LiFePO4'
        self.cap_Nominal  = 130000
        self.volt_Nominal  = 720
        self.ah_Nominal  = 180
        self.charge_rate_standerd = 0.5
        self.discharge_rate_standerd = 1
        self.charge_rate_limited = 2.5
        self.discharge_rate_limited = 3
        self.charge_volt_end = 821
        self.discharge_volt_end = 562
        self.circle = 3000
        self.soc_limited = 0.2
#        self.sample_interval = sys_settings.sample_interval
        
        self.initialize_dynamic_settings()
        
    def initialize_dynamic_settings(self):
        '''初始化系统变量设置'''
        #1表示工作,0表示停机
        self.active = 0
        #为1表示给储能充电，-1表示逆变放电
        self.power_direction = 1
        self.charge_rate_current = self.charge_rate_standerd
        self.discharge_rate_current = self.discharge_rate_standerd
        self.soc = 1.0
        '''
        self.discharge_ticks = int(
                self.sample_interval / self.discharge_rate_curren)
        self.charge_ticks = int(
                self.sample_interval / self.charge_rate_current)
        '''
    def regulate_settings(self, eb_settings):
        '''调整相关参数'''
        self.active = eb_settings.active