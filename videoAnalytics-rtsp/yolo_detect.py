# -*- coding: utf-8 -*-
import numpy as np 
import os 
import time 
import cv2
#######################################   
def yolo_detect(pathIn='', 
                 pathOut=None, 
                 label_path='./cfg/coco.names', 
                 config_path='./cfg/yolov3.cfg', 
                 weights_path='./cfg/yolov3.weights', 
                 confidence_thre=0.5, 
                 nms_thre=0.3, 
                 jpg_quality=80): 
       
     
         LABELS = open(label_path).read().strip().split("\n") 
      
         # 为每个类别随机匹配边界框颜色
         nclass = len(LABELS) 
         np.random.seed(42) 
         COLORS = np.random.randint(0, 255, size=(nclass, 3), dtype='uint8')
 
         #载入图片并获取图片维度
         base_path = os.path.basename(pathIn) 
         img = cv2.imread(pathIn) 
         (H, W) = img.shape[:2] 

   
         # 加载模型配置文件和权重文件
         print("loading yolo...") 
         net = cv2.dnn.readNetFromDarknet(config_path, weights_path) 

   
         # 获取YOLO输出层的名字
         ln = net.getLayerNames() 
         ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()] 

         # 将图片转换为blob，并设置图片尺寸
         # YOLO 前馈网络计算，获取边界框和相应概率
         blob = cv2.dnn.blobFromImage(img, 1 / 255.0, (416, 416), swapRB=True, crop=False)
         net.setInput(blob)
         start = time.time() 
         layerOutputs = net.forward(ln) 
         end = time.time()

  
         print("YOLO modle spent {:.2f} second predicting this image".format(end - start))

   
         # 初始化（YOLO执行完毕后）边界框，概率（置信度）和类别
         boxes = [] 
         confidences = [] 
         classIDs = []

         # 迭代每个输出层，总共三个
         for output in layerOutputs:
     
          # 迭代每个检测
          for detection in output: 
  
           # 提取类别ID和置信度
           scores = detection[5:] # 从下标为5的元素开始截取列表
           classID = np.argmax(scores) # score中最大值的下标
           confidence = scores[classID] # 得分最高的score

           # 只保留阈值的边界值置信度大于
           if confidence > confidence_thre: 
             # 将边界框的坐标还原至与原图片相匹配
             box = detection[0:4] * np.array([W, H, W, H]) # detection[0],detection[1],detection[2],detection[3],
             (centerX, centerY, width, height) = box.astype("int") # 转换box数组的数据类型为int

             # 计算边界框左上角的位置
             x = int(centerX - (width / 2))
             y = int(centerY - (height / 2)) 

            # 更新边界框，置信度，和类别
             boxes.append([x, y, int(width), int(height)]) 
             confidences.append(float(confidence)) 
             classIDs.append(classID) 

          #使用非极大值抑制方法抑制弱、重叠边框
          idxs = cv2.dnn.NMSBoxes(boxes, confidences, confidence_thre, nms_thre) 

          #确保至少一个边框值
          if len(idxs) > 0:
            # 迭代每个边框值
            for i in idxs.flatten():
              #提取边界框的坐标
              (x, y) = (boxes[i][0], boxes[i][1])
              (w, h) = (boxes[i][2], boxes[i][3])

              
              color = [int(c) for c in COLORS[classIDs[i]]]
              #print(classIDs[i])
              #print(color)
              cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
              text = '{}: {:.3f}'.format(LABELS[classIDs[i]], confidences[i])
              #print(text)
              (text_w, text_h), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
              #cv2.rectangle(img, (x, y-text_h-baseline), (x + text_w, y), color, -1)
              #cv2.putText(img, text, (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

     
          if pathOut is None:
            cv2.imwrite('with_box_'+base_path, img, [int(cv2.IMWRITE_JPEG_QUALITY), jpg_quality])
          else:
            cv2.imwrite(pathOut, img, [int(cv2.IMWRITE_JPEG_QUALITY), jpg_quality])
