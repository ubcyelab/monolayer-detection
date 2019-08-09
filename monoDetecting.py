# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 15:16:23 2019

@author: zhang
"""

import cv2 
import numpy as np
from skimage.morphology import remove_small_objects
# from matplotlib import pyplot as plt

# functions
def contrastfind(img,dist):
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
    # plt.plot(bins,counts)
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
    #cv2.imshow(name+"1",target )
    # get contrast
#    print(sample is target)
    contrast = 1 - np.divide(sample,target)
    #cv2.imshow(name+"contrast",-contrast/30)
    return contrast

def contrastfilter(img,up,down):
    width = img.shape[0]
    height = img.shape[1]
    mask = np.zeros((width,height))
    mask[(img > down) & (img < up)] = 1
    # cv2.imshow(name+"contrastmask",mask)
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
    r[mask==255] = 0
    g[mask==255] = 255
    b[mask==255] = 0
    res = cv2.merge((b,g,r))
    return res

def normalizedfilter(img,back,up,down,dist):
    im = img / back * 255
    contrast = contrastfind(im.astype(np.uint16),dist)
    mask = contrastfilter(contrast,up,down)
    return mask


#  constant

gup,gdown = 0.121,0.065
rup,rdown = 0.07,0.01
bup,bdown = 0.6,-0.1


# main
def monoDetect(backpath,filepath,ResFolderPath,size,loc,nowStr,f):
#    begin = time.time()
    
    background = cv2.imread(backpath,cv2.IMREAD_COLOR)
    background = background[165:1115,480:1430,:]
    b0,g0,r0 = cv2.split(background)
    
    imSample = cv2.imread(filepath,cv2.IMREAD_COLOR)
    imSample = imSample[165:1115,480:1430,:]
    b,g,r = cv2.split(imSample)
    
    
    maskg = normalizedfilter(g,g0,gup,gdown,2)
    maskr = normalizedfilter(r,r0,rup,rdown,2)
    
    mask = np.logical_and(maskg,maskr).astype(np.uint8)
    
    # imopen
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(4,4))
    mask = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_OPEN, kernel)
    
    # floodfill
    mask = fill(mask.astype(np.uint8))
    
    # remove
    num,labels,stats,centroids = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 3, cv2.CV_32S) 
    if num > 2:
        mask = remove_small_objects(mask.astype(np.bool),110)
    elif num == 2:
        area =  stats[1,4]
        if area < 110:
           mask=np.zeros((950,950))
           
#    try:
#         mask = remove_small_objects(mask.astype(np.int),200)
#    except UserWarning:
#        pass
    
    # label
    res = label(mask,imSample)
    # cv2.imshow("finalresult",res) 
    
    # count
    num_labels,labels,stats,centroids = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 3, cv2.CV_32S)
    
    # summary
    filename = '%s_%dx%d_%d_%d.jpg' % (
        nowStr, size[0], size[1], loc[0], loc[1])
    
    filename2 = '%s_%dx%d_%d_%d (original).jpg' % (
        nowStr, size[0], size[1], loc[0], loc[1])
    

    if num_labels > 1:
       cv2.imwrite(ResFolderPath + filename, res)
       cv2.imwrite(ResFolderPath + filename2, imSample)
       f.write(str(loc)+" "+str(num_labels - 1)+"\r\n")
       f.write(str(stats[1:,:])+"\r\n")
       
    
#    end = time.time()
    
#    print(end-begin)
    print("There are " + str(num_labels - 1) + " monolayers.")













    

