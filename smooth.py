import cv2
img = cv2.imread('novitech.png')

#dst = cv2.GaussianBlur(src, (kernel),borderType)

gaussianImg = cv2.GaussianBlur(img, (41, 41), 0)

gaussianImg1 = cv2.GaussianBlur(img, (21, 21), 10)


cv2.imshow("GaussianBlur", gaussianImg)
cv2.imshow("GaussianBlur1", gaussianImg1)
		
