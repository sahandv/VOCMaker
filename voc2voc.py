#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 21:09:19 2018

@author: https://github.com/sahandv

USE PYTHON 2.7 FOR THIS CODE
"""
from __future__ import print_function
from os.path import isfile
import json as js
import cv2 as cv2
import random
import sys
#import xml.etree.ElementTree as et
from lxml import etree as et
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import os
import glob
from shutil import copyfile
import string
import random
# =============================================================================
# This code is intended to generate custom classes out of VOC format dataset. 
# Annotations are expected to be XML.
# =============================================================================
# Project init
# Set file path
# =============================================================================
label_white_list = {33,34,35,36,37,38,39,81} # Change this to anything you like. Use http://apolloscape.auto/scene.html
make_additional_zeros = False
blackilist_to_other_label_chance = 50 ;   # Percentage
source_dir_root = '/media/sahand/Archive A/DataSets/BaiduVOC_02/Annotations'
output_dir_root = '/media/sahand/Archive A/DataSets/BaiduVOC_02/newAnnotations'
expected_network_input_size = [300,300];
display_progress = True


# =============================================================================
# Scan in/output dirs and iterate over source directory 
# =============================================================================
if not os.path.exists(source_dir_root):
    sys.exit("Invalid source directory! Breaking...")

if not os.path.exists(output_dir_root):
                os.makedirs(output_dir_root)

for root, dirs, files in os.walk(source_dir_root):
    for file in files:
        if file.endswith(".xml"):
            file_path = os.path.join(root, file)
            if display_progress == True:
                print(file_path)
            # =============================================================================
            # Read and parse JSON
            # =============================================================================    
            tree = ET.parse(file_path)
            root = tree.getroot()
            for child in root:
                print(child.tag, child.attrib)
            
            
            
            
            
            
            
            
            