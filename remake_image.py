import cv2
import os

list_to_white = [
    {"h": 13, "w": 3},


]

list_to_black = [
]

img = cv2.imread(os.getcwd() + "\\sheet_test\\cc22.png", 0)

for i in range(0, len(list_to_white)):
    img[list_to_white[i]["h"]][list_to_white[i]["w"]] = 255

for i in range(0, len(list_to_black)):
    img[list_to_black[i]["h"]][list_to_black[i]["w"]] = 0

cv2.imwrite(os.getcwd() + f'\\sheet_test\\cc23.png', img)