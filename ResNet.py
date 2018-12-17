import tensorflow as tf
import numpy as np
"""
(1)构造函数__init__参数
  input_sz：  输入层placeholder的4-D shape，如mnist是[None,28,28,1] 
(2)train函数：训练一步
   batch_input： 输入的batch
   batch_output: label
   learning_rate:学习率
   返回：正确率和loss值(float)   格式：{"accuracy":accuracy,"loss":loss}
(3)forward：训练后用于测试
(4)save(save_path,steps)保存模型
(5)restore(path):从文件夹中读取最后一个模型
(6)loss函数使用cross-entrop one-hot版本:y*log(y_net)
(7)optimizer使用adamoptimier
"""
class ResNet:   
  sess=None
  #Tensor
  input=None 
  output=None
  desired_out=None
  loss=None
  #iscorrect=None
  #accuracy=None
  optimizer=None
  param_num=0             #参数个数
  #参数
  learning_rate=None 
  MOMENTUM         = 0.9
  WEIGHT_DECAY     = 1e-4       #L2 REGULARIZATION
  ACTIVATE         = None
  CONV_PADDING     = "SAME"
  MAX_POOL_PADDING = "SAME"
  CONV_WEIGHT_INITAILIZER = tf.keras.initializers.he_normal()#tf.truncated_normal_initializer(stddev=0.1)
  CONV_BIAS_INITAILIZER   = tf.constant_initializer(value=0.0)
  FC_WEIGHT_INITAILIZER   = tf.keras.initializers.he_normal()#tf.truncated_normal_initializer(stddev=0.1)
  FC_BIAS_INITAILIZER     = tf.constant_initializer(value=0.0)
  
  
  def train(self,batch_input,batch_output,learning_rate):  
    _,loss=self.sess.run([self.optimizer,self.loss],
       feed_dict={self.input:batch_input,self.desired_out:batch_output,self.learning_rate:learning_rate})
    return loss
    
  def forward(self,batch_input):
    return self.sess.run(self.output,feed_dict={self.input:batch_input})
  
  def save(self,save_path,steps):
    saver=tf.train.Saver(max_to_keep=5)
    saver.save(self.sess,save_path,global_step=steps)
    print("[*]save success")
  
  def restore_round(self,round_id):
    path="./data/model-%d" %(round_id)
    saver=tf.train.Saver(max_to_keep=5)
    saver.restore(self.sess,path)
    print("[*]Restore from %s success" %(path))
    return True
    
  def restore(self,restore_path):
    path=tf.train.latest_checkpoint(restore_path)
    if path==None:
      return False
    saver=tf.train.Saver(max_to_keep=5)
    saver.restore(self.sess,path)
    print("[*]Restore from %s success" %(path))
    return True
  
  def restore_except_softmax_layer(self,restore_path):
    path=tf.train.latest_checkpoint(restore_path)
    if path==None:
      return False
    var_list=tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES,scope="LAYERS_EXCEPT_SOFTMAX")
    saver=tf.train.Saver(var_list=var_list)
    saver.restore(self.sess,path)
    print("[*]restore_except_softmax_layer %s success" %(path)) 
    return True
  
  
  def bn(self,x,name="bn"):
    with tf.variable_scope(name):
      #return x
      axes = [d for d in range(len(x.get_shape()))]
      beta = self._get_variable("beta", shape=[],initializer=tf.constant_initializer(0.0))
      gamma= self._get_variable("gamma",shape=[],initializer=tf.constant_initializer(1.0))
      x_mean,x_variance=tf.nn.moments(x,axes)  
      y=tf.nn.batch_normalization(x,x_mean,x_variance,beta,gamma,1e-10)
      return y
    
  def get_optimizer(self): 
    self.optimizer =tf.train.MomentumOptimizer(self.learning_rate,self.MOMENTUM).minimize(self.loss)            #9000 steps后达到误差范围。  
  
  #对x执行一次卷积操作+Relu
  def conv(self,x,name,channels,ksize=[3,3],strides=[1,1,1,1]):
    with tf.variable_scope(name):
      x_shape=x.get_shape()
      x_channels=x_shape[3].value
      weight_shape=[ksize[0],ksize[1],x_channels,channels]
      bias_shape=[channels]
      weight = self._get_variable("weight",weight_shape,initializer=self.CONV_WEIGHT_INITAILIZER)
      bias   = self._get_variable("bias",bias_shape,initializer=self.CONV_BIAS_INITAILIZER) 
      y=tf.nn.conv2d(x,weight,strides=strides,padding=self.CONV_PADDING)
      y=tf.add(y,bias)
      return y
  
  def max_pool(self,x,name):
    return tf.nn.max_pool(x,ksize=[1,2,2,1],strides=[1,2,2,1],padding=self.MAX_POOL_PADDING,name=name)
    
  #定义_get_variable方便进行l2_regularization以及其他一些操作
  def _get_variable(self,name,shape,initializer):
    param=1
    for i in range(0,len(shape)):
      param*=shape[i]
    self.param_num+=param
    
    if self.WEIGHT_DECAY>0:
      regularizer=tf.contrib.layers.l2_regularizer(self.WEIGHT_DECAY)
    else:
      regularizer=None  
    return tf.get_variable(name,
                           shape=shape,
                           initializer=initializer,
                           regularizer=regularizer)
                           
  def fc(self,x,num,name):  
    x_num=x.get_shape()[1].value
    weight_shape=[x_num,num]
    bias_shape  =[num]
    weight=self._get_variable("weight",shape=weight_shape,initializer=self.FC_WEIGHT_INITAILIZER)
    bias  =self._get_variable("bias",shape=bias_shape,initializer=self.FC_BIAS_INITAILIZER)
    y=tf.add(tf.matmul(x,weight),bias,name=name)
    return y 
  def _loss(self):  
    #sqr=tf.reduce_sum((self.output-self.desired_out)*(self.output-self.desired_out),name="Loss0")
    
    sqr = -tf.reduce_sum(self.desired_out*tf.log(tf.clip_by_value(self.output,1e-10,1.0))
                                  +(1.0-self.desired_out)*tf.log(tf.clip_by_value(1.0-self.output,1e-10,1.0)),
                                  name="Loss0")
    
    regularization_losses=tf.get_collection(tf.GraphKeys.REGULARIZATION_LOSSES)
    self.loss = tf.add_n([sqr]+regularization_losses,name="Loss")
    #tf.scalar_summary('loss', loss_)
    return self.loss
  
  def res_block(self,x,channels,name,increase=False): 
    with tf.variable_scope(name):
      if increase:
        strides=[1,2,2,1]
      else:
        strides=[1,1,1,1]
      #1
      y=self.bn(x,"bn_a")
      y=self.ACTIVATE(y)
      y=self.conv(y,"conv_a",channels,[3,3],strides)
      #2
      y=self.bn(y,"bn_b")
      y=self.ACTIVATE(y)
      y=self.conv(y,"conv_b",channels)
      if increase:
        projection=self.conv(x,"conv_proj",channels,[3,3],[1,2,2,1])
        y=tf.add(projection,y)
      else:
        y=tf.add(x,y)
      return y
    
  def __init__(self,input_sz,stack_n): #
    with tf.variable_scope("LAYERS_EXCEPT_SOFTMAX"):
    #if True:
        self.ACTIVATE=tf.nn.relu
        self.param_num=0  #返回参数个数
        self.sess=tf.Session()
        layers=[]
        #(1)placeholder定义(输入、输出、learning_rate)
        #input
        self.input=tf.placeholder(tf.float32,input_sz,name="input") 
        layers.append(self.input)
        #
        #layers.append(self.bn(layers[-1])) 
        #(2)插入卷积层+池化层
        x=layers[-1]
        y=self.conv(x,"first_conv",128,ksize=[3,3]) 
        layers.append(y) 
        with tf.variable_scope("Residual_Blocks"):
          with tf.variable_scope("Residual_Blocks_STACK_0"):
            for id in range(stack_n):
              x=layers[-1]
              b=self.res_block(x,128,"block_%d" %(id))
              layers.append(b)
          with tf.variable_scope("Residual_Blocks_STACK_1"):
            x=layers[-1]
            b=self.res_block(x,256,"block_0",True)
            layers.append(b)
            for id in range(1,stack_n):
              x=layers[-1]
              b=self.res_block(x,256,"block_%d" %(id))
              layers.append(b) 
        #maxpool
        """
        x=layers[-1]
        y=self.max_pool(x,"maxpool_after_resblocks")
        layers.append(y)
        """
        #(3)卷积层flatten
        with tf.variable_scope("Flatten"):
          last_layer=layers[-1]
          last_shape=last_layer.get_shape()
          neu_num=1
          for dim in range(1,len(last_shape)): 
           neu_num*= last_shape[dim].value
          flat_layer=tf.reshape(last_layer,[-1,neu_num],name="flatten")
          layers.append(flat_layer) 
        #(4)全连接层 #!!!!!!!!!最后一层不要加上relu!!!!!! 
    with tf.variable_scope("fcn"):  #
      x=layers[-1]
      y=self.bn(x)
      y=self.fc(y,1,"fc")
      layers.append(y) 
      #(5)softmax和loss函数
      self.output=tf.sigmoid(layers[-1])
    
    #output 
    self.desired_out=tf.placeholder(tf.float32,[None,1],name="desired_out")
    self.learning_rate=tf.placeholder(tf.float32,name="learning_rate")
    #loss函数
    self._loss() 
    #(7)优化器和 variables初始化
    self.get_optimizer()
    self.sess.run(tf.global_variables_initializer())
    writer = tf.summary.FileWriter("./tboard/",self.sess.graph)  
    
  def __del__(self):
    self.sess.close()
#########################################
##超级收敛 super convergent
def get_lr(cnt):
   if cnt<1000:
     return 1e-4 
   else:
     if cnt==10:
       print("----开始超级收敛-----")
     return 1e-2
   
if __name__ =="__main__":
   resnet=ResNet([None,15,8,8],2)
   print("[*]网络初始化成功:网络参数%d" %(resnet.param_num)) 
   cnt=0
   
   print("Test")
   input=np.random.rand(10,15,8,8)
   print(resnet.forward(input))
   
   for _ in range(10):
    cnt+=1
    lr=get_lr(cnt)
    for _ in range(50):
     input=np.random.rand(50,15,8,8)
     label=[[0.2] for _ in range(50)]
     ret=resnet.train(input,label,lr) 
    print(ret) 
   print("Test")
   input=np.random.rand(10,15,8,8)
   print(resnet.forward(input))