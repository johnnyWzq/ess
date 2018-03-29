#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 19:49:44 2018

@author: zhiqiangwu
"""

class Node():
    def __init__(self,data,p=0):
        self.data = data
        self.next = p
        
class LinkList():
    def __init__(self):
         self.head = 0

    def initlist(self, data):

        self.head = Node(data)

    def getlength(self):
        p = self.head
        length = 0
        while p!=0:
            length+=1
            p = p.next

        return length
        #print("当前链表的长度为%d="%length)

    def is_empty(self):

        if self.getlength() ==0:
            return True
        else:
            return False

    def clear(self):

        self.head = 0


    def append(self,item):

        q = Node(item)
        if self.head ==0:
            self.head = q
        else:
            p = self.head
            while p.next!=0:
                p = p.next
            p.next = q

            
    def getitem(self,index):

        if self.is_empty():
          #  print ('Linklist is empty.')
            return
        j = 0
        p = self.head

        while p.next!=0 and j <index:
            p = p.next
            j+=1

        if j ==index:
            return p.data
            #print("在链表的%d位置上的数值是"%(p.data))

        else:

            print ('target is not exist!')

    def insert(self,index,item):

        if self.is_empty() or index<0 or index >self.getlength():
          #  print ('Linklist is empty.')
            return
        p=self.head
        if index ==0:
            q = Node(item)
            q.next=self.head
            self.head=q
        else:
            p = self.head
            post  = self.head
            j = 0
            while p.next!=0 and j<index:
                post = p
                p = p.next
                j+=1

            if index ==j:
                q = Node(item,p)
                post.next = q
                q.next = p
        p=self.head
        

    def delete(self,index):

        if self.is_empty() or index<0 or index > self.getlength():
            print ('Linklist is empty.')
            return
        p=self.head
        if index ==0:
            q = self.head

            self.head = q.next
            p=self.head
        else:
            p = self.head
            post  = self.head
            j = 0
            while p.next!=0 and j<index:
                post = p
                p = p.next
                j+=1

            if index ==j:
                post.next = p.next

            
    def index(self,value):

        if self.is_empty():
            print ('Linklist is empty.')
            return

        p = self.head
        i = 0
        while p.next!=0 and not p.data ==value:
            p = p.next
            i+=1

        if p.data == value:
            return i
          #  print("要找的值在链表中的第%d位,"%(i+1))
        else:
            return -1
           # print("没有此值!")

'''
test
'''

if __name__=="__main__":
       l = LinkList()
       l.initlist(3)
       l.append(40)
       l.append(12)
       l.insert(2,50)
       l.getitem(1)
       sd = l.getlength()
       print(sd)
       si = l.index(50)
       print(si)
       p = l.head
       while p != 0:
           print(p.data)
           p = p.next
       l.delete(1)
       while l.head != 0:
           print(l.head.data)
           l.head = l.head.next
    #   l.rever()
     #  l.getlength()
      # l.getitem(0)
       #l.delete(0)
       #l.insert(0,1)
       #l.index(2)
       #l.getitem(0)
       #l.append(1)