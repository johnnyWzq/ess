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
    
    def __init__(self, data_lens):
        
        self.fitting = False
        col_list = ['Gn', 'bills', 'price_coe', 'load', 'iswork', 
                    'SOE', 'delta_energy', 'work_state', 'rate']
        #delta_energy充为正，放为负
        #col_list.insert(0, 'time')#增加时间列
        self.data = pd.DataFrame(columns = col_list) #创建代表拟合器输出的dataframe 
        self.col_list = col_list
        self.g_name = col_list[0]
        self.e_name = col_list[3]
        self.load_ticks_max = data_lens
        self.data['index'] = range(data_lens)
        self.data = self.data.set_index(['index'])
        self.data = self.data.fillna(0)
        self.data['price_coe'] = [1] * data_lens
        self.ebx_min_cd_interval = 1
        self.ebx_min_cd_interval_bk = self.ebx_min_cd_interval
        self.ebx_work_state = 'rest'
        self.load_regular = True
        
    def input_conditon(self, **kwg):
        for x in kwg:
            if x == 'sys_s':
                sys_s = kwg[x]
                self.trans_cap_limit = sys_s.cap_limit
            if x == 'ebx_min_cd_interval':
                self.ebx_min_cd_interval = kwg[x]
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
        
    def update_value(self, ticks, ebx):
        """
        更新系统相关参数
        """
        ebx.update_value(self.targe) #ebx更新当前值
           
        self.ebx_active = ebx.active
        self.ebx_soe = ebx.soe
        self.ebx_charge_energy = ebx.charge_energy
        self.ebx_discharge_energy = ebx.discharge_energy
        self.ebx_charge_rate = ebx.charge_rate
        self.ebx_discharge_rate = ebx.discharge_rate
        
        self.update_cd_rate(ebx.max_charge_rate, ebx.max_discharge_rate)#更新充放电倍率     
        #将更新值存在work_value表中
        self.data.loc[ticks, ['iswork']] = ebx.active
        self.data.loc[ticks, ['SOE']] = self.ebx_soe
                    
    def update_cd_rate(self, c_rate, d_rate):
        """
        暂时不做调节
        """
        if self.targe == 'day_cost':
            self.charge_rate = c_rate
            self.discharge_rate = d_rate
            
    def sys_fitting(self, ticks, ebx, data, col_name='L0'):
        """
        选择调整策略
        """
        load = data[:]
        self.update_value(ticks, ebx)
        self.loads_value = load.loc[ticks, [col_name]]
        
        self.ebx_min_cd_interval -= 1
        if self.ebx_min_cd_interval > 0:
            return
        else:
            self.ebx_min_cd_interval = self.self.ebx_min_cd_interval.bk
            if self.targe == 'normal':
                normal_fitting()
            if self.targe == 'day_cost':
                self.day_cost_fitting()
            
            
        #将更新值存在work_value表中
        self.data.loc[ticks, ['loads']] = self.loads_value
        self.data.loc[ticks, ['work_state']] = self.ebx_work_state
        if self.ebx_work_state == 'charge':
            self.data.loc[ticks, ['C_D_rate']] = self.ebx_charge_rate
        elif self.ebx_work_state == 'discharge':
            self.data.loc[ticks, ['C_D_rate']] = self.ebx_discharge_rate
        else:
            self.data.loc[ticks, ['C_D_rate']] = 0
        
    def normal_fitting(self):
        return
        
    def day_cost_fitting(self):
        """
        如果负载不允许调整，则需要优先满足负荷需要
        """
        if self.load_regular == False:
            return
        else:
            self.day_cost_algorithm(self)
            
        ''' 
        l0 = data[:]
        l0 = l0[[col_name]]
        g0 = self.day_cost_algorithm(self, l0)
        self.data[self.col_list] = g0[self.col_list]
         '''   
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
        
    def day_cost_algorithm(self):

        pre_charge, pre_discharge, discharge = 0, 0, 0
        pre_rest, rest = 0, 0
        charge = int(-100)
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
        

    def draw(self):
        fp.draw_plot(self.data, figure_output='program_output/gird.jpg',
                     y_axis=self.l_name)#,x_axis='cur')
            
'''test'''


def main():
    from energy_box import Energybox

    df = FittingDevice(100)
    df0 = pd.read_excel('data/model1.xls', index_col=0)
    df0 = df0.fillna(0)
    p = df0['price_coe']
    l = df0['L0']
    ebox = Energybox(10, p)
    df.input_conditon(price=p, ebx_min_cd_interval=2)
    df.set_targe('day_cost')
    df.grid_cost(l)
    print(df.data)
    df.sys_fitting(3, ebox, df0)
   # print(df.ebx , df.targe, '\n')
    #c = df.day_cost_algorithm()
   # df.fitting(3, ebox, df0)

if __name__ == '__main__':
    main()