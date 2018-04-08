# -*- coding: utf-8 -*-
"""
Created on Fri Mar 30 14:50:16 2018

@author: wuzhiqiang
"""
import pandas as pd
import scipy.signal

import file_process as fp
import data_preprocessing as dp
import sys_control as sc

class FittingDevice():
    
    def __init__(self, ebx, grid, data_lens):
        
        self.fitting = False
        col_list = ['Gn', 'load_origin', 'delta_load', 'load_regular',
                    'fit_power', 'work_state', 'rate', 'iswork', 
                     'SOE',  'delta_energy', 'bills_regular', 'bills_origin', 'price_coe']
        #delta_energy充为正，放为负
        #load_origin为原始负载，load_regular为需要调整对负载，变化代表要对负载进行调节
        #col_list.insert(0, 'time')#增加时间列
        self.data = pd.DataFrame(columns = col_list) #创建代表拟合器输出的dataframe 
        self.col_list = col_list
        self.g_name = col_list[0]
        self.l_name = col_list[3]
        self.load_ticks_max = data_lens
        self.data['index'] = range(self.load_ticks_max)
        self.data = self.data.set_index(['index'])
        #self.data = self.data.fillna(0)
        self.data['price_coe'] = grid.grid_data['price_coe']
        
        self.trans_cap = grid.cap_limit
        self.etg = grid.xtg
        self.price_list = grid.price_list
        
        self.delta_load = 0 #正为减负载，负为加负载
        self.load_regular_enable = True #允许调节负载
        self.lte = False #允许负载放电
        
        self.ebx_soe = ebx.soe_min#ebx.soe
        self.ebx_soe_max = ebx.soe_max
        self.ebx_soe_min = ebx.soe_min
        self.ebx_cap = ebx.cap_nominal
        self.ebx_charge_rate = ebx.charge_rate
        self.ebx_charge_rate_bk = self.ebx_charge_rate
        self.ebx_discharge_rate = ebx.discharge_rate
        self.ebx_discharge_rate_bk = self.ebx_discharge_rate
        self.ebx_work_state = ebx.work_state     
        self.ebx_discharge_rate_limited = ebx.discharge_rate_limited
        self.ebx_charge_rate_limited = ebx.charge_rate_limited    
        self.ebx_volt = ebx.volt_nominal
        self.ebx_cur = ebx.ah_nominal
        self.ebx_cur_charge = ebx.ah_nominal * self.ebx_charge_rate
        self.ebx_cur_discharge = ebx.ah_nominal * self.ebx_discharge_rate
        self.ebx_active = 'enable'
        self.ebx_min_cd_interval_ticks = ebx.min_cd_interval_ticks#将一个小时分为多少份
        self.ebx_min_cd_interval = ebx.min_cd_interval
        self.ebx_min_cd_interval_bk = ebx.min_cd_interval
        self.sample_interval = ebx.sample_interval
        self.charge_rate_calc(self.data['price_coe'])
        
        #day_cost algorithm初始化各操作带来的收益
        self.profit = {'pre_charge':0, 'pre_discharge':0, 'pre_rest':0,
                       'charge':-100, 'discharge':0, 'rest':0}
        self.input_condition()
        self.price_describe()
        
        self.active = 'enable'
        
    def input_condition(self, **kwg):

        for x in kwg:
            if x == 'price':
                self.data['price_coe'] = kwg[x]

    def set_settings(self, targe='day_cost', load_regular_enable=True, lte=False):
        """
        targe:
            day_cost当天收益最大化
            bat_life电池寿命最优
            normal只补充配电不足
        """
        self.targe = targe
        self.load_regular_enable = load_regular_enable
        self.lte = lte
    def set_on_off(self, command=True):
        self.active = command
        
    def update_ess_value(self, ticks, ebx):
        """
        更新ess设备相关参数
        """
        self.update_cd_rate()#更新充放电倍率  
        self.ebx_cur_charge = self.ebx_cur * self.ebx_charge_rate
        self.ebx_cur_discharge = self.ebx_cur * self.ebx_discharge_rate
         #更新单位时间能量流动值
        self.ebx_charge_energy = self.ebx_cap * self.ebx_charge_rate / self.ebx_min_cd_interval_ticks#单位时间可以充入的能量
        self.ebx_discharge_energy = self.ebx_cap *self.ebx_discharge_rate / self.ebx_min_cd_interval_ticks#单位时间可以放出的能量
        ebx.update_value(self.targe) #ebx更新当前值
        self.ebx_soe_nominal = ebx.soe_nominal
        self.ebx_input_mode = ebx.input_mode
        if self.ebx_input_mode == 'out':#从外部ebx数据更新
            self.ebx_active = ebx.active
            self.ebx_soe = ebx.soe
            self.ebx_charge_energy = ebx.charge_energy
            self.ebx_discharge_energy = ebx.discharge_energy
            #将更新值存在work_value表中
            self.data.loc[ticks, ['iswork']] = ebx.active
            self.data.loc[ticks, ['SOE']] = self.ebx_soe
        #更新可充放对能量后再选择允许对充放能量
        self.now_energy_calc(ticks)
        
    def update_cd_rate(self):
        """
        """
        self.cd_rate_regular()
            
        if self.targe == 'day_cost':
            if self.ebx_charge_rate < self.rd_charge_rate:
                self.ebx_charge_rate = self.rd_charge_rate
            if self.ebx_discharge_rate < self.rd_discharge_rate:
                self.ebx_discharge_rate = self.rd_discharge_rate
        if self.ebx_charge_rate >= self.ebx_charge_rate_limited:
            self.ebx_charge_rate = self.ebx_charge_rate_limited
        if self.ebx_discharge_rate >= self.ebx_discharge_rate_limited:
            self.ebx_discharge_rate = self.ebx_discharge_rate_limited
            
    def update_value(self, ticks):

        self.ebx_work_state = self.data.loc[ticks, ['work_state']]     
        if self.ebx_work_state[0] == 'charge':
            #需要将能量转换为功率，即＊以min_cd_interval,转换后即当前能量值等于功率
            self.ebx_charge_power = self.ebx_charge_energy_allow_bk * self.ebx_min_cd_interval_ticks
            self.grid_value = self.load_origin + self.ebx_charge_power
            if self.trans_cap < self.grid_value:
                if self.load_regular_enable == True:
                    self.delta_load = self.trans_cap - self.grid_value
                else:
                    self.delta_load = 0
                self.load_regular = self.load_origin + self.delta_load
                self.grid_value = self.load_regular
            else:
                 self.delta_load = 0
                 self.load_regular = self.load_origin + self.delta_load
                    
        elif self.ebx_work_state[0] == 'discharge':
            self.ebx_discharge_power = self.ebx_discharge_energy_allow_bk * self.ebx_min_cd_interval_ticks
            self.grid_value = self.load_origin - self.ebx_discharge_power
            if self.trans_cap < self.grid_value:
                if self.load_regular_enable == True:
                    self.delta_load = self.trans_cap - self.grid_value
                else:
                    self.delta_load = 0
                self.load_regular = self.load_origin + self.delta_load
                self.grid_value = self.load_regular - self.ebx_discharge_power 
            else:
                 self.delta_load = 0
                 self.load_regular = self.load_origin + self.delta_load
         #   self.grid_value = self.load_regular
        else:
            self.grid_value = self.load_origin
            self.load_regular = self.load_origin
            self.delta_load = 0
            if self.trans_cap < self.load_origin:
                if self.load_regular_enable == True:
                    self.delta_load = self.load_origin - self.trans_cap               
                    self.load_regular = self.load_origin - self.delta_load
                    self.grid_value = self.load_regular
            
        #将更新值存在work_value表中
        self.data.loc[ticks, ['Gn']] = self.grid_value
        self.data.loc[ticks, ['load_origin']] = self.load_origin
        self.data.loc[ticks, ['load_regular']] = self.load_regular
        self.data.loc[ticks, ['delta_load']] = self.delta_load
        self.data.loc[ticks, ['bills_regular']] = self.grid_value * self.price / self.ebx_min_cd_interval_ticks
        self.data.loc[ticks, ['bills_origin']] = self.load_origin * self.price / self.ebx_min_cd_interval_ticks
        self.grid_cost_t = self.grid_value * self.price
        self.ebx_work_state = self.data.loc[ticks, ['work_state']]
        if self.ebx_work_state[0] == 'charge':
            self.data.loc[ticks, ['rate']] = self.ebx_charge_rate
            self.data.loc[ticks, ['fit_power']] = 0-self.ebx_charge_power
            self.data.loc[ticks, ['delta_energy']] = self.ebx_charge_energy_allow_bk
        elif self.ebx_work_state[0] == 'discharge':
            self.data.loc[ticks, ['rate']] = self.ebx_discharge_rate
            self.data.loc[ticks, ['fit_power']] = self.ebx_discharge_power
            self.data.loc[ticks, ['delta_energy']] = self.ebx_discharge_energy_allow_bk
        else:
            self.data.loc[ticks, ['rate']] = 0
            self.data.loc[ticks, ['fit_power']] = 0
            self.data.loc[ticks, ['delta_energy']] = 0
        if self.ebx_input_mode == 'in':
            self.data.loc[ticks, ['iswork']] = self.ebx_active
            self.data.loc[ticks, ['SOE']] = self.ebx_soe
            
    def sys_fitting(self, ticks, ebx, load_value, load=None):
        """
        选择调整策略
        """
        self.load_origin = load_value
        self.load_regular = self.load_origin
        self.grid_value = self.load_origin
        self.price = self.data.loc[ticks, ['price_coe']]
        self.price = self.price[0]
        if load:
            self.load_total = load
        self.update_ess_value(ticks, ebx)

        if self.active == 'enable':
            self.ebx_min_cd_interval -= 1
            if self.ebx_min_cd_interval > 0:
                return
            else:#到了ebx可以调整的时刻
                self.ebx_min_cd_interval = self.ebx_min_cd_interval_bk
                #更新时间片内对值
                #start = ticks + 1 - self.ebx_min_cd_interval
                #end = ticks - 1
                #if self.grid_cost_t != None:
                 #   self.data.loc[start:end, ['bills']] = self.grid_cost_t
                #如果使能了day_cost模式
                if self.targe == 'day_cost':
                    self.day_cost_algorithm_1(ticks)
                if self.targe == 'normal':
                    self.normal_algorithm(ticks)
        
        self.update_value(ticks)#更新各值
                
    def normal_algorithm(self, ticks):
        """
        """
        if self.trans_cap < self.load_origin:
            if self.ebx_soe > self.ebx_soe_min:
                self.data.loc[ticks, ['work_state']] = 'discharge'
                self.next_energy_calc('discharge')
            else:
                self.data.loc[ticks, ['work_state']] = 'rest'
                self.next_energy_calc('rest')
        elif self.ebx_soe < self.ebx_soe_nominal:
                self.data.loc[ticks, ['work_state']] = 'charge'
                self.next_energy_calc('charge')
        elif self.data.loc[ticks-self.ebx_min_cd_interval, ['work_state']][0] == 'charge' and self.ebx_soe < self.ebx_soe_max:
                self.data.loc[ticks, ['work_state']] = 'charge'
                self.next_energy_calc('charge')
        else:
            self.data.loc[ticks, ['work_state']] = 'rest'
            #self.next_energy_calc('rest')
            
    def day_cost_algorithm_1(self, ticks):

        self.data.loc[ticks, ['work_state']] = 'rest'
        #self.next_energy_calc('rest')
        if self.price >= self.discharge_price and self.load_origin != 0:
            self.data.loc[ticks, ['work_state']] = 'discharge'
            self.next_energy_calc('discharge')

        if self.price <= self.charge_price and self.ebx_soe < self.ebx_soe_max:
            self.data.loc[ticks, ['work_state']] = 'charge'
            self.next_energy_calc('charge')

        if self.trans_cap < self.load_origin:
            if self.ebx_soe > self.ebx_soe_min:
                self.data.loc[ticks, ['work_state']] = 'discharge'
                self.next_energy_calc('discharge')

        if self.ebx_soe < self.ebx_soe_nominal and self.price < self.discharge_price and self.trans_cap > self.load_origin:
            self.data.loc[ticks, ['work_state']] = 'charge'
            self.next_energy_calc('charge')
  
            
    def day_cost_algorithm(self, ticks):
        """
        计算出最大收益
        """
        '''
        if (self.load_ticks_max - self.ebx_min_cd_interval) > ticks:
            price_list = self.data.iloc[[ticks, ticks+self.ebx_min_cd_interval],[-1]] #取时间片中的电价
        else:
            price_list = self.data.iloc[[ticks, self.load_ticks_max-1],[-1]]
        price = 0
        for p in price_list['price_coe']:
            price += p#将时间片中的电价积分
        '''
        price = self.price
        self.profit['pre_charge'] = self.profit['charge']
        self.profit['pre_rest'] = self.profit['rest']
        self.profit['pre_discharge'] = self.profit['discharge']

        c_cost = self.ebx_charge_energy_allow * price
        d_cost = self.ebx_discharge_energy_allow * price
        
        if self.ebx_charge_energy_allow != 0:
            self.profit['charge'] = max(self.profit['pre_charge']-c_cost, 
                   self.profit['pre_discharge']-c_cost, self.profit['pre_rest']-c_cost)
        if self.ebx_discharge_energy_allow != 0:
            self.profit['discharge'] = max(self.profit['pre_charge']+d_cost,
                   self.profit['pre_discharge']+d_cost)
        self.profit['rest'] = max(self.profit['pre_charge'],
                       self.profit['pre_discharge'])
    
        if self.profit['discharge'] > self.profit['pre_discharge']:
            if self.ebx_discharge_energy_allow == 0:
                self.data.loc[ticks, ['work_state']] = 'rest'
            else:
                self.data.loc[ticks, ['work_state']] = 'discharge'
                #判断第i次可以充或放的能量，如果本次单价高但能量成本不足以达到上一次购入能量的成本，同样不放
                self.next_energy_calc('discharge')
            self.profit['charge'] = self.profit['discharge']
        elif self.profit['charge'] > self.profit['pre_charge']:
            if self.ebx_charge_energy_allow == 0:
                self.data.loc[ticks, ['work_state']] = 'rest'
            else:
                self.data.loc[ticks, ['work_state']] = 'charge'
                self.next_energy_calc('charge')
            self.profit['discharge'] = self.profit['charge'] #修正下一次pre_discharge

        else:
            self.data.loc[ticks, ['work_state']] = 'rest'
            self.next_energy_calc('rest')

    def now_energy_calc(self, ticks):

        self.ebx_discharge_energy_allow =min(self.ebx_discharge_energy,
                                             #self.ebx_discharge_energy_allow,
                                             self.ebx_soe-self.ebx_soe_min)#单位时间允许放出的能量
        self.ebx_charge_energy_allow = min(self.ebx_charge_energy,
                                           #self.ebx_charge_energy_allow,
                                           self.ebx_soe_max-self.ebx_soe)#单位时间允许充入的能量
        self.ebx_charge_power = self.ebx_charge_energy_allow * self.ebx_min_cd_interval_ticks
        self.ebx_discharge_power = self.ebx_discharge_energy_allow * self.ebx_min_cd_interval_ticks
        if self.etg == False: 
            self.ebx_discharge_power =min(self.ebx_discharge_power,
                                             self.load_origin)
            self.ebx_discharge_energy_allow = self.ebx_discharge_power / self.ebx_min_cd_interval_ticks
        if self.lte == False:
            self.ebx_charge_power = min(self.ebx_charge_power,
                                           self.trans_cap)
            self.ebx_charge_energy_allow = self.ebx_charge_power / self.ebx_min_cd_interval_ticks
        
        if (self.ebx_discharge_power+self.trans_cap) < self.load_origin:
            
            if self.load_regular_enable == True:
                if self.targe == 'normal':
                    self.load_regular_algorithm_profit(ticks)
                elif self.targe == 'day_cost':
                    self.load_regular_algorithm_profit(ticks)
            else:
                #需要提高放电倍率
                    self.cd_rate_regular()
            
    def next_energy_calc(self, work_state):
        """
        计算下一次允许充放对能量
        """
        if work_state == 'discharge':
            self.ebx_discharge_energy_allow_bk = self.ebx_discharge_energy_allow
            self.ebx_soe = self.ebx_soe - self.ebx_discharge_energy_allow
            self.ebx_discharge_energy_allow = min(self.ebx_discharge_energy,
                                              self.ebx_soe-self.ebx_soe_min)
            self.ebx_charge_energy_allow = min(self.ebx_charge_energy,
                                               self.ebx_soe_max-self.ebx_soe)
        elif work_state == 'charge':
            self.ebx_charge_energy_allow_bk = self.ebx_charge_energy_allow
            self.ebx_soe = self.ebx_soe + self.ebx_charge_energy_allow
            self.ebx_charge_energy_allow = min(self.ebx_charge_energy,
                                               self.ebx_soe_max-self.ebx_soe)
            self.ebx_discharge_energy_allow = min(self.ebx_discharge_energy,
                                              self.ebx_soe-self.ebx_soe_min)
        '''
        elif work_state == 'rest':
            self.ebx_charge_energy_allow_bk = self.ebx_charge_energy_allow
            self.ebx_charge_energy_allow = min(self.ebx_charge_energy,
                                               self.ebx_soe_max-self.ebx_soe)
            self.ebx_discharge_energy_allow = min(self.ebx_discharge_energy,
                                              self.ebx_soe-self.ebx_soe_min)
         '''   
    def load_regular_algorithm_normal(self, ticks):
        """
        优先调节最先工作的负载，如果调节还不足以则调节下一个，直到小于配电负荷
        """
        delta_power = self.load_origin - self.ebx_discharge_power - self.trans_cap
        ld = self.loads_link.head
        while ld != 0:
            value = ld.data.load_data.loc[ticks, [ld.data.sys_settings.calc_para]]
            value = value[0]
            if value >= delta_power:
                ld.data.regular_power = value - delta_power
                break
            else:
                ld.data.regular_power = 0
                delta_power = delta_power - value
            ld.regular = True
      
    def load_regular_algorithm_profit(self, ticks):
        delta_power = self.load_origin - self.ebx_discharge_power - self.trans_cap
        ld = self.load_total.loads_link.head
        while ld != 0:
            value = self.load_total.load_t.loc[ticks, [ld.data.name]]
            value = value[0]
            if value >= delta_power:
                ld.data.regular_power = value - delta_power
                break
            else:
                ld.data.regular_power = 0
                delta_power = delta_power - value
            ld.data.regular = True
            ld = ld.next
            
    def cd_rate_regular(self):
        """
        调节充放电倍率
        """
        if self.trans_cap < self.load_origin:
            self.delta_power = self.load_origin - self.trans_cap
            self.ebx_discharge_rate = self.delta_power / self.ebx_cap
        else:
            self.ebx_discharge_rate = self.ebx_discharge_rate_bk
        
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
          #根据最低最高时段可以最大程度充放能量推荐的倍率      
        self.rd_charge_rate = float((self.ebx_soe_max - self.ebx_soe_min) / self.ebx_cap * (low_price_num / self.sample_interval))# / (low_price_num)) #self.ebx_volt / self.ebx_cur_charge * 1000
        self.rd_discharge_rate = float((self.ebx_soe_max - self.ebx_soe_min) / self.ebx_cap * (low_price_num / self.sample_interval))#self.ebx_volt / self.ebx_cur_charge * 1000         

    def price_describe(self):
        prices = list(self.data['price_coe'])
        self.price_dict = {}
        for price in self.price_list:
            self.price_dict[price] = prices.count(price)
        if len(self.price_list) > 3:
            prices_total = sum(prices)
            y = []
            for price in self.price_dict:
                price = price * self.price_dict[price]
                x = price / prices_total
                y.append(x)
            x = 0
            z = 0
            i = 0
            for i in range(len(prices)):
                x += y[i]
                if x > 0.25:
                    self.discharge_price = self.price_list[i]
                    break
                i += 1
            for i in range(len(prices)):    
                z += y[-1-i]
                if z > 0.15:
                    self.charge_price = self.price_list[-1-i]
                    break
                i += 1
        elif len(self.price_list) > 1:
            self.discharge_price = self.price_list[0]
            self.charge_price = self.price_list[1]
        else:
            self.set_targe('normal')
            
    def draw(self, **kwg):
        fp.draw_plot(self.data, figure_output='program_output/gird.jpg',
                     y_axis=self.l_name)#,x_axis='cur')
            
'''test'''


def main():
    from energy_box import Energybox
    from grid import Grid
    
    df0 = pd.read_excel('data/model1.xls', index_col=0)
    df0 = df0.fillna(0)
    l = df0['L0']
    g = Grid(len(l))
    p = fp.read_load_file(0,'data/price.xls')
    g.get_power_price_data(p)
    ebox = Energybox(360)
    df = FittingDevice(ebox, g, len(l))


    df.set_settings('day_cost')
    for i in range(100):
        load = l[i]
       # df.sys_fitting(i, ebox, load)
    print(df.data)

   # print(df.ebx , df.targe, '\n')
    #c = df.day_cost_algorithm()
   # df.fitting(3, ebox, df0)

if __name__ == '__main__':
    main()