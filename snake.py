# ****************** Boccardo Gagliardi @PiMlB MALGA  ***************
# SNAKE ENVIRONMENT: evolution, reward, state, rendering
# 
# ********************************************************************

from tools import *

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
            food_rew=1.0, 
            lose_rew=-10.0, 
            step_rew=0.0,
            trun_rew=-5.0,
            verbose=True,
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
        elif state_mode=='body_length':
            fractions = 3
            self._box_fraction = self.box_size/fractions
            self.get_state = self.get_state_body_length
            bodyFractions = [b for b in range(fractions**2)]
            for d in head_dirs:
                for c in compass_dirs:
                    for b in bodyFractions:
                        self.states.append((d,c,b))
        elif state_mode=='tail_compass':
            self.get_state = self.get_state_tail_compass
            for d in head_dirs:
                for c in compass_dirs:
                    for t in compass_dirs:
                        self.states.append((d,c,t))
        elif state_mode=='com_compass':
            self.get_state = self.get_state_com_compass
            for d in head_dirs:
                for c in compass_dirs:
                    for t in compass_dirs_empty:
                        self.states.append((d,c,t))
        elif state_mode=='proximity':
            self.get_state = self.get_state_proximity
            for d in head_dirs:
                for c in compass_dirs:
                    for p in prox_values:
                        self.states.append((d,c,p))
        elif state_mode=='spirality':
            self.get_state = self.get_state_spirality
            for d in head_dirs:
                for c in compass_dirs:
                    for p in prox_values:
                        for s in spir_values:
                            self.states.append((d,c,p,s))
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

        # initialize turns history and spirality
        if self.state_mode=='spirality':
            self.turns_history = [0 for i in range(size-2)]
            self.spirality = 0

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

    def check_spirality(self, action):
        # check value of turn assigned to choosen action
        try: turn = actions_turn_map[action]
        except KeyError: turn = 0

        # append new turn to the top of turns_history
        self.turns_history.insert(0, turn)

        # pop last element if snake body did not grow
        if not self.food_eaten:
            self.turns_history.pop()

        # spirality is just the sum of all the turns
        return np.sum(self.turns_history)

    # check if pos is out of box bounds
    def out_of_bounds(self, pos):
        return pos[0] < 0 or pos[0] > self.box_length-self.cell_size or pos[1] < 0 or pos[1] > self.box_height-self.cell_size
                
    # calculate body length as fraction of the box length
    def get_body_length_fraction(self):
        self.body_length_fraction = int(self.body_size/self._box_fraction) 

    ################################## STATE DEFS ##############################

    def get_state_simple(self):
        self.compass = self.check_compass(self.food_position)
        return (self.direction, self.compass)

    def get_state_body_length(self):
        self.compass = self.check_compass(self.food_position)
        self.get_body_length_fraction()
        return (self.direction, self.compass, self.body_length_fraction)

    def get_state_tail_compass(self):
        self.compass = self.check_compass(self.food_position)
        self.tail_compass = self.check_compass(self.body[-1])
        return (self.direction, self.compass, self.tail_compass)

    def get_state_com_compass(self):
        self.compass = self.check_compass(self.food_position)
        self.com_compass = self.check_compass(self.calculate_com_with_pbc())
        return (self.direction, self.compass, self.com_compass)

    def get_state_proximity(self):
        self.compass = self.check_compass(self.food_position)
        self.proximity = self.check_proximity()
        return (self.direction, self.compass, self.proximity)

    def get_state_spirality(self):
        self.compass = self.check_compass(self.food_position)
        self.proximity = self.check_proximity()
        # NB spirality is calculated outside this function because it needs the action
        return (self.direction, self.compass, self.proximity, self.spirality)

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

        if self.state_mode=='spirality':
            self.spirality = self.check_spirality(action)

        # if food was eaten, spawn a new one
        if self.food_eaten:
            self.spawn_food()

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
            self.init_render()

        # reset the game
        state = self.reset()
        print(state)

        # game loop
        while True:
            if policy is None:
                # check if a key has been pressed
                action = read_keys()
            else:
                action = policy[state]

            # update snake position
            next_state, reward, terminated, truncated = self.step(action)

            if terminated or truncated:
                if render:
                    self.game_over()
                    pygame.quit()
                    sys.exit()
                else:
                    return self.score, truncated

            if render:
                self.render_frame()

            # shift state
            state = next_state
            print(state)

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
        self.main_font = pygame.font.SysFont('arial', 20)

        # create fotn used in the game over screen
        self.game_over_font = pygame.font.SysFont('arial', 50)

        # radii to draw the rounded edges 
        self.food_radius = self.cell_size // 3
        snake_radius = self.cell_size // 5

        self.direction_corners = {
            'UP': (snake_radius, snake_radius, 0, 0),
            'RIGHT': (0, snake_radius, 0, snake_radius),
            'DOWN': (0, 0, snake_radius, snake_radius),
            'LEFT': (snake_radius, 0, snake_radius, 0)
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

    # display score onscreen
    def show_score(self, color):
        # create the display surface object 
        self.score_surface = self.main_font.render('Score: ' + str(self.score), True, color)

        # display text
        self.game_window.blit(self.score_surface, (4,0))

    # display info about state onscreen
    def show_state_info(self, color):
        self.compass_surface = self.main_font.render('Compass: ' + str(self.compass), True, color)
        self.compass_rect = self.score_surface.get_rect()
        self.game_window.blit(self.compass_surface, (self.box_length-128,0))

        if self.state_mode=='body_length':
            self.body_info_surface = self.main_font.render('body: frac, len = ' + str(self.body_length_fraction)+", "+str(self.body_size), True, 'green')
            self.body_info_rect = self.body_info_surface.get_rect()
            self.game_window.blit(self.body_info_surface, (4, self.box_length-25))

        elif self.state_mode=='tail_compass':
            self.body_info_surface = self.main_font.render('Tail comp: ' + str(self.tail_compass), True, 'green')
            self.body_info_rect = self.body_info_surface.get_rect()
            self.game_window.blit(self.body_info_surface, (4, self.box_length-25))

        elif self.state_mode=='com_compass':
            self.body_info_surface = self.main_font.render('COM comp: ' + str(self.com_compass), True, 'green')
            self.body_info_rect = self.body_info_surface.get_rect()
            self.game_window.blit(self.body_info_surface, (4, self.box_length-25))
        elif self.state_mode=='proximity':
            self.body_info_surface = self.main_font.render('Prox: ' + str(self.proximity), True, 'green')
            self.body_info_rect = self.body_info_surface.get_rect()
            self.game_window.blit(self.body_info_surface, (4, self.box_length-25))

    def game_over(self):
        # create a semi-transparent overlay with the size of the game window
        overlay = pygame.Surface((self.box_length, self.box_height))

        # set transparency level (0 fully transparent, 255 fully opaque) 
        overlay.set_alpha(60) 

        # fill the surface with red color
        overlay.fill(red)

        # blit the overlay onto the game window
        self.game_window.blit(overlay, (0, 0))
            
        # create a text surface on which text will be drawn
        self.game_over_surface = self.game_over_font.render('Your score is: ' + str(self.score), True, red)
        
        # create a rectangular object for the text 
        self.game_over_rect = self.game_over_surface.get_rect()
        
        # set position of the text
        self.game_over_rect.midtop = (self.box_length/2, self.box_height/4)
        
        # blit the text on screen
        self.game_window.blit(self.game_over_surface, self.game_over_rect)
        pygame.display.flip()
        
        # wait for user input to return
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

    # calculate shifts needed to unwrap coordinates
    def unwrap_coords(self, coords):
        # ensure float for calculation
        coords = coords.astype(float)  
        unwrapped_coords = np.copy(coords)

        diffs = np.diff(coords)
        shift = np.zeros(coords.shape[0])
        
        # shift elements by adding box_length when there is a negative difference greater than half the box size
        shift[np.where(diffs < -self.box_length / 2)[0] + 1] = self.box_length

        # shift elements by subtracting box_length when there is a positive difference greater than half the box size
        shift[np.where(diffs > self.box_length / 2)[0] + 1] = -self.box_length
        
        unwrapped_coords += np.cumsum(shift)
        return unwrapped_coords

    # TODO without PBC is easy, it's just the mean(axis=0) of the body!
    def calculate_com_with_pbc(self):
        # convert body to numpy array for easier manipulation
        body = np.array(self.body)
        
        # unwrap x and y coordinates
        x_coords = self.unwrap_coords(body[:, 0])
        y_coords = self.unwrap_coords(body[:, 1])
        
        # calculate mean positions of unwrapped coordinates
        mean_x = np.mean(x_coords) % self.box_length
        mean_y = np.mean(y_coords) % self.box_height

        return np.array([mean_x, mean_y])

    # render the current frame
    def render_frame(self):
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

        # # draw rest of the body
        # for pos in self.body[1:]:
        #     body_rect = pygame.Rect(pos[0], pos[1], self.cell_size, self.cell_size)
        #     pygame.draw.rect(self.game_window, green, body_rect)

        # draw rest of the body with gradient colors
        for i, pos in enumerate(self.body[1:], start=1):
            factor = i / (self.body_size - 1)  # factor for interpolation
            color = self.interpolate_color(factor)
            body_rect = pygame.Rect(pos[0], pos[1], self.cell_size, self.cell_size)
            pygame.draw.rect(self.game_window, color, body_rect)

        # draw center of mass (accounts for PBC)
        if self.state_mode=='com_compass':
            com = self.calculate_com_with_pbc()
            pygame.draw.circle(self.game_window, blue, (int(com[0]), int(com[1])), self.eye_radius)

        # draw food
        food_rect = pygame.Rect(self.food_position[0], self.food_position[1], self.cell_size, self.cell_size), 
        pygame.draw.rect(self.game_window, red, food_rect, border_radius=self.food_radius)
        
        # display score and state info
        self.show_score(white)
        self.show_state_info(white)

        # draw window border if PBC is not activated
        if not self.periodic:
            pygame.draw.rect(self.game_window, red, self.game_window.get_rect(), 2)

        # FPS/refresh Rate
        self.fps.tick(self.snake_speed)

        # refresh game screen
        pygame.display.update()
