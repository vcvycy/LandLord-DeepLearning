# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 21:55:58 2017

@author: XuGang
"""
from myclass import Cards, Player, PlayRecords
from myutil import game_init
import jsonpickle
import time
import copy        
import myutil           
class Game(object):
    def __init__(self):
        #初始化一副扑克牌类
        self.cards = Cards()
        
        #play相关参数
        self.end = False
        self.last_move_type = self.last_move = "start"
        self.playround = 1             #回合(3个人出完叫一个回合)
        self.i = 0                     #当前轮到第几个人出牌了(0,1,2)
        self.yaobuqis = 0              #之前有几个要不起。当为2时，说明当前出牌的可以任意出牌了。
        self.landlord=1                #1号玩家是地主
        
    #发牌
    def game_start(self):
        self.end = False
        self.playround = 1
        self.yaobuqis = 0
        self.i=0
        self.last_move_type = self.last_move = "start"
        #初始化players
        self.players = []
        for i in range(1,4):
            self.players.append(Player(i))
        
        #初始化扑克牌记录类
        self.playrecords = PlayRecords()    
        
        #发牌
        game_init(self.players, self.playrecords, self.cards)
    
    #返回扑克牌记录类
    def get_record(self):
        web_show = WebShow(self.playrecords)
        return jsonpickle.encode(web_show, unpicklable=False)
        
    #游戏进行    
    def go_back(self):  #回退一步
       if self.playround==1 and self.i==0:
         print("[*]第一步，无法再回退...")
         return
       #
       self.i-=1
       if self.i==-1:
         self.playround-=1 
         self.i=2 
       self.end=False
       self.playrecords.winner=0
       self.players[self.i].go_back(self.playrecords)  #玩家self.i收回手牌
       #
       self.yaobuqis,self.last_move,self.last_move_type=self.playrecords.go_back_info()
    
    def get_next_move_num(self): #可以出牌的数量
        self.players[self.i].get_all_moves(self.last_move_type,self.last_move)
        sz=len(self.players[self.i].next_moves)
        if self.last_move_type != "start":
          sz+=1
        return sz
        
    def next_move(self,model="random"):
        #下一个人选择一步来出牌 
        self.last_move_type, self.last_move, self.end, self.yaobuqi = self.players[self.i].go(self.last_move_type, self.last_move, self.playrecords, model)
        
        if self.yaobuqi: 
            self.yaobuqis+=1
        else:
            self.yaobuqis=0 
        #都要不起
        if self.yaobuqis ==2:
            self.yaobuqis = 0
            self.last_move_type = self.last_move = "start"
        if self.end:
            self.playrecords.winner = self.i+1
        self.i = self.i + 1
        #一轮结束
        if self.i > 2:
            #playrecords.show("=============Round " + str(playround) + " End=============")
            self.playround = self.playround + 1
            #playrecords.show("=============Round " + str(playround) + " Start=============")
            self.i = 0    
    def show(self):
      print("\n\n[*]  round:%d  %d/3" %(self.playround,self.i+1))    
      print("[*]  other info yaobuqi[%d] end=%s winner[%s] last_move【%s:" %(self.yaobuqis,self.end,self.playrecords.winner,self.last_move_type),end="")
      myutil.display_cards(self.last_move)
      self.playrecords.show("】\n[*] 玩家手牌和出牌记录:")
      input("")
      
if __name__=="__main__":
    begin = time.time()
    game_ddz = Game() 
    for j in range(2):
        print("------------游戏开始--------------------")
        game_ddz.game_start()
        #game_ddz = copy.deepcopy(game_ddz)
        i = 0
        game_ddz.show()
        while(game_ddz.playrecords.winner == 0):  
            chooses=game_ddz.get_next_move_num()
            print("可以选择%d [0~%d]" %(chooses,chooses-1))
            #idx=int(input("输入选择"))
            #idx=chooses-1
            idx="random"
            game_ddz.next_move(idx)
            game_ddz.show()  
            mat=myutil.state_encode(game_ddz) 
            #myutil.show_mat(mat)
            i = i + 1
            while True:
              k=input("输入b回退一步")
              if k.strip()=="b":
                game_ddz.go_back()
                game_ddz.show()
              else:
                break
            
        print("游戏结束，赢家%s" %(game_ddz.playrecords.winner))
    print(time.time()-begin)
    