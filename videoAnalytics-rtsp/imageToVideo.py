# -*- coding: utf-8 -*-
import numpy as np 
import os 
import time 
import cv2
import argparse
########################
def imageToVideo(pathIn='./source_images/sample6.mp4',  #输入图片的路径
                 pathOut='./test_videos/sample3.mp4',  # 输出视频文件的路径
                 frame_rate=30): 
     
         # vs为指向视频文件的文件指针，初始化视频编写器（writer）和帧尺寸
         vs=cv2.VideoCapture(pathIn)
         writer=None

         #dirs=os.listdir(pathIn)

         #for imageName in dirs:
         for i in range(302):

            imageName='frame'+str(i)+'.jpg'
            #载入图片
            img = cv2.imread(pathIn+'/'+imageName) 
            
            #writer为空时，为处理的第一个image，对writer初始化
            if writer is None:
                #初始化视频writer
                fourcc=cv2.VideoWriter_fourcc(*"mp4v")
                writer=cv2.VideoWriter(pathOut,fourcc,frame_rate,(img.shape[1],img.shape[0]),True)

            writer.write(img)
     
    
         writer.release()
         vs.release()


##imageToVideo()
##print('over')

