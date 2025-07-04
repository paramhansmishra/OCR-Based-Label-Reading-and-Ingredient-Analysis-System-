import pytesseract
import cv2
from PIL import Image 
import numpy as np
import re
from general_dietary_guide import NUTRIENT_THRESHOLDS

img_path = r"Food_Inspector\db\Amul Butter\nutritional_info.jpg"
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
img = cv2.imread(img_path)
if img is None:
    print('no image')
else:
    #2---------------------------------
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    #de-noising
    denoised = cv2.bilateralFilter(gray,7,75,75)

    #3-------------------------------
    #Thresholding
    thresh = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,15,6)
    kernel = np.ones((1, 1), np.uint8)
    dilated = cv2.dilate(thresh, kernel, iterations=1)
    sharp = cv2.addWeighted(dilated, 1.5, gray, -0.5, 0)
    text = pytesseract.image_to_string(sharp)

    #4----------------------------------
    nutrient = {}
    lines = text.strip().splitlines()

    for line in lines:
        match = re.search(r"(.+?)\s[-:]?\s?(\d+\.?\d*)$",line)    
        if match:
            key = match.group(1).strip()
            val = float(match.group(2))   
            nutrient[key]=val
    # for k,v in nutrient.items():
    #     print(f"{k}:{v}")

    #5------------------------
    def analysis(nutrient):
        result = {}
        for nutri,val in nutrient.items():
            if nutri in NUTRIENT_THRESHOLDS:
                threshold, flag, note = NUTRIENT_THRESHOLDS[nutri]
                if flag=="high" and val > threshold:
                    result[nutri] = (val,f"High - {note}")
                elif flag == "low" and val < threshold:
                    result[nutri] = (val,f"low - {note}")
                elif flag == "caution" and val > threshold:
                    result[nutri] = (val,f"Carefull - {note}")
                elif flag == "harmful" and val>threshold:
                    result[nutri] = (val,f"Avoid Immidiately - {note}")

        return result
    final_output = analysis(nutrient)
    for k,(v,note) in final_output.items():
        print(f"{k}: {v} \nresult:- {note}")

    # cv2.imshow('Adaptive Threshold',sharp)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()