#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 27 08:53:26 2018

@author: zhiqiangwu
"""

import pandas as pd


class Loadtotal():
    
    def __init__(self, data_lens, col_num, l_name='Lo'):

        col_list = ['p'] * col_num
        for i in range(col_num):
            col_list[i] = 'p' + str(i+1)
        col_list.insert(0, l_name)
        self.load_t = pd.DataFrame(columns = col_list) #创建代表总负载的dataframe 
        self.col_list = col_list
        self.l_name = l_name
        self.load_ticks_max = data_lens
        self.load_t['index'] = range(data_lens)
        self.load_t = self.load_t.set_index(['index'])
        self.load_t = self.load_t.fillna(0)

'''test'''


def main():
    df = Loadtotal(100, 4)
    print(df.load_t)

if __name__ == '__main__':
    main()