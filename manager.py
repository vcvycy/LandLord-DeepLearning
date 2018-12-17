import main_ddz
import myutil
import myclass 
from SelfPlay import SelfPlay
from ResNet import ResNet
import math

width  = myutil.width
height = myutil.height
chan   = myutil.chan
epochs = 30
bat_sz = 50 

if __name__=="__main__":
   #(1)卷积网络
   #init cnn
   cnn=ResNet([None,width,height,chan],3)
   #cnn.restore("./data/") 
   round=31
   if round>1:
      cnn.restore_round(round-1)
   print("[*]网络初始化成功:网络参数%d" %(cnn.param_num)) 
   #init selfplay
   splay=SelfPlay(cnn) 
   #
   play_game_num=5000 
   while True: 
     print("\n【round %d】" %(round))
     #(1)selfplay，如果已经存在，则读取，否则生成
     print("  [*]正在产生数据...")
     data_path="./data/round-%d.data" %(round)
     splay.start(play_game_num,data_path)
     train_sz=len(splay.input)
     print("  [*]成功，一共有%d条数据" %(train_sz))
     
     #(3)train
     if round>20:
       learning_rate=1e-5
     else:
       learning_rate=1e-4 
     print("  [*]开始训练...") 
     for epoch in range(epochs): 
       print("  [*]epoch_%d learning_rate=%s" %(epoch,learning_rate),end=" ")
       sz=train_sz 
       mean_loss=0
       while sz>0:
         data=splay.get_minibatch(bat_sz)
         sz-=bat_sz
         loss=cnn.train(data[0],data[1],learning_rate)
         mean_loss+=loss
       print("mean_loss=%s" %(mean_loss/math.ceil(train_sz/50)))
     
     #(4)save model
     cnn.save("./data/model",round)
     round+=1
#要修改的
"""
 (1) 数据产生添加进度
 (2) epoch训练到loss不再减少为止
"""
