# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 15:16:23 2019

@author: zhang
"""

import cv2 
import numpy as np
import time
from matplotlib import pyplot as plt
from skimage.morphology import remove_small_objects


# functions
def contrastfind(img,dist,name):
    # get hist and setup
    img = cv2.GaussianBlur(img,(5,5),0)
    counts = cv2.calcHist([img],[0],None,[400],[0, 400])
    counts = np.transpose(counts)
    counts = counts[0]
    bins = np.arange(0,len(counts),1)
    target = img.copy()
    sample = img.copy()
    # get background
    threshold = bins[np.where(counts > 5000)]
    plt.plot(bins,counts)
    maxbin = bins[np.where(counts == max(counts))]
    threshold = threshold[np.where(threshold >= max((maxbin-dist),0))]
    threshold = threshold[np.where(threshold <= min((maxbin+dist),len(counts)))]
    #print(threshold)
    thresholdup = max(threshold)
    thresholddown = min(threshold)
    mean = (thresholdup + thresholddown) / 2
    #print(mean)
    # get threshold
    target[sample > thresholdup] = mean
    target[sample < thresholddown] = mean
    # get contrast
    contrast = 1 - np.divide(sample,target)
    cv2.imshow(name+"contrast",contrast*30)
    return contrast

def contrastfilter(img,up,down,name):
    width = img.shape[0]
    height = img.shape[1]
    mask = np.zeros((width,height))
    mask[(img > down) & (img < up)] = 1
    cv2.imshow(name+"contrastmask",mask)
    #mask = fill(mask.astype(np.uint8))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return mask



    

def fill(img):
    # Mask used to flood filling.
    # Notice the size needs to be 2 pixels than the image.
    im_th = img * 255
    
    h, w = im_th.shape[:2]
    mask = np.zeros((h + 2, w + 2), np.uint8)
    
    im_floodfill = im_th.copy()
    
    # Floodfill from point (0, 0)
    cv2.floodFill(im_floodfill, mask, (450,450), 255);
    
    # Invert floodfilled image
    im_floodfill_inv = cv2.bitwise_not(im_floodfill)
    
    # Combine the two images to get the foreground.
    fill_image = im_th | im_floodfill_inv
    return fill_image

def label(mask,img):
    im = img.copy()
    b = im[:,:,0]
    g = im[:,:,1]
    r = im[:,:,2]
    r[mask==1] = 0
    g[mask==1] = 255
    b[mask==1] = 0
    res = cv2.merge((b,g,r))
    return res

def normalizedfilter(img,back,up,down,dist,name):
    im = np.divide(img,back) * 255
    cv2.imshow("normalized"+name,img)
    contrast = contrastfind(im.astype(np.uint16),dist,name)
    mask = contrastfilter(contrast,up,down,name)
    return mask



#  constant

#gup,gdown = 0.14,0.01
#rup,rdown = -3.5,-14.7
#bup,bdown = 0.6,-0.1

#gup,gdown = 0.01,-0.01
#rup,rdown = 0.01,-0.01
#bup,bdown = 0.6,-0.1

gup,gdown = 0.121,0.065
rup,rdown = 0.07,0.01
bup,bdown = 0.6,-0.1

#gup,gdown = -17,-18
#rup,rdown = 10,-29
#bup,bdown = 0.6,-0.1


# main

def monodetect():
    begin = time.time()
    
    background = cv2.imread(r"C:\Users\zhang\OneDrive\Desktop\2019_08_01\2019_08_01_5602.jpg",cv2.IMREAD_COLOR)
    #background = cv2.imread(r"E:\2019_08_01_5289.jpg",cv2.IMREAD_COLOR)
    background = background[165:1115,480:1430,:]
    b0,g0,r0 = cv2.split(background)
    #r0 = cv2.GaussianBlur(r0,(5,5),0)
    #g0 = cv2.GaussianBlur(g0,(5,5),0)
    
    imSample = cv2.imread(r"C:\Users\zhang\OneDrive\Desktop\2019_08_01\201908011634_13x11_11_4.jpg",cv2.IMREAD_COLOR)
    #imSample = cv2.imread(r"E:\201908011536_13x11_11_3 (original).jpg",cv2.IMREAD_COLOR)
    imSample = imSample[165:1115,480:1430,:]
    cv2.imshow("imSample",imSample)
    b,g,r = cv2.split(imSample)
    #r = cv2.GaussianBlur(r,(5,5),0)
    #g = cv2.GaussianBlur(g,(5,5),0)

    
    maskg = normalizedfilter(g,g0,gup,gdown,2,"g")

    maskr = normalizedfilter(r,r0,rup,rdown,2,"r")
    
    mask = np.logical_and(maskg,maskr).astype(np.uint8)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(4,4))
    mask = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_OPEN, kernel)
    
    
    mask = fill(mask.astype(np.uint8))
    cv2.imshow("filled",mask)
    
    mask = remove_small_objects(mask.astype(np.bool),110)
    #cv2.imshow("final",mask.astype(np.uint8)*100)
    
    
    res = label(mask,imSample)
    cv2.imshow("finalresult",res) 
    
    num_labels,labels,stats,centroids = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 3, cv2.CV_32S)
    
    end = time.time()
    
    print("Running time: ", end-begin)
    print("There are " + str(num_labels - 1) + " monolayers.")


monodetect()











    

