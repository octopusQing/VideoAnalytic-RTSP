# -*- coding: utf-8 -*-
import numpy as np 
import os 
import time 
import cv2
import argparse
from profile import *
from yolo_video import * 
from videoAnalytics_rtsp import * 



def update_windowT(source_path='',  #输入视频(raw)帧本地路径
                 start_frameW='',
                 end_frameW='', # 以确定需要处理的video window
                 segment_time='',
                 knob_values='', # 所有对应的knob的取值空间
                 k='', # top-k的k的值
                 inputFps='',
                 profile_time=None,
                 golden_configration=None,#作为ground truth的configration /   k个中选一个最佳为的次优ground truth（分析窗口的第一个段与剩余段的ground truth不同）
                 configrationW=None,#该 window的k个configration
                 isLeader=None,
                 cost=None,
                 analyseConfigration=None,
                 cover_thre=None,
                 f1_thre=None,
                 pipe=None,
                 lock=None
                ): 

     i=0
     configration=[] # 存储该profilewindow每个segment最佳的configration
     
     # 对leader video的profile window的第一个segment进行configration的全分析（取segment前一秒）
     # 返回top-k的configration
     start_frameP=start_frameW
     end_frameP=start_frameW+profile_time*inputFps
     if end_frameP>end_frameW:
         end_frameP=end_frameW

     #检查configrationW是否为空，一般不会执行
     if configrationW==None:
        configrationW=profile(source_path,start_frameP,end_frameP,knob_values,k,golden_configration,cost,inputFps,cover_thre,f1_thre)
        ####configrationW=[[2,[1280,720]],[5,[1280,960]],[15,[1280,720]],[2,[1280,960]],[5,[1280,720]]]


     if isLeader==1:
         #第一个segment的最佳configration即为configrationW的第0个
         configration.append(configrationW[0])

         #segment的起始帧、结束帧
         start_frameS=start_frameW
         end_frameS=start_frameS+segment_time*int(inputFps)
         if end_frameS>end_frameW:
            end_frameS=end_frameW
               
         #获取configration中各knob的具体值
         if start_frameS%4>2:
             frame_rate=5
             image_W=1200 
             image_H=720
         else:
             frame_rate=configrationW[0][0]
             image_W=configrationW[0][1][0]  
             image_H=configrationW[0][1][1]
         #更新analyseConfigration
         lock.acquire()
         analyseConfigration[0]=frame_rate
         analyseConfigration[1][0]=image_W
         analyseConfigration[1][1]=image_H
         lock.release()
         #setAnalyseConfigration(frame_rate,image_W,image_H)
         print("\n第",start_frameS,"-",end_frameS,"帧的segment的configration:",frame_rate,image_W,image_H,"\n") 
         
         #yolo_video(source_path,start_frameS,end_frameS,frame_rate,image_H,image_W,inputFps,pipe)
     



     #对profile window中从leader第二个/follower的第一个 segment开始的其余segment进行top-k中的configration的分析

     #对knob_values进行更新
     knob_valuesK=[None]*len(configrationW[0])
     #最佳的k个configration中包含的knob值
     i=0
     while i<len(configrationW[0]):
         knob_valuesK[i]=[]
         i=i+1

     for conf in configrationW:
         
         i=0
         while i<len(configrationW[0]):
             tag=1
             for kn in knob_valuesK[i]:
               if conf[i]==kn :
                   tag=-1
                   break
             if tag==1:
                 knob_valuesK[i].append(conf[i])
             i=i+1
             
     print("knob_valuesK",knob_valuesK)   
     



     if isLeader==1:
       start_frameP=start_frameW+segment_time*inputFps  # 第二个segment的开始帧
     else:
       start_frameP=start_frameW
     
     while start_frameP<end_frameW:
          
          k=1 #top-k的值
          end_frameP=start_frameP+profile_time*inputFps #取segmet前一秒
          if end_frameP>end_frameW:
              end_frameP=end_frameW
          space_configration=configrationW
          print("") 
          print("start_frameP"+str(start_frameP)+",end_frameP"+str(end_frameP)) 
          configrationS=profile(source_path,start_frameP,end_frameP,knob_valuesK,k,golden_configration,cost,inputFps,cover_thre,f1_thre,space_configration,knob_values)

          ##########开始回传video
          #segment的起始帧、结束帧
          start_frameS=start_frameP
          end_frameS=start_frameS+segment_time*int(inputFps)
          if end_frameS>end_frameW:
            end_frameS=end_frameW
               
          #获取configration中各knob的具体值
          frame_rate=configrationS[0]   
          image_W=configrationS[1][0]  
          image_H=configrationS[1][1]
          print("\n第",start_frameS,"-",end_frameS,"帧的segment的configration:",frame_rate,image_W,image_H,"\n") 

          #更新analyseConfigration
          lock.acquire()
          analyseConfigration[0]=frame_rate
          analyseConfigration[1][0]=image_W
          analyseConfigration[1][1]=image_H
          lock.release()
          #setAnalyseConfigration(frame_rate,image_W,image_H)
          #yolo_video(source_path,start_frameS,end_frameS,frame_rate,image_H,image_W,inputFps,pipe)
          ##################

          configration.append(configrationS)
          start_frameP=start_frameP+segment_time*inputFps
          
     print("") 
          

     return configration