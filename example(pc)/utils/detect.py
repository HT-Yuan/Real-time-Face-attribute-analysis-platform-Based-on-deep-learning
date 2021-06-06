import cv2 as cv
import numpy as np
import torch
import torchvision.transforms as transforms
from PIL import Image
from keras.models import load_model
from utils.utils import expre_preprocess_input

# 网络模型  和  预训练模型


face_cascade = cv.CascadeClassifier('models/haarcascade_frontalface_default.xml')

age_genderModel = torch.load('models/efficientnet-b0.pth',map_location = 'cpu')

age_genderModel.eval()
emotionNet = load_model("models/fer2013_mini_XCEPTION.102-0.66.hdf5", compile=False)


# 标签转换
ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
genderList = ['Child', 'Female','Male']
emotionList = ['angry','disgust', 'fear', 'happy','sad', 'surprise', 'neutral']


agegender_size =224
age_gender_Transforms = transforms.Compose([
            transforms.Grayscale(num_output_channels=3),
            transforms.Resize(agegender_size),
            transforms.CenterCrop(agegender_size),
            transforms.ToTensor(),transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])


"""---------------------------------------------------------------"""
def detect(frame,ex_Flag,age_Flag,gender_Flag):# 一张图像不一定仅有一张人脸
    """
    INput:原生图像（经过镜像翻转),bbox为人脸位置(可以是多个)
    """
    label_str = []
    frameFace = frame
    bboxes =  face_cascade.detectMultiScale(frame, 1.3, 5)
    
    for bbox in bboxes:
        face = frameFace[bbox[1]:bbox[1]+bbox[3],bbox[0]:bbox[0]+bbox[2]]
        if(len(face) == 0):
            break
        label = ""
        if age_Flag or gender_Flag:
            age_inputs = Image.fromarray(face)
            age_inputs = age_gender_Transforms(age_inputs)
            age_inputs = torch.unsqueeze(age_inputs, 0)
            output_age,output_gender,pro_age = age_genderModel(age_inputs)
        if gender_Flag:
            _, genderPreds = torch.max(output_gender.data, 1)
            print(output_gender.data)
            gender = genderList[genderPreds]
            #gender = 'Male'
            label += "{}".format(gender)
        label +=" "
        if age_Flag:
            pro_age = pro_age > 0.5
            agePreds = torch.sum(pro_age, dim=1)
            age = ageList[agePreds]
            label += "{}".format(age)
        label +=" "

        # 灰度图像为表情识别需要
        if ex_Flag:
            gray_face = cv.cvtColor(face, cv.COLOR_BGR2GRAY)
            gray_face = expre_preprocess_input(gray_face,True)
            emotion_prediction = emotionNet.predict(gray_face)
            # 置信度
            emotion_probability = np.max(emotion_prediction)
            emotion = emotionList[np.argmax(emotion_prediction)]
            label += "{}".format(emotion)

        if(label != "  "):
            label_str.append(label)
        cv.rectangle(frameFace, (bbox[0], bbox[1]), (bbox[0]+bbox[2], bbox[1]+bbox[3]), (0, 255, 0), int(round(frameFace.shape[0] / 150)),8)
        cv.putText(frameFace, label, (bbox[0], bbox[1] - 10), cv.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2,cv.LINE_AA)

    return frameFace,label_str
