# ****************** Boccardo Gagliardi @PiMlB MALGA  ***************
# SNAKE ENVIRONMENT: evolution, reward, state, rendering
# 
# ********************************************************************

from tools import *

# in case we need to reload the library
from importlib import reload
reload(sys.modules['tools'])
from tools import *

class Snake:
    def __init__(self, actionMode=4, stateMode='simple', cell_size=30, box_size=30, snake_speed=15, periodic=True, food_rew=1, lose_rew=-10, step_rew=-0.02):
        # initialize states and actions
        self.initialize_states(stateMode)
        self.initialize_actions(actionMode)
        
        # constants
        self.cell_size = cell_size
        self.box_size = box_size
        self.snake_speed = snake_speed
        self.periodic = periodic

        # calculate size of the simulation box
        self.box_length = cell_size*box_size
        self.box_height = cell_size*box_size
        self.box_half_length = int(self.box_length/2)
        self.box_half_height = int(self.box_height/2)

        # rewards for food reached/game over/timestep
        self.food_rew = food_rew
        self.lose_rew = lose_rew
        self.step_rew = step_rew

        # state mode 
        self.stateMode = stateMode

        # reset the environment
        self.reset()

        # show info in terminal
        print(f'Action mode = {actionMode}')
        print(f'State mode = {stateMode}')

    # buil list of actions
    def initialize_actions(self, actionMode):
        if actionMode == 4:
            self.get_direction_from_actions = self._get_direction_4_actions
            self.actions = ['UP', 'RIGHT', 'DOWN', 'LEFT']
        elif actionMode == 3:
            self.get_direction_from_actions = self._get_direction_3_actions
            # list of actions
            self.actions = ['NO_TURN', 'RIGHT', 'LEFT']
            # create maps to cycle through actions
            self._directionIndexMap = {'UP':0,'LEFT':1,'DOWN':2,"RIGHT":3}
            self._indexDirectionMap = {0:'UP',1:'LEFT',2:'DOWN',3:"RIGHT"}
        else:
            raise LookupError('Invalid actionMode')

    # build list of states
    def initialize_states(self, stateMode):
        self.states = []
        if stateMode=='simple':
            self.get_state = self.get_state_simple
            for d in head_dirs:
                for c in compass_dirs:
                    self.states.append((d,c))
        elif stateMode=='body_length':
            fractions = 4
            self._boxFraction = box_size/fractions
            self.get_state = self.get_state_body_length
            bodyFractions = [b for b in range(fractions**2)]
            for d in head_dirs:
                for c in compass_dirs:
                    for b in bodyFractions:
                        self.states.append((d,c,b))
        elif stateMode=='tail_compass':
            self.get_state = self.get_state_body_position
            for d in head_dirs:
                for c in compass_dirs:
                    for t in compass_dirs:
                        self.states.append((d,c,t))
        else:
            raise LookupError('Invalid stateMode')
        self.states.append('Term')

    # TODO random spawning
    def initialize_body(self, direction, size, random=False):
        # head position
        head = [self.box_length/2, self.box_height/2] 

        # create  body parts
        if direction == "RIGHT": index, increment = 0, -1
        elif direction == "LEFT": index, increment = 0, 1
        elif direction == "UP": index, increment = 1, 1
        elif direction == "DOWN": index, increment = 1, -1

        body = []
        for i in range(size):
            bodypart = head.copy()
            bodypart[index] += increment*i * self.cell_size
            body.append(bodypart.copy())

        return head, body
    
    @property
    def body_size(self):
        return len(self.body)

    # reset the environment and output the corresponding state
    def reset(self):
        # snake's head initial position
        self.position, self.body = self.initialize_body(init_direction, init_size)

        # reset snake direction towards RIGHT
        self.direction = init_direction

        # sparn food in a random position
        self.spawn_food()

        # reset initial score
        self.score = 0

        # output state
        return self.get_state()

    # get reading from the food compass
    def get_compass(self):
        # calculate distances of food on y and x directions
        dist_y = self.food_position[1] - self.position[1]
        dist_x = self.food_position[0] - self.position[0]
        
        # determine the cardinal direction of food, considering PBC
        south = (dist_y > 0) != (abs(dist_y) > self.box_half_height)
        east = (dist_x > 0) != (abs(dist_x) > self.box_half_length)
        
        # determine compass directions based on the distances
        compass_ns = '' if dist_y == 0 else ('S' if south else 'N')
        compass_ew = '' if dist_x == 0 else ('E' if east else 'W')
        
        # set compass attribute
        self.compass = compass_ns + compass_ew
    
    def get_compass_tail(self):
        # calculate distances of tail on y and x directions
        tail_position = self.body[-1]
        dist_y = tail_position[1] - self.position[1]
        dist_x = tail_position[0] - self.position[0]
        
        # determine the cardinal direction of food, considering PBC
        south = (dist_y > 0) != (abs(dist_y) > self.box_half_height)
        east = (dist_x > 0) != (abs(dist_x) > self.box_half_length)
        
        # determine compass directions based on the distances
        compass_ns = '' if dist_y == 0 else ('S' if south else 'N')
        compass_ew = '' if dist_x == 0 else ('E' if east else 'W')
        
        # set compass attribute
        self.tail_compass = compass_ns + compass_ew

    # calculate body length as fraction of the box length
    def get_body_length_fraction(self):
        self.bodyLengthF = int(self.body_size/self._boxFraction) 

    def get_state_simple(self):
        self.get_compass()
        return (self.direction, self.compass)

    def get_state_body_length(self):
        self.get_compass()
        self.get_body_length_fraction()
        return (self.direction, self.compass, self.bodyLengthF)

    def get_state_body_position(self):
        self.get_compass()
        self.get_compass_tail()
        return (self.direction, self.compass, self.tail_compass)

    ################################## LOCOMOTION ##############################

    def spawn_food(self):
        '''
        Spawn food at random locations avoiding overlap with snake body
        '''
        self.food_position = [rng.randrange(1, (self.box_length//self.cell_size)) * self.cell_size, 
                              rng.randrange(1, (self.box_height//self.cell_size)) * self.cell_size]
        if self.food_position in self.body:
            self.spawn_food()
        self.food_spawn = True

    # update snake head and body positions
    def advance(self):
        if self.direction == 'UP':
            self.position[1] -= self.cell_size
            if self.position[1] < 0 and self.periodic:
                self.position[1] = self.box_height-self.cell_size
        if self.direction == 'DOWN':
            self.position[1] += self.cell_size
            if self.position[1] > self.box_height-self.cell_size and self.periodic:
                self.position[1] = 0
        if self.direction == 'LEFT':
            self.position[0] -= self.cell_size
            if self.position[0] < 0 and self.periodic:
                self.position[0] = self.box_length-self.cell_size
        if self.direction == 'RIGHT':
            self.position[0] += self.cell_size
            if self.position[0] > self.box_length-self.cell_size and self.periodic:
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
            if self.position[0] < 0 or self.position[0] > self.box_length-self.cell_size:
                terminated = True
            if self.position[1] < 0 or self.position[1] > self.box_height-self.cell_size:
                terminated = True

        for block in self.body[1:]:
            if self.position[0] == block[0] and self.position[1] == block[1]:
                terminated = True
                
        return terminated
    
    def _get_direction_4_actions(self, action):
        '''
        Avoids self intersection
        '''
        direction = self.direction
        if action == "NO_TURN":
            pass
        else:
            if action == 'UP' and self.direction != 'DOWN': direction = 'UP'
            if action == 'DOWN' and self.direction != 'UP': direction = 'DOWN'
            if action == 'LEFT' and self.direction != 'RIGHT': direction = 'LEFT'
            if action == 'RIGHT' and self.direction != 'LEFT': direction = 'RIGHT'
        
        return direction

    def _get_direction_3_actions(self, action):
        '''
        Can only turn or do nothing. No self intersection to be prevented.
        '''
        
        direction = self.direction
        if action == "NO_TURN" or action == 'UP' or action == 'DOWN':
            pass
        else:
            current_index = self._directionIndexMap[self.direction]
            if action == 'LEFT':
                new_index = (current_index + 1) % 4
            elif action == 'RIGHT':
                new_index = (current_index - 1) % 4
            direction = self._indexDirectionMap[new_index]

        return direction 

    # do one timestep
    def step(self, action):
        self.direction = self.get_direction_from_actions(action)

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
            next_state = self.get_state()
        else:
            next_state = 'Term'

        return next_state, reward, terminated

    # play with a given policy or against a user
    def play(self, policy = None):
        self.init_render()
        self.init_render()

        # reset the game
        state = self.reset()

        # game loop
        while True:
            if policy is None:
                # check if a key has been pressed
                action = read_keys()
            else:
                action = policy[state]

            # update snake position
            next_state, reward, terminal = self.step(action)
            
            self.render()
            
            if terminal:
                self.game_over()

            # shift state
            state = next_state

    
    ############################## RENDERING METHODS #######################

    # initialize rendering environment (pygame)
    def init_render(self):
        # initialise pygame 
        pygame.init()
        
        # initialise game window
        pygame.display.set_caption('Snake')
        self.game_window = pygame.display.set_mode((self.box_length, self.box_height))
        
        # FPS (frames per second) controller
        self.fps = pygame.time.Clock()

        # create main font object 
        self.main_font = pygame.font.SysFont(font, font_size)

    # display score onscreen
    def show_score(self, color):
        # create the display surface object 
        self.score_surface = self.main_font.render('Score: ' + str(self.score), True, color)

        # create a rectangular object for the text
        self.score_rect = self.score_surface.get_rect()
        
        # display text
        self.game_window.blit(self.score_surface, self.score_rect)

    # display info about state onscreen
    def show_state_info(self, color):
        self.compass_surface = self.main_font.render('Compass: ' + str(self.compass), True, color)
        self.compass_rect = self.score_surface.get_rect()
        self.game_window.blit(self.compass_surface, (self.box_length-125,0))

        if self.stateMode=='body_length':
            self.bodyInfo_surface = self.main_font.render('body: fraction, length : ' + str(self.bodyLengthF)+", "+str(self.body_size), True, 'green')
            self.bodyInfo_rect = self.bodyInfo_surface.get_rect()
            self.game_window.blit(self.bodyInfo_surface, (0, self.box_length-25))

        elif self.stateMode=='tail_compass':
            self.bodyInfo_surface = self.main_font.render('Tail comp: ' + str(self.tail_compass), True, 'green')
            self.bodyInfo_rect = self.bodyInfo_surface.get_rect()
            self.game_window.blit(self.bodyInfo_surface, (0, self.box_length-25))

    def game_over(self):
        # create font object my_font
        self.my_font = pygame.font.SysFont('arial', 50)
        
        # create a text surface on which text will be drawn
        self.game_over_surface = self.my_font.render('Your score is: ' + str(self.score), True, red)
        
        # create a rectangular object for the text 
        self.game_over_rect = self.game_over_surface.get_rect()
        
        # set position of the text
        self.game_over_rect.midtop = (self.box_length/2, self.box_height/4)
        
        # blit will draw the text on screen
        self.game_window.blit(self.game_over_surface, self.game_over_rect)
        pygame.display.flip()
        
        # after 2 seconds
        time.sleep(2)
        
        # deactivate pygame library
        pygame.quit()

        # exit python
        sys.exit()

    # render the current frame
    def render(self):
        # clear the screen (fill with black)
        self.game_window.fill(black)

        # draw head 
        pygame.draw.rect(self.game_window, light_green, pygame.Rect(self.body[0][0], self.body[0][1], self.cell_size, self.cell_size))

        # draw rest of the body
        for pos in self.body[1:]:
            pygame.draw.rect(self.game_window, green, pygame.Rect(pos[0], pos[1], self.cell_size, self.cell_size))

        # draw food
        pygame.draw.rect(self.game_window, red, pygame.Rect(self.food_position[0], self.food_position[1], self.cell_size, self.cell_size), 
                border_radius=int(self.cell_size/3))
        
        # display score and state info
        self.show_score(white)
        self.show_state_info(white)

        # FPS/refresh Rate
        self.fps.tick(self.snake_speed)

        # refresh game screen
        pygame.display.update()
