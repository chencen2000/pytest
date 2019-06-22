import sys
import cv2
import numpy as np


print(cv2.__version__)


def func_1():
    params = [(0, 0, 0), (5, 3, 0)]
    kernel = np.ones((3, 3), np.uint8)

    for p in params:
        m = cv2.imread(r'C:\Tools\avia\images\test.1\iphone6 Plus Space Gary\5747.1.jpg')
        gm = cv2.cvtColor(m, cv2.COLOR_BGR2GRAY)
        if p[0] > 0:
            gm = cv2.erode(gm, kernel, iterations=p[0])
        if p[1] > 0:
            gm = cv2.dilate(gm, kernel, iterations=p[1])
        gm = cv2.GaussianBlur(gm, (3, 3), 0)
        otsu, mt = cv2.threshold(gm, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        sigma = 0.25
        lower = max(1, (1-sigma)*otsu)
        upper = min(255, (1+sigma)*otsu)
        mt = cv2.Canny(gm, lower, upper)
        cv2.imwrite("temp_1.jpg", mt)


def prepare_ocr_image():
    kernel = cv2.getStructuringElement(shape=cv2.MORPH_RECT, ksize=(3, 3))
    img = cv2.imread(r'temp_txt_2.jpg')
    g = cv2.GaussianBlur(img, (3, 3), 0)
    g = cv2.cvtColor(g, cv2.COLOR_BGR2GRAY)
    ret, binary = cv2.threshold(g, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
    ret = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    return ret


