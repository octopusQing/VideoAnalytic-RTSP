# -*- coding: utf-8 -*-
import numpy as np 
import os 
import time 
import cv2
import argparse
from getConfigrationCost import *
########################
def getAllConfigrationCost(pathIn='',  #输入视频文件的路径
                 knob_values='', # 所有对应knob的取值空间
                 fps='',
                 confidence_thre=0.6, 
                 nms_thre=0.3, 
                 jpg_quality=80): 

     
     cost=[]

    
     i=0
     while i<len(knob_values[0]):
       j=0
       while j<len(knob_values[1]):
           frame_rate=knob_values[0][i]
           image_W=knob_values[1][j][0]
           image_H=knob_values[1][j][1]
           start_frame=0
           end_frame=start_frame+1*fps
           print("frame_rate",frame_rate,"image_W",image_W,"image_H",image_H,"end_frame",end_frame)
           config_cost=getConfigrationCost(pathIn,start_frame,end_frame,frame_rate,image_H,image_W)
           print("config_cost",config_cost*1.0/(end_frame-start_frame))
           cost.append(config_cost*1.0/(end_frame-start_frame))
              
           j=j+1
       i=i+1
    
     print(cost)


     return cost
