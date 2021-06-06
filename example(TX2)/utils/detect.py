import pycuda.autoinit 
import pycuda.driver as cuda
import tensorrt as trt
import time 
import cv2,os
import numpy as np
import utils.box_utils_numpy as box_utils



TRT_LOGGER = trt.Logger()
# 标签转换
ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
genderList = ['Child', 'Female','Male']
emotionList = ['angry','disgust', 'fear', 'happy','sad', 'surprise', 'neutral']

def get_age_nchw(filename):
    #image = cv2.imread(filename)
    image_cv = cv2.cvtColor(filename, cv2.COLOR_BGR2GRAY)
    image_cv = cv2.cvtColor(image_cv, cv2.COLOR_GRAY2RGB)
    image_cv = cv2.resize(image_cv, (224, 224))
    miu = np.array([0.485, 0.456, 0.406]).reshape(3, 1, 1)
    std = np.array([0.229, 0.224, 0.225]).reshape(3, 1, 1)
    img_np = np.array(image_cv, dtype=np.float)/255.
    img_np = img_np.transpose((2, 0, 1))
    img_np -= miu
    img_np /= std
    img_np_nchw = img_np[np.newaxis]
    img_np_nchw = np.tile(img_np_nchw,(1, 1, 1, 1))
    return img_np_nchw
def get_face_nchw(filename):
    image_cv = cv2.cvtColor(filename,cv2.COLOR_BGR2RGB)
    image_cv = cv2.resize(image_cv, (320, 240))

    image_mean = np.array([127, 127, 127])
    image_cv = (image_cv - image_mean) / 128
    blob_ = np.array(image_cv,dtype=np.float)
    blob_ = blob_.transpose((2,0,1))
    blob = blob_[np.newaxis]
    blob = np.tile(blob,(1,1,1,1)).astype(np.float32)
    return blob
def get_emotion_nchw(filename):
    image_cv = cv2.cvtColor(filename,cv2.COLOR_BGR2GRAY)
    image_cv = cv2.resize(image_cv, (64,64))
    x = image_cv.astype('float32')
    x = x / 255.0
    x = x - 0.5
    x = x * 2.0
    x = np.expand_dims(x, 0)
    x = np.expand_dims(x, -1)
    return x



class HostDeviceMem(object):
    def __init__(self, host_mem, device_mem):
        """
        host_mem: cpu memory
        device_mem: gpu memory
        """
        self.host = host_mem
        self.device = device_mem

    def __str__(self):
        return "Host:\n" + str(self.host)+"\nDevice:\n"+str(self.device)

    def __repr__(self):
        return self.__str__()

def allocate_buffers(engine):
    inputs, outputs, bindings = [], [], []
    stream = cuda.Stream()
    for binding in engine:
        # print(binding) # 绑定的输入输出
        # print(engine.get_binding_shape(binding)) # get_binding_shape 是变量的大小
        size = trt.volume(engine.get_binding_shape(binding))*engine.max_batch_size
        # volume 计算可迭代变量的空间，指元素个数
        # size = trt.volume(engine.get_binding_shape(binding)) # 如果采用固定bs的onnx，则采用该句
        dtype = trt.nptype(engine.get_binding_dtype(binding))
        # get_binding_dtype  获得binding的数据类型
        # nptype等价于numpy中的dtype，即数据类型
        # allocate host and device buffers
        host_mem = cuda.pagelocked_empty(size, dtype)  # 创建锁业内存
        device_mem = cuda.mem_alloc(host_mem.nbytes)    # cuda分配空间
        # print(int(device_mem)) # binding在计算图中的缓冲地址
        bindings.append(int(device_mem))
        #append to the appropriate list
        if engine.binding_is_input(binding):
            inputs.append(HostDeviceMem(host_mem, device_mem))
        else:
            outputs.append(HostDeviceMem(host_mem, device_mem))
    return inputs, outputs, bindings, stream

def get_engine(engine_file_path=""):
    """
    params max_batch_size:      预先指定大小好分配显存
    params onnx_file_path:      onnx文件路径
    params engine_file_path:    待保存的序列化的引擎文件路径
    params fp16_mode:           是否采用FP16
    params save_engine:         是否保存引擎
    returns:                    ICudaEngine
    """
    # 如果已经存在序列化之后的引擎，则直接反序列化得到cudaEngine
    if os.path.exists(engine_file_path):
        print("Reading engine from file: {}".format(engine_file_path))
        with open(engine_file_path, 'rb') as f, \
            trt.Runtime(TRT_LOGGER) as runtime:
            return runtime.deserialize_cuda_engine(f.read())  # 反序列化
    else:
        print("{} Not Found!!".format(engine_file_path))



def do_inference(context, bindings, inputs, outputs, stream, batch_size=1):
    # Transfer data from CPU to the GPU.
    [cuda.memcpy_htod_async(inp.device, inp.host, stream) for inp in inputs]
    # htod： host to device 将数据由cpu复制到gpu device
    # Run inference.
    context.execute_async_v2(bindings=bindings, stream_handle=stream.handle)
    # 当创建network时显式指定了batchsize， 则使用execute_async_v2, 否则使用execute_async
    # Transfer predictions back from the GPU.
    [cuda.memcpy_dtoh_async(out.host, out.device, stream) for out in outputs]
    # gpu to cpu
    # Synchronize the stream
    stream.synchronize()
    # Return only the host outputs.
    return [out.host for out in outputs]

def predict(width, height, confidences, boxes, prob_threshold, iou_threshold=0.3, top_k=-1):
    boxes = boxes[0]
    confidences = confidences[0]
    picked_box_probs = []
    picked_labels = []
    for class_index in range(1, confidences.shape[1]):
        probs = confidences[:, class_index]
        mask = probs > prob_threshold
        probs = probs[mask]
        if probs.shape[0] == 0:
            continue
        subset_boxes = boxes[mask, :]
        box_probs = np.concatenate([subset_boxes, probs.reshape(-1, 1)], axis=1)
        box_probs = box_utils.hard_nms(box_probs,
                                       iou_threshold=iou_threshold,
                                       top_k=top_k,
                                       )
        picked_box_probs.append(box_probs)
        picked_labels.extend([class_index] * box_probs.shape[0])
    if not picked_box_probs:
        return np.array([]), np.array([]), np.array([])
    picked_box_probs = np.concatenate(picked_box_probs)
    picked_box_probs[:, 0] *= width
    picked_box_probs[:, 1] *= height
    picked_box_probs[:, 2] *= width
    picked_box_probs[:, 3] *= height
    return picked_box_probs[:, :4].astype(np.int32)





efficient_trt_path = './utils/trt/efficient.trt'
face_trt_path = './utils/trt/ultra.trt'
emotion_trt_path = './utils/trt/emotion.trt'
engine_eff = get_engine(efficient_trt_path)
engine_face = get_engine(face_trt_path)
engine_emo = get_engine(emotion_trt_path)
# 创建CudaEngine之后,需要将该引擎应用到不同的卡上配置执行环境
context = engine_eff.create_execution_context()
context_face = engine_face.create_execution_context()
context_emo = engine_emo.create_execution_context()
inputs, outputs, bindings, stream = allocate_buffers(engine_eff)
inputs_face, outputs_face, bindings_face, stream_face = allocate_buffers(engine_face)
inputs_emo, outputs_emo, bindings_emo, stream_emo = allocate_buffers(engine_emo)
shape_of_output = [(1,4420,2),(1,4420,4)]
# Load data to the buffer

def get_FaceBox(frame,threshold=0.6):
    h, w = frame.shape[:2]
         
    blob = get_face_nchw(frame)
    inputs_face[0].host = blob.reshape(-1)
    outputs_face_ = do_inference(context_face, bindings=bindings_face, inputs=inputs_face, outputs=outputs_face, stream=stream_face)
    confidence,boxes = [output.reshape(shape) for output, shape in zip(outputs_face_, shape_of_output)]
    boxes = predict(w, h, confidence, boxes, threshold)

    return boxes








"""---------------------------------------------------------------"""
def detect(frame,ex_Flag,age_Flag,gender_Flag):# 一张图像不一定仅有一张人脸
    """
    INput:原生图像（经过镜像翻转),bbox为人脸位置(可以是多个)
    """
    label_str = []
    frameFace = frame
    t1 = time.time()
    bboxes =  get_FaceBox(frame,0.6)
    t2 = time.time()
    #print(t2-t1)


    for bbox in bboxes:
        bbox = bbox[:4]
        face = frameFace[bbox[1]:bbox[3],bbox[0]:bbox[2]]
        if(len(face) == 0):
            break
        label = ""
        if age_Flag or gender_Flag:
            img_np_nchw = get_age_nchw(face).astype(np.float32)
            inputs[0].host = img_np_nchw.reshape(-1)
            trt_outputs = do_inference(context, bindings=bindings, inputs=inputs, outputs=outputs, stream=stream) # numpy data
        if gender_Flag:
            genderPreds = trt_outputs[0].argmax()
            gender = genderList[genderPreds]
            label += "{}".format(gender)
        label += " "
        if age_Flag:
            age = trt_outputs[2]>0.5
            age = age.sum()
            age = ageList[age]
            label += "{}".format(age)
        label += ' '
        if ex_Flag:

            gray_face = get_emotion_nchw(face)
            inputs_emo[0].host = gray_face.reshape(-1)
            emotion_prediction =do_inference(context_emo, bindings=bindings_emo, inputs=inputs_emo, outputs=outputs_emo, stream=stream_emo)
            # 置信度
            #print(len(emotion_prediction[0]))
            emotion_probability = np.max(emotion_prediction[0])
            emotion = emotionList[np.argmax(emotion_prediction)]
            label += "{}".format(emotion)


        if(label != "  "):
            label_str.append(label)
        cv2.rectangle(frameFace, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), int(round(frameFace.shape[0] / 150)),3)
        cv2.putText(frameFace, label, (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2,cv2.LINE_AA)


    return frameFace,label_str

if __name__ == '__main__':
    img = cv2.imread('./02.jpg')
    img,stri = detect(img,1,1,1)
    print(stri)
    cv2.imwrite('im2.jpg',img)


