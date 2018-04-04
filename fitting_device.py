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
    
    def __init__(self, ebx, grid):
        
        self.fitting = False
        col_list = ['Gn', 'load_origin', 'load_regular', 'delta_load', 
                    'bills', 'iswork', 
                    'SOE', 'delta_energy', 'work_state', 'rate', 'price_coe']
        #delta_energy充为正，放为负
        #load_origin为原始负载，load_regular为需要调整对负载，变化代表要对负载进行调节
        #col_list.insert(0, 'time')#增加时间列
        self.data = pd.DataFrame(columns = col_list) #创建代表拟合器输出的dataframe 
        self.col_list = col_list
        self.g_name = col_list[0]
        self.e_name = col_list[3]
        self.load_ticks_max = len(grid.grid_data)
        self.data['index'] = range(self.load_ticks_max)
        self.data = self.data.set_index(['index'])
        self.data = self.data.fillna(0)
        self.data['price_coe'] = grid.grid_data['price_coe']
    
        self.ebx_soe = ebx.soe
        self.ebx_soe_max = ebx.soe_max
        self.ebx_soe_min = ebx.soe_min
        self.ebx_charge_rate = ebx.charge_rate
        self.ebx_discharge_rate = ebx.discharge_rate
        self.ebx_work_state = ebx.work_state
        self.ebx_min_cd_interval = ebx.min_cd_interval
        self.ebx_min_cd_interval_bk = ebx.min_cd_interval
        self.ebx_discharge_rate_limited = ebx.discharge_rate_limited
        self.ebx_charge_rate_limited = ebx.charge_rate_limited
        
        self.ebx_volt = ebx.volt_nominal
        self.ebx_cur = ebx.ah_nominal
        self.ebx_cur_charge = ebx.ah_nominal * self.ebx_charge_rate
        self.ebx_cur_discharge = ebx.ah_nominal * self.ebx_discharge_rate
        self.ebx_active = 'enable'
        self.charge_rate_calc(self.data['price_coe'])
 
        self.trans_cap = grid.cap_limit
        self.etg = grid.xtg
        
        self.delta_load = 0 #正为减负载，负为加负载
        self.load_regular_enable = True #允许调节负载
        self.lte = True #允许负载放电
        
        #初始化各操作带来的收益
        self.profit = {'pre_charge':0, 'pre_discharge':0, 'pre_rest':0,
                       'charge':-100, 'discharge':0, 'rest':0}
        self.input_condition()
        
    def input_condition(self, **kwg):

        for x in kwg:
            if x == 'price':
                self.data['price_coe'] = kwg[x]

    def set_targe(self, targe):
        """
        targe:
            day_cost当天收益最大化
            bat_life电池寿命最优
            normal只补充配电不足
        """
        self.targe = targe
        
    def update_ess_value(self, ticks, ebx):
        """
        更新ess设备相关参数
        """
        self.update_cd_rate()#更新充放电倍率  
        self.ebx_cur_charge = self.ebx_cur * self.ebx_charge_rate
        self.ebx_cur_discharge = self.ebx_cur * self.ebx_discharge_rate
         #更新单位时间能量流动值
        self.ebx_charge_energy = self.ebx_min_cd_interval * self.ebx_volt * self.ebx_cur_charge / 1000#单位时间可以充入的能量
        self.ebx_discharge_energy = self.ebx_min_cd_interval * self.ebx_volt * self.ebx_cur_discharge / 1000#单位时间可以放出的能量
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
        self.now_energy_calc()
        
    def update_cd_rate(self):
        """
        暂时不做调节
        """
        if self.targe == 'day_cost':
            self.cd_rate_regular()
            
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
            if self.trans_cap > (self.load_origin+self.ebx_charge_energy_allow_bk):
                self.grid_value = self.load_origin+self.ebx_charge_energy_allow_bk
                self.load_regular = self.load_origin
                self.delta_load = 0
            else:               
                #在变压器不满足当前整个负荷要求时
                self.delta_load = self.load_origin - self.trans_cap - self.ebx_charge_energy_allow_bk
                self.load_regular = self.load_origin - self.delta_load
                self.grid_value = self.load_regular - self.ebx_charge_energy_allow_bk
        elif self.ebx_work_state[0] == 'discharge':
                #放电情况下负载需要调整值
                if self.load_regular_enable == True:
                    if self.trans_cap < (self.load_origin-self.ebx_discharge_energy_allow_bk):
                        self.delta_load = self.load_origin - self.ebx_discharge_energy_allow_bk - self.trans_cap
                    else:
                        self.grid_value = self.load_origin - self.ebx_discharge_energy_allow_bk
                        self.load_regular = self.load_origin
                        self.delta_load = 0
        else:
            self.grid_value = self.load_origin
            self.load_regular = self.load_origin
            self.delta_load = 0
            
        #将更新值存在work_value表中
        self.data.loc[ticks, ['Gn']] = self.grid_value
        self.data.loc[ticks, ['load_origin']] = self.load_origin
        self.data.loc[ticks, ['load_regular']] = self.load_regular
        self.data.loc[ticks, ['delta_load']] = self.delta_load
        self.ebx_work_state = self.data.loc[ticks, ['work_state']]
        if self.ebx_work_state[0] == 'charge':
            self.data.loc[ticks, ['rate']] = self.ebx_charge_rate
            self.data.loc[ticks, ['delta_energy']] = self.ebx_charge_energy_allow_bk
        elif self.ebx_work_state[0] == 'discharge':
            self.data.loc[ticks, ['rate']] = self.ebx_discharge_rate
            self.data.loc[ticks, ['delta_energy']] = self.ebx_discharge_energy_allow_bk
        else:
            self.data.loc[ticks, ['rate']] = 0
        if self.ebx_input_mode == 'in':
            self.data.loc[ticks, ['iswork']] = self.ebx_active
            self.data.loc[ticks, ['SOE']] = self.ebx_soe
            
    def sys_fitting(self, ticks, ebx, data, col_name='L0'):
        """
        选择调整策略
        """
        load = data[:]
        self.load_origin = load.loc[ticks, [col_name]]#更新负载值
        self.load_origin = self.load_origin[0]
        self.load_regular = self.load_origin
        self.grid_value = self.load_origin
        self.update_ess_value(ticks, ebx)

        self.ebx_min_cd_interval -= 1
        if self.ebx_min_cd_interval > 0:
            return
        else:#到了ebx可以调整的时刻
            self.ebx_min_cd_interval = self.ebx_min_cd_interval_bk
            #如果使能了day_cost模式
            if self.targe == 'day_cost':
                self.day_cost_algorithm(ticks)
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
            if self.ebx_soe < self.ebx_soe_max:
                self.data.loc[ticks, ['work_state']] = 'charge'
                self.next_energy_calc('charge')
            else:
                self.data.loc[ticks, ['work_state']] = 'rest'
                self.next_energy_calc('rest')
        else:
            self.data.loc[ticks, ['work_state']] = 'rest'
            self.next_energy_calc('rest')
         
    def grid_cost(self, data):
        """
        进行计算，并将计算结果分别放入self.data的Gn，L0,En,bills中
        """
        df = dp.data_merge(self.data, data) #将表合并到df中
        #计算L0和*price, 先计算能量，对l0积分，然后在乘以price，因为price是系数，
       # 经过公式变化L0和*price等效于L0*price

        cost0 = 0
        c = df['L0'] * df['price_coe']
        for i in c:
            cost0 += i
        print('the original cost is :' + str(cost0))

        return df
        
    def day_cost_algorithm(self, ticks):
        """
        计算出最大收益
        """
        if (self.load_ticks_max - self.ebx_min_cd_interval) > ticks:
            price_list = self.data.iloc[[ticks, ticks+self.ebx_min_cd_interval],[-1]] #取时间片中的电价
        else:
            price_list = self.data.iloc[[ticks, self.load_ticks_max-1],[-1]]
        price = 0
        for p in price_list['price_coe']:
            price += p#将时间片中的电价积分
          
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


    def now_energy_calc(self):
        
        self.ebx_discharge_energy_allow =min(self.ebx_discharge_energy,
                                             self.ebx_soe-self.ebx_soe_min)#单位时间允许放出的能量
        self.ebx_charge_energy_allow = min(self.ebx_charge_energy,
                                           self.ebx_soe_max-self.ebx_soe)#单位时间允许充入的能量
        if self.etg == False: 
            self.ebx_discharge_energy_allow =min(self.ebx_discharge_energy_allow,
                                             self.load_origin)
        if self.lte == False:
            self.ebx_charge_energy_allow = min(self.ebx_charge_energy_allow,
                                           self.trans_cap)
        if self.load_regular_enable == False:
            if (self.ebx_discharge_energy_allow+self.trans_cap) < self.load_origin:
            #需要提高放电倍率
                print('to be describing')
            
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
       
    def max_profit_test(self):
        
        E0 = 0#初始能量
        En = 100#额定能量
        v_c = 5#充电速度
        v_d = 8#放电速度
        t = 1#单位时间片
        Ecx = v_c * t#单位时间可以充入的能量
        Edx = v_d * t#单位时间可以放出的能量
        Es = E0#剩余能量
        Exd = min(Edx, Es)#单位时间允许放出的能量
        Exc = min(Ecx, En-E0)#单位时间允许充入的能量
        act = []
        i = 0
        pre_discharge, discharge, pre_rest, rest, pre_charge = 0,0,0,0,0
        charge = -100
        for price in self.data['price_coe']:      
            pre_charge = charge
            pre_rest = rest
            pre_discharge = discharge

            c_cost = Exc * price
            d_cost = Exd * price

            if Exc != 0:
                #charge = max(pre_charge, pre_rest-c_cost)
                charge = max(pre_charge-c_cost, pre_discharge-c_cost, pre_rest-c_cost)
            if Exd != 0:
                #discharge = max(pre_charge+d_cost, pre_discharge)
                discharge = max(pre_charge+d_cost, pre_discharge+d_cost)#weishenmbunengjia!!!
            print('Exc='+str(Exc) + ' Exd='+str(Exd)+
                  ' c_cost='+str(c_cost)+ ' d_cost='+str(d_cost))   
      
            rest = max(pre_charge, pre_discharge)

            #判断第i次可以充或放的能量，如果本次单价高但能量成本不足以达到上一次购入能量的成本，同样不放
            if discharge > pre_discharge:
                if Exd == 0:
                    act.append('rest')
                else:
                    act.append('discharge')
                Es = Es - Exd
                Exd = min(Edx, Es)
                Exc = min(Ecx, En-Es)
                charge = discharge
            elif charge > pre_charge:
                if Exc == 0:
                    act.append('rest')
                else:
                    act.append('charge')
                Es = Es + Exc
                Exc = min(Ecx, En-Es)
                Exd = min(Edx, Es)
                discharge = charge #修正下一次pre_discharge

            else:
                act.append('rest')

            i += 1
            print(price, charge, discharge, rest)
            print(act)
            print('Es='+str(Es) + '\n')
            
        print(discharge)
        return discharge
    
    def cd_rate_regular(self):
        """
        调节充放电倍率
        """
        
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
        self.rd_charge_rate = float((self.ebx_soe_max - self.ebx_soe_min) / low_price_num) / self.ebx_volt / self.ebx_cur_charge * 1000
        self.rd_discharge_rate = float((self.ebx_soe_max - self.ebx_soe_min) / high_price_num) / self.ebx_volt / self.ebx_cur_charge * 1000


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
    g.get_power_price_data(price=df0['price_coe'])
    ebox = Energybox(21)
    df = FittingDevice(ebox, g)


    df.set_targe('day_cost')
    df.grid_cost(l)
    print(df.data)
    for i in range(100):
       df.sys_fitting(i, ebox, df0)
    print(df.data)

   # print(df.ebx , df.targe, '\n')
    #c = df.day_cost_algorithm()
   # df.fitting(3, ebox, df0)

if __name__ == '__main__':
    main()