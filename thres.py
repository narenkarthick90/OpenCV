#dst = cv2.threshold(src, threshold, maxValueForThreshold,binary,type)[1] 
import cv2

img=cv2.imread("novitech.png")

grayImg = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

thresholdImg = cv2.threshold(grayImg,170,255,cv2.THRESH_BINARY)[1]

cv2.imshow("original",img)

cv2.imshow("threshold.jpg",thresholdImg)
