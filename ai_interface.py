
import main_ddz
import myutil
import myclass 
from SelfPlay import SelfPlay
from ResNet import ResNet
import math

def LandLordAI:
  def __init__():
    width  = myutil.width
    height = myutil.height
    chan   = myutil.chan
    #
    self.cnn=ResNet([None,width,height,chan],2)
    self.cnn.restore_round(24)
    self.game=Game()
    
  def load_game():
    self.game.load