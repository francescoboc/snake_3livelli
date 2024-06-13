# ****************** Boccardo Gagliardi @PiMlB MALGA  ***************
# SNAKE ENVIRONMENT: evolution, reward, state, rendering
# 
# ********************************************************************
# COMMENTS:
#   snake.play(policy=None) --> if policy is not None play the policy

#TODO Reward function
#reset gives state 

import pygame
import time
import random
import sys


# colors
black = pygame.Color(15, 15, 15)
white = pygame.Color(255, 255, 255)
red = pygame.Color(245, 61, 5)
green = pygame.Color(141, 245, 5)
light_green = pygame.Color(225, 245, 5)
blue = pygame.Color(0, 0, 255)

head_dirs = ['UP', 'RIGHT', 'DOWN', 'LEFT']
compass_dirs =['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']



def read_keys():
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                return 'UP'
            if event.key == pygame.K_DOWN:
                return 'DOWN'
            if event.key == pygame.K_LEFT:
                return 'LEFT'
            if event.key == pygame.K_RIGHT:
                return 'RIGHT'
    return "NO_TURN"





class Snake:
    def __init__(self, actionMode,cell_size=25, box_size=30, snake_speed=15, periodic=True, food_rew=1, lose_rew=-100, step_rew=-0.1,considerBodyLength=False):
        
        # ACTION SPACE SELECTION
        if actionMode == 4:
            self.getDirectionFromActions = self._getDirection4Actions
            # list of actions
            self.actions = ['UP', 'RIGHT', 'DOWN', 'LEFT']
            print("4 actions mode")
        elif actionMode == 3:
            self.getDirectionFromActions = self._getDirection3Actions
            # list of actions
            self.actions = ['NO_TURN', 'RIGHT', 'LEFT']
            print("3 actions mode")
        else:
            raise LookupError("Select admissible action space")
        # constants
        self.cell_size = cell_size
        self.box_size = box_size
        self.snake_speed = snake_speed
        self.periodic = periodic

        # size of the simulation box
        self.box_length = cell_size*box_size
        self.box_height = cell_size*box_size
        self.box_half_length = int(self.box_length/2)
        self.box_half_height = int(self.box_height/2)

        # rewards
        self.food_rew = food_rew
        self.lose_rew = lose_rew
        self.step_rew = step_rew


        # list of states
        self.states = []
        self.considerBodyL = considerBodyLength
        fractions = 4
        self._boxFraction = self.box_size/fractions
        if considerBodyLength:
            print("** States enriched with body length info **")
            self.get_state = self._get_state_bodyL
            bodyFractions = [b for b in range(fractions**2)]
            for d in head_dirs:
                for c in compass_dirs:
                    for b in bodyFractions:
                        self.states.append((d,c,b))
        else:   
            self.get_state = self._get_state_default
            for d in head_dirs:
                for c in compass_dirs:
                    self.states.append((d,c))


        self.state_size = len(self.states) 



        self._directionIndexMap = {'UP':0,'LEFT':1,'DOWN':2,"RIGHT":3}
        self._indexDirectionMap = {0:'UP',1:'LEFT',2:'DOWN',3:"RIGHT"}

        self.reset()


    def initialize_body(self,direction,size=4):
        #TODO random initial direction
        #TODO: Random spawning
        head = [self.box_length/2, self.box_height/2] 
        # body = [head.copy()]
        # index = 0 
        # increment = -1
        # for i in range(size):

        #     body.append()
        
        if direction=="RIGHT":
            body = [head.copy(),[head[0]-self.cell_size, head[1]],
                    [head[0]-2*self.cell_size, head[1]],
                    [head[0]-3*self.cell_size, head[1]],
                    ]
        else:
            raise KeyError("Not implemented")
        return head, body
    
    @property
    def body_size(self):
        return len(self.body)


    def reset(self):
        # snake's head initial position
        direction = "RIGHT"
        size = 4
        self.position,self.body = self.initialize_body(direction=direction)
        # random food position
        self.spawnFood()

        # reset snake direction towards RIGHT
        self.direction = direction

        # reset initial score
        self.score = 0


        return self.get_state()


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
    
    def get_bodyLengthFraction(self):
        '''
        body length as box fraction.
        '''
        output = int(self.body_size/self._boxFraction) 
        return output


    def _get_state_default(self):
        self.get_compass()
        return (self.direction, self.compass)

    def _get_state_bodyL(self):
        self.get_compass()
        return (self.direction, self.compass,self.get_bodyLengthFraction())
    


    
    #################
    ############################## * RENDERING METHODS * #######################

    def init_render(self):
        # initialise pygame 
        pygame.init()
        
        # initialise game window
        pygame.display.set_caption('Snake')
        self.game_window = pygame.display.set_mode((self.box_length, self.box_height))
        

        # FPS (frames per second) controller
        self.fps = pygame.time.Clock()

    # function to display score
    def show_score(self, color, font, size,bodyLenghtF = None):
        # creating font object score_font
        self.score_font = pygame.font.SysFont(font, size)
        
        # create the display surface object 
        self.score_surface = self.score_font.render('Score: ' + str(self.score), True, color)
        self.compass_surface = self.score_font.render('Compass: ' + str(self.compass), True, color)

        #extra body length
        if bodyLenghtF is not None:
            self.bodyInfo_surface = self.score_font.render('BodyF: ' + str((bodyLenghtF,self.body_size)), True, 'green')
            self.bodyInfo_rect = self.bodyInfo_surface.get_rect()
            self.game_window.blit(self.bodyInfo_surface ,(0,self.box_length-25))
        # create a rectangular object for the text
        self.score_rect = self.score_surface.get_rect()
        self.compass_rect = self.score_surface.get_rect()
        
        # display text
        self.game_window.blit(self.score_surface, self.score_rect)
        self.game_window.blit(self.compass_surface, (self.box_length-125,0))

    # game over function
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

    def render(self,bodyLength = None):

        
        self.game_window.fill(black)
        pygame.draw.rect(self.game_window, light_green, pygame.Rect(self.body[0][0], self.body[0][1], self.cell_size, self.cell_size))
        for pos in self.body[1:]:
            pygame.draw.rect(self.game_window, green, pygame.Rect(pos[0], pos[1], self.cell_size, self.cell_size))

        pygame.draw.rect(self.game_window, red, pygame.Rect(self.food_position[0], self.food_position[1], self.cell_size, self.cell_size), 
                border_radius=int(self.cell_size/3))
        
        # display score continuously
        self.show_score(white, 'arial', 20,bodyLength)
        # FPS/refresh Rate
        self.fps.tick(self.snake_speed)
        # refresh game screen
        pygame.display.update()
    
#############################

################################## LOCOMOTION ##############################

    def spawnFood(self):
        '''
        Spawn food at random locations avoiding overlap with snake body
        '''
        self.food_position = [random.randrange(1, (self.box_length//self.cell_size)) * self.cell_size, 
                              random.randrange(1, (self.box_height//self.cell_size)) * self.cell_size]
        if self.food_position in self.body:
            self.spawnFood()
        self.food_spawn = True


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
        # if food and snake collide then scores will be incremented 
        self.body.insert(0, list(self.position))

        if self.position[0] == self.food_position[0] and self.position[1] == self.food_position[1]:
            self.score += 1
            self.food_spawn = False
        else:
            self.body.pop()
        
        return not self.food_spawn

    
    def isTerminal(self):
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
    

    def _getDirection4Actions(self, action):
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

    def _getDirection3Actions(self, action):
        '''
        Can only turn or doi nothing. No self intersection to be prevented.
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

    def step(self, action):
        

        self.direction = self.getDirectionFromActions(action)

        ########### DISPLACEMENT #################################
        gotFood = self.advance()
        #####
        
        ##### CHECK TERMINATION + GET REWARDS

        terminated = self.isTerminal()
        if gotFood:
            reward = self.food_rew
        elif terminated:
            reward = self.lose_rew
        else:
            reward = self.step_rew
        
        # if food was captured, spawn a new one
        if self.food_spawn == False:
            self.spawnFood()

        next_state = self.get_state()

        
        return next_state, reward, terminated


    
        # # if nothing was pressed, return 'NO_TURN' action
        # return 'NO_TURN'

    



###############################################
# ############################  


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
                # print(state,action)
                # action = self.actions[action]

            # update snake position
            next_state,reward,terminal = self.step(action)
            
            #Test
            bodyLengthF = self.get_bodyLengthFraction()

            self.render(bodyLengthF)
            
            if terminal:
                self.game_over()

            # shift state
            state = next_state

            
            

