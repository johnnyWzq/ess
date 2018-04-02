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
            
    def fitting(self, data, col_name):
        l0 = data[:]
        l0 = l0[[col_name]]
        if self.targe == 'day_cost':
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
        '''
                for price in self.data['price_coe']:
            pre_charge = charge
            charge = max(pre_discharge-price, pre_charge)
            pre_discharge = discharge
            discharge = max(pre_charge+price, pre_discharge)
        
            print(price, charge, discharge)
        '''
        pre_charge, pre_discharge, discharge = 0, 0, 0
        pre_rest, rest = 0, 0
        charge = int(-100)
        E0 = 4#初始能量
        En = 4#额定能量
        v_c = 1#充电速度
        v_d = 2#放电速度
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
            elif charge > pre_charge:
                if Exc == 0:
                    act.append('rest')
                else:
                    act.append('charge')
                Es = Es + Exc
                Exc = min(Ecx, En-Es)
                Exd = min(Edx, Es)
                discharge = charge #修正下一次pre_discharge
               # rest = charge
            else:
                act.append('rest')

            i += 1
            print(price, charge, discharge, rest)
            print(act)
            print('Es='+str(Es) + '\n')
            
        print(discharge)
        return discharge
        
        '''
        找不到充电时刻
        k = 3
        price = self.data['price_coe']
        maxprofit_d = pd.DataFrame(index=range(len(price)), columns = range(0, k))
        maxprofit_d = maxprofit_d.fillna(int(0))     
        minprofit_c = pd.DataFrame(index=range(len(price)), columns = range(0, k))
        minprofit_c = maxprofit_d.fillna(int(0))        
        time_d = []
        time_c = []
        diff_c = price[0]
        diff_d = price[0]
        for i in range(1, len(price)):
            diff1_c = price[i] - diff_c
            diff1_d = price[i] - diff_c
            for j in range(1, k):
                maxprofit_d.iat[i,j] = max(maxprofit_d.iat[i-1,j],
                               maxprofit_d.iat[i-1,j-1]+diff1_d)

            diff_c = price[i]
            
            if(maxprofit_d.iat[i-1, k-1] < maxprofit_d.iat[i, k-1]):
                time_d.append(i)

        print('\n' + str(time_d))
        print(maxprofit_d)
        '''
        '''
        print('\n' + str(time_c))
        print(minprofit_c)
        '''
        return maxprofit_d  
        

    def draw(self):
        fp.draw_plot(self.data, figure_output='program_output/gird.jpg',
                     y_axis=self.l_name)#,x_axis='cur')
            
'''test'''


def main():
    df = FittingDevice(6)
    df0 = pd.read_excel('data/model1.xls', index_col=0)
    df0 = df0.fillna(0)
    p = df0['price_coe']
    l = df0['L0']
    df.input_conditon(ebx=2, price=p)
    df.set_targe('day_cost')
    df.day_cost_algorithm(l)
    print(df.data)
   # print(df.ebx , df.targe, '\n')
    c = df.max_profit()

if __name__ == '__main__':
    main()