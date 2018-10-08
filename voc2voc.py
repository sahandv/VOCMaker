#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 21:09:19 2018

@author: https://github.com/sahandv

USE PYTHON 2.7 FOR THIS CODE
"""
from __future__ import print_function
import sys
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import os
from shutil import copyfile
# =============================================================================
# This code is intended to whitelist classes out of VOC format dataset. 
# Annotations are expected to be XML.
# Annotations with no object will be removed.
# =============================================================================
# Project init
# Set file path
# =============================================================================
label_white_list = {'bicycle','bus','car','motorbike','people','train','person'} # Change this to anything you like. Use http://host.robots.ox.ac.uk/pascal/VOC/voc2012/
make_additional_zeros = False
blackilist_to_other_label_chance = 50 ;   # Percentage
source_dir_root = '/home/sahand/Documents/VOCdevkit/VOC2012'
output_dir_root = '/home/sahand/Documents/VOCdevkit/VOC2012_limited'
output_dir_suffix = ''
display_progress = True


# =============================================================================
# Scan input directory
# Gerenerate output dirs
# Iterate over source directory 
# =============================================================================
if not os.path.exists(source_dir_root):
    sys.exit("Invalid source directory! Breaking...")

if not os.path.exists(output_dir_root):
                os.makedirs(output_dir_root)
if not os.path.exists(output_dir_root+os.sep+"Annotations"+output_dir_suffix):
                os.makedirs(output_dir_root+os.sep+"Annotations"+output_dir_suffix)
if not os.path.exists(output_dir_root+os.sep+"JPEGImages"+output_dir_suffix):
                os.makedirs(output_dir_root+os.sep+"JPEGImages"+output_dir_suffix)
if not os.path.exists(output_dir_root+os.sep+"ImageSets"+os.sep+"Main"):
                os.makedirs(output_dir_root+os.sep+"ImageSets"+os.sep+"Main")
                
##
                
for root, dirs, files in os.walk(source_dir_root+os.sep+'Annotations'):
    for file in files:
        if file.endswith(".xml"):
            file_path = os.path.join(root, file)
            if display_progress == True:
                print(file_path)
            # =================================================================
            # Read and parse JSON
            # =================================================================
            tree = ET.parse(file_path)
            eroot = tree.getroot()
            eroot_original = eroot.copy()
            have_object = False
            for child in eroot_original:
                if child.tag == "object":
                    if child._children[0].text in label_white_list:
#                        This class is white listed
                        have_object = True
                        print(child._children[0].text+" is white listed")
                    else:
#                        Thisclass is not white listed and this child will be removed
                        print(child._children[0].text+" is black listed")
                        eroot.remove(child)
                        
            # =================================================================
            # Save output to file
            # Copy image
            # =================================================================
            if have_object == True:
                output_xml = ET.tostring(eroot, encoding='utf8').decode('utf8')
                with open(os.path.join(output_dir_root+os.sep+"Annotations"+output_dir_suffix, file), "w+") as f1:
                    f1.write(output_xml)
                    
                image_in = source_dir_root+os.sep+"JPEGImages"+os.sep+str.split(os.path.basename(file),'.')[0]+'.jpg'
                image_out = output_dir_root+os.sep+"JPEGImages"+output_dir_suffix+os.sep+str.split(os.path.basename(file),'.')[0]+'.jpg'
                try:
                    copyfile(image_in, image_out)
                except EnvironmentError:
                    print("*Error occured while copying image '",source_dir_root,"' to '",image_out,"'")

# =============================================================================
# Get list of files in directory and make train, test and val sets
# =============================================================================

all_files = []
for root, dirs, files in os.walk(output_dir_root+os.sep+'JPEGImages'):
    for file in files:
        if file.endswith(".jpg"):
            file_path = os.path.join(root, file)
            print(file_path)
            file_name = str.split(os.path.basename(file_path),'.')[0]
            all_files.append(file_name)
            
TrainDataRaw = pd.DataFrame(all_files)

# TrainVal set
remove_n = int(TrainDataRaw.shape[0]/6)
drop_indices = np.random.choice(TrainDataRaw.index, remove_n, replace=False)
train_val_set = TrainDataRaw.drop(drop_indices)
# Test set (remaining)
test_set = TrainDataRaw.loc[drop_indices]

# Train and Val sets
remove_n = int(train_val_set.shape[0]/5)
drop_indices = np.random.choice(train_val_set.index, remove_n, replace=False)
train_set = train_val_set.drop(drop_indices)
val_set = train_val_set.loc[drop_indices]

val_set.to_csv(output_dir_root+os.sep+"ImageSets"+os.sep+"Main"+os.sep+'val.txt',index=False,header=False)
train_set.to_csv(output_dir_root+os.sep+"ImageSets"+os.sep+"Main"+os.sep+'train.txt',index=False,header=False)
test_set.to_csv(output_dir_root+os.sep+"ImageSets"+os.sep+"Main"+os.sep+'test.txt',index=False,header=False)
train_val_set.to_csv(output_dir_root+os.sep+"ImageSets"+os.sep+"Main"+os.sep+'trainval.txt',index=False,header=False)









