# -*- coding: utf-8 -*-
import numpy as np 
import os 
import time 
import cv2
import argparse


def eval_f1(label_locationR=None,label_locationG=None, configrationR=None,  golden_configration=None, cover_thre=None): 

    sum_f1=0

    # 遍历profile视频的每个帧
    i=0
    while i<len(label_locationG):
        frameR=label_locationR[i] 
        frameG=label_locationG[i]

        true_box=0 #R识别到的正确的box

        if len(frameG)==0:
            if len(frameR)==0:
              frame_f1=1
            else:
              frame_f1=0
        elif len(frameR)==0:
            frame_f1=0
        else:
            # 遍历configrationR分析的每个帧的识别object及其位置
            j=0
            while j<len(frameR):
                k=0
                tag=0
                while k<len(frameG) and tag==0:

                    # 若识别到的label相同，则box比较覆盖度
                    # R的帧与G的帧所有label相同的box比较，覆盖率达到阈值，则为正确识别的box，若比较完毕且都达不到覆盖阈值，则为未识别正确的box
                    if frameR[j]==frameG[k]:
                        
                        x_r1=frameR[j+1][0]*(golden_configration[1][0]*1.0/configrationR[1][0])
                        x_r2=frameR[j+2][0]*(golden_configration[1][0]*1.0/configrationR[1][0])
                        y_r1=frameR[j+1][1]*(golden_configration[1][1]*1.0/configrationR[1][1])
                        y_r2=frameR[j+2][1]*(golden_configration[1][1]*1.0/configrationR[1][1])
                        
                        x=[x_r1,x_r2,frameG[k+1][0],frameG[k+2][0]]
                        y=[y_r1,y_r2,frameG[k+1][1],frameG[k+2][1]]
                       
                        s_x=abs(x_r1-x_r2)+abs(frameG[k+1][0]-frameG[k+2][0])-(max(x)-min(x)) #两个box覆盖的宽，若为0则不覆盖
                        s_y=abs(y_r1-y_r2)+abs(frameG[k+1][1]-frameG[k+2][1])-(max(y)-min(y)) #两个box覆盖的长，若为0则不覆盖
                        
                        if(s_x>=0 and s_y>=0):
                            s_g=abs(frameG[k+1][0]-frameG[k+2][0])*abs(frameG[k+1][1]-frameG[k+2][1])# golden configration识别到的box面积
                            s=s_x*s_y 

                            if s*1.0/s_g>cover_thre:
                                true_box=true_box+1
                                tag=1

                    k=k+3

                j=j+3

            

            if true_box==0:
                frame_f1=0
            else:
                precision=true_box*1.0/(len(frameG)/3)
                recall=true_box*1.0/(len(frameR)/3)
                frame_f1=2.0/(1.0/precision+1.0/recall)

        sum_f1=sum_f1+frame_f1
        i=i+1

    
    # 最终返回profile视频段的frame-f1平均值作为configrationR的accuracy
    
    if sum_f1==0:
        avg_f1=0
    else:
        avg_f1=sum_f1*1.0/len(label_locationG)

    return avg_f1