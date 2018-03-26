#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 24 11:11:21 2018

@author: zhiqiangwu
"""

class Settings():
    '''
    存储储能系统中对所有设置
    '''
    
    def __init__(self):
        '''初始化'''
        #变压器设置
        self.trans_cap = 800
        self.trans_rate = 0.8
        self.trans_limit = self.trans_cap * self.trans_rate
        #选择哪个参数计算
        self.calc_para = 'power'
        #充电桩设置
        self.charger_nums = 10
    #    self.charger_pout_max = 50
        #逆变器设置
        self.pcs_nums = 1
        #储能单元设置
        self.es_nums = 1
        #监控与调度单元设置
        
        #其他设置
        self.power_lose = 0
        #系统采样时间为1S，1小时3600个采样点
        self.sample_interval = 3600
        
        self.initialize_dynamic_settings()
        
    def initialize_dynamic_settings(self):
        '''初始化系统变量设置'''
        #为1表示给储能充电，-1表示逆变放电
        self.power_direction = 1
        self.charges_iswork = [0] * 10
        
    def update_settings(self, settings):
        self.power_direction = settings.power_dircetion
