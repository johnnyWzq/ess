# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 16:11:45 2018

@author: Admin
"""
import pandas as pd


from datetime import datetime,date,timedelta  
now = datetime.now();  
nextDay = now + timedelta(days = 1);#增加一天后的时间  
nextSecond = now + timedelta(seconds = 1);#增加一秒后的时间  
span  = now - nextDay;#获取时间差对象  
print(now);  
print(nextDay);  
print(nextSecond);  
print(span.total_seconds());#获取时间差 以秒为单位  

def reset_index(ticks,data):
    '''重设index'''
    data['index'] = range(ticks, len(data)+ticks)
    data = data.set_index(['index'])
    return data

def data_single_calc(ticks):
    df1.loc[ticks, ['power']] = 4

def data_col_rename(data, n, re):
    data.rename(columns={n:re}, inplace=True)
    return data

def maxProfit(prices):
        """
        :type prices: List[int]
        :rtype: int
        """
        buy, pre_buy, sell, pre_sell, rest, pre_rest = 0, 0, 0, 0, 0, 0
        i = 0
        for price in prices:
            buy = max(pre_rest-price, pre_buy)
            pre_sell = sell
            sell = max(pre_buy+price, pre_sell)
            rest = max(pre_sell, pre_rest)
            print(i, price, buy, sell)
            i += 1
        return sell
p = [1,2,3,0,2]
test = maxProfit(p)
print(test)

df1 = pd.read_excel('data/blank.xls', index_col=0)
df1.rename(columns={'power':'p1'}, inplace=True)

df2 = pd.read_excel('data/model.xls', index_col=0)
df2 = df2[['price_coe']]
df2 = reset_index(10, df2)
p = 'price_coe'
df2 = data_col_rename(df2, p, 'p'+str(2))#df2.rename(columns={'power':'p2'}, inplace=True)

df3 = pd.read_excel('data/model.xls', index_col=0)
df3.rename(columns={'price_coe':'p3'}, inplace=True)
df3 = reset_index(40, df3)
df3.loc[1, ['p3']] = 4

df4 = pd.read_excel('data/model.xls', index_col=0)
df4.rename(columns={'price_coe':'p4'}, inplace=True)
#df4 = reset_index(60, df4)

df4.loc[1, ['p4']] = df4.loc[1, ['p4']] - 3
e= df4.loc[1, ['p4']]
f = df4.iloc[[1,2],[2]]
j = 0

df4 =  df4[['p4']]
print(df4)
a = []
a.append(df1)
a.append(df2)

r = max(-1,2,4,-2)

h = 'p3'
if h in df3.columns:
    print(h)

q=['xq','yd','zr']
for i in range(len(q)):
    print(q[i])

l = range(1, 10)

x = [1] * 10
f = list(l)
w = f[4]
'''
df1.rename(columns={'power':'p1'}, inplace=True)
df2.rename(columns={'power':'p2'}, inplace=True)

new_df = pd.concat([df1['p1'], df2['p2']], axis=1)

s1 = new_df['p2']
'''
#df2['index'] = range(len(df1))
#df2 = df2.set_index(['index'])

#获取指定行列的用法

s = df3['p3']
df3['p3'] = 1
#h = df3.loc['p3']
m = df3.loc[40]
x = m['p3']

y = df3.iloc[4]
j = 0
for i in y:
    j += i 
    print(i)


#df1['power'] = df3['power'] + df2['power'] #两个series相加

#df1 = df1[['power']] #留下power列
df1 = df1.fillna(0) #空值全部置0
#df1.fillna(0)
#df1['power'][df1['power'] == None] = 0
#new_df['power'][df['power'] == None] = 0
df2 = df2[0:18]
ls = ['volt','cur']
df2[ls] = df1[ls]



print(df2)
'''
new_df1 = new_df.add(s1, axis=0)
l = list[df1, df2]
for i in l:
    df = i['power']
'''
x = 1


print(df1)
print(x)

k = [0] * 4
k[0],k[2] = 1,1

import math

def insert_data(data, sel_col, n):
    '''
    均匀补齐数据
    '''
    data0 = data[:]
    if (n == 0):
        return data0
    else:
        data0['index'] = range(0, 2*len(data0), 2)      
        data0 = data0.set_index(['index'])
    
        df = pd.DataFrame(columns = [sel_col]) #创建代表总负载的dataframe 
        df['index'] = range(2*len(data0))
        df = df.set_index(['index'])
        
        df = pd.concat([data0, df], axis=1)
        #留下del_col列表中的数据
        df = df[sel_col]
    
       # s0 = result.loc[[0]]
        for i in range(2):
            s0 = df.iloc[:,i] #取指定列
            if s0[0] != None:
                df0 = s0
                break
    
        for j in range(len(df0)):
            if df0.values[j] > 120: #如果为空即插值。
                df0[j] = ployinterp_column(df0, j, 2)
        df = df0.to_frame()
                
        return insert_data(df, sel_col, n-1)

from scipy.interpolate import lagrange #导入拉格朗日插值函数

def ployinterp_column(s, n, k=2):
    '''
    自定义列向量插值函数
    s为列向量，n为被插值的位置，k为取前后的数据个数，默认为5
    '''
    y = s[list(range(n-k, n)) + list(range(n+1, n+1+k))] #取数
    y = y[y.notnull()] #剔除空值
    return lagrange(y.index, list(y))(n) #插值并返回插值结果
   
for i in range(1,10):
    j = math.log((i/2.0), 2)
    k = math.log(i ,2) - math.log(2, 2)



a = [1,2,3,4,5,6,7,8, '', None]
b = 2.1
k = 0
if b in a:
    print("is:" + str(b))
for b in a:
    if b == None:
        k += 1
        print(k)

def delete_data(data, sel_col, n):
    '''
    均匀删除数据
    '''
    #计算要翻倍数据的次数
    
    if int(len(data)/2) == 1:
        data0 = data[0:-1]
    else:
        data0 = data[:]
        
    if (n == 0):
        return data0
    else:
        #按偶数行删除
        l = list(range(0, len(data0), 2))
        data0 = data0.drop(l)
        data0['index'] = range(len(data0))
        data0 = data0.set_index(['index'])
    return delete_data(data0, sel_col, n-1)


def del_test(data, sample_interval, sel_col):
    '''
    计算要压缩数据的次数
    但是为了不必要的程序开销，压缩后数据均会比目标大，大的部分直接去掉
    '''
    num = int(math.log((len(data)/sample_interval), 2))

    if num < 8: # 最多删减8次
        data = delete_data(data, sel_col, num)
        if len(data) > sample_interval:#超出,删除超出的后面数据部分
            data = data[0:sample_interval]
    else:
        print('the data is too small!')
    return data


df4 = df4[0:223]
df5 = del_test(df4, 36, 'p4')


'''
df4 = df4[0:11]
df5 = insert_data(df4, 'p4', 3)
df5 = df5[0:50]
'''
'''
def data_merge(data1, data2, num):

        result = pd.concat([data1, date2], axis=1)
        result = result[['p1', 'p2', 'p3']]
'''