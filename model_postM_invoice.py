# -*- coding: utf-8 -*-

from config import opencvFlag, GPU, IMGSIZE, ocrFlag
import keras
import tensorflow as tf
config = tf.ConfigProto(device_count = {'CPU': 4})
import os
os.environ["CUDA_VISIBLE_DEVICES"] = '-1'
# config = tf.ConfigProto()
# config.gpu_options.allow_growth = True
# config.gpu_options.per_process_gpu_memory_fraction = 0.8
# keras.backend.tensorflow_backend.set_session(tf.Session(config=config))

graph = tf.get_default_graph()
if not GPU:
    import os

    os.environ["CUDA_VISIBLE_DEVICES"] = '-1'  ##不启用GPU

if ocrFlag == 'torch':
    from crnn.crnn_torch import crnnOcr as crnnOcr  ##torch版本ocr
elif ocrFlag == 'keras':
    from crnn.crnn_keras import crnnOcr as crnnOcr  ##keras版本OCR
import cv2
import numpy as np

from text.detector.detectors import TextDetector
from apphelper.image import get_boxes, letterbox_image

from text.opencv_dnn_detect import angle_detect  ##文字方向检测,支持dnn/tensorflow
from apphelper.image import estimate_skew_angle, rotate_cut_img, xy_rotate_box, sort_box, box_rotate, solve

# if opencvFlag == 'opencv':
#     from text import opencv_dnn_detect as detect  ##opencv dnn model for darknet

# elif opencvFlag == 'darknet':
#     from text import darknet_detect as detect
# else:
#     ## keras版本文字检测
#     from text import keras_detectM_invoice as detect
from text import keras_detectM_invoice as detect


print("Text detect engine:{}".format(opencvFlag))

def text_detect(img,
                MAX_HORIZONTAL_GAP=30,
                MIN_V_OVERLAPS=0.6,
                MIN_SIZE_SIM=0.6,
                #原置信度0.7
                TEXT_PROPOSALS_MIN_SCORE=0.7,
                TEXT_PROPOSALS_NMS_THRESH=0.3,
                TEXT_LINE_NMS_THRESH=0.3,
                ):
    boxes, scores = detect.text_detect(np.array(img))
    print("这里是识别检测")
    boxes = np.array(boxes, dtype=np.float32)
    scores = np.array(scores, dtype=np.float32)
    textdetector = TextDetector(MAX_HORIZONTAL_GAP, MIN_V_OVERLAPS, MIN_SIZE_SIM)
    shape = img.shape[:2]
    boxes = textdetector.detect(boxes,
                                scores[:, np.newaxis],
                                shape,
                                TEXT_PROPOSALS_MIN_SCORE,
                                TEXT_PROPOSALS_NMS_THRESH,
                                TEXT_LINE_NMS_THRESH,
                                )

    text_recs = get_boxes(boxes)
    newBox = []
    rx = 1
    ry = 1
    for box in text_recs:
        x1, y1 = (box[0], box[1])
        x2, y2 = (box[2], box[3])
        x3, y3 = (box[6], box[7])
        x4, y4 = (box[4], box[5])
        newBox.append([x1 * rx, y1 * ry, x2 * rx, y2 * ry, x3 * rx, y3 * ry, x4 * rx, y4 * ry])
    return newBox


def crnnRec(im, boxes, leftAdjust=False, rightAdjust=False, alph=0.3, f=1.0):
    """
    crnn模型，ocr识别
    leftAdjust,rightAdjust 是否左右调整box 边界误差，解决文字漏检
    """
    results = []
    im = Image.fromarray(im)
    for index, box in enumerate(boxes):
        degree, w, h, cx, cy = solve(box)
        partImg, newW, newH = rotate_cut_img(im, degree, box, w, h, leftAdjust, rightAdjust, alph)
        text = crnnOcr(partImg.convert('L'))
        print("Boxj聚合识别:"+text)
        if text.strip() != u'':
            results.append({'cx': cx * f, 'cy': cy * f, 'text': text, 'w': newW * f, 'h': newH * f,
                            'degree': degree * 180.0 / np.pi})

    return results


def eval_angle(im, detectAngle=True):
    """
    估计图片偏移角度
    @@param:im
    @@param:detectAngle 是否检测文字朝向
    """
    angle = 0
    img = np.array(im)
    if detectAngle:
        angle = angle_detect(img=np.copy(img))  ##文字朝向检测
        if angle == 90:
            im = Image.fromarray(im).transpose(Image.ROTATE_90)
        elif angle == 180:
            im = Image.fromarray(im).transpose(Image.ROTATE_180)
        elif angle == 270:
            im = Image.fromarray(im).transpose(Image.ROTATE_270)
        img = np.array(im)

    return angle, img

def plot_box(img, boxes):
    blue = (0, 0, 0)  # 18
    tmp = np.copy(img)
    for box in boxes:
        cv2.rectangle(tmp, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), blue, 1)  # 19

    return Image.fromarray(tmp)

def model(img, detectAngle=True, config={}, leftAdjust=False, rightAdjust=False, alph=0.3):
    """
    @@param:img,
    @@param:ifadjustDegree 调整文字识别倾斜角度
    @@param:detectAngle,是否检测文字朝向
    """
    angle, img = eval_angle(img, detectAngle=detectAngle)  ##文字方向检测
    if opencvFlag != 'keras':
        img, f = letterbox_image(Image.fromarray(img), IMGSIZE)  ## pad
        img = np.array(img)
    else:
        f = 1.0  ##解决box在原图坐标不一致问题
    config['img'] = img
    text_recs = text_detect(**config)  ##检测
    newBox = sort_box(text_recs)
    result = crnnRec(np.array(img), newBox, leftAdjust, rightAdjust, alph, 1.0 / f)#识别
    return img, result, angle
####################################################################################################

from PIL import Image

from apphelper.image import xy_rotate_box, box_rotate, solve



def ocr(img):
    _, result, angle = model(img,
                                   detectAngle=True,  ##是否进行文字方向检测
                                   config=dict(MAX_HORIZONTAL_GAP=10,  ##字符之间的最大间隔，用于文本行的合并
                                               MIN_V_OVERLAPS=0.6,
                                               MIN_SIZE_SIM=0.6,
                                               TEXT_PROPOSALS_MIN_SCORE=0.1,
                                               TEXT_PROPOSALS_NMS_THRESH=0.3,
                                               TEXT_LINE_NMS_THRESH=0.1,  ##文本行之间测iou值
                                               ),
                                   leftAdjust=True,  ##对检测的文本行进行向左延伸
                                   rightAdjust=True,  ##对检测的文本行进行向右延伸
                                   alph=0.08,  ##对检测的文本行进行向右、左延伸的倍数
                                   )
    return result


