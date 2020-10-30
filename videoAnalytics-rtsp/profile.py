# -*- coding: utf-8 -*-
import numpy as np 
import os 
import time 
import cv2
import argparse
from eval_f1 import *
from profile_label_location import *

def profile(pathIn='', start_frame='', end_frame='',  knob_values='', k='',golden_configration=None,
                 cost=None, fps='', cover_thre=None,f1_thre=None,
                 space_configration=None, #在top k中选一个的top k个configration
                 knob_values_all=None #在top k中选一个，利用这个对cost进行定位
                 ): 

     
     knob_count=len(knob_values) # knob的个数
     knobValueToScore=[None]*knob_count
     i=0
     while i<knob_count:
         knobValueToScore[i]=[]
         i=i+1
 
     configration_count=1  # 初始化需要search 的configration组合的个数

     i=0 #对循环计数i清零

     print('fps',golden_configration[0],'image_W=',golden_configration[1][0], 'image_H=',golden_configration[1][1])
     
     #获得使用 golden configration在分析视频段中识别到的label以及location
     label_locationG=profile_label_location(pathIn,start_frame, end_frame,golden_configration,fps) 
     #print("label_locationG",label_locationG[0])

     k=int(k) #k个最佳configration

     #循环分析每个knob(除golden之外）
     while i<knob_count:
         
         j=0
         if k!=1:
           knobValueToScore[i].append(1) #第0个为golden knob，该knob的f1值为1
           j=1 

         configration_count=configration_count*len(knob_values[i])
         
         # 对第i个knob中每个取值进行分析
         while j<len(knob_values[i]):

           if k==1 and knob_values[i][j]==golden_configration[i]:
               f1=1
           else:
             # 获取第j个knob（r）的值(Vr)
             knobR_value=knob_values[i][j]
             
             configrationR=[]
             # 获取第j个knob值为r的configration( c(Vr) )，其余knobs的值为golden knob
             for g in golden_configration:
                 configrationR.append(g)
             configrationR[i]=knobR_value
             
             # 将包含Vr的configration与golden configration比较，得出c（Vr）的score
             print('fps',configrationR[0],'image_W=',configrationR[1][0], 'image_H=',configrationR[1][1])

             #configration全分析，对fps进行profile情况
             #i==0时，knob指的是fps，第j个knob的label-location对ground truth（golden/top-k中的参照值）忽略掉某些帧即可得
             #可忽略帧计算的前提是r的所有采样帧都被ground truth所包含
             label_locationR=[]
             if  i==0 and golden_configration[0]%(configrationR[0])==0:
                 timeF=fps/(configrationR[0])
                 index1=0
                 while index1<len(label_locationG):
                     if(index1==0 or index1%timeF==0):
                       label_locationR.append(label_locationG[index1])
                     else:
                       label_locationR.append(label_locationR[len(label_locationR)-1])
                     index1=index1+1
             else:
                 label_locationR=profile_label_location(pathIn,start_frame, end_frame,configrationR,fps) #获得configrationR在分析视频段中识别到的label以及location
             
             
             f1=eval_f1(label_locationR,label_locationG,configrationR,golden_configration,cover_thre)
             #print("f1=",f1)
             
           
           knobValueToScore[i].append(f1)
             
           j=j+1

         i=i+1
         
 
     scoreC=[] #达到阈值的configration组合的score
     accurateConfigs=[]# 所有accuracy达到阈值的configration 
     config_cost=[]

     #所有符合精确度的congfigration组合及对应的score和cost
     i=0
     while i<len(knob_values[0]):
       j=0
       while j<len(knob_values[1]):
           score=knobValueToScore[0][i]*knobValueToScore[1][j]
           #print("score0",score)
           if score>f1_thre:
               #k==1时,在k个configration中选择一个
               if(k==1):
                   if [knob_values[0][i],knob_values[1][j]] in space_configration:
                       scoreC.append(score)
                       accurateConfigs.append([knob_values[0][i],knob_values[1][j]])
                       i_index=knob_values_all[0].index(knob_values[0][i])
                       j_index=knob_values_all[1].index(knob_values[1][j])
                       config_cost.append(cost[i_index*len(knob_values_all[1])+j_index]) 
               else:
                   scoreC.append(score)
                   accurateConfigs.append([knob_values[0][i],knob_values[1][j]])
                   config_cost.append(cost[i*len(knob_values[1])+j]) 
               
           j=j+1
       i=i+1


     #k个中选择一个最佳时，如果没有满足条件的configration，则用ground truth作为分析的configration
     if len(accurateConfigs)==0 and k==1:
         accurateConfigs.append(golden_configration)
         scoreC.append(1)
         i_index=knob_values_all[0].index(golden_configration[0])
         j_index=knob_values_all[1].index(golden_configration[1])
         config_cost.append(cost[i_index*len(knob_values_all[1])+j_index]) 

     #print(scoreC)#各configration 的f1得分
     #print(accurateConfigs)#满足条件的configration
     #print(config_cost)#满足条件configration的计算开销（cost）

     i=0
     configrationW=[] #top-K configration
     # 获取k个cost最小的configration
     while i<k and i<len(scoreC):
         min_cost=min(config_cost)
         min_index=config_cost.index(min_cost)
         
         if k==1:
             configrationW=accurateConfigs[min_index]
         else:
             configrationW.append(accurateConfigs[min_index])
             del config_cost[min_index]
             del accurateConfigs[min_index]
         i=i+1


     #print(knobValueToScore)
     #print(scoreC)
     
     #print("===========top k configration：")
     # print(configrationW)
     

     return configrationW