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
#import xml.etree.ElementTree as et
from lxml import etree as et
import pandas as pd
import numpy as np
import os
import sys
import glob
from shutil import copyfile
import string
import random
# =============================================================================
# This code is intended to generate VOC formatted data out of Baidu dataset. It
# gets JSON annotations and generates XML files and other directory structures 
# as required.
# =============================================================================
# Project init
# Set file path
# =============================================================================
label_white_list = {33,34,35,36,37,38,39,81} # Change this to anything you like. Use http://apolloscape.auto/scene.html
make_additional_zeros = False
blackilist_to_other_label_chance = 50 ;   # Percentage
source_dir_root = '/media/sahand/Archive A/DataSets/Baidu/road01_ins/Label'
output_dir_root = '/media/sahand/Archive A/DataSets/BaiduVOC_02/'
expected_network_input_size = [300,300];
new_height = 2710
display_progress = True

if not os.path.exists(source_dir_root):
    sys.exit("Invalid source directory! Breaking...")
# =============================================================================
# Dictionary element access simplifier
# Credits to https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary
# =============================================================================
class Map(dict):

    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.iteritems():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.iteritems():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]
        
# =============================================================================
# Other functions:
# =============================================================================
def random_char(y):
    return ''.join(random.choice(string.letters) for x in range(y))


def get_expected_object_area(xmin,ymin,xmax,ymax):
    x = xmax-xmin
    y = ymax-ymin
    
    return x*y


def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    # usage: img = image_resize(img, height = 720)
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

# =============================================================================
# Scan and iterate over source directory 
# =============================================================================

for root, dirs, files in os.walk(source_dir_root):
    for file in files:
        if file.endswith(".json"):
            file_path = os.path.join(root, file)
            if display_progress == True:
                print(file_path)
            # =============================================================================
            # Read and parse JSON
            # =============================================================================            
                    
            with open(file_path, 'r') as fp:
                try:
                    json_output = js.load(fp)
                except ValueError:
                    print("error loading JSON")
                
            m = Map(json_output)
            objects = m.objects
            
            # =============================================================================
            # Creat output directories for SSD
            # =============================================================================
            
            dest_img_path = output_dir_root+'JPEGImages/'
            dest_set_path = output_dir_root+'ImageSets/Main/'
            dest_xml_path = output_dir_root+'Annotations/'
            dest_annot_json_path = output_dir_root+'Annotations_JSON/'
            if not os.path.exists(output_dir_root):
                os.makedirs(output_dir_root)
                os.makedirs(dest_xml_path)
                os.makedirs(dest_set_path)
                os.makedirs(dest_img_path)
                os.makedirs(dest_annot_json_path)
            
            
            # =================================================================
            # Generate input/output paths and names for image and annotation
            # =================================================================
            file_name_img = str.split(os.path.basename(file_path),'.')[0]+'.jpg'
            file_name_xml = str.split(os.path.basename(file_path),'.')[0]+'.xml'
            file_name_json = os.path.basename(file_path)
            
            file_path_img_source = file_path.replace(os.path.basename(file_path),file_name_img)
            file_path_img_source = file_path_img_source.replace('Label','ColorImage')
            
            img_out_path = dest_img_path+file_name_img
#            xml_out_path = dest_annot_path+file_name_xml
#            json_out_path = dest_annot_json_path+file_name_json
            
            # If the image already exist in dest dir, rename all files to new file (filename+rand_chrs) to prevent overwriting       
            if os.path.exists(img_out_path):
                chars = random_char(3)
                file_name_img = str.split(os.path.basename(file_path),'.')[0]+chars+'.jpg'
                file_name_xml = str.split(os.path.basename(file_path),'.')[0]+chars+'.xml'
                file_name_json =str.split(os.path.basename(file_path),'.')[0]+chars+'.json'
                
            img_out_path = dest_img_path+file_name_img
            xml_out_path = dest_xml_path+file_name_xml
            json_out_path = dest_annot_json_path+file_name_json
            
            folder_name = str.split(file_path_img_source,os.sep)[len(str.split(file_path_img_source,os.sep))-3]
            
            # =================================================================
            # Read Image            
            # =================================================================
            img = cv2.imread(file_path_img_source)
            orig_height, orig_width, channels = img.shape
            resize_ratio = float(float(new_height)/float(orig_height))
            # =================================================================
            # Render XML
            # =================================================================
            xml_annotation = et.Element('annotation')
            xml_folder = et.SubElement(xml_annotation, 'folder')
            xml_filename = et.SubElement(xml_annotation, 'filename')
            xml_path = et.SubElement(xml_annotation, 'path')
            xml_source = et.SubElement(xml_annotation, 'source')
            xml_database = et.SubElement(xml_source,'database')
            xml_size = et.SubElement(xml_annotation, 'size')
            xml_width = et.SubElement(xml_size,'width')
            xml_height = et.SubElement(xml_size,'height')
            xml_depth = et.SubElement(xml_size,'depth')
            xml_segmented = et.SubElement(xml_annotation, 'segmented')
            
            xml_folder.text = folder_name 
            xml_filename.text = file_name_img
            xml_path.text = img_out_path
            xml_database.text = 'Unknown'
            xml_width.text = str(int(m.imgWidth*resize_ratio))
            xml_height.text = str(int(m.imgHeight*resize_ratio))
            xml_depth.text = '3'                                               # For RGB/color images
            xml_segmented.text = '0'
            
            # Iterate over objecs found in JSON           
            
            for i_objects in range(len(objects)):
                label = objects[i_objects]['label']
                if label in label_white_list:
                    xmax = 0
                    ymax = 0
                    xmin = m.imgWidth*resize_ratio
                    ymin = m.imgHeight*resize_ratio
                    
                    for i_points in range(len(objects[i_objects]['polygons'][0])):
                        x_tmp = objects[i_objects]['polygons'][0][i_points][0]*resize_ratio
                        y_tmp = objects[i_objects]['polygons'][0][i_points][1]*resize_ratio
                        if  x_tmp > xmax:
                            xmax = x_tmp
                        if  y_tmp > ymax:
                            ymax = y_tmp
                        if  x_tmp < xmin:
                            xmin = x_tmp
                        if  y_tmp < ymin:
                            ymin = y_tmp
                            
                    expected_object_area = get_expected_object_area(xmin,ymin,xmax,ymax)
                    
                    if expected_object_area > 10:
                        if xmin-3 >= 0:
                            xmin = xmin-3
                        if ymin-3 >= 0:
                            ymin = ymin-3
                            
                        if xmax+3 <= int(m.imgWidth*resize_ratio):
                            xmax = xmax+3
                        if ymax+3 <= int(m.imgHeight*resize_ratio):
                            ymax = ymax+3
                            
                        xml_object = et.SubElement(xml_annotation, 'object')
                        xml_name = et.SubElement(xml_object,'name')
                        xml_pose = et.SubElement(xml_object,'pose')
                        xml_truncated = et.SubElement(xml_object,'truncated')
                        xml_difficult = et.SubElement(xml_object,'difficult')
                        xml_bndbox = et.SubElement(xml_object,'bndbox')
                        xml_xmin = et.SubElement(xml_bndbox,'xmin')
                        xml_ymin = et.SubElement(xml_bndbox,'ymin')
                        xml_xmax = et.SubElement(xml_bndbox,'xmax')
                        xml_ymax = et.SubElement(xml_bndbox,'ymax')
                        
                        xml_name.text = str(label)
                        xml_pose.text = 'Unspecified'
                        xml_truncated.text = '0'
                        xml_difficult.text = '0'
                            
                        xml_xmin.text = str(int(xmin))
                        xml_ymin.text = str(int(ymin))
                        xml_xmax.text = str(int(xmax))
                        xml_ymax.text = str(int(ymax))
                    
                else:
                    if random.random() < blackilist_to_other_label_chance and make_additional_zeros == True:
                        xmax = 0
                        ymax = 0
                        xmin = m.imgWidth*resize_ratio
                        ymin = m.imgHeight*resize_ratio
                        
                        for i_points in range(len(objects[i_objects]['polygons'][0])):
                            x_tmp = objects[i_objects]['polygons'][0][i_points][0]*resize_ratio
                            y_tmp = objects[i_objects]['polygons'][0][i_points][1]*resize_ratio
                            if  x_tmp > xmax:
                                xmax = x_tmp
                            if  y_tmp > ymax:
                                ymax = y_tmp
                            if  x_tmp < xmin:
                                xmin = x_tmp
                            if  y_tmp < ymin:
                                ymin = y_tmp
                                
                        expected_object_area = get_expected_object_area(xmin,ymin,xmax,ymax)
                        
                        if expected_object_area > 10:
                            if xmin-3 >= 0:
                                xmin = xmin-3
                            if ymin-3 >= 0:
                                ymin = ymin-3
                                
                            if xmax+3 <= int(m.imgWidth*resize_ratio):
                                xmax = xmax+3
                            if ymax+3 <= int(m.imgHeight*resize_ratio):
                                ymax = ymax+3
                                
                            xml_object = et.SubElement(xml_annotation, 'object')
                            xml_name = et.SubElement(xml_object,'name')
                            xml_pose = et.SubElement(xml_object,'pose')
                            xml_truncated = et.SubElement(xml_object,'truncated')
                            xml_difficult = et.SubElement(xml_object,'difficult')
                            xml_bndbox = et.SubElement(xml_object,'bndbox')
                            xml_xmin = et.SubElement(xml_bndbox,'xmin')
                            xml_ymin = et.SubElement(xml_bndbox,'ymin')
                            xml_xmax = et.SubElement(xml_bndbox,'xmax')
                            xml_ymax = et.SubElement(xml_bndbox,'ymax')
                            
                            xml_name.text = str(label)
                            xml_pose.text = 'Unspecified'
                            xml_truncated.text = '0'
                            xml_difficult.text = '0'
                                
                            xml_xmin.text = str(int(xmin))
                            xml_ymin.text = str(int(ymin))
                            xml_xmax.text = str(int(xmax))
                            xml_ymax.text = str(int(ymax))
            
            
            # =================================================================
            # Generate XML
            # =================================================================
            mydata = et.tostring(xml_annotation, pretty_print=True)  
            
            # =================================================================
            # Copy Image and XML to Dest
            # =================================================================
            with open(xml_out_path, "w+") as f1:
                f1.write(mydata)
            
            try:
                img = image_resize(img, height = new_height)
                cv2.imwrite(img_out_path,img)
            except cv2.error as e:
                    print("*Error occured while saving image '",file_path_img_source,"' to '",img_out_path,"'")
            
            try:
                copyfile(file_path, json_out_path)
            except EnvironmentError:
                    print("*Error occured while copying json '",file_path,"' to '",json_out_path,"'")


# =============================================================================
# Get list of files in directory and make train, test and val sets
# =============================================================================
                    
all_files = []
for root, dirs, files in os.walk(output_dir_root+'JPEGImages/'):
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

val_set.to_csv(dest_set_path+'val.txt',index=False,header=False)
train_set.to_csv(dest_set_path+'train.txt',index=False,header=False)
test_set.to_csv(dest_set_path+'test.txt',index=False,header=False)
train_val_set.to_csv(dest_set_path+'trainval.txt',index=False,header=False)
