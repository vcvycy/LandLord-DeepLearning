from main_ddz import Game
import myutil
import myclass 
import time
import random
import os
import sys
import random
class SelfPlay:
  def __init__(self,cnn):
    self.cnn=cnn           #卷积网络，估算自己出牌后的概率
    self.game=Game()  
    #数据
    self.input=[]          #用于训练的输入
    self.score=[]          #训练数据当前的评分
    self.label=[]          #训练数据期望的评分
    
  def show_one_game(self):
    idx=0
    while idx<len(self.input):
      myutil.show_mat(self.input[idx])
      try:
        print("score=%s label=%s" %(self.score[idx],self.label[idx]))
      except:
         print("label=%s" %(self.label[idx]))
      idx+=1
      input("")
      
  def choose_best_move(self):
    #终局
    #if self.game.playrecords.winner !=0:
    #  return None
      
    #有chooses种出牌方式，选择最优的一种
    chooses=self.game.get_next_move_num()
    #得到所有可能的下一个状态，传入CNN
    mats=[]
    for idx in range(chooses):
      #前进 
      self.game.next_move(idx) 
      #append
      mats.append(myutil.state_encode(self.game))
      #回退
      self.game.go_back()     
    #跑神经网络，选择某一步。choose best
    out=self.cnn.forward(mats)  
    #最优的胜率
    bestIdx=0
    bestMat=None
    bestScore=0 
    for i in range(chooses):
      if out[i][0]>bestScore:
        bestScore=out[i][0] 
        bestIdx=i
        bestMat=mats[i]
    """
    #胜率在0.5%以内的，随机选择，平均概率 
    cnt=0
    for i in range(chooses):
      if out[i][0]+0.005>maxScore:
        cnt+=1 
        #myutil.show_mat(mats[i]) 
    #选择第tmp个
    bestIdx=0
    bestMat=None
    bestScore=0
    tmp=random.randint(1,cnt)  
    
    for i in range(chooses):
      if out[i][0]+0.005>maxScore: 
        tmp-=1
        if tmp==0:
          bestIdx=i 
          bestMat=mats[i]
          bestScore=out[i][0]
          break  
    """   
    #前进一步
    self.game.next_move(bestIdx)
    #
    return bestMat,bestScore
    
  def get_minibatch(self,sz):
    batch=[],[]
    train_sz=len(self.input)
    for i in range(sz):
      idx=random.randint(0,train_sz-1)
      batch[0].append(self.input[idx])
      batch[1].append(self.label[idx])
    return batch
    
  def gen_label(self,winner):  #最新的一局label初始化
    startIdx=len(self.label)
    endIdx=len(self.input)
    #print("start :%d end:%d\n" %(startIdx,endIdx))
    #申请空间
    for i in range(startIdx,endIdx):
      self.label.append(0.0)
    #数据产生
    curIdx=startIdx
    while curIdx <= endIdx-4:
      #以一轮后的分数作为期望估分
      self.label[curIdx]=[ self.score[curIdx+3] ]
      curIdx+=1
    #最后3步
    if winner==1:  #地主赢
      self.label[endIdx-3]=[0.0] #输家
      self.label[endIdx-2]=[0.0] #输家
      self.label[endIdx-1]=[1.0] #赢家
    elif winner==2: #
      self.label[endIdx-3]=[1.0] #输家
      self.label[endIdx-2]=[0.0] #输家
      self.label[endIdx-1]=[1.0] #赢家
    elif winner==3:
      self.label[endIdx-3]=[0.0] #输家
      self.label[endIdx-2]=[1.0] #输家
      self.label[endIdx-1]=[1.0] #赢家
    else:
      print("wrong")
      sys.exit(0)
    #for i in range(startIdx,endIdx):
    #  print("score %s -> %s" %(self.score[i],self.label[i]))
    #input(" step :%d" %(endIdx-startIdx))
  def gen_label_multi_weight(self,winner):  #最新的一局label初始化
    startIdx=len(self.label)
    endIdx=len(self.input)
    #print("start :%d end:%d\n" %(startIdx,endIdx))
    #申请空间 
    for i in range(startIdx,endIdx):
      self.label.append(0.0)
    
    #第1到倒数第四步
    curIdx=startIdx
    turn=1  #当前轮到谁了
    while curIdx <= endIdx-4:
      #以一轮后的分数+最终结果=作为期望估分
      #当前人最终赢还是输
      _win=0
      if (winner==1 and turn==1) or (winner!=1 and turn!=1):  #当前curIdx这个人最终是否是赢家
        _win=1
        
      self.label[curIdx]=[ 0.9*self.score[curIdx+3]+0.1*_win ]
      curIdx+=1 
      #
      if turn==3:
        turn=1
      else:
        turn+=1
      
    #最后3步
    if winner==1:  #地主赢
      self.label[endIdx-3]=[0.0] #输家
      self.label[endIdx-2]=[0.0] #输家
      self.label[endIdx-1]=[1.0] #赢家
    elif winner==2: #
      self.label[endIdx-3]=[1.0] #输家
      self.label[endIdx-2]=[0.0] #输家
      self.label[endIdx-1]=[1.0] #赢家
    elif winner==3:
      self.label[endIdx-3]=[0.0] #输家
      self.label[endIdx-2]=[1.0] #输家
      self.label[endIdx-1]=[1.0] #赢家
    else:
      print("wrong")
      sys.exit(0)
    #for i in range(startIdx,endIdx):
    #  print("score %s -> %s" %(self.score[i],self.label[i]))
    #input(" step :%d" %(endIdx-startIdx))
  
  def save_data(self,filename): 
    #打开文件
    f=open(filename,"wb")
    for x in range(0,len(self.input)):
      idx=0
      val=0
      ba=bytearray()
      #编码input
      for i in range(0,len(self.input[0])):
        for j in range(0,len(self.input[0][0])):
          for k in range(0,len(self.input[0][0][0])):
            idx+=1
            val<<=1
            if self.input[x][i][j][k]==1:
              val+=1
            if idx==8:
              idx=0
              ba.append(val)
              val=0 
      #编码label
      s=int(self.label[x][0]*1000000000)
      for i in range(4):
        ba.append(s&0xff)
        s>>=8
      #写入文件
      f.write(ba)
    f.close() 
    
  def load_data(self,filename):
    tot_sz= os.path.getsize(filename)                 #文件大小
    sz=((myutil.width*myutil.height*myutil.chan)>>3)+4  #每一组数据大小。高位在前，低位在后
    if tot_sz % sz!=0:
      print("  [!]数据大小有误%s! %d/%d" %(filename,tot_sz,sz))
      sys.exit(0)
    #
    num=int(tot_sz/sz)
    print("  [*]从文件:%s 读取数据! 训练数据大小：%d" %(filename,num))
    f=open(filename,"rb")
    for x in range(num):
      ba=f.read(sz)
      curIdx=0
      curBit=7
      #input
      input=[[[0 for _ in range(myutil.chan)] for _ in range(myutil.height)] for _ in range(myutil.width)] 
      for i in range(myutil.width):
        for j in range(myutil.height):
          for k in range(myutil.chan):
            if curBit==-1:
              curIdx+=1
              curBit=7
            if (ba[curIdx]&(1<<curBit))>0:
              input[i][j][k]=1.0
            else:
              input[i][j][k]=0.0
            curBit-=1
      self.input.append(input) 
      #label  
      sco=ba[curIdx+1]+(ba[curIdx+2]<<8)+(ba[curIdx+3]<<16)+(ba[curIdx+4]<<24) 
      sco=sco/1000000000
      self.label.append([sco]) 
      #print("curIdx=%d\n" %(curIdx))
      self.show_one_game()
    f.close()
    print("  [*]数据读取成功!")
    
  #自我出牌game_num次
  def start(self,game_num,data_path): 
    self.input=[]
    self.label=[]
    self.score=[]
    #if os.path.exists(data_path):
    #  self.load_data(data_path)
    #  return
    
    #生成数据
    t1=time.time()
    #一共打game_num把游戏  
    
    while game_num>0: 
      #开始新一把游戏
      self.game.game_start()
      #记录当前游戏 
      while (self.game.playrecords.winner == 0):
        #选择最优一步，然后记录下来
        mat,sco=self.choose_best_move()
        self.input.append(mat)
        self.score.append(sco) 
        #self.game.show()                   #显示全局状态
      #当前游戏产生label
      self.gen_label_multi_weight(self.game.playrecords.winner)  
      #      
      self.show_one_game()
      game_num-=1
    print("  [*]正在保存数据到:%s" %(data_path))
    self.save_data(data_path)
    print("  Time:%d " %(time.time()-t1))

if __name__ =="__main__":
    ba=bytearray()
    for i in range(0,4):
      ba.append(val&0xff) 
      val>>=8  
