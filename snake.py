from tools import *

# check if python is running on macOS
import platform
if platform.system() == 'Darwin': ON_MAC = True
else: ON_MAC = False

# load retro font from a .ttf file 
FONT_PATH = 'fonts/ARCADECLASSIC.TTF'  

class Snake:
    def __init__(self, 
            action_mode=3, 
            state_mode='simple', 
            cell_size=30, 
            box_size=30, 
            snake_speed=15, 
            periodic=True, 
            rand_init_body_length=False,
            rand_init_direction=False,
            show_compass=True,
            sound_effects=False,
            show_state_info=False,
            team_name=None,
            window_position=None,
            verbose=True,
            food_rew=1.0, 
            lose_rew=-10.0, 
            step_rew=0.0,
            trun_rew=-5.0,
            ):
        
        # constants
        self.cell_size = cell_size
        self.box_size = box_size
        self.snake_speed = snake_speed
        self.periodic = periodic
        self.box_size_sq = box_size*box_size

        # calculate size of the simulation box
        self.box_length = cell_size*box_size
        self.box_height = cell_size*box_size
        self.box_half_length = int(self.box_length/2)
        self.box_half_height = int(self.box_height/2)

        # rewards for food reached/game over/timestep
        self.food_rew = food_rew
        self.lose_rew = lose_rew
        self.step_rew = step_rew
        self.trun_rew = trun_rew

        # flags to randomize the initial configuration of the snake
        self.rand_init_body_length = rand_init_body_length
        self.rand_init_direction = rand_init_direction

        # initialize states and actions
        self.initialize_states(state_mode)
        self.initialize_actions(action_mode)

        # the state_mode flag needs to be seen by some methods
        self.state_mode = state_mode

        # flags for sounds and state info
        self.show_compass = show_compass
        self.sound_effects = sound_effects
        self.show_state_info = show_state_info

        self.window_position = window_position
        self.team_name = team_name

        # load compass images
        if self.show_compass:
            self.compass_images = {
                'N': pygame.image.load('./img/north.png'),
                'NE': pygame.image.load('./img/north_east.png'),
                'E': pygame.image.load('./img/east.png'),
                'SE': pygame.image.load('./img/south_east.png'),
                'S': pygame.image.load('./img/south.png'),
                'SW': pygame.image.load('./img/south_west.png'),
                'W': pygame.image.load('./img/west.png'),
                'NW': pygame.image.load('./img/north_west.png')
            }

            # resize images
            for key in self.compass_images:
                self.compass_images[key] = pygame.transform.smoothscale(self.compass_images[key], (self.cell_size*4 , self.cell_size*4))

            # load proximity images
            if self.state_mode == 'proximity':
                self.proximity_images = {
                    'f': pygame.image.load('./img/prox_f.png'),
                    'l': pygame.image.load('./img/prox_l.png'),
                    'r': pygame.image.load('./img/prox_r.png'),
                    'fl': pygame.image.load('./img/prox_fl.png'),
                    'fr': pygame.image.load('./img/prox_fr.png'),
                    'lr': pygame.image.load('./img/prox_lr.png'),
                    'flr': pygame.image.load('./img/prox_flr.png'),
                }

                # resize images
                for key in self.proximity_images:
                    self.proximity_images[key] = pygame.transform.smoothscale(self.proximity_images[key], (self.cell_size*1.7 , self.cell_size*1.7))

                # rotation angles depending on head directions
                self.rotation_angles = {
                    'UP': 0,
                    'RIGHT': -90,
                    'DOWN': -180,
                    'LEFT': -270,
                    }

        # reset the environment
        self.reset()

        # show info in terminal
        if verbose:
            print(f'Action mode = {action_mode}')
            print(f'State mode = {state_mode}')
            print(f'Periodic = {periodic}')
            print(f'Random initial body length = {rand_init_body_length}')
            print(f'Random initial direction = {rand_init_direction}')

    # buil list of actions
    def initialize_actions(self, action_mode):
        if action_mode == 4:
            self.get_direction_from_actions = self._get_direction_4_actions
            self.actions = ['UP', 'RIGHT', 'DOWN', 'LEFT']
        elif action_mode == 3:
            self.get_direction_from_actions = self._get_direction_3_actions
            # list of actions
            self.actions = ['LEFT', 'NO_TURN', 'RIGHT']
            # create maps to cycle through actions
            self._direction_index_map = {'UP':0,'LEFT':1,'DOWN':2,"RIGHT":3}
            self._index_direction_map = {0:'UP',1:'LEFT',2:'DOWN',3:"RIGHT"}
        else:
            raise LookupError('Invalid action_mode')

    # build list of states
    def initialize_states(self, state_mode):
        self.states = []
        if state_mode=='simple':
            self.get_state = self.get_state_simple
            for d in head_dirs:
                for c in compass_dirs:
                    self.states.append((d,c))
        elif state_mode=='proximity':
            self.get_state = self.get_state_proximity
            for d in head_dirs:
                for c in compass_dirs:
                    for p in prox_values:
                        self.states.append((d,c,p))
        else:
            raise LookupError('Invalid state_mode')
        self.states.append('Term')

    def initialize_body(self, direction, size):
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
            bodypart[index] += increment*i * self.cell_size
            body.append(bodypart.copy())

        return head, body
    
    @property
    def body_size(self):
        return len(self.body)

    # reset the environment and output the corresponding state
    def reset(self):
        if self.rand_init_body_length:
            size = rng.randrange(init_size,int(self.box_size/2))
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

        # reset counters to check for truncation
        self.old_score = 0
        self.stuck_counter = 0

        # output state
        return self.get_state()

    # get reading from the compass
    def check_compass(self, target_coords):
        # calculate distances of target on y and x directions
        dist_y = target_coords[1] - self.position[1]
        dist_x = target_coords[0] - self.position[0]
        
        # determine the cardinal direction of target
        if self.periodic:
            south = (dist_y > 0) != (abs(dist_y) > self.box_half_height)
            east = (dist_x > 0) != (abs(dist_x) > self.box_half_length)
        else:
            south = dist_y > 0
            east = dist_x > 0
        
        # determine compass directions based on the distances
        compass_ns = '' if dist_y == 0 else ('S' if south else 'N')
        compass_ew = '' if dist_x == 0 else ('E' if east else 'W')
        
        # set compass attribute
        return compass_ns + compass_ew

    def check_proximity(self):
        if self.periodic:
            dir_up = [self.position[0], (self.position[1] - self.cell_size) % self.box_height]
            dir_down = [self.position[0], (self.position[1] + self.cell_size) % self.box_height]
            dir_left = [(self.position[0] - self.cell_size) % self.box_length, self.position[1]]
            dir_right = [(self.position[0] + self.cell_size) % self.box_length, self.position[1]]
        else:
            dir_up = [self.position[0], (self.position[1] - self.cell_size)]
            dir_down = [self.position[0], (self.position[1] + self.cell_size)]
            dir_left = [(self.position[0] - self.cell_size), self.position[1]]
            dir_right = [(self.position[0] + self.cell_size), self.position[1]]

        # define front, left, right positions depending on direction
        if self.direction == 'UP':
            front = dir_up
            left = dir_left
            right = dir_right

        elif self.direction == 'DOWN':
            front = dir_down
            left = dir_right
            right = dir_left

        elif self.direction == 'LEFT':
            front = dir_left
            left = dir_down
            right = dir_up

        elif self.direction == 'RIGHT':
            front = dir_right
            left = dir_up
            right = dir_down

        prox_front, prox_left, prox_right = '', '', ''

        # check proximity with snake body
        for block in self.body[1:]:
            if front == block:
                prox_front = 'f'
            if left == block:
                prox_left = 'l'
            if right == block:
                prox_right = 'r'

        # check proximity with box boundaries
        if not self.periodic:
            if self.out_of_bounds(front):
                prox_front = 'f'
            if self.out_of_bounds(left):
                prox_left = 'l'
            if self.out_of_bounds(right):
                prox_right = 'r'

        return prox_front + prox_left + prox_right

    # check if pos is out of box bounds
    def out_of_bounds(self, pos):
        return pos[0] < 0 or pos[0] > self.box_length-self.cell_size or pos[1] < 0 or pos[1] > self.box_height-self.cell_size
                
    ################################## STATE DEFS ##############################

    def get_state_simple(self):
        self.compass = self.check_compass(self.food_position)
        return (self.direction, self.compass)

    def get_state_proximity(self):
        self.compass = self.check_compass(self.food_position)
        self.proximity = self.check_proximity()
        return (self.direction, self.compass, self.proximity)

    ################################## LOCOMOTION ##############################

    # spawn food at random locations avoiding overlap with snake body
    def spawn_food(self):
        self.food_position = [rng.randrange(1, (self.box_length//self.cell_size)) * self.cell_size, 
                              rng.randrange(1, (self.box_height//self.cell_size)) * self.cell_size]
        if self.food_position in self.body:
            self.spawn_food()
        self.food_eaten = False

    # update snake head and body positions
    def advance(self):
        if self.periodic:
            if self.direction == 'UP':
                self.position[1] = (self.position[1] - self.cell_size) % self.box_height
            elif self.direction == 'DOWN':
                self.position[1] = (self.position[1] + self.cell_size) % self.box_height
            elif self.direction == 'LEFT':
                self.position[0] = (self.position[0] - self.cell_size) % self.box_length
            elif self.direction == 'RIGHT':
                self.position[0] = (self.position[0] + self.cell_size) % self.box_length
        else:
            if self.direction == 'UP':
                self.position[1] = self.position[1] - self.cell_size
            elif self.direction == 'DOWN':
                self.position[1] = self.position[1] + self.cell_size
            elif self.direction == 'LEFT':
                self.position[0] = self.position[0] - self.cell_size
            elif self.direction == 'RIGHT':
                self.position[0] = self.position[0] + self.cell_size

        # snake body growing mechanism 
        self.body.insert(0, list(self.position))

        # if food and snake collide 
        if self.position[0] == self.food_position[0] and self.position[1] == self.food_position[1]:
            # increment score
            self.score += 1
            # change flag to keep track of food spawning
            self.food_eaten = True
        else:
            # otherwise, delete the last body element
            self.body.pop()

    # check if a terminal state was reached
    def is_terminal(self):
        terminated = False

        # check collision with box boundaries
        if not self.periodic:
            if self.position[0] < 0 or self.position[0] > self.box_length-self.cell_size:
                terminated = True
            if self.position[1] < 0 or self.position[1] > self.box_height-self.cell_size:
                terminated = True

        # check collision with snake body
        for block in self.body[1:]:
            if self.position == block:
                terminated = True
                
        return terminated
    
    def _get_direction_4_actions(self, action):
        direction = self.direction
        if action == "NO_TURN":
            pass
        # avoids self intersection
        else:
            if action == 'UP' and self.direction != 'DOWN': direction = 'UP'
            if action == 'DOWN' and self.direction != 'UP': direction = 'DOWN'
            if action == 'LEFT' and self.direction != 'RIGHT': direction = 'LEFT'
            if action == 'RIGHT' and self.direction != 'LEFT': direction = 'RIGHT'
        
        return direction

    # can only turn or do nothing (no self intersection to be prevented)
    def _get_direction_3_actions(self, action):
        direction = self.direction
        if action == "NO_TURN" or action == 'UP' or action == 'DOWN':
            pass
        else:
            current_index = self._direction_index_map[self.direction]
            if action == 'LEFT':
                new_index = (current_index + 1) % 4
            elif action == 'RIGHT':
                new_index = (current_index - 1) % 4
            direction = self._index_direction_map[new_index]

        return direction 

    # advance one timestep
    def step(self, action):
        # set direction based on action and advance snake in time
        self.direction = self.get_direction_from_actions(action)
        self.advance()

        # check if terminal state or truncation was reached
        terminated = self.is_terminal()
        truncated = self.is_truncated()

        # if food was eaten, spawn a new one
        if self.food_eaten:
            self.spawn_food()
            # play sound
            if self.sound_effects:
                self.sound_chomp.play()

        # assign rewards
        if terminated:
            reward = self.lose_rew
        elif truncated:
            reward = self.trun_rew
        elif self.food_eaten:
            reward = self.food_rew
        else:
            reward = self.step_rew
        
        # get reading of new state
        if not terminated:
            next_state = self.get_state()
        else:
            next_state = 'Term'

        return next_state, reward, terminated, truncated

    # check if the snake is stuck in a loop
    def is_truncated(self):
        truncated = False

        # if score didn't change, increase counter
        if self.score == self.old_score: self.stuck_counter += 1
        else: self.stuck_counter = 0

        # if the counter is stuck for too long, truncate
        if self.stuck_counter == self.box_size_sq:
            truncated = True

        self.old_score = self.score
        return truncated

    # play with a given policy or against a user
    def play(self, policy=None, render=True):
        if render:
            self.init_render()

        # reset the game
        state = self.reset()

        # game loop
        escape_pressed = False
        while not escape_pressed:
            if policy is None:
                # check if an action key has been pressed
                action, escape_pressed = read_keys()
            else:
                # check if ESC has been pressed
                escape_pressed = read_esc()
                action = policy[state]

            # update snake position
            next_state, reward, terminated, truncated = self.step(action)

            if terminated or truncated:
                if render:
                    self.game_over()
                    return self.score, truncated
                else:
                    return self.score, truncated

            if render:
                self.render_frame()

            # shift state
            state = next_state

    ############################## RENDERING METHODS #######################

    # initialize rendering environment (pygame)
    def init_render(self):
        # set position of game window
        if self.window_position is not None:
            set_window_position(*self.window_position)  

        # initialise pygame 
        pygame.init()

        # initialise game window (add height of info bar)
        pygame.display.set_caption('Snake')
        self.game_window = pygame.display.set_mode((self.box_length, self.box_height), pygame.NOFRAME)
        
        # FPS (frames per second) controller
        self.fps = pygame.time.Clock()

        # create main font object 
        self.main_font = pygame.font.Font(FONT_PATH, self.box_height//20)

        # create fotn used in the game over screen
        self.game_over_font = pygame.font.Font(FONT_PATH, self.box_height//10)

        # radii to draw the rounded edges 
        self.food_radius = self.cell_size // 3
        self.snake_radius = self.cell_size // 5

        self.direction_corners = {
            'UP': (self.snake_radius, self.snake_radius, 0, 0),
            'RIGHT': (0, self.snake_radius, 0, self.snake_radius),
            'DOWN': (0, 0, self.snake_radius, self.snake_radius),
            'LEFT': (self.snake_radius, 0, self.snake_radius, 0)
        }

        # eyes parameters
        self.eye_radius = self.cell_size // 6
        self.eye_inner_radius = self.cell_size // 10
        self.eye_offset = self.cell_size // 4

        # initial and final color of the snake
        self.start_color = yellow
        self.end_color = green

        # color of the head
        self.head_color = yellow

        # values to position text on screen
        self.vert_shift = self.main_font.get_height() + 5
        self.hor_shift = 10

        # initialize audio mixer
        pygame.mixer.init()

        # load sounds
        if self.sound_effects:
            self.sound_chomp = pygame.mixer.Sound('./sound/chomp.mp3')
            self.sound_proximity = pygame.mixer.Sound('./sound/prox_beep.wav')
            self.sound_gameover = pygame.mixer.Sound('./sound/game_over.wav')

            # adjust volume
            self.sound_proximity.set_volume(0.5)

    def get_eye_positions(self):
        # dictionary to map directions to eye positions
        if self.direction == 'UP': 
            return  (self.body[0][0] + self.eye_offset, self.body[0][1] + self.eye_offset),\
                (self.body[0][0] + self.cell_size - self.eye_offset, self.body[0][1] + self.eye_offset)
        elif self.direction == 'RIGHT': 
            return (self.body[0][0] + self.cell_size - self.eye_offset, self.body[0][1] + self.eye_offset),\
                (self.body[0][0] + self.cell_size - self.eye_offset, self.body[0][1] + self.cell_size - self.eye_offset)
        elif self.direction == 'DOWN': 
            return (self.body[0][0] + self.eye_offset, self.body[0][1] + self.cell_size - self.eye_offset),\
                (self.body[0][0] + self.cell_size - self.eye_offset, self.body[0][1] + self.cell_size - self.eye_offset)
        elif self.direction == 'LEFT': 
            return (self.body[0][0] + self.eye_offset, self.body[0][1] + self.eye_offset),\
                (self.body[0][0] + self.eye_offset, self.body[0][1] + self.cell_size - self.eye_offset)

    def game_over(self, wait_for_user=True):
        # play sound
        if self.sound_effects:
            self.sound_gameover.play()

        # create a semi-transparent overlay with the size of the game window
        overlay = pygame.Surface((self.box_length, self.box_height))

        # set transparency level (0 fully transparent, 255 fully opaque) 
        overlay.set_alpha(50) 

        # fill the surface with red color
        overlay.fill(red)

        # blit the overlay onto the game window
        self.game_window.blit(overlay, (0, 0))
            
        # create a text surface on which text will be drawn
        self.game_over_surface = self.game_over_font.render('GAME OVER!', True, red)
        self.game_over_surface1 = self.game_over_font.render(f'PUNTEGGIO {self.score}', True, red)
        
        # create a rectangular object for the text 
        self.game_over_rect = self.game_over_surface.get_rect()
        self.game_over_rect1 = self.game_over_surface1.get_rect()
        
        # set position of the text
        self.game_over_rect.center = (self.box_length/2, self.box_height/2 - self.game_over_font.get_height()/2)
        self.game_over_rect1.center = (self.box_length/2, self.box_height/2 + self.game_over_font.get_height()/2)
        
        # blit the text on screen
        self.game_window.blit(self.game_over_surface, self.game_over_rect)
        self.game_window.blit(self.game_over_surface1, self.game_over_rect1)

        # refresh game screen
        pygame.display.flip()

        # wait for user input to return
        if wait_for_user:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN 
                            and event.key == pygame.K_ESCAPE):
                        return
            
    # interpolate between two colors
    def interpolate_color(self, factor):
        return tuple([
            int(self.start_color[i] + (self.end_color[i] - self.start_color[i]) * factor)
            for i in range(3)
        ])

    # display score onscreen
    def display_score(self, color):
        # create the display surface object 
        self.score_surface = self.main_font.render(f'{self.score}', True, color)
        # Set transparency 
        self.score_surface.set_alpha(int(0.75 * 255))

        # display text
        self.game_window.blit(self.score_surface, (self.hor_shift, 0))

    # display team name onscreen
    def display_team_name(self, text_color):
        # create the display surface object 
        self.team_name_surface = self.main_font.render(self.team_name, True, text_color)
        self.team_name_surface.set_alpha(int(0.75 * 255))  

        # calculate the position to center the text
        text_rect = self.team_name_surface.get_rect(center=(self.box_length // 2, self.team_name_surface.get_height() // 2))

        # display the black text on top
        self.game_window.blit(self.team_name_surface, text_rect.topleft)

    # display info about state onscreen
    def display_state_info(self, color, head_rect):
        if self.show_compass:
            # add image corresponding to proximity state
            if self.state_mode=='proximity':
                if self.proximity != '':
                    # get the correct proximity image
                    proximity_image = self.proximity_images.get(self.proximity) 
                    # rotate it accordingly
                    proximity_image = pygame.transform.rotate(proximity_image, self.rotation_angles[self.direction])
                    # place it on the head of the snake
                    proximity_rect = proximity_image.get_rect(center=head_rect.center)
                    self.game_window.blit(proximity_image, proximity_rect)
                    # play sound
                    if self.sound_effects:
                        self.sound_proximity.play()

            # same thing for the food compass
            compass_image = self.compass_images.get(self.compass) 
            compass_rect = compass_image.get_rect(center=head_rect.center)
            self.game_window.blit(compass_image, compass_rect)

        # simpler text version
        if self.show_state_info:
            self.compass_surface = self.main_font.render(f'Bussola: {self.compass}', True, color)
            self.compass_rect = self.score_surface.get_rect()
            self.game_window.blit(self.compass_surface, (self.hor_shift, self.box_length-self.vert_shift))
            if self.state_mode=='proximity':
                self.body_info_surface = self.main_font.render(f'Prossimità: {self.proximity}', True, color)
                self.body_info_rect = self.body_info_surface.get_rect()
                self.game_window.blit(self.body_info_surface, (self.hor_shift, self.box_length-self.vert_shift*1.8))

    # render the current frame
    def render_frame(self):

        # wait for user input to return
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN 
                    and event.key == pygame.K_ESCAPE):
                return
        
        # clear the screen (fill with black)
        self.game_window.fill(black)

        # draw head 
        head_rect = pygame.Rect(self.position[0], self.position[1], self.cell_size, self.cell_size)
        tl, tr, bl, br = self.direction_corners[self.direction]
        pygame.draw.rect(self.game_window, self.head_color, head_rect, border_top_left_radius=tl, 
                border_top_right_radius=tr, border_bottom_left_radius=bl, border_bottom_right_radius=br)

        # get the eye positions based on the current direction
        eye1_center, eye2_center = self.get_eye_positions()
        pygame.draw.circle(self.game_window, white, eye1_center, self.eye_radius)
        pygame.draw.circle(self.game_window, white, eye2_center, self.eye_radius)
        pygame.draw.circle(self.game_window, black, eye1_center, self.eye_inner_radius)
        pygame.draw.circle(self.game_window, black, eye2_center, self.eye_inner_radius)

        # draw rest of the body with gradient colors
        for i, pos in enumerate(self.body[1:], start=1):
            factor = i / (self.body_size - 1)  # factor for interpolation
            color = self.interpolate_color(factor)
            body_rect = pygame.Rect(pos[0], pos[1], self.cell_size, self.cell_size)
            pygame.draw.rect(self.game_window, color, body_rect)

        # draw food
        food_rect = pygame.Rect(self.food_position[0], self.food_position[1], self.cell_size, self.cell_size), 
        pygame.draw.rect(self.game_window, red, food_rect, border_radius=self.food_radius)
        
        # display score and state info
        self.display_score(white)
        self.display_state_info(green, head_rect)

        # display team name
        if self.team_name != None:
            self.display_team_name(white)

        # draw window border (if PBC is not activated)
        # if not self.periodic:
        pygame.draw.rect(self.game_window, white, self.game_window.get_rect(), 1)

        # FPS/refresh Rate (increase speed with score)
        self.fps.tick(self.snake_speed + self.score/10)

        # refresh game screen
        pygame.display.flip()

        # fix for macOS screen refresh on multiprocessing
        if ON_MAC: pygame.event.pump()
