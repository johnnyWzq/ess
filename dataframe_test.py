# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 16:11:45 2018

@author: Admin
"""
import pandas as pd

df1 = pd.read_excel('data/blank.xls', index_col=0)
df2 = pd.read_excel('data/model.xls', index_col=0)
'''
df1.rename(columns={'power':'p1'}, inplace=True)
df2.rename(columns={'power':'p2'}, inplace=True)

new_df = pd.concat([df1['p1'], df2['p2']], axis=1)

s1 = new_df['p2']
'''
#df2['index'] = range(len(df1))
#df2 = df2.set_index(['index'])

df1['power'] = df1['power'] + df2['power']
df1 = df1[['power']]

df1['power'][df1['power'] == None] = 0
#new_df['power'][df['power'] == None] = 0

'''
new_df1 = new_df.add(s1, axis=0)
l = list[df1, df2]
for i in l:
    df = i['power']
'''

print(df1)