# -*- coding: utf-8 -*-
import numpy as np 
import os
import time 
import cv2
import argparse
from darknet import *
from server import *
import subprocess as sp
import videoAnalytics_rtsp as main
  





path="./result_imgs"


######
frame0=cv2.imread(path+'/frame0.jpg')
cv2.putText(frame0, "No.0 frame", (50, 50), cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 0, 0), 2)

cv2.imshow('text', frame0)

cv2.waitKey()
############



isExists=os.path.exists(path)
if not isExists:
  os.makedirs(path) 

sizeStr=str(1280) + 'x' + str(720)
frame_rate=10
outputUrl = 'rtsp://192.168.137.1/play'
command = ['ffmpeg',
'-y',
'-f', 'rawvideo',
'-vcodec','rawvideo',
'-pix_fmt', 'bgr24',
'-s', sizeStr,
'-r', str(frame_rate),
'-i', '-',
'-c:v', 'libx264',
'-pix_fmt', 'yuv420p',
'-preset', 'ultrafast',
'-f', 'rtsp', 
outputUrl]  #推流命令行

#管道特性配置
# pipe = sp.Popen(command, stdout = sp.PIPE, bufsize=10**8)
pipe = sp.Popen(command, stdin=sp.PIPE)
   
k=0






while True:
            
    #则到达视频流结尾，跳出循环
    if k>=1:
        break

    frame0=cv2.imread(path+'/frame'+str(k)+'.jpg')
    frame = cv2.resize(frame0, (int(1280), int(720)), interpolation=cv2.INTER_AREA)
    k=k+3       
    # 获取帧的尺寸
    #if W is None or H is None:
    #    (H,W)=frame0.shape[:2]

    # 调整图片大小
      
            
    #filePath=path+"/frame"+str(k)+".jpg"
              
    #分析结果保存本地，并返回
    #result_image=performDetectImage(frame,filePath)


 
    pipe.stdin.write(frame.tostring())

            

                       

                       
#writer为空时，为处理的第一帧，对writer初始化
#if writer is None:
    #初始化视频writer
    #fourcc=cv2.VideoWriter_fourcc(*"mp4v")
    # writer=cv2.VideoWriter(pathOut,fourcc,frame_rate,(frame.shape[1],frame.shape[0]),True)

# print("estimated total time to finish:{:.4f}".format(elap*total))
#writer.write(result_image)
#vs.set(cv2.CAP_PROP_POS_FRAMES, k+timeF)    
  # k=k+timeF

#writer.release()
#vs.release()

