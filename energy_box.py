# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 14:49:10 2018

@author: wuzhiqiang
"""

class Energybox():
    '''
    定义储能电池系统
    '''
    def __init__(self, sample_interval, input_mode='in'):
        '''
        初始化
        '''
        self.bat_type = 'LiFePO4'
        self.cap_nominal  = 800
        self.volt_nominal  = 720
        self.ah_nominal  = 180
        self.charge_rate_standerd = 0.5
        self.discharge_rate_standerd = 1
        self.charge_rate_limited = 2.5
        self.discharge_rate_limited = 3
        self.charge_volt_end = 821
        self.discharge_volt_end = 562
        self.circle = 3000
        self.soc_limited_min = 0.2
        self.soc_limited_max = 1
        
        self.sample_interval = sample_interval
        self.min_cd_interval = int(sample_interval / 10) #一次充／放电时间至少1分钟
        
        self.input_mode = input_mode
        
        self.initialize_dynamic_settings()
        
    def initialize_dynamic_settings(self):
        '''初始化系统变量设置'''
        #1表示工作,0表示停机
        self.active = 'disenable'
        #state:rest, charge, discharge
        self.work_state = 'rest'
        self.charge_rate = self.charge_rate_standerd
        self.discharge_rate = self.discharge_rate_standerd
        self.soe = self.cap_nominal
        self.soe_min = self.cap_nominal * self.soc_limited_min
        self.soe_max = self.cap_nominal * self.soc_limited_max
        self.soe_nominal = self.cap_nominal * 0.5
        
        #self.charge_rate_calc(price)

    def update_settings(self):
        '''调整相关参数'''


    def update_value(self, targe, enable='enable', **kwg):
        """
        更新ess的各项值，包括：充放电状态，电池剩余容量，电池系统状态等
        """
        self.active = enable
        if self.input_mode == 'out':
            for x in kwg:
                self.active = kwg[x][0]
                self.soe = kwg[x][1]      
                self.volt_current = kwg[x][2]
                self.cur_current = kwg[x][3]
            #更新单位时间能量流动值
            self.charge_energy = self.min_cd_interval * self.volt_current * self.cur_current / 1000
            self.discharge_energy = self.min_cd_interval * self.volt_current * self.cur_current / 1000
        



"""
test
"""
def main():

    import pandas as pd
      
    v = [1,2,3,4,5,6]
    p = pd.Series([7,8,9,0,1])
    ebx = Energybox(2, input_mode='out')
    ebx.update_value('day_cost', ess_value=v)
    print(ebx.charge_rate)
    
if __name__ == '__main__':
    main()   