import cv2 as cv
import numpy as np
# 检测人脸并绘制人脸bounding box


def expre_preprocess_input(x, v2=True):
    x = cv.resize(x, (64,64))

    x = x.astype('float32')
    x = x / 255.0
    if v2:
        x = x - 0.5
        x = x * 2.0
    x = np.expand_dims(x, 0)
    x = np.expand_dims(x, -1)
    return x


