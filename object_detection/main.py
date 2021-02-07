import cv2 as cv
import numpy as np
import math
import matplotlib.pyplot as plt
import os
from ximea import xiapi     # API for camera
from scipy.spatial import distance
import object_detection
import cam

if __name__ == "__main__":
    counter = 0
    while True:
        cam = Cam()
        image = cam.take_img()
        detection = object_detection(image)
        img = detection.img_preprocessing(image)
        if not detection.distance(img):
            continue
        detection.show_img(img)
        counter += 1
