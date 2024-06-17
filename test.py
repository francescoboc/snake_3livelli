from snake import *

# in case we need to reload the library
from importlib import reload
reload(sys.modules['snake'])
from snake import *

# seed to initialize the RNG
seed = None
seed_rng(seed)

# snake parameters
snake_speed = 15
periodic = True

actionMode = 4

stateMode = 'simple'
# stateMode = 'body_length'
# stateMode = 'tail_compass'

snake = Snake(actionMode, stateMode, snake_speed=snake_speed)
snake.play()
