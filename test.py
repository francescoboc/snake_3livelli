import sys
from snake import *

# in case we need to reload the library
from importlib import reload
reload(sys.modules['snake'])
from snake import *

actionMode = 4

# snake parameters
cell_size = 25
box_size = 30
snake_speed = 10
periodic = True

game = Snake(actionMode)
game.play()
