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
        col_list = []
        col_list.insert(0, 'Ebxn')
        col_list.insert(0, 'price_coe')
        col_list.insert(0, 'bills')
        col_list.insert(0, 'Gn') 
   #     col_list.insert(0, 'time')#增加时间列
        self.data = pd.DataFrame(columns = col_list) #创建代表拟合器输出的dataframe 
        self.col_list = col_list
        self.g_name = col_list[0]
        self.e_name = col_list[3]
        self.load_ticks_max = data_lens
        self.data['index'] = range(data_lens)
        self.data = self.data.set_index(['index'])
        self.data = self.data.fillna(0)
        self.data['price_coe'] = [1] * data_lens
 
    def input_conditon(self, **kwg):
        for x in kwg:
            if x == 'sys_s':
                sys_s = kwg[x]
                self.cap_limit = sys_s.cap_limit
            if x == 'ebx':
                ebx = kwg[x]
                self.ebx = ebx
            if x == 'price':
                self.data['price_coe'] = kwg[x]
        

    def set_targe(self, targe):
        self.targe = targe
        
    def charge_rate_calc(self):
        """
        计算在一天电价变化的情况下，电池充放电倍率预期最大最小值
        """
        price_list = self.data['price_coe']
        price_list = list(price_list.sort_values())
        self.high_price = price_list[:-1]
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
        self.max_charge_v = float(self.ebx.cap_Nominal * self.ebx.soc_limited / low_price_num) /self.ebx.volt_Nominal
        self.max_discharge_v = float(self.ebx.cap_Nominal * self.ebx.soc_limited / high_price_num) / self.ebx.volt_Nominal
        if self.max_charge_v >= self.ebx.charge_rate_limited:
            self.max_charge_v = self.ebx.charge_rate_limited
        if self.max_discharge_v >= self.ebx.discharge_rate_limited:
            self.max_discharge_v = self.ebx.discharge_rate_limited
            
        
    def day_cost_fitting(self, data, col_name):
        l0 = data[:]
        l0 = l0[[col_name]]
        g0 = self.day_cost_algorithm(self, l0)
        self.data[self.col_list] = g0[self.col_list]
            
    def day_cost_algorithm(self, data):
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
        
    def max_profit(self):

        pre_charge, pre_discharge, discharge = 0, 0, 0
        pre_rest, rest = 0, 0
        charge = int(-100)
        E0 = 0#初始能量
        En = 4#额定能量
        v_c = 1#充电速度
        v_d = 1#放电速度
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
            #如果本次不能充电，则将充电成本设置为放电成本
            #如果本次不能放电，则将放电成本设置为充电成本
            if Exc != 0:
                #charge = max(pre_charge, pre_rest-c_cost)
                charge = max(pre_charge-c_cost, pre_discharge-c_cost, pre_rest-c_cost)
            if Exd != 0:
                #discharge = max(pre_charge+d_cost, pre_discharge)
                discharge = max(pre_charge+d_cost, pre_discharge+d_cost)#weishenmbunengjia!!!
            print('Exc='+str(Exc) + ' Exd='+str(Exd)+
                  ' c_cost='+str(c_cost)+ ' d_cost='+str(d_cost))   
            
            
            
            rest = max(pre_charge, pre_discharge)
            """
            charge = max(pre_charge-c_cost, pre_discharge-c_cost, pre_rest-c_cost)
            discharge = max(pre_charge+d_cost, pre_discharge+d_cost, pre_rest+d_cost)
            rest = max(pre_charge, pre_discharge, pre_rest)
            """
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
    
    ebox = Energybox(250)
    df = FittingDevice(100)
    df0 = pd.read_excel('data/model1.xls', index_col=0)
    df0 = df0.fillna(0)
    p = df0['price_coe']
    l = df0['L0']
    df.input_conditon(price=p, ebx=ebox)
    df.set_targe('day_cost')
    df.day_cost_algorithm(l)
    print(df.data)
   # print(df.ebx , df.targe, '\n')
    c = df.max_profit()
    df.charge_rate_calc()

if __name__ == '__main__':
    main()