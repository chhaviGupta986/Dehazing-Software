import cv2
import math
import numpy as np

#DARK CHANNEL 
def DCP(img,r):
    neighbourhood = 2*r + 1
    B,G,R = cv2.split(img)    #opencv follows bgr instad of rgb
    min_bgr = cv2.min(cv2.min(B,G),R)   
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(neighbourhood,neighbourhood))
    dark = cv2.erode(min_bgr,kernel)
    #RETURNS DARK CHNANEL
    return dark

def EstimateTransmap(img, A, r, omega):
    #omega = 0.95
    img_temp = np.empty(img.shape, img.dtype)
    for i in range(3):
        img_temp[:,:,i] = img[:,:,i]/A[0,i]
    trans = 1 - omega*DCP(img_temp, r)
    return trans

#ATMOSPHERIC LIGHT
def EstimateAL(img,dark_channel):
    h,w = img.shape[:2]
    img_size = h*w
    num_pixel = int(max(math.floor(img_size/1000),1))
    
    img_temp = img.reshape(img_size,3)
    dark_temp = dark_channel.reshape(img_size,1)
    
    index = dark_temp[:,0].argsort()
    index_use = index[img_size-num_pixel:]
    
    AL_sum = np.zeros([1,3])
    for i in range(num_pixel):
        AL_sum = AL_sum + img_temp[index_use[i]]
        
    AL = AL_sum/num_pixel
    thread = np.array([[0.95,0.95,0.95]])
    A = cv2.min(AL,thread)
    return A
def estimate_haze_density(image):
#calculating dark channel of the image
    dark_channel = DCP(image)

#estimating atmospheric light
    atmospheric_light = EstimateAL(image, dark_channel)

#ealculating haze density
    haze_density = 1.0 - (np.min(atmospheric_light) / 255.0)

    return haze_density

def Guided_filter(I,p,r,eps):
    mean_I = cv2.boxFilter(I, cv2.CV_64F, (r,r))
    mean_p = cv2.boxFilter(p, cv2.CV_64F, (r,r))
    corr_I = cv2.boxFilter(I*I, cv2.CV_64F, (r,r))
    corr_Ip = cv2.boxFilter(I*p, cv2.CV_64F, (r,r))
    
    var_I = corr_I - mean_I*mean_I
    cov_Ip = corr_Ip - mean_I*mean_p
    
    a = cov_Ip / (var_I + eps)
    b = mean_p - a*mean_I
    
    mean_a = cv2.boxFilter(a, cv2.CV_64F, (r,r))
    mean_b = cv2.boxFilter(b, cv2.CV_64F, (r,r))
    
    q = mean_a * I + mean_b
    
    return q

def dehaze_frame(img, r, n = 8, thre = 0.1, eps = 0.001, omega = 0.8):    
    #img_pro=img.astype('float64')/255
    img_pro=np.float64(img)/255
    J_dark=DCP(img_pro, r)
    A = EstimateAL(img_pro, J_dark)
    t = EstimateTransmap(img_pro, A, r, omega)
    
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_gray = np.float64(img_gray)/255
    t_ref = Guided_filter(img_gray,t,r*n,eps)
    
    t_thre = cv2.max(t_ref, thre)
    ret = np.empty(img_pro.shape, img_pro.dtype)
    for i in range(3):
        ret[:,:,i] = (img_pro[:,:,i]-A[0,i])/t_thre + A[0,i]
    
    return ret
