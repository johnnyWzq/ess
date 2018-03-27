# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 16:11:45 2018

@author: Admin
"""
import pandas as pd



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


df1 = pd.read_excel('data/blank.xls', index_col=0)
df1.rename(columns={'power':'p1'}, inplace=True)

df2 = pd.read_excel('data/model.xls', index_col=0)
df2 = df2[['power']]
df2 = reset_index(10, df2)
p = 'power'
df2 = data_col_rename(df2, p, 'p'+str(2))#df2.rename(columns={'power':'p2'}, inplace=True)

df3 = pd.read_excel('data/model.xls', index_col=0)
df3.rename(columns={'power':'p3'}, inplace=True)
df3 = reset_index(40, df3)
df3.loc[1, ['p3']] = 4

df4 = pd.read_excel('data/model.xls', index_col=0)
df4.rename(columns={'power':'p4'}, inplace=True)
df4 = reset_index(60, df4)
df4.loc[1, ['p4']] = 6

h = 'p3'
if h in df3.columns:
    print(h)

q=['x','y','z']
print(q)

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
m = df3.loc[50]
x = m['p3']

y = df3.iloc[4]
j = 0
for i in y:
    j += i 
    print(i)


print(list['x','y'])
#df1['power'] = df3['power'] + df2['power'] #两个series相加

#df1 = df1[['power']] #留下power列
df1 = df1.fillna(0) #空值全部置0
#df1.fillna(0)
#df1['power'][df1['power'] == None] = 0
#new_df['power'][df['power'] == None] = 0

'''
new_df1 = new_df.add(s1, axis=0)
l = list[df1, df2]
for i in l:
    df = i['power']
'''
x = 1

def data_col_rename(data, n, re, x):
    data.rename(columns={n:re}, inplace=False)
    x= 2
    return data

df1 = data_col_rename(df1, 'p1', 'cxx', x)

print(df1)
print(x)

k = [0] * 4
k[0],k[2] = 1,1


'''
def data_merge(data1, data2, num):

        result = pd.concat([data1, date2], axis=1)
        result = result[['p1', 'p2', 'p3']]
'''