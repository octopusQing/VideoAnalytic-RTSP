# -*- coding=utf-8 -*-
import socket
import time
import cv2
import numpy
import copy
import os
import threading
import struct
from VideoAnalytic_gpu import *
from dataTrasfer import *
from update_windowS import *
from darknet import *


#需要分析的videos，第一个为leader video（分享最佳k个从configration的video）
pathIn=[]

#knob值（帧采样率，分辨率）#默认最佳放在第一个
knob_values=[[30,10,5,2,1],[[1200,720],[1000,600],[800,480]]]
#由本地一次性运行，各configration的cost
cost=[0.1059193, 0.1157906, 0.11597854, 0.0479253, 0.0480274, 0.0382485, 0.0210720, 0.0214134, 0.0210260, 0.0110009, 0.0108665, 0.01090126, 0.0076344, 0.0071999, 0.0074666]
#作为truth ground的configration
golden_configration=[30,[1200,720]]
#每次分析最佳k个configration的视频时长（秒）
profile_time=1
#视频段（秒），每段从top k 个configration中分析出最佳的configration
segment_time=4
#视频分析窗口（秒），每个窗口一次configration全分析,必须是segment_time的倍数
profile_window_time=8
#top k 个configration中  k的数量
k=4
#raw视频帧率(由接收获得）
fps=0
#raw 视频总帧数(由接收获得）
total_frame=[]
#在top k中选择一个最佳的configration时，用到的ground truth configration 
ground_configration=[30,[1000,600]]
#每个识别目标框的覆盖率与ground truth相比达到多少来计算是否识别正确
cover_thre=0.75
#configration的精确度需要高于这个精确度阈值
f1_thre=0.7


def recvall(sock, count):
        buf = b''  # buf是一个byte类型
        while count:
            # 接受TCP套接字的数据。数据以字符串形式返回，count指定要接收的最大数据量.
            newbuf = sock.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)
        return buf

def addBackImage(filePath1='',image1=None):
    global  filePathGl,imageGl
    filePathGl.append(filePath1)
    imageGl.append(image1)

def SendBack(conn=None):
   
   readIndex=0
   while 1:
        if readIndex==-1:
           break
        length=len(filePathGl)
        if length>0:
            filePathList=[]
            imageList=[]
            if filePathGl[length-1]!='over':
                filePathList=filePathGl[readIndex:length]
                if len(imageGl)<length:
                    time.sleep(1)
                imageList=imageGl[readIndex:length]
                readIndex=length
            else: 
                if len(imageGl)<length:
                    time.sleep(1)
                filePathList=filePathGl[readIndex:length-1]
                imageList=imageGl[readIndex:length-1]
                readIndex=-1
              
            i=0
            while i<len(filePathList):
                # 压缩参数，后面cv2.imencode将会用到，对于jpeg来说，15代表图像质量，越高代表图像质量越好为 0-100，默认95
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 100]

                #发送视频文件名字
                conn.send(str.encode(str(filePathList[i]).ljust(48)))
     
                result, imgencode = cv2.imencode('.jpg', imageList[i], encode_param)
       
                data = np.array(imgencode)
                # 将numpy矩阵转换成字符形式，以便在网络中传输
                stringData = data.tostring()

                # 先发送要发送的数据的长度
                # ljust() 方法返回一个原字符串左对齐,并使用空格填充至指定长度的新字符串
                conn.send(str.encode(str(len(stringData)).ljust(16)))
                # 发送数据
                conn.send(stringData)

                i=i+1
   conn.send(str.encode('over').ljust(16))  
   

   #接收video图片（存到本地）
def ReceiveVideo(conn=None):
    #cond.acquire()#申请一个锁，当视频名称读取完毕，激活视频分析线程

    videoCount=int(recvall(conn, 16))  #待分析视频数
    print('待接收video数：',videoCount)

    global total_frame
    for i in range(videoCount):
       frameCount=int(recvall(conn, 16))
       total_frame.append(frameCount)
    print('video_total_frame：',total_frame) #存入每个视频的总帧数

    global fps
    fps=int(recvall(conn, 16)) #视频的fps
    print('fps=',fps)
    
    while 1:
        filename = recvall(conn, 16).decode().strip() #传入filename，确定当前接受帧为哪个视频
        print(filename)
        if filename=='over':
            break
      
        path='./source_images/'+filename
        isExists=os.path.exists(path)
        if not isExists:
            os.makedirs(path) 
        
        global pathIn_flag
        if pathIn_flag==0:
            if len(pathIn)==0 :
                pathIn.append(path)
            elif path!=pathIn[0]:
                pathIn.append(path)
            else:
                pathIn_flag=1
       
        #获取正在传输的是第几个视频
        videoIndex=pathIn.index('./source_images/'+filename)
        print('videoIndex=',videoIndex)
        #获取这个video传输的开始帧
        frameIndex = int(recvall(conn, 16))#获取当前传输帧序号
        print('frameIndex=',frameIndex)

        if frameIndex+30>total_frame[videoIndex]:# 计算该轮获取视频帧的end帧序号
            end=total_frame[videoIndex]-frameIndex
        else:end=30

        print('end=',end)

        for h in range(0,end):
            #if(end!=30):print('h=',h)
            length = recvall(conn, 16)  # 获得图文件的长度,16代表获取长度
            if length==None:
                break
            stringData = recvall(conn, int(length))  # 根据获得的文件长度，获取图片文件
            data = numpy.frombuffer(stringData, numpy.uint8)  # 将获取到的字符流数据转换成1维数组
            decimg = cv2.imdecode(data, cv2.IMREAD_COLOR)  # 将数组解码成图像
            
            filePathR=path+"/frame"+str(frameIndex)+".jpg"
            cv2.imwrite(filePathR,decimg) #将图片存储到本地
            
            frameIndex=frameIndex+1
        

def connect():
    address = ('127.0.0.1', 50007)
    #address = ('172.19.89.214', 50007)

    # socket.AF_INET：服务器之间网络通信,socket.SOCK_STREAM：流式socket , for TCP
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 将套接字绑定到地址, 在AF_INET下,以元组（host,port）的形式表示地址.
    s.bind(address)
    # 开始监听TCP传入连接。参数指定在拒绝连接之前，操作系统可以挂起的最大连接数量。该值至少为1，大部分应用程序设为5就可以了。
    s.listen(5)

    # 接受TCP连接并返回（conn,address）,其中conn是新的套接字对象，可以用来接收和发送数据。addr是连接客户端的地址。
    # 没有连接则等待有连接
   
    conn, addr= s.accept()
    print('connect from:' + str(addr))
    return s,conn


def yolo_video(pathIn='',start_frame='',end_frame='',frame_rate='',image_H='',image_W='',fps=''):
    
         timeF=int(fps/frame_rate)
         k=int(start_frame) 

         index=pathIn.rindex('/')
         path="./result_imgs/"+pathIn[index+1:]
        
         while k<end_frame:
            frame0=cv2.imread(pathIn+'/frame'+str(k)+'.jpg')
            frame = cv2.resize(frame0, (int(image_W), int(image_H)), interpolation=cv2.INTER_AREA)  
            filePath=path+"/frame"+str(k)+".jpg"
            result_image=performDetectImage(frame)
            addBackImage(filePath,result_image)#将filepath（client的保存路径，主要是标识video和帧）和result_image回传
            k=k+timeF

def analyseThread():

    while pathIn_flag==0:
        time.sleep(1)
    print(pathIn)

    ##########total_frame=[172,35,50]
    print("total——frame：",total_frame)

    start_frameW=0 #视频帧计数，直到视频末尾
  
    while start_frameW<total_frame[0]:
        end_frameW=start_frameW+profile_window_time*fps

        if end_frameW>total_frame[0]:  end_frameW=total_frame[0]
        
        configration=update_windowS(pathIn,start_frameW,end_frameW,segment_time,knob_values,k,fps,profile_time,golden_configration,cost,total_frame,ground_configration,cover_thre,f1_thre)
        
        m=0
        n=0#未完成分析的video
        while m<len(pathIn):
            start_frame=start_frameW
            end_frame=start_frame+segment_time*fps
            if start_frame<total_frame[m]:
               #分析窗口中对segment计数，以获取对应的configration
               s=0
               #剩余video长度可能小于leader的分析窗口长度
               end_frameW_i=min(end_frameW,total_frame[m])
               while start_frame<end_frameW_i:
            
                 if end_frame>end_frameW_i:
                    end_frame=end_frameW_i
               
                 #获取configration中各knob的具体值
                 frame_rate=configration[n][s][0]
                 image_W=configration[n][s][1][0]
                 image_H=configration[n][s][1][1]

                 yolo_video(pathIn[m],start_frame,end_frame,frame_rate,image_H,image_W,fps)
              
                 start_frame=end_frame
                 end_frame=start_frame+segment_time*fps

                 s=s+1
               n=n+1
            m=m+1

        start_frameW=end_frameW

    #向回传socket发送结束消息
    addBackImage('over')
    time.sleep(5)

   
if __name__ == '__main__':
    filePathGl=[] #待回传列表（保存路径，标识video名及帧）
    imageGl=[]  #待回传列表（已分析的帧）
    pathIn_flag=0 #记录client上传视频名是否读取完毕

    cond = threading.Condition()
    cond_sendback = threading.Condition()

    s,conn=connect()

    # 创建新线程
    analyseThread = threading.Thread(target=analyseThread)
    receiveThread = threading.Thread(target=ReceiveVideo,args=(conn,))
    SendBackThread = threading.Thread(target=SendBack,args=(conn,))
 
    # 开启新线程
    analyseThread.start()
    receiveThread.start()
    SendBackThread.start()
    
    receiveThread.join()
    analyseThread.join()
    SendBackThread.join()

    s.close()

    