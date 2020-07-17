from flask import Flask, redirect, url_for, request, render_template
import pytesseract
import cv2
import re
from PIL import Image
from io import BytesIO
import base64

app = Flask(__name__)

@app.route("/")
def index():
    
    return render_template("upload.html")

@app.route('/upload', methods=["GET","POST"])
def upload_image():
    data1=""
    data2=""
    if request.method=="POST":
        data1=request.form['value1']
        data2=request.form['value2']
    data1=str.encode(data1)
    data2=str.encode(data2)
    #Extracting Adhar details
    #decoding base64 to image 
    im=Image.open(BytesIO(base64.b64decode(data1)))
    im.save('test.png','PNG')
    
    #if .exe file is present in working directory then we can skip this line
    pytesseract.pytesseract.tesseract_cmd=r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    
    img=cv2.imread('test.png')
    
    #preprocessing the image 
    #convert image to gray
    img=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    
    #applying adaptive_threshold
    img=cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY, 57 , 22)
    
    config = ('-l eng --oem 1 --psm 3')
    #date_config =  ('-l eng --psm 12')
    #custom_config = r'--oem 3 --psm 6 outputbase digits'
    text=str(pytesseract.image_to_string(img,config=config))
    #d = pytesseract.image_to_data(img, output_type=Output.DICT)
    #numbers= str(pytesseract.image_to_string(img,config=custom_config))
    #date=str(pytesseract.image_to_string(img,config=date_config))
    text=text.split('\n')
    text = [i for i in text if i]
    adhar_dict={"Name":"","Gender":"","DOB":"","Adhar_ID":""}
    j=""
    for i in text:
        if(re.search('MALE|Male',i)):
            adhar_dict['Gender']='MALE'
        elif(re.search('FEMALE|Female',i)):
            adhar_dict['Gender']='FEMALE'
        #date pattern in regex
        y=re.search('(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[012])/(19|20)\d\d$',i)
        if y:
            adhar_dict['DOB']=y.string.split(':')[1]
            adhar_dict['Name']=j
        #adhar_card_no pattern in regex    
        x=re.match("([0-9]{4} [0-9]{4} [0-9]{4})",i)
        if x:
            adhar_dict['Adhar_ID']=x.string
        j=i
    print(adhar_dict)
    
    #Extracting PAN details
    im=Image.open(BytesIO(base64.b64decode(data2)))
    im.save('test.png','PNG')
    pytesseract.pytesseract.tesseract_cmd=r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    img=cv2.imread('test.png')
    img=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    img=cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY, 57 , 22)
  
    config = ('-l eng --oem 1 --psm 3')
    text=str(pytesseract.image_to_string(img,config=config))
    text=text.split('\n')
    text = [i for i in text if i]
    print(text)
    
    pan_dict={"Name":"","Father's Name":"","DOB":"","PAN_NO":""}
    names=[]
    for i in text:
        if re.search('^[A-Z \d\W]+$',i):
            names.append(i)
        #date pattern in regex
        y=re.search('(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[012])/(19|20)\d',i)
        if y:
            pan_dict["DOB"]=y.string.split(' ')[0]
        #pan_no pattern in regex
        x=re.match("([A-z]{5}[0-9]{4}[A-Z]{1})",i)
        if x:
            pan_dict["PAN_NO"]=x.string
    p_name=names[0]
    f_name=names[1]

    for i in names:
        if(re.match("(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[012])/(19|20)\d",i)):
            break
        else:
            p_name=f_name
            f_name=i
    pan_dict["Name"]=p_name
    pan_dict["Father's Name"]=f_name
    print(pan_dict)
    return render_template("details.html",name=adhar_dict["Name"],gender=adhar_dict["Gender"],dob=adhar_dict["DOB"],a_id=adhar_dict["Adhar_ID"],pname=pan_dict["Name"],p_fname=pan_dict["Father's Name"],p_dob=pan_dict["DOB"],pan_num=pan_dict["PAN_NO"])

if __name__ == '__main__':
    app.run(debug=True)