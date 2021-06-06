### 说明
#### 1.该版本默认运行在cpu设备，gpu仅需小小改动，不在赘述
#### 2.人脸检测使用opencv的haar检测；性别识别与年龄段估计使用基于efficientnet的多任务网络(adience >0.85);
#### 表情识别为Real-time Convolutional Neural Networks for Emotion and Gender Classification(fer>0.66)
#### 文件说明：
####         efficientnet：efficientnet模型的框架
####         images：pyqt界面(客户端)所需图标等
####         models：人脸检测算法、性别识别与年龄段估计算法、表情属性识别算法
####         qtsouce：pyqt界面设计源代码
####         test：测试样例
####         utils：检测代码在此，不需要客户端的同学即可直接调用detect.py
####         share.py: 客户端各界面的功能实现(涉及web服务器的交换)
####         Ui_login.py: 登录窗口

#### 运行命令: python Ui_login.py
#### 环境: python3.6
#### keras==2.0.5
#### tensorflow==1.1.0
#### pandas==0.19.1
#### numpy==1.12.1
#### h5py==2.7.0
#### statistics
#### opencv-python==3.2.0
#### pytorch ==1.7.0
#### pyqt5 == 5.0.1
