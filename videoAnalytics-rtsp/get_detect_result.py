# -*- coding: utf-8 -*-
import numpy as np 
import os 
import time 
import cv2
import argparse
from darknet import *


def get_detect_result(frame0='',  image_W='',image_H='',file_name='',pathIn=None): 

         detect_result=[]
         frame = cv2.resize(frame0, (int(image_W), int(image_H)), interpolation=cv2.INTER_AREA) 
             
         index=pathIn.rindex('/')
         path="./profile_imgs/"+pathIn[index+1:]
         isExists=os.path.exists(path)
         if not isExists:
           os.makedirs(path) 
         filePath=path+"/frame"+file_name+".jpg"
       
         #detect_result=performBatchDetect1(frame,filePath)

         #profile不写入
         detect_result=performBatchDetect1(frame)
         #print(detect_result)

         return detect_result