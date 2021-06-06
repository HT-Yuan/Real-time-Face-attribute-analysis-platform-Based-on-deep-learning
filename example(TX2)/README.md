### 运行命令: python Ui_login.py
### 环境配置：
### NVIDIA TX2: jetpack4.4（tensorRT==7.1 python==3.6)  pyqt5   opencv == 3.4

### 说明：整个系统运行在nvidia tx2 的模板例程 与PC版本的区别在于 
### 1.人脸检测算法使用了ultraface替代opencv人脸检测，原因在于opencv在嵌入式端设备运行效率低下(无法充分利用nvidia的gpu资源)
### 2.对人脸检测、性别识别与年龄段估计、表情属性分析算法均进行了tensorRT加速 pytorch->onnx->trt 量化模式为fp16
### 3.摄像头使用mpi板载摄像头
