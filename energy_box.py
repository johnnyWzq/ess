# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 14:49:10 2018

@author: wuzhiqiang
"""

class Energybox():
    '''
    定义储能电池系统
    '''
    def __init__(self, sample_interval, price, input_mode='in'):
        '''
        初始化
        '''
        self.bat_type = 'LiFePO4'
        self.cap_nominal  = 130
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
        
        self.initialize_dynamic_settings(price)
        
    def initialize_dynamic_settings(self, price):
        '''初始化系统变量设置'''
        #1表示工作,0表示停机
        self.active = 0
        #state:rest, charge, discharge
        self.power_direction = 'rest'
        self.charge_rate = self.charge_rate_standerd
        self.discharge_rate = self.discharge_rate_standerd
        self.soe = self.cap_nominal
        self.soe_min = self.soe * self.soc_limited_min
        self.soe_max = self.soe * self.soc_limited_max
        
        self.charge_rate_calc(price)

    def update_settings(self):
        '''调整相关参数'''


    def update_value(self, targe, enable='enable', **kwg):
        """
        更新ess的各项值，包括：充放电状态，电池剩余容量，电池系统状态等
        """
        self.active = enable
        
        #更新单位时间能量流动值,按额定电压电流计算
        self.charge_energy = self.charge_rate * self.volt_nominal * self.ah_nominal / 1000
        self.discharge_energy = self.discharge_rate * self.volt_nominal * self.ah_nominal / 1000
        
        if self.input_mode == 'out':
            for x in kwg:
                self.active = kwg[x][0]
                self.soe = kwg[x][1]
                if self.charge_rate > kwg[x][2]:
                    self.charge_rate = kwg[x][2]
                if self.discharge_rate > kwg[x][3]:
                    self.discharge_rate = kwg[x][3]
                #更新单位时间能量流动值
                self.charge_energy = self.charge_rate * kwg[x][4] * kwg[x][5] / 1000
                self.discharge_energy = self.discharge_rate * kwg[x][4] * kwg[x][5] / 1000

            
    def charge_rate_calc(self, price):
        """
        计算在一天电价变化的情况下，电池充放电倍率预期最大最小值
        """
        price_list = price
        price_list = list(price_list.sort_values())
        self.high_price = price_list[-1]
        self.low_price = price_list[0]
        if self.high_price == self.low_price:
            high_price_num = len(price_list)
            low_price_num = high_price_num
        else:
            high_price_num = 1
            low_price_num = 1
            for i in range(len(price_list)):
                if price_list[i+1] == price_list[i]:
                    low_price_num += 1
                else:
                    break
            for i in range(len(price_list)):
                if price_list[0-i-1] == price_list[0-i-2]:
                    high_price_num += 1
                else:
                    break
        self.max_charge_rate = float((self.soe_max - self.soe_min) / low_price_num) /self.volt_nominal
        self.max_discharge_rate = float((self.soe_max - self.soe_min) / high_price_num) / self.volt_nominal
        if self.max_charge_rate >= self.charge_rate_limited:
            self.max_charge_rate = self.charge_rate_limited
        if self.max_discharge_rate >= self.discharge_rate_limited:
            self.max_discharge_rate = self.discharge_rate_limited


"""
test
"""
def main():

    import pandas as pd
      
    v = [1,2,3,4,5,6]
    p = pd.Series([7,8,9,0,1])
    ebx = Energybox(2, p, input_mode='out')
    ebx.update_value('day_cost', ess_value=v)
    print(ebx.charge_rate)
    
if __name__ == '__main__':
    main()   