import picamera
from time import sleep
import serial
import RPi.GPIO as GPIO
from subprocess import call
#send log data to google sheets
import ssl
import json
import sys
import time
import datetime
import os
import gspread
import subprocess
from oauth2client.client import SignedJwtAssertionCredentials
priKey= u"-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCL8HYC8xksPtWA\ntUPCKDyrNje8gTRdJUMVs/2KWIyIOiU5O+x0+NMuTMtP12YWFeRiPw+bPeiWbhvd\nU2gvpYZq3gReBokDkKSEUJ5mKftx9N6RG80m4Y2ycD9sLOhyLh8ByIwfY9PweZnQ\nvgpgfIQnOweDeit2h5Oitod0uDVNpRHXQySh3tbcoo2BRFES05gSrr73+LtWuihT\nR+SweRO2lB5sHUlhzlm4hns6BIVOrF1PRWrIFEw0lGbKp0KduNNvGlrBXdMnEhbk\nBQjNg4yphauPs9a+jbCEBCx8UdKRGFeZLOmHGQSm9mNdEQ2ejHN9L2QtzGqpxtGm\nOKmQw3lBAgMBAAECggEAOfmJ+pjaEfGKJEN0aeifkdLpbmgc2IYKb+BcpscemYV1\nTGvd/2vimajpBg/X1EiHkIhNn+QbCs9dLelTHYI22OlX59hPRTHUZpi7ttmnuUNY\nPcfFy1jgik9khx1nw34GDIgYPRzvfg3ywn8o72ZGnbYf28FuZjGu4Vc7cQir1Jl0\nn0tSyxNv8eAFAxncZhVOzBL/tsDpSeS0UKsBfM9IxyJCJUhQpmuj4WrhmZutgb0Y\nu9SOMyJ+lzlIB0F1vQ5NLj355xdwAMKx8S0XX79z/5ikNXU75Y7zUddNL3v1kDR+\nZPRUxm+5NR3lV5jn7G30Ku4aE62zhUU5BGqJu/JxvQKBgQC/S0JMP8p5+3d3y87q\nAXT4Wu5MMoYUblNLsKqpww2zcpUfwoHlXPJXlgE06T2mtX0DANrEzXMUGzHfM/fv\nC8/8grd7NBtLsogQ2/hxxvSvYKhkBaqjgi4UKZ8nIYXr5y0pV75yRbrsGOcj97r/\nyPDycbUzUSKVYvWg1RNC3H/jHwKBgQC7Rj2QyW9xwHqqHcBPL3M6En73uBAEdjNq\nqC783n7x0DOFC5+6gutHsxpyXxizWEMoed74dvNiRGZpcwLkvVQbs3Q2G2n3/Emo\nAlgvOdyM3ckTUmSIeUQK0BjnAWuFF+7LsVDOOAmvBTqDCHXrFheBYD0+TM03ozsS\npfxH7v53nwKBgEM6N7qEUKw96+Z2AenLSUhe7JBq0SQtAakAFXpDynTeN/pJaU0q\nNSEC3rmxnrEP5zc+/aNccK0IQaanpOKlzBp59fGehlk8DQWfyNhzi1p3JbbBJw7/\nmSIM3pnp9h7Jx91XsN6IEwEWX2UMkvOBsuwBeiTmxripZpl3SKWeyHMRAoGAOdEI\nps+ZqWu8MxL2UTwb/dzB+CaKQ2Zen1oHD6h9Vphpn3SkPoe2ra8cxhyX2p6wNSnS\n7bCDmV32pC2OwiG1esvfX+j8wUPRVZ5LrWDWt2KtdlqkkQGnQRNX7NGiaTenUJmQ\nken5C2C43MVa6lYqsZWNstMxNDEfxrUZ+vdM9o8CgYAily5LpmOyVFgmn9tKZEVQ\nuns4PpJ2Tl8AAoWIVIkIkGDZnQIFS2Zo6Cpx9rPKOkYyJvm091zN6Y91YdeNBK73\nexgzL4nAc5RNnBMwMGFS6m598tawP+eU/jih2KErCbAZ4gNeQERGOJdMO5PqjuxL\n4FnTJId4CgrUfyvsul3FGA==\n-----END PRIVATE KEY-----\n".encode("utf8")

gdocs_oauth_json='ultrasonic.json'

gdocs_spreadsheet_name='Faultstatus'

def login_open_sheet(oauth_key_file,spreadsheet):
    json_key=json.load(open(oauth_key_file),strict=False)
    credentials=SignedJwtAssertionCredentials(json_key['client_email'],priKey,['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive'])
    gc=gspread.authorize(credentials)
    worksheet=gc.open(spreadsheet).sheet1
    return worksheet
worksheet=None
def start_camera(i):
    camera=picamera.PiCamera()
    camera.resolution=(1024,768)
    camera.brightness=60
    camera.start_preview()
    camera.annotate_text='rail surface fault detected'
    sleep(5)
    camera.capture('/home/pi/Desktop/data/fault'+str(i)+'.jpg') 
    camera.stop_preview()
    camera.close()
    Upload = '/home/pi/Dropbox-Uploader/dropbox_uploader.sh upload /home/pi/Desktop/data/fault'+str(i)+'.jpg fault_detected'+str(i)+'.jpg'
    call ([Upload], shell=True)
    i=i+1
def crack_detect(i):
    import cv2
    import numpy as np
    from skimage.io import imread_collection
    from skimage import morphology
    import numpy as np
    col_dir = '/home/pi/Desktop/data/fault'+str(i)+'.jpg'
    col = imread_collection(col_dir)
    for img in col:
        img = cv2.resize(img,(300 , 300))
        img=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        cv2.imshow('img',img)
        img=cv2.medianBlur(img,9)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        gradient_image = cv2.morphologyEx(img, cv2.MORPH_GRADIENT, kernel)
        gradient_image=cv2.morphologyEx(gradient_image, cv2.MORPH_CLOSE, kernel)
        sobely = cv2.Sobel(gradient_image,cv2.CV_8U,0,1,ksize=3)
        denoised = cv2.fastNlMeansDenoising(sobely,None,50,7,21)
        kernel=cv2.getStructuringElement(cv2.MORPH_RECT,(1,1))
        th2=cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel)
        th3=cv2.morphologyEx(th2, cv2.MORPH_OPEN, kernel)
        cv2.imshow('processed output- crack',th3)
        surf=cv2.xfeatures2d.SURF_create()
        [kp, des] = surf.detectAndCompute(th3,None)
        cv2.imwrite('/home/pi/Desktop/outputs/crack'+str(i)+'.jpg',th3)
        i=i+1
        if len(kp)>120:
            print('no crack detected')
            cv2.imshow('no crack detected',img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            print('crack detected')
            cv2.imshow('FRACTURE DETECTED!', img)
            img2 = cv2.drawKeypoints(th3,kp,None,(0,0,255),4)
            cv2.imshow('FEATURE EXTRACTION OF FRACTURE',img2)
            Upload = '/home/pi/Dropbox-Uploader/dropbox_uploader.sh upload /home/pi/Desktop/outputs/crack'+str(i)+'.jpg crack_detected'+str(i)+'.jpg'
            call ([Upload], shell=True)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
def squats_detect(i):
    import cv2
    import numpy as np
    from skimage.io import imread_collection
    from skimage import morphology
    import numpy as np
    col_dir = '/home/pi/Desktop/data/fault'+str(i)+'.jpg'
    col = imread_collection(col_dir)
    for img in col:
        img = cv2.resize(img,(300 , 300))
        img=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        img=cv2.medianBlur(img,7)
        blur = cv2.GaussianBlur(img,(5,5),0)
        ret2,th2 = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        th2=cv2.bitwise_not(th2)
        cv2.imshow('otsu',th2)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        gradient_image = cv2.morphologyEx(th2, cv2.MORPH_GRADIENT, kernel)
        gradient_image=cv2.morphologyEx(gradient_image, cv2.MORPH_CLOSE, kernel)
        denoised = cv2.fastNlMeansDenoising(gradient_image,None,60,7,21)
        kernel=cv2.getStructuringElement(cv2.MORPH_RECT,(1,1))
        th2=cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel)
        th3=cv2.morphologyEx(th2, cv2.MORPH_OPEN, kernel)
        cv2.imshow('preprocessed image- squats',th3)
        surf=cv2.xfeatures2d.SURF_create()
        [kp, des] = surf.detectAndCompute(th3,None)
        cv2.imwrite('/home/pi/Desktop/outputs/squats'+str(i)+'.jpg',th3)
        i=i+1
        if len(kp)<200:
            return False
            print('corrugations detected')
            cv2.imshow('corrugations DETECTED!', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            print('squats detected')
            cv2.imshow('SQUATS DETECTED!', img)
            img2 = cv2.drawKeypoints(denoised,kp,None,(0,0,255),4)
            cv2.imshow('FEATURE EXTRACTION OF SQUATS',th3)
            Upload = '/home/pi/Dropbox-Uploader/dropbox_uploader.sh upload /home/pi/Desktop/outputs/squats'+str(i)+'.jpg squats_detected'+str(i)+'.jpg'
            call ([Upload], shell=True)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

def rust_detect(i):
    import cv2
    import numpy as np
    img=cv2.imread('/home/pi/Desktop/data/fault'+str(i)+'.jpg')
    img=cv2.resize(img,(360,360))
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    lower_red = np.array([0,50,50])
    upper_red = np.array([21,255,255])
    lower_red2 = np.array([175,50,50])
    upper_red2 = np.array([179,255,255])
# Threshold the HSV image to get only red colors
    mask1 = cv2.inRange(hsv, lower_red, upper_red)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask=mask1+mask2
    ret,maskbin = cv2.threshold(mask,127,255,cv2.THRESH_BINARY) 
    res=cv2.bitwise_and(img,img,mask=mask)
    cv2.imshow('rusted area',res)
    cv2.imwrite('/home/pi/Desktop/outputs/rust'+str(i)+'.jpg',res)
    height, width = maskbin.shape
    size=height * width
    percentage=(cv2.countNonZero(maskbin)/float(size))*100
    if percentage>0.3:
        print(str('%.2f'%percentage)+'% rust area found')
        Upload = '/home/pi/Dropbox-Uploader/dropbox_uploader.sh upload /home/pi/Desktop/outputs/rust'+str(i)+'.jpg rust_detected'+str(i)+'.jpg'
        call ([Upload], shell=True)
    else:
        print('no rust detected')
    cv2.waitKey(0)
    cv2.destroyAllWindows()
# detect GPS location
def GPS_detect():
    while True:
        lat_in_degrees = 12.971395275521685
        long_in_degrees = 79.15953446983758
        from time import sleep
        import webbrowser
        print("lat in degrees:"+str(lat_in_degrees)+" long in degree: "+ str(long_in_degrees)+ "\n")
        map_link = 'http://maps.google.com/?q=' + str(lat_in_degrees) + ',' + str(long_in_degrees)    #create link to plot location on Google map
        a=input('press 0 to plot location on google maps: ')
    #sleep(2)
        if (a=='0'):
            webbrowser.open(map_link)
            break
            
        
    #create table in google sheets
if worksheet is None:
    worksheet=login_open_sheet(gdocs_oauth_json,gdocs_spreadsheet_name)
GPIO.setmode(GPIO.BOARD)
in1=7
in2=11
in3=3
in4=5
GPIO.setup(in1,GPIO.OUT)
GPIO.setup(in2,GPIO.OUT)
GPIO.setup(in3,GPIO.OUT)
GPIO.setup(in4,GPIO.OUT)
GPIO.setwarnings(False)
i=1
try:
    arduino=serial.Serial('/dev/ttyACM0',9600,timeout=0.1)
    while True:
        data=arduino.readline()[:-2]
        #print(data)
        sleep(3)
        if data:
            if data==b'0':
                GPIO.output(in1,GPIO.HIGH)
                GPIO.output(in2,GPIO.LOW)
                GPIO.output(in3,GPIO.LOW)
                GPIO.output(in4,GPIO.HIGH)
                
            elif data==b'1':
                GPIO.output(in1,GPIO.LOW)
                GPIO.output(in2,GPIO.HIGH)
                GPIO.output(in3,GPIO.LOW)
                GPIO.output(in4,GPIO.LOW)
                arduino.close()
                start_camera(i)
                arduino.open()
                crack_detect(i)
                values=[[str(datetime.datetime.now()),"Railway line fracture detected","1"]]
                for line in values:
                    worksheet.append_row(line)
                    break
                GPS_detect()
                
            elif data=='11':
                GPIO.output(in1,GPIO.LOW)
                GPIO.output(in2,GPIO.HIGH)
                GPIO.output(in3,GPIO.LOW)
                GPIO.output(in4,GPIO.LOW)
                arduino.close()
                start_camera(i)
                arduino.open()
                out=squats_detect(i)
                if out==False:
                    values=[[str(datetime.datetime.now()),"Rail surface corrugations detected","1"]]
                    for line in values:
                        worksheet.append_row(line)
                        break
                else:
                    values=[[str(datetime.datetime.now()),"Rail surface squats detected","1"]]
                    for line in values:
                        worksheet.append_row(line)
                        break
        GPIO.output(in1,GPIO.LOW)
        GPIO.output(in2,GPIO.HIGH)
        GPIO.output(in3,GPIO.LOW)
        GPIO.output(in4,GPIO.LOW)
        arduino.close()
        start_camera(i)
        arduino.open()
        rust_detect(i)
        values=[[str(datetime.datetime.now()),"Railway Rust detected","1"]]
        for line in values:
            worksheet.append_row(line)
            break
        GPS_detect()
except KeyboardInterrupt:
    print ('keyboard interrupted')
finally:
    GPIO.cleanup()
