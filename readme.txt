对原来的修改：
删除
class PlayRecords(object):中的
        #self.next_moves1 = []
        #self.next_moves2 = []
        #self.next_moves3 = []

        #出牌记录
        #self.next_move1 = []
        #self.next_move2 = []
        #self.next_move3 = []
添加回退功能：
修改显示当前状态函数。
删除WEB_SHOW
删除record_move中的同步部分(无意义)
record添加type

这个也不是正宗的斗地主：
  (1) 没有飞机,没有连对
  (2) 没有地主，3个人各自为战
  (3) 没有底牌，一个人各发18张。


增强学习：
    状态表示:
        对玩家i出牌后进行评估：
           玩家i可以看到的：桌上的牌，每个人的历史出牌、当前轮出的牌。
        枚举玩家i所有的出牌，选择评分最高的。
    