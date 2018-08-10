#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 11 00:47:08 2018

@author: https://github.com/sahandv

USE PYTHON 2.7 FOR THIS CODE
"""
import pandas as pd
import numpy as np
import cv2 as cv2
import os


# =============================================================================
# Inputs
# =============================================================================
input_dir = '/home'
output_dir = '/home/resized/'
image_ext = '.jpg'
display_progress = False
# =============================================================================
# Code
# =============================================================================
def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]
    if width is None and height is None:
        return image
    if width is None:

        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))
    resized = cv2.resize(image, dim, interpolation = inter)
    return resized

if not os.path.exists(output_dir):
    print('Making outputdir: '+output_dir)
    os.makedirs(output_dir)

print('Resizing images in: '+input_dir)
all_files = []
for root, dirs, files in os.walk(input_dir):
    for file in files:
        if file.endswith(image_ext):
            file_path = os.path.join(root, file)
            file_name = os.path.basename(file_path)
#            file_dir_path = file_path.replace(file_name,'')
            if display_progress == True:
                print(file_path)

            img = cv2.imread(file_path)
            img = image_resize(img, height = 720)
            cv2.imwrite(output_dir+file_name,img)
            
