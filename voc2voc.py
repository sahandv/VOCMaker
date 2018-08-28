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
#from lxml import etree as et
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
label_white_list = {'34','39','35','36','37','38','81'} # Change this to anything you like. Use http://apolloscape.auto/scene.html
make_additional_zeros = False
blackilist_to_other_label_chance = 50 ;   # Percentage
source_dir_root = '/home/sahand/sample xml/baidu'
output_dir_root = '/home/sahand/sample xml/baidu_rework'
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
            eroot = tree.getroot()
            eroot_original = eroot.copy()
            for child in eroot_original:
                if child.tag == "object":
                    if child._children[0].text in label_white_list:
#                        This class is white listed
                        print(child._children[0].text+" is white listed")
                    else:
#                        Thisclass is not white listed and this child will be removed
                        print(child._children[0].text+" is black listed")
                        eroot.remove(child)
                        
            # =============================================================================
            # Save output to file            
            # =============================================================================
            output_xml = ET.tostring(eroot, encoding='utf8').decode('utf8')
            with open(os.path.join(output_dir_root, file), "w+") as f1:
                f1.write(output_xml)


                        
                        
                        
            
            
            
            
            
            
            
            