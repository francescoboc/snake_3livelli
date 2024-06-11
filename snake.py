# ****************** Boccardo Gagliardi @PiMlB MALGA  ***************
# SNAKE ENVIRONMENT: evolution, reward, state, rendering
# 
# ********************************************************************
# COMMENTS:
#   snake.play(policy=None) --> if policy is not None play the policy
#
# TODO:
# Insert pygame initializations somewhere

import pygame
import time
import random

# colors
black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)

class Snake:
    def __init__(self, cell_size, box_size, snake_speed, periodic = True):
        # constants
        self.cell_size = cell_size
        self.box_size = box_size
        self.snake_speed = snake_speed
        self.periodic = periodic

        # size of the simulation box
        self.box_length = cell_size*box_size
        self.box_height = cell_size*box_size

        # initialise rendering window
        self.init_render()

    def reset(self):
        # snake's head initial position
        self.position = [self.box_length/2, self.box_height/2] 

        # first 4 blocks of snake body (head + 3 body blocks)
        self.body = [self.position.copy(),
                [self.position[0]-self.cell_size, self.position[1]],
                [self.position[0]-2*self.cell_size, self.position[1]],
                [self.position[0]-3*self.cell_size, self.position[1]],
                ]

        # random food position
        self.food_position = [random.randrange(1, (self.box_length//self.cell_size)) * self.cell_size, 
                        random.randrange(1, (self.box_height//self.cell_size)) * self.cell_size]

        # food flag
        self.food_spawn = True

        # reset snake direction towards RIGHT
        self.direction = 'RIGHT'
        self.change_to = self.direction

        # reset initial score
        self.score = 0

    def init_render(self):
        # initialise pygame 
        pygame.init()

        # initialise game window
        pygame.display.set_caption('Snake')
        self.game_window = pygame.display.set_mode((self.box_length, self.box_height))

        # FPS (frames per second) controller
        self.fps = pygame.time.Clock()

    # function to display score
    def show_score(self, color, font, size):

        # creating font object score_font
        self.score_font = pygame.font.SysFont(font, size)
        
        # create the display surface object 
        self.score_surface = self.score_font.render('Score: ' + str(self.score), True, color)
        
        # create a rectangular object for the text
        self.score_rect = self.score_surface.get_rect()
        
        # display text
        self.game_window.blit(self.score_surface, self.score_rect)

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
        exit()

    def play(self):
        # reset the game
        self.reset()

        # game loop
        while True:
            # handling key events
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.change_to = 'UP'
                    if event.key == pygame.K_DOWN:
                        self.change_to = 'DOWN'
                    if event.key == pygame.K_LEFT:
                        self.change_to = 'LEFT'
                    if event.key == pygame.K_RIGHT:
                        self.change_to = 'RIGHT'

            if self.change_to == 'UP' and self.direction != 'DOWN': self.direction = 'UP'
            if self.change_to == 'DOWN' and self.direction != 'UP': self.direction = 'DOWN'
            if self.change_to == 'LEFT' and self.direction != 'RIGHT': self.direction = 'LEFT'
            if self.change_to == 'RIGHT' and self.direction != 'LEFT': self.direction = 'RIGHT'

            # move the snake
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
                
            if not self.food_spawn:
                self.food_position = [random.randrange(1, (self.box_length//self.cell_size)) * self.cell_size, 
                                random.randrange(1, (self.box_height//self.cell_size)) * self.cell_size]
                
            self.food_spawn = True
            self.game_window.fill(black)
            
            # draw
            for pos in self.body:
                pygame.draw.rect(self.game_window, green, pygame.Rect(pos[0], pos[1], self.cell_size, self.cell_size))

            pygame.draw.rect(self.game_window, white, pygame.Rect(self.food_position[0], self.food_position[1], self.cell_size, self.cell_size))

            # game over conditions
            if not self.periodic:
                if self.position[0] < 0 or self.position[0] > self.box_length-cell_size:
                    self.game_over()
                if self.position[1] < 0 or self.position[1] > box_height-cell_size:
                    self.game_over()

            for block in self.body[1:]:
                if self.position[0] == block[0] and self.position[1] == block[1]:
                    self.game_over()

            # display score continuously
            self.show_score(white, 'arial', 20)

            # refresh game screen
            pygame.display.update()

            # FPS/refresh Rate
            self.fps.tick(self.snake_speed)
