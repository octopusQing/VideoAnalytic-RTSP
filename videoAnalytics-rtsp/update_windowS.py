# -*- coding: utf-8 -*-
import numpy as np 
import os 
import time 
import cv2
import argparse
from profile import *
from update_windowT import *

global frameCount
frameCount=0

#输入视频流读取完毕，更新视频总帧数
def setFrameCount(frameCount1):
    global frameCount
    frameCount=frameCount1


def update_windowS(pathIn='',   #raw frame保存地址
                   start_frameW='',#视频分析窗口 起始帧
                   end_frameW='', #视频分析窗口 结束帧
                   segment_time='', #视频段的时间
                   knob_values='',  #全部的knob值   /   k个promising的configration包含的knob值
                   k='', #k个promising值  /  1个（promising中选出一个最佳的作为某个segment的configration）
                   fps='',   #输入视频流的帧率
                   profile_time=None,   #profile的时间（1s）
                   golden_configration=None,  #全分析时为golden configration。 
                   cost=None,   #由offline one-time生成的全部configration的cost值
                   ground_configration=None,   #k个中选一个最佳为次优的ground truth？
                   cover_thre=None,   #object覆盖度阈值
                   f1_thre=None,    #根据每帧分析的f1值，来确定该帧是否为准确帧
                   pipe=None   #输出视频流的pipe
                   ): 


     #leader_pathIn=pathIn[0]    #多个视频
     #leader 的raw video本地保存路径
     leader_pathIn=pathIn
    
     #profile 部分的起始帧和结束帧
     start_frameP=start_frameW
     end_frameP=start_frameW+profile_time*fps
     if end_frameP>end_frameW:
         end_frameP=end_frameW
     
     #获取一个window的top k个最佳configration
     configrationW=profile(leader_pathIn,start_frameP,end_frameP,knob_values,k,
                           golden_configration,cost,fps,cover_thre,f1_thre) #leader topK

     #leader profile window中每个segment的configration
     isLeader=1
     

     #若输入视频流读取完毕，更新总帧数（更新视频的window结束帧）
     global frameCount
     if frameCount!=0 and end_frameW>frameCount:
          end_frameW=frameCount


     #获取window中每个segment的最佳（1个）configration
     #过渡：将不返回configration
     leader_configration=update_windowT(leader_pathIn,start_frameW,end_frameW,segment_time,knob_values,k,fps,profile_time,ground_configration,configrationW,isLeader,cost,cover_thre,f1_thre,pipe)
     result_configration=[]
     result_configration.append(leader_configration)
     
     ##
     i=1
     isLeader=0

     #多个视频时需要获取followers的configration
     #while i<len(pathIn):
        #if start_frameW<total_frame[i]:
         # if end_frameW>total_frame[i]:  
            #end_frameW=total_frame[i]
        
          #follower_configration=update_windowT(pathIn[i],start_frameW,end_frameW,segment_time,knob_values,k,fps,profile_time,ground_configration,configrationW,isLeader,cost,cover_thre,f1_thre)
         # result_configration.append(follower_configration)
       # i=i+1
     ## 
        

     return result_configration
