#!/usr/bin/python  
# -*- conding:utf-8 -*-  

import json
from bottle import *                                                          #导入bottle相关的包  
 
@route('/ai', methods=['GET'])                     #url接口，注意参数书写格式，前面有个冒号表示是参数  
def artificial_intelligence():  
    try:
      #三人的牌
      print(request.params["c1"])
      c1=json.loads(request.params["c1"])   
      c2=json.loads(request.params["c2"])
      c3=json.loads(request.params["c3"])
      #历史出牌
      h0=json.loads(request.params["h0"])
      h1=json.loads(request.params["h1"])
      h2=json.loads(request.params["h2"])
      h3=json.loads(request.params["h3"])
      #最后出牌的
      last_player=int(request.params["last_player"])
      last_cards=json.loads(request.params["last_cards"])
      
      ret="地主的牌： %s<br> 农民一： %s<br> 农民二：%s<br>" %(c1,c2,c3)
      ret+="<br>history: %s %s %s %s   " %(h0,h1,h2,h3)
      ret+="<br>last %d <br>last card%s" %(last_player,last_cards)
      return ret                                    #返回前台数据，此处返回一个字符串  
    except:
      return "param error!"
      
@route('/')
def index():
  path='./web/index.html'
  return static_file(path, root='.') #静态文件  
  
@route('/:file')
def jsfiles(file):
  path='./web/%s' %(file) 
  return static_file(path, root='.') #静态文件  
@route('/img/:file')
def image(file):
  path='./web/img/%s' %(file) 
  return static_file(path, root='.') #静态文件  

from ai_interface import LandLordAI
  
if __name__=="__main__": 
  landlordAI=LandLordAI()
  run(host='0.0.0.0', port=8080)                                                #表示本机，接口是8080  