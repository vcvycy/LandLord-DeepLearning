# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 21:55:58 2017

@author: XuGang
"""
#import numpy as np
from myutil import card_show, choose
import myutil

############################################
#              扑克牌相关类                 #
############################################
class Cards(object):
    """
    一副扑克牌类,54张排,abcd四种花色,小王14-a,大王15-a
    """
    def __init__(self):
        #初始化扑克牌类型
        self.cards_type = ['1-a-12', '1-b-12','1-c-12','1-d-12',
                           '2-a-13', '2-b-13','2-c-13','2-d-13',
                           '3-a-1', '3-b-1','3-c-1','3-d-1',
                           '4-a-2', '4-b-2','4-c-2','4-d-2',
                           '5-a-3', '5-b-3','5-c-3','5-d-3',
                           '6-a-4', '6-b-4','6-c-4','6-d-4',
                           '7-a-5', '7-b-5','7-c-5','7-d-5',
                           '8-a-6', '8-b-6','8-c-6','8-d-6',
                           '9-a-7', '9-b-7','9-c-7','9-d-7',
                           '10-a-8', '10-b-8','10-c-8','10-d-8',
                           '11-a-9', '11-b-9','11-c-9','11-d-9',
                           '12-a-10', '12-b-10','12-c-10','12-d-10',
                           '13-a-11', '13-b-11','13-c-11','13-d-11',
                           '14-a-14', '15-a-15']
        #初始化扑克牌类                  
        self.cards = self.get_cards()

    #初始化扑克牌类
    def get_cards(self):
        cards = []
        for card_type in self.cards_type:
            cards.append(Card(card_type))  
        #打乱顺序
        #np.random.shuffle(cards)
        return cards
    
class Card(object):
    """
    扑克牌类
    """
    def __init__(self, card_type):
        self.card_type = card_type
        #名称
        self.name = self.card_type.split('-')[0]
        #花色
        self.color = self.card_type.split('-')[1]
        #大小
        self.rank = int(self.card_type.split('-')[2])
        
    #判断大小
    def bigger_than(self, card_instance):
        if (self.rank > card_instance.rank):
            return True
        else:
            return False
     
class PlayRecords(object):
    """
    扑克牌记录类
    """
    def __init__(self):
        #当前手牌。指向player[1,2,3]中的card_left字段
        self.cards_left1 = []
        self.cards_left2 = []
        self.cards_left3 = []
        
        #可能出牌选择
        #self.next_moves1 = []
        #self.next_moves2 = []
        #self.next_moves3 = []

        #出牌记录
        #self.next_move1 = []
        #self.next_move2 = []
        #self.next_move3 = []
        
        #出牌记录
        self.records = []
        
        #胜利者
        #winner=0,1,2,3 0表示未结束,1,2,3表示winner
        self.winner = 0
    def go_back_info(self):
        #
        yaobuqis=0
        idx=len(self.records)-1
        while idx>=0:
          if self.records[idx]["move"] in ["yaobuqi","buyao"]:
            yaobuqis+=1
          else:
            break
          idx-=1
        # 
        last_move=None
        last_move_type=None
        if len(self.records)==0 or yaobuqis==2:
          last_move="start"
          last_move_type="start"
          yaobuqis=0
          
        elif yaobuqis==0:
          last_move=self.records[-1]["move"]
          last_move_type=self.records[-1]["type"]
          
        elif yaobuqis==1:
          last_move=self.records[-2]["move"]
          last_move_type=self.records[-2]["type"]
          
        return yaobuqis,last_move,last_move_type
        
    #展示
    def show(self, info):
        print(info)
        card_show(self.cards_left1, "  【地主】手牌", 1)
        card_show(self.cards_left2, "  【农民一】手牌", 1)
        card_show(self.cards_left3, "  【农民二】手牌", 1)
        card_show(self.records, "  [-]出牌历史记录", 3)


############################################
#              出牌相关类                   #
############################################
class Moves(object):
    """
    出牌类,单,对,三,三带一,三带二,顺子,炸弹
    """ 
    def __init__(self):
        #出牌信息
        self.dan = []
        self.dui = []
        self.san = []
        self.san_dai_yi = []
        self.san_dai_er = []
        self.bomb = []
        self.shunzi = []
        
        #牌数量信息
        self.card_num_info = {}        #记录每一张牌有多少张，如一对3就是[3 : [card方块3,card梅花3]] 
        #牌顺序信息,计算顺子
        self.card_order_info = []
        #王牌信息
        self.king = []
        
        #下次出牌
        self.next_moves = []
        #下次出牌类型
        self.next_moves_type = []
        
    #获取全部出牌列表
    def get_moves(self, cards_left):  #card_left必须有序
        #统计牌数量/顺序/王牌信息
        for i in cards_left:
            #王牌信息
            if i.rank in [14,15]:
                self.king.append(i)
            #数量
            tmp = self.card_num_info.get(i.name, [])
            if len(tmp) == 0:
                self.card_num_info[i.name] = [i]
            else:
                self.card_num_info[i.name].append(i)           
            #顺序
            if i.rank in [13,14,15]: #不统计2,小王,大王
                continue
            elif len(self.card_order_info) == 0:
                self.card_order_info.append(i)
            elif i.rank != self.card_order_info[-1].rank:
                self.card_order_info.append(i)  
        #王炸 
        if len(self.king) == 2:
            self.bomb.append(self.king)
        #出单,出对,出三,炸弹(考虑拆开)
        for k, v in self.card_num_info.items():
            if len(v) == 1:
                self.dan.append(v)
            elif len(v) == 2:
                self.dui.append(v)
                self.dan.append(v[:1])
            elif len(v) == 3:
                self.san.append(v)
                self.dui.append(v[:2])
                self.dan.append(v[:1])
            elif len(v) == 4:
                self.bomb.append(v)
                self.san.append(v[:3])
                self.dui.append(v[:2])
                self.dan.append(v[:1])
        #连对-------------add bycjf--------------------
        start=0
        end=-2
        pokes=[]
        liandui=[]
        for dui in self.dui:
           cur_rank=dui[0].rank
           if cur_rank>=13:    #2，小王，大王不算连对
             break 
           #和前面的对连接在一起
           if end!=cur_rank-1: #无法接在一起
             start=cur_rank 
             pokes=[]
           end=cur_rank
           #添加到扑克里
           for poke in dui: 
             pokes.append(poke)
           #只接受长度3以上连对
           #print("poke start=%d end=%d len=%d" %(start,end,len(pokes)))
           for x in range(start,end-1):
             tmp=(x-start)*2 
             liandui.append(pokes[tmp:])
        
        
        
        #------------------------------------------
        #三带一,三带二
        for san in self.san:
            for dan in self.dan:
                #防止重复
                if dan[0].name != san[0].name:
                    self.san_dai_yi.append(san+dan)
            for dui in self.dui:
                #防止重复
                if dui[0].name != san[0].name:
                    self.san_dai_er.append(san+dui)  
        #飞机，暂时只考虑二连飞机 ----------add by cjf--------------- 
        prev_san=None
        feiji_dai_dan=[]
        feiji_dai_dui=[]
        for san in self.san:
            if san[0].rank>=13:  #2，小王大王
              break
            if prev_san!=None and prev_san[0].rank==san[0].rank-1: 
              #带两个单牌
              for dan1 in self.dan:  
                for dan2 in self.dan:
                  if dan1[0].rank!=san[0].rank-1 and dan2[0].rank!=san[0].rank-1:
                    if dan1[0].rank!=san[0].rank and dan2[0].rank!=san[0].rank and dan2[0].rank>dan1[0].rank: #三者互不相同且dan2大于dan1
                      feiji_dai_dan.append(prev_san+san+dan1+dan2)
              #带两个对
              for dui1 in self.dui:
                for dui2 in self.dui:
                  if dui1[0].rank!=san[0].rank-1 and dui2[0].rank!=san[0].rank-1:
                    if dui1[0].rank!=san[0].rank and dui2[0].rank!=san[0].rank and dui2[0].rank>dui1[0].rank:
                      feiji_dai_dui.append(prev_san+san+dui1+dui2)
            prev_san=san
        
        self.san_dai_yi+=feiji_dai_dan
        self.san_dai_er+=feiji_dai_dui
        """
        tmp=self.san_dai_yi+self.san_dai_er
        for x in tmp:
          for card in x:
            print(card.name,end=" ")
          print("以上三带x")
        input("")
        #  """      
                    
        #获取最长顺子
        max_len = []
        for i in self.card_order_info:
            if i == self.card_order_info[0]:
                max_len.append(i)
            elif max_len[-1].rank == i.rank - 1:
                max_len.append(i)
            else:
                if len(max_len) >= 5:
                   self.shunzi.append(max_len) 
                max_len = [i]
        #最后一张牌结尾的特殊处理
        if len(max_len) >= 5:
           self.shunzi.append(max_len)
        #拆顺子 
        shunzi_sub = []             
        for i in self.shunzi:
            len_total = len(i)
            n = len_total - 5
            #遍历所有可能顺子长度
            while(n > 0):
                len_sub = len_total - n
                j = 0
                while(len_sub+j <= len(i)):
                    #遍历该长度所有组合
                    shunzi_sub.append(i[j:len_sub+j])
                    j = j + 1
                n = n - 1
        self.shunzi.extend(shunzi_sub)
        #myutil.display_shunzi(self.shunzi)
        
        
        #对加上连对(放在最后处理，方便三带二，飞机带二的枚举)---cjf
        self.dui+=liandui
        """
        for dui in self.dui:
          for poke in dui:
            print(poke.name,end=" ")
          print("以上连对")
        """
        
    #获取下次出牌列表
    def get_next_moves(self, last_move_type, last_move): 
        #没有last,全加上,除了bomb最后加
        if last_move_type == "start":
            moves_types = ["dan", "dui", "san", "san_dai_yi", "san_dai_er", "shunzi"]
            i = 0
            for move_type in [self.dan, self.dui, self.san, self.san_dai_yi, 
                      self.san_dai_er, self.shunzi]:
                for move in move_type:
                    self.next_moves.append(move)
                    self.next_moves_type.append(moves_types[i])
                i = i + 1
        #出单
        elif last_move_type == "dan":
            for move in self.dan:
                #比last大
                if move[0].bigger_than(last_move[0]):
                    self.next_moves.append(move)  
                    self.next_moves_type.append("dan")
        #出对(包括连对)
        elif last_move_type == "dui":
            for move in self.dui:
                #比last大
                if len(move)==len(last_move) and move[0].bigger_than(last_move[0]):
                    self.next_moves.append(move) 
                    self.next_moves_type.append("dui")
        #出三个
        elif last_move_type == "san":
            for move in self.san:
                #比last大
                if len(move)==len(last_move) and move[0].bigger_than(last_move[0]):
                    self.next_moves.append(move) 
                    self.next_moves_type.append("san")
        #出三带一
        elif last_move_type == "san_dai_yi":
            for move in self.san_dai_yi:
                #比last大
                if len(move)==len(last_move) and move[0].bigger_than(last_move[0]):
                    self.next_moves.append(move)    
                    self.next_moves_type.append("san_dai_yi")
        #出三带二
        elif last_move_type == "san_dai_er":
            for move in self.san_dai_er:
                #比last大
                if len(move)==len(last_move) and move[0].bigger_than(last_move[0]):
                    self.next_moves.append(move)   
                    self.next_moves_type.append("san_dai_er")
        #出炸弹
        elif last_move_type == "bomb":
            for move in self.bomb:
                #比last大
                if move[0].bigger_than(last_move[0]):
                    self.next_moves.append(move) 
                    self.next_moves_type.append("bomb")
        #出顺子
        elif last_move_type == "shunzi":
            for move in self.shunzi:
                #相同长度
                if len(move) == len(last_move):
                    #比last大
                    if move[0].bigger_than(last_move[0]):
                        self.next_moves.append(move) 
                        self.next_moves_type.append("shunzi")
        else:
            print("last_move_type_wrong %s" %(last_move_type))
            
        #除了bomb,都可以出炸
        if last_move_type != "bomb":
            for move in self.bomb:
                self.next_moves.append(move) 
                self.next_moves_type.append("bomb")
                
        return self.next_moves_type, self.next_moves
    
    
    #展示
    def show(self, info):
        print(info)
        #card_show(self.dan, "dan", 2)
        #card_show(self.dui, "dui", 2)
        #card_show(self.san, "san", 2)
        #card_show(self.san_dai_yi, "san_dai_yi", 2)
        #card_show(self.san_dai_er, "san_dai_er", 2)
        #card_show(self.bomb, "bomb", 2)
        #card_show(self.shunzi, "shunzi", 2)
        #card_show(self.next_moves, "next_moves", 2)


############################################
#              玩家相关类                   #
############################################        
class Player(object):
    """
    player类
    """
    def __init__(self, player_id):
        self.player_id = player_id
        self.cards_left = []           #当前玩家的手牌
        self.total_moves=None
        self.next_move=None
        self.next_moves=None
        self.next_move_type=None
        self.next_move_types=None

    #展示
    def show(self, info):
        self.total_moves.show(info)
        card_show(self.next_move, "next_move", 1)
        #card_show(self.cards_left, "card_left", 1)
        
    
    #根据next_move同步cards_left
    def record_move(self, playrecords):
        #playrecords中records记录[id,next_move]
        if self.next_move_type in ["yaobuqi", "buyao"]:
            self.next_move = self.next_move_type
            #playrecords.records.append([self.player_id, self.next_move_type])
            playrecords.records.append({"playerId":self.player_id, "move":self.next_move_type,"type":self.next_move_type})
        else:
            #playrecords.records.append([self.player_id, self.next_move])
            playrecords.records.append({"playerId":self.player_id, "move":self.next_move,"type":self.next_move_type})
            for i in self.next_move:   
               self.cards_left.remove(i)
               
        #同步playrecords
        """
        if self.player_id == 1:
            playrecords.cards_left1 = self.cards_left
            playrecords.next_moves1.append(self.next_moves)
            playrecords.next_move1.append(self.next_move)
        elif self.player_id == 2:
            playrecords.cards_left2 = self.cards_left 
            playrecords.next_moves2.append(self.next_moves)
            playrecords.next_move2.append(self.next_move)
        elif self.player_id == 3:
            playrecords.cards_left3 = self.cards_left  
            playrecords.next_moves3.append(self.next_moves)
            playrecords.next_move3.append(self.next_move)
        """
        #是否牌局结束
        end = False
        if len(self.cards_left) == 0:
            end = True
        return end
        
    #回退一步
    def go_back(self,playrecords):
        end=False
        if playrecords.records[-1]["type"] not in ["yaobuqi", "buyao"]:
           for card in playrecords.records[-1]["move"]:
             #需要排序，否则出问题 
             self.cards_left.append(card)
             #向左冒泡
             idx=len(self.cards_left)-1
             while idx>0:
               c1=self.cards_left[idx-1] 
               c2=self.cards_left[idx]
               if c1.rank>c2.rank:
                 self.cards_left[idx-1]=c2
                 self.cards_left[idx]=c1
                 idx-=1
               else:
                 idx=0
        playrecords.records.pop()
        
    #出牌
    def get_all_moves(self, last_move_type, last_move):
        #所有出牌可选列表
        self.total_moves = Moves()
        #获取全部出牌列表                  
        self.total_moves.get_moves(self.cards_left)
        #获取下次出牌列表
        self.next_move_types, self.next_moves = self.total_moves.get_next_moves(last_move_type, last_move)
      
    def go(self, last_move_type, last_move, playrecords, model):
        #在next_moves中选择出牌方法
        self.next_move_type, self.next_move = choose(self.next_move_types, self.next_moves, last_move_type, model)
        #记录
        end = self.record_move(playrecords)
        #展示
        #self.show("Player " + str(self.player_id))  
        #要不起&不要
        yaobuqi = False
        if self.next_move_type in ["yaobuqi","buyao"]:
            yaobuqi = True
            self.next_move_type = last_move_type
            self.next_move = last_move
            
        return self.next_move_type, self.next_move, end, yaobuqi
    
 