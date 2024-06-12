import sys
from snake import *

# in case we need to reload the library
from importlib import reload
reload(sys.modules['snake'])
from snake import *

# snake parameters
cell_size = 25
box_size = 30
snake_speed = 15
periodic = True

game = Snake(cell_size, box_size, snake_speed, periodic)
game.play()
