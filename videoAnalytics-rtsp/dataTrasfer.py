########################old file

# -*- coding: utf-8 -*-
import numpy as np 
import os 
import time 
import cv2
import argparse
from darknet import *
import  server 


def dataTrasfer(): 
    path="./result_imgs/sample4.mp4/"
    k=12
    while k<=20:
           
        frame0=cv2.imread(path+'frame'+str(k)+'.jpg')
            
        filePath=path+"frame"+str(k)+".jpg"
                
        addBackImage(filePath,frame0)
    
        k=k+3
    addBackImage('over')



