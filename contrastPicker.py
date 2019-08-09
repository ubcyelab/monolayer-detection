import cv2
import tkinter as tk
import numpy as np

image_contrast = None
pixel = 0#RANDOM DEFAULT VALUE

tol = 0.02

def pick_color(event,x,y,flags,param):
    
    if event == cv2.EVENT_LBUTTONDOWN:
        
        pixel = image_contrast[y,x]

        #HUE, SATURATION, AND VALUE (BRIGHTNESS) RANGES. TOLERANCE COULD BE ADJUSTED.
        upper =  pixel+tol
        lower =  pixel-tol
        print("threashold",lower, upper)
        print("contrast",pixel)
        print("position",x,y)

        #A MONOCHROME MASK FOR GETTING A BETTER VISION OVER THE COLORS 
        image_mask = cv2.inRange(image_contrast,lower,upper)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(6,6))
        image_mask = cv2.erode(image_mask,kernel,iterations = 1)
        cv2.imshow("Mask",image_mask)

        
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
    #plt.plot(bins,counts)
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
    #cv2.imshow("1",target )
    # get contrast
    contrast = 1 - np.divide(sample,target)
    #cv2.imshow("contrast",contrast*30)
    return contrast

def contrastfilter(img,up,down):
    width = img.shape[0]
    height = img.shape[1]
    mask = np.zeros((width,height))
    mask[(img > down) & (img < up)] = 1
    #cv2.imshow("contrastmask",mask)
    #mask = fill(mask.astype(np.uint8))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(4,4))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return mask        


def normalizedcontrast(img,back,dist):
    im = np.divide(img,back) * 255
    contrast = contrastfind(im.astype(np.uint16),dist)
    return contrast

def contrastpicker():

    global image_contrast, pixel

    #OPEN DIALOG FOR READING THE IMAGE FILE
    root = tk.Tk()
    root.withdraw() #HIDE THE TKINTER GUI
    background = cv2.imread(r"C:\Users\zhang\OneDrive\Desktop\2019_08_01\2019_08_01_5602.jpg",cv2.IMREAD_COLOR)
    background = background[165:1115,480:1430,:]
    b0,g0,r0 = cv2.split(background)
    image_src = cv2.imread(r"C:\Users\zhang\OneDrive\Desktop\2019_08_01\201908011634_13x11_11_4.jpg",cv2.IMREAD_COLOR)
    image_src = image_src[165:1115,480:1430,:]
    b,g,r = cv2.split(image_src)
    cv2.imshow("BGR",image_src)

    #CREATE THE contrast FROM THE BGR IMAGE
    image_contrast = normalizedcontrast(g,g0,2) # could be changed to red channel
    cv2.imshow("contrast",image_contrast)

    #CALLBACK FUNCTION
    cv2.setMouseCallback("contrast",pick_color)

    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__=='__main__':
    contrastpicker()