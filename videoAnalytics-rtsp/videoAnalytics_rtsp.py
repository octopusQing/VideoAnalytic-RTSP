# -*- coding: utf-8 -*-
import numpy as np 
import os 
import time 
import cv2
import argparse
import subprocess as sp
import threading
from update_windowS import *
from yolo_video import * 

inputUrl="rtsp://192.168.137.1/test"  #输入视频流
outputUrl = 'rtsp://192.168.137.1/play'  #输出视频流


#knob值（帧采样率，分辨率）#默认最佳放在第一个
knob_values=[[30,10,5,2,1],[[1200,720],[1000,600],[800,480]]]
#输入流的帧率
inputFps=0 
#视频段（秒），每段从top k 个configration中分析出最佳的configration
segment_time=4
#视频分析窗口（秒），每个窗口一次configration全分析,必须是segment_time的倍数
profile_window_time=4*segment_time
#top k 个configration中  k的数量
k=4
#每次分析最佳k个configration的视频时长（秒）
profile_time=1
#作为truth ground的configration
golden_configration=[30,[1200,720]]
#在top k中选择一个最佳的configration时，用到的ground truth configration 
ground_configration=[30,[1000,600]]
#由本地一次性运行，各configration的cost
cost=[0.1059193, 0.1157906, 0.11597854, 0.0479253, 0.0480274, 0.0382485, 0.0210720, 0.0214134, 0.0210260, 0.0110009, 0.0108665, 0.01090126, 0.0076344, 0.0071999, 0.0074666]
#每个识别目标框的覆盖率与ground truth相比达到多少来计算是否识别正确
cover_thre=0.75
#configration的精确度需要高于这个精确度阈值
f1_thre=0.7
#raw frame保存地址
source_path='./source_images'
#保存到本地的result视频帧率（待调整）
frame_rate=30
#video总帧数
global frameCount
frameCount=0


def receiveThread():

    timeF = 1  # 视频帧计数间隔频率（根据帧采样率设置）
    n = 1  # 对帧计数，标记当前读取帧
    writer=None 
    i = 0#记录当前是第几帧
    rval=True
    while rval:  # 循环读取视频帧
        rval, frame = vc.read()
        if rval==False:
           print("receive frameCount:",i)
           global frameCount
           frameCount=i
           setFrameCount(frameCount)
           break
        #print("rval=",rval)
        #print("frame=",frame[5][0],"\n")
        if (n % timeF == 0):  #每隔timeF帧进行操作
        
            #print(i)
            cv2.imwrite(source_path+'/frame{}.jpg'.format(i), frame)  # 存储帧到文件夹
            global isReadVideo
            
            isReadVideo=True


            i += 1
            #writer为空时，为处理的第一帧，对writer初始化
            #if writer is None:
                #初始化视频writer
               # fourcc=cv2.VideoWriter_fourcc(*"mp4v")
                #writer=cv2.VideoWriter('./source_videos/source_video.mp4',fourcc,frame_rate,(frame.shape[1],frame.shape[0]),True) #保存输入视频到本地
                #sizeStr = str(frame.shape[1]) + 'x' + str(frame.shape[0])
           
            #writer.write(frame)
            
        

        n = n + 1
        cv2.waitKey(1)
    
    #writer.release()
    vc.release()



def analyseThread():

    global isReadVideo
    while isReadVideo==False:
         time.sleep(1)


    start_frameW=0 #视频帧计数，直到视频末尾

    global frameCount
    while frameCount==0 or start_frameW<frameCount:

        end_frameW=start_frameW+profile_window_time*inputFps

        if frameCount!=0 and end_frameW>frameCount:
           end_frameW=frameCount
        

        #profile window的每个segment获得的最佳configration
        global pipe  #过渡：将不返回configration，获取到每段的configration后直接开始分析并返回分析流
        configration=update_windowS(source_path,start_frameW,end_frameW,segment_time,
                      knob_values,k,int(inputFps),profile_time,golden_configration,cost,
                      ground_configration,cover_thre,f1_thre,pipe)
        

        """
        
        n=0#未完成分析的video
        #segment的起始帧、结束帧
        start_frame=start_frameW
        end_frame=start_frame+segment_time*int(inputFps)

        #若frameCount为0，则视频流还未传输读取完毕； 若不为零，视频流已读取完毕，frameCount为总帧数
        if frameCount==0 or start_frame<frameCount:
            #分析窗口中对segment计数，以获取对应的configration
            s=0
            #剩余video长度可能小于leader的分析窗口长度
            if frameCount>0:
               end_frameW_i=min(end_frameW,frameCount)
            else:
               end_frameW_i=end_frameW

            while start_frame<end_frameW_i:
            
                if end_frame>end_frameW_i:
                   end_frame=end_frameW_i
               
                #获取configration中各knob的具体值
                frame_rate=configration[n][s][0]
                image_W=configration[n][s][1][0]  #n表示第n个video
                image_H=configration[n][s][1][1]
           
                global pipe
                yolo_video(source_path,start_frame,end_frame,frame_rate,image_H,image_W,inputFps,pipe)
              
                start_frame=end_frame
                end_frame=start_frame+segment_time*inputFps

                s=s+1
            n=n+1
        """

        start_frameW=end_frameW




if __name__ == '__main__':

    rval=False  #标记输入url地址是否有视频流，初始设为false
    global isReadVideo
    isReadVideo=False  #标记receive线程是否已读取到数据
   
  
    #监听输入rtsp视频流
    while rval==False:
        vc = cv2.VideoCapture(inputUrl)
        if vc.isOpened():  # 判断是否正常打开
            rval=True

            receiveThread = threading.Thread(target=receiveThread)
            receiveThread.start()

            inputFps=vc.get(cv2.CAP_PROP_FPS)
            inputFps=math.ceil(inputFps)
            print('INPUTfps=',inputFps)
            #frame_counter = int(vc.get(cv2.CAP_PROP_FRAME_COUNT)) 
            break
        else:
            rval = False
            #print("当前无视频传输！")
            vc.release()
            #time.sleep(1) #间隔1秒
 



    ####
    global pipe
    sizeStr=str(1200) + 'x' + str(720)  #返回帧的大小（实时调整？）
    frame_rate=10   #返回fps

    command = ['ffmpeg',
    '-y',
    '-f', 'rawvideo',
    '-vcodec','rawvideo',
    '-pix_fmt', 'bgr24',
    '-s', sizeStr,
    '-r', str(frame_rate/3),   #待调整
    '-i', '-',
    '-c:v', 'libx264',
    '-pix_fmt', 'yuv420p',
    '-preset', 'ultrafast',
    '-rtsp_transport','tcp',
    '-f', 'rtsp', 
    outputUrl]  #推流命令行

    pipe = sp.Popen(command, stdin=sp.PIPE)
    ########

    analyseThread = threading.Thread(target=analyseThread)
    analyseThread.start()

    analyseThread.join()
    receiveThread.join()






     






            




