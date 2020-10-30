# -*- coding: utf-8 -*-
import cv2

print("hello")

from yolo_detect import *
from yolo_video import *
from profile import *
from update_windowT import *
from imageToVideo import *
from update_windowS import *
from getAllConfigrationCost import *
import tensorflow

#######################################   
print(tensorflow.test.is_gpu_available())

'''
pathIn = './test_imgs/image002115.jpg'
pathOut = './result_imgs/image002115.jpg'
yolo_detect(pathIn,pathOut)
pathIn = './test_imgs/image002115.jpg'
pathOut = './result_imgs/image002115.jpg'
yolo_detect(pathIn,pathOut)
pathIn = './test_imgs/image002115.jpg'
pathOut = './result_imgs/image002115.jpg'
yolo_detect(pathIn,pathOut)
pathIn = './test_imgs/image002115.jpg'
pathOut = './result_imgs/image002115.jpg'
yolo_detect(pathIn,pathOut)
'''
'''
pathIn = './test_imgs/test1.jpg'
pathOut = './result_imgs/test1.jpg'
yolo_detect(pathIn,pathOut)



img = cv2.imread("./test_imgs/test1.jpg", -1)  
if img ==None:  
    print "Error: could not load image"  
    os._exit(0)  
      
height, width = img.shape[:2]  
  
# 缩小图像  
size = (int(width*0.5), int(height*0.5))  
shrink = cv2.resize(img, size, interpolation=cv2.INTER_AREA)  
  
# 显示  
cv2.imshow("src", img)  
cv2.imshow("shrink", shrink)  
cv2.imwrite("sample.jpg",shrink)

  
cv2.waitKey(0)  
'''
'''
configrationR=[30,[1280,720]]
golden_configration=[30,[1280,960]]
label_locationR=[[],[],['car',(233,2),(519,96)],['car',(242,3),(521,97)],['car',(244,1),(523,97)]]
label_locationG=[[],[],['car',(233,4),(519,129)],['car',(233,4),(519,129)],['car',(233,4),(519,129)]]

f1=eval_f1(label_locationR,label_locationG,configrationR,golden_configration)
print("f1=",f1)
'''

'''
start_frame=601
end_frame=630
pathIn = './test_videos/sample2.mp4'
knob_valuesK=[None]*2
knob_valuesK[0]=[1,2]
knob_valuesK[1]=[[640,480],[1280,720],[1280,960]]
golden_configration=[30,[1280,960]]
space_configration=[[1,[640,480],[1,[1280,720]],[2,[640,480]],[2,[1280,720]],[1,[1280,960]]]
a=[1,2,5,10,30]
b=[[640,480],[1280,720],[1280,960]]
profile(pathIn,start_frame,end_frame,knob_valuesK,1,[30,[1280,960]],space_configration,knob_values)
'''
'''
print("hello_image")
pathIn = './test_imgs/image001834.jpg'
pathOut = './result_imgs/image001834.jpg'
yolo_detect(pathIn,pathOut)

print("hello_image")
pathIn = './test_imgs/image002115.jpg'
pathOut = './result_imgs/image002115.jpg'
yolo_detect(pathIn,pathOut)
'''

pathIn = ['./test_videos/sample4.mp4','./test_videos/sample5.mp4','./test_videos/sample6.mp4']

vs=cv2.VideoCapture(pathIn[0])
#获取leader总帧数
prop=cv2.CAP_PROP_FRAME_COUNT
total_frame=int(vs.get(prop))
#获取leader帧率
fps = vs.get(cv2.CAP_PROP_FPS)
#获取leader视频时长
video_time = total_frame/fps


knob_values=[None]*2
knob_values[0]=[30,10,5,2,1]
knob_values[1]=[[1200,720],[1000,600],[800,480]]#######################
k=5

#cost=getAllConfigrationCost(pathIn[0],knob_values,fps)
cost=[3.098, 3.074, 3.064, 1.036, 1.011, 1.004, 0.515, 0.535, 0.510, 0.215, 0.214, 0.217, 0.116, 0.115, 0.118]

# t=1s，对应fps*1s个帧
# T=4s,对应fps*4s个帧
# 设profilewindow为两个segment，即8s；对应fps*8s个帧
# 一个profilewindow包含两个T
golden_configration=[30,[1200,720]]######################
profile_time=1
segment_time=20
profile_window_time=3*segment_time

i=1 #视频帧计数，直到视频末尾
v=1 #输出视频名称参数
while i<total_frame:
    start_frameW=i
    end_frameW=i+profile_window_time*fps-1 

    #最后一个profile_window的长度可能小于8s
    if end_frameW>total_frame:
        end_frameW=total_frame

    #获取该视频profile_window中每个segment的最佳configration
    configration=update_windowS(pathIn,start_frameW,end_frameW,segment_time,knob_values,k,fps,profile_time,golden_configration,cost)
    ##configration=[ [[2,[1280,720]],[5,[1280,960]]], [[2,[1280,720]],[5,[1280,960]]], [[2,[1280,720]],[5,[1280,960]]] ]
    

    #循环对每个video的该windowprofile的每个segment进行处理
    j=start_frameW
    k=0
    while j<end_frameW:
        start_frame=j
        end_frame=j+segment_time*fps-1
        
        m=0
        while m<len(pathIn):
          #获取configration中各knob的具体值
          frame_rate=configration[m][k][0]
          image_W=configration[m][k][1][0]
          image_H=configration[m][k][1][1]

          index=pathIn[m].rindex('/')
          path="./result_videos/"+pathIn[m][index+1:]
          isExists=os.path.exists(path)
          if not isExists:
               os.makedirs(path) 
          
          pathOut = path+'/sample'+str(v)+'.mp4'
          yolo_video(pathIn[m],pathOut,start_frame,end_frame,frame_rate,image_H,image_W)
          m=m+1

        j=end_frame+1
        v=v+1
        k=k+1

    i=end_frameW+1
    



'''
pathIn = './test_imgs/test4.jpg'
base_path = os.path.basename(pathIn) 
img = cv2.imread(pathIn) 
(H, W) = img.shape[:2] 
detect_result=get_detect_result(img,W,H,'test12.jpg')
'''




'''

start_frame=1
end_frame=686
frame_rate=2
image_H=720
image_W=1280
pathIn = './test_videos/sample2.mp4'
pathOut = './result_videos/sample5.mp4'
yolo_video(pathIn,pathOut,start_frame,end_frame,frame_rate,image_H,image_W)
'''
