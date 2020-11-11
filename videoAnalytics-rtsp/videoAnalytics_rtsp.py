# -*- coding: utf-8 -*-
import numpy as np 
import os 
import time 
import cv2
import argparse
import subprocess as sp
import threading
from update_windowS import *
from darknet import *
import videoAnalytics_rtsp as main

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
ground_configration=[10,[1000,600]]
#由本地一次性运行，各configration的cost
#cost=[0.1059193, 0.1157906, 0.11597854, 0.0479253, 0.0480274, 0.0382485, 0.0210720, 0.0214134, 0.0210260, 0.0110009, 0.0108665, 0.01090126, 0.0076344, 0.0071999, 0.0074666]
#cost=[0.1359193, 0.1157906, 0.11597854, 0.0559253, 0.0400274, 0.0382485, 0.0410720, 0.0410134, 0.0200000, 0.0210009, 0.0108665, 0.01090126, 0.0106344, 0.0071999, 0.0070666]
cost=[0.1159193, 0.0857906, 0.06597854, 
      0.0479253, 0.03300274, 0.0302485, 
      0.0210720, 0.0174134, 0.0120260,
      0.0110009, 0.0098665, 0.01000126, 
      0.0076344, 0.0061999, 0.0034666]
#cost=[3.098, 3.074, 3.064, 1.036, 1.011, 1.004, 0.515, 0.535, 0.510, 0.215, 0.214, 0.217, 0.116, 0.115, 0.118]
#每个识别目标框的覆盖率与ground truth相比达到多少来计算是否识别正确
cover_thre=0.7
#configration的精确度需要高于这个精确度阈值
f1_thre=0.8
#raw frame保存地址
source_path='./source_images'
#保存到本地的result视频帧率（待调整）
frame_rate=30
#video总帧数
global frameCount
frameCount=0


def receiveThread():

    timeF = 1  # 视频帧计数间隔频率（根据帧采样率设置,no,no,no之后全部获取，采样在传输之前完成）
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
            #cv2.imwrite(source_path+'/frame{}.jpg'.format(i), frame)  # 存储帧到文件夹
            global isReadVideo
            
            isReadVideo=True
            break

            i += 1

        n = n + 1
        #cv2.waitKey(1)
    
    #writer.release()
    vc.release()



def analyseThread(analyseConfigration=None,lock=None):

    global isReadVideo
    while isReadVideo==False:
         #time.sleep(1)
         isReadVideo==False

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
                      ground_configration,cover_thre,f1_thre,pipe,analyseConfigration,lock)
        

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

#yolo_video转移为streamTread。线程分析并回传。
def streamTread(pathIn='',  #输入视频文件的路径
                 fps='',  #输入视频原始fps
                 pipe=None,  #推流的pipe
                 analyseConfigration=None, 
                 confidence_thre=0.6, 
                 nms_thre=0.3, 
                 jpg_quality=80): 
     
         #frame_rate='',#每秒帧采样 image_H='',#image高度  image_W='',这些传入参数转为全局变量   analyseConfigration=[30,[1200,720]]
         #total_frame='' 直接判断frameCount
         #k=int(start_frame) #记录当前读取[vs.read()]的是第几帧

         #初始化分析参数
         image_W=None
         image_H=None
         frame_rate=None

         #global analyseConfigration
         while analyseConfigration==[0,[0,0]]:
            time.sleep(1)


         k=0  #从第0帧开始
         configrationChangeCount=1 #记录configration修改的次数

         while True:

            #到达视频流结尾，跳出循环
            global frameCount
           # if frameCount!=0 and k>=frameCount:
            if k>=3120:
                 pipe.terminate()
                 #sys.exit(1)
                 break

            # 获取帧的尺寸
            #if W is None or H is None:
            #    (H,W)=frame0.shape[:2]

            ##不写入本地
            # 调整图片大小
            #frame0=cv2.imread(pathIn+'/frame'+str(k)+'.jpg')
            #frame = cv2.resize(frame0, (int(image_W), int(image_H)), interpolation=cv2.INTER_AREA)  
            #result_image=performDetectImage(frame)

            '''
            sendback_frame = cv2.resize(result_image, (int(1200), int(720)), interpolation=cv2.INTER_AREA)  

            text="No."+str(k)+" frame    " +str(image_W)+"x"+str(image_H) +"    timeF: " +str(timeF)
            cv2.putText(sendback_frame, text, (50, 50), cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 0, 0), 2)

            pipe.stdin.write(sendback_frame.tostring())
            '''


            
            #获取分析进程的最新参数，若变化则即时更新
            #global analyseConfigration
            if analyseConfigration[0]!=frame_rate or analyseConfigration[1][0]!=image_W or analyseConfigration[1][1]!=image_H:
                image_W=analyseConfigration[1][0]
                image_H=analyseConfigration[1][1]
                frame_rate=analyseConfigration[0]
                print("\n第",configrationChangeCount,"次修改configration为：",frame_rate,",",image_W,",",image_H,",","当前下一分析帧为：",k,"\n") 
                configrationChangeCount=configrationChangeCount+1

            reSize=(int(image_W), int(image_H))
            timeF=int(fps/frame_rate)

            ##不写入本地，analyse完直接推流，非采样帧不分析，直接采用上一分析帧结果
            #path:source图片存储路径；第k个帧需要分析；k后面的timeF-1个帧采用第k的检测结果；reSize调整分辨率后再分析；pipe推流管道
            result_image=performDetectImageAndStream(pathIn,k,timeF,reSize,pipe)
            time.sleep(0.1)
            #main.pipe.stdin.write(result_image.tobyte())  # 存入管道用于直播

            #进入待回传buffer
            #addBackImage(filePath,result_image)

            k=k+timeF



if __name__ == '__main__':

    rval=False  #标记输入url地址是否有视频流，初始设为false
    global isReadVideo
    isReadVideo=False  #标记receive线程是否已读取到数据
    #实际视频分析使用configration
    global analyseConfigration
    analyseConfigration=[0,[0,0]]
    lock = threading.Lock()  #申请一个锁，用于修改分析的configration时使用


  
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
    frame_rate=30   #fps

    command = ['ffmpeg',
    '-y',
    '-f', 'rawvideo',
    '-vcodec','rawvideo',
    '-pix_fmt', 'bgr24',
    '-s', sizeStr,
    '-r', str(frame_rate),   #待调整
    '-i', '-',
    '-c:v', 'libx264',
    '-pix_fmt', 'yuv420p',
    '-preset', 'ultrafast',
    '-rtsp_transport','tcp',
    '-f', 'rtsp', 
    outputUrl]  #推流命令行

    pipe = sp.Popen(command, stdin=sp.PIPE)
    ########

    analyseThread = threading.Thread(target=analyseThread,args=(analyseConfigration,lock))
    analyseThread.start()
  
    streamTread = threading.Thread(target=streamTread,args=(source_path,inputFps,pipe,analyseConfigration))
    streamTread.start()

    streamTread.join()
    analyseThread.join()
    receiveThread.join()
    












     






            




