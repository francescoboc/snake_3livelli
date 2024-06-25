import numpy as np
import gymnasium as gym
from gymnasium import spaces
from tools import *

dir_id_wheel = {'UP':0,'LEFT':1,'DOWN':2,"RIGHT":3}
id_dir_wheel = {0:'UP',1:'LEFT',2:'DOWN',3:"RIGHT"}

actions_map = {0:'NO_TURN',1:'RIGHT',2:'LEFT'}

cell_size=30
# box_size=36
box_size=10
snake_speed=15
periodic=True 
food_rew=1 
lose_rew=-10 
step_rew=-0.02
rand_init_body_length=True
rand_init_direction=True

N_DISCRETE_ACTIONS = 3
N_CHANNELS, HEIGHT, WIDTH = 1, box_size, box_size

class SnakeEnv(gym.Env):
    """Custom Environment that follows gym interface."""
    def __init__(self):
        super(SnakeEnv, self).__init__()
        # Define action and observation space
        # They must be gym.spaces objects
        self.action_space = spaces.Discrete(N_DISCRETE_ACTIONS)

        # Example for using image as input (channel-first; channel-last also works):
        self.observation_space = spaces.Box(low=0, high=255,
                                            shape=(N_CHANNELS, HEIGHT, WIDTH), dtype=np.uint8)

        # constants
        self.cell_unit = 1
        self.box_size = box_size
        self.snake_speed = snake_speed
        self.periodic = periodic

        # calculate size of the simulation box
        self.box_length = self.cell_unit*box_size
        self.box_height = self.cell_unit*box_size
        self.box_half_length = int(self.box_length/2)
        self.box_half_height = int(self.box_height/2)

        # rewards for food reached/game over/timestep
        self.food_rew = food_rew
        self.lose_rew = lose_rew
        self.step_rew = step_rew

        # flags to randomize the initial configuration of the snake
        self.rand_init_body_length = rand_init_body_length
        self.rand_init_direction = rand_init_direction

    def reset(self, seed=None, pygame_render=False):
        if self.rand_init_body_length:
            size = rng.randrange(init_size, self.box_size//2)
        else:
            size = init_size
        if self.rand_init_direction:
            direction = rng.choice(head_dirs)
        else:
            direction = init_direction

        # snake's head initial position
        self.position, self.body = self.initialize_body(direction, size)

        # reset snake direction towards RIGHT
        self.direction = direction

        # sparn food in a random position
        self.spawn_food()

        # reset initial score
        self.score = 0

        # initialize render window
        if pygame_render:
            self.init_render()

        # return current state
        return (self.get_state(), {})

    def step(self, action, human_action=False):
        if human_action:
            self.direction = self.get_direction_from_actions(action)
        else:
            self.direction = self.get_direction_from_actions(actions_map[action])

        gotFood = self.advance()
        
        terminated = self.is_terminal()

        if gotFood:
            reward = self.food_rew
        elif terminated:
            reward = self.lose_rew
        else:
            reward = self.step_rew
        
        # if food was captured, spawn a new one
        if self.food_spawn == False:
            self.spawn_food()

        # get reading of new state
        if not terminated:
            observation = self.get_state()
        else:
            observation = box = np.zeros((self.box_height, self.box_length), np.uint8)

        return observation, reward, terminated, False, {}

    def get_state(self):
        # create empty array for the sim box
        box = np.zeros((1,self.box_height, self.box_length), np.uint8)

        # body
        for pos in self.body[1:]:
            box[0][pos[1], pos[0]] = 255

        # head
        box[0][self.body[0][1], self.body[0][0]] = 200

        # food
        box[0][self.food_position[1], self.food_position[0]] = 100
        return box

    def get_direction_from_actions(self, action):
        direction = self.direction
        if action == "NO_TURN" or action == 'UP' or action == 'DOWN':
            pass
        else:
            current_index = dir_id_wheel[self.direction]
            if action == 'LEFT':
                new_index = (current_index + 1) % 4
            elif action == 'RIGHT':
                new_index = (current_index - 1) % 4
            direction = id_dir_wheel[new_index]

        return direction 

    # update snake head and body positions
    def advance(self):
        if self.direction == 'UP':
            self.position[1] -= 1
            if self.position[1] < 0 and self.periodic:
                self.position[1] = self.box_height-1
        if self.direction == 'DOWN':
            self.position[1] += 1
            if self.position[1] > self.box_height-1 and self.periodic:
                self.position[1] = 0
        if self.direction == 'LEFT':
            self.position[0] -= 1
            if self.position[0] < 0 and self.periodic:
                self.position[0] = self.box_length-1
        if self.direction == 'RIGHT':
            self.position[0] += 1
            if self.position[0] > self.box_length-1 and self.periodic:
                self.position[0] = 0
            
        # snake body growing mechanism 
        self.body.insert(0, list(self.position))

        # if food and snake collide 
        if self.position[0] == self.food_position[0] and self.position[1] == self.food_position[1]:
            # increment score
            self.score += 1
            self.food_spawn = False
        else:
            # otherwise, delete the last body element
            self.body.pop()
        
        return not self.food_spawn

    # check if a terminal state was reached
    def is_terminal(self):
        terminated = False
        if not self.periodic:
            if self.position[0] < 0 or self.position[0] > self.box_length-1:
                terminated = True
            if self.position[1] < 0 or self.position[1] > self.box_height-1:
                terminated = True

        for block in self.body[1:]:
            if self.position[0] == block[0] and self.position[1] == block[1]:
                terminated = True
                
        return terminated

    def initialize_body(self, direction, size, random=False):
        # head position
        head = [self.box_length//2, self.box_height//2] 
        # create  body parts
        if direction == "RIGHT": index, increment = 0, -1
        elif direction == "LEFT": index, increment = 0, 1
        elif direction == "UP": index, increment = 1, 1
        elif direction == "DOWN": index, increment = 1, -1

        body = []
        for i in range(size):
            bodypart = head.copy()
            bodypart[index] += increment*i * self.cell_unit
            body.append(bodypart.copy())

        return head, body

    def spawn_food(self):
        # spawn food at random locations avoiding overlap with snake body
        self.food_position = [rng.randrange(1, (self.box_length//self.cell_unit)) * self.cell_unit, 
                              rng.randrange(1, (self.box_height//self.cell_unit)) * self.cell_unit]
        if self.food_position in self.body:
            self.spawn_food()
        self.food_spawn = True


    # RENDERING METHODS
    def render(self):
        # clear the screen (fill with black)
        self.game_window.fill(black)

        # draw rest of the body
        for pos in self.body:
            bodyRect = pygame.Rect(pos[0]*cell_size, pos[1]*cell_size, cell_size, cell_size)
            pygame.draw.rect(self.game_window, green, bodyRect)

        # draw food
        food_rect = pygame.Rect(self.food_position[0]*cell_size, self.food_position[1]*cell_size, cell_size, cell_size), 
        pygame.draw.rect(self.game_window, red, food_rect)
        
        # FPS/refresh Rate
        self.fps.tick(self.snake_speed)

        # refresh game screen
        pygame.display.update()

    # initialize rendering environment (pygame)
    def init_render(self):
        # initialise pygame 
        pygame.init()
        
        # initialise game window
        pygame.display.set_caption('Snake')
        self.game_window = pygame.display.set_mode((self.box_length*cell_size, self.box_height*cell_size))
        
        # FPS (frames per second) controller
        self.fps = pygame.time.Clock()

        # eyes parameters
        self.eye_radius = self.cell_unit // 6
        self.eye_inner_radius = self.cell_unit // 10
        self.eye_offset = self.cell_unit // 4

# snake = SnakeEnv()
# obs = snake.reset()
# for i in range(10):
#     # action = 'NO_TURN'
#     action = 0
#     obs, rew, term, _, _ = snake.step(action)
#     print(obs)
#     print(rew, term)
#     time.sleep(1)
#     print()
