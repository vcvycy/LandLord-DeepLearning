# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 21:55:58 2017

@author: XuGang
"""
import numpy as np 
 
#展示扑克函数
def card_show(cards, info, n):
    
    #扑克牌记录类展示：手牌
    if n == 1:
        print(info+": ",end="")
        #names = []
        for i in cards:
            #names.append(i.name+i.color)
            print(i.name,end=".")
        print("")
        #print(names)    
        
    #Moves展示
    elif n == 2:
        if len(cards) == 0:
            return 0
        print(info)
        moves = []
        for i in cards:
            names = []
            for j in i:
                names.append(j.name+j.color)
            moves.append(names)
        print(moves)  
    #record展示，出牌历史记录
    elif n == 3: 
        print(info)  
        for x in cards:
          print("[player %s %s] " %(x["playerId"],x["type"]),end="")
        
          try:
            for card in x["move"]:
              print("%s" %(card.name),end=".")
          except:
            print("%s" %(x["move"]),end="")
          print(" ==>",end="") 
        
        print("")
       
def display_shunzi(shunzi):
  for x in shunzi:
    for y in x:
      print("%s " %(y.name),end="")
    print("")
  input("---pause---")

def display_cards(card_arr):
  try:
    for card in card_arr:
      print("%s" %(card.name),end=".")
  except:
    print(card_arr,end="")
  
#在Player的next_moves中选择出牌方法
def choose(next_move_types, next_moves, last_move_type, model):
    #buyao和yaobuqi需要额外判断，并不在next_move_types里面 
    if model == "random":
        return choose_random(next_move_types, next_moves, last_move_type)
    else:
        return choose_specific(next_move_types,next_moves,last_move_type,model)

#random
def choose_random(next_move_types, next_moves, last_move_type):
    #要不起
    if len(next_moves) == 0:
        return "yaobuqi", []
    else:
        #start不能不要
        if last_move_type == "start":
            r_max = len(next_moves)
        else:
            r_max = len(next_moves)+1
        r = np.random.randint(0,r_max)
        #添加不要
        if r == len(next_moves):
            return "buyao", []
        
    return next_move_types[r], next_moves[r] #random
def choose_specific(next_move_types, next_moves, last_move_type,idx):
    #要不起
    num=len(next_moves)
    if num == 0:
        return "yaobuqi", []
    else: 
        #添加不要
        if idx == num:
            return "buyao", []
        
    return next_move_types[idx], next_moves[idx] 
    
#发牌
def game_init(players, playrecords, cards):
    
    #洗牌
    np.random.shuffle(cards.cards)
    #排序(1号玩家是地主)
    p1_cards = cards.cards[:20]
    p1_cards.sort(key=lambda x: x.rank)
    p2_cards = cards.cards[20:37]
    p2_cards.sort(key=lambda x: x.rank)
    p3_cards = cards.cards[37:]
    p3_cards.sort(key=lambda x: x.rank)
    players[0].cards_left = playrecords.cards_left1 = p1_cards
    players[1].cards_left = playrecords.cards_left2 = p2_cards
    players[2].cards_left = playrecords.cards_left3 = p3_cards    
    
#当前状态转为矩阵形式
width  = 15
height = 4
chan   = 8
#将牌按rank写到mat的chan_id通道里。以append方式。
def cards_encode(mat,chan_id,cards):
    for card in cards:
      h=0
      while (mat[card.rank-1][h][chan_id]!=0):
        h+=1
      mat[card.rank-1][h][chan_id]=1
#不同类型的进行编码
def set_val(mat,chan_id,val): 
    for i in range(width):
      for j in range(height):
          mat[i][j][chan_id]=val
#要不起(不要)编码：0，1，2
def yaobuqi_encode(mat,chan_id,game):
    yaobuqis=game.yaobuqis
    if game.last_move_type == "start":
      yaobuqis=2
        
    for i in range(width):
      for j in range(height): 
        if yaobuqis==2 or (yaobuqis==1 and (i&1)==0):
          mat[i][j][chan_id]=1 
          
def mat2list(mat,chan_id):
    ret=[]
    for i in range(width):
      for j in range(height):
        if mat[i][j][chan_id]==1:
          ret.append(i)
    return ret;
    
def show_pokes(list):
    print("{",end="")
    for card in list:
      if card==13:
        print("小王",end=" ")
      elif card==14:
        print("大王",end=" ")
      elif card==11:
        print("A",end=" ")
      elif card==12:
        print("2",end=" ")
      else:
        print("%s" %(card+3),end=" ")
    print("}")
    
def show_mat(mat):
    print("----------show Mat------------")
    print("  [*]手牌:",end="")
    show_pokes(mat2list(mat,0))
    print("  [*]上家历史出牌",end="")
    show_pokes(mat2list(mat,1))
    print("  [*]上上家历史出牌:",end="")
    show_pokes(mat2list(mat,2))
    print("  [*]牌桌:",end="")
    show_pokes (mat2list(mat,3))
    print("  [*]lastmove: ",end="") 
    show_pokes(mat2list(mat,4))
    #print("  [*]movetype: %s" %(mat2list(mat,5)))
    #print("  [*]yaobuqi: %s" %(mat2list(mat,6)))
    #print("  [*]yaobuqi: %s" %(mat2list(mat,7)))
    
    
def state_encode(game):
    mat=[[[0 for _ in range(chan)] for _ in range(height)] for _ in range(width)] 
    #最后一个出牌的人(0,1,2)
    last_player=(game.i+2)%3
    #(0)自己的手牌
    cards_encode(mat,0,game.players[last_player].cards_left)
    #(1,2,3)上家、上上家历史出牌，牌桌上的牌
    for record in game.playrecords.records: 
       type=record["type"]
       if type not in ["yaobuqi","buyao"]:
         cur_player = record["playerId"]-1  #标记是1，2，3所以要-1
         cards    = record["move"] 
         dist=(last_player+3-cur_player)%3
         #print("type=%s last_player %s cur_player %s" %(type,last_player,cur_player))
         #上家
         if dist==1:
           cards_encode(mat,1,cards)
         #上上家
         elif dist==2:
           cards_encode(mat,2,cards)
         #牌桌上的牌
         cards_encode(mat,3,cards)
    #(4)  last move(如果为start则全0)
    if game.last_move != "start":       #可以随意出牌则全0
        cards_encode(mat,4,game.last_move)
    #(6)自己是否是地主(是为1，不是为0)
    if last_player == 0:  #0是地主
      set_val(mat,5,1) 
    #(6)如果自己不是地主:下家是队友则为1，不是则为0
    if last_player == 1:
      set_val(mat,6,1)
    #(6) yaobuqi的个数
    yaobuqi_encode(mat,7,game)
    return mat