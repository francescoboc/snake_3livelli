import random
from tools import *

class Snake:
    def __init__(self, 
            action_mode=3, 
            state_mode='simple', 
            cell_size=20, 
            box_size=30, 
            snake_speed=15, 
            periodic=True, 
            rand_init_body_length=False,
            rand_init_direction=False,
            show_state=True,
            show_actions=False,
            sound_effects=False,
            team_name=None,
            window_position=None,
            verbose=True,
            countdown_seconds=3,
            color_scheme='green',
            seed=None,
            food_rew=1.0, 
            lose_rew=-10.0, 
            step_rew=0.0,
            trun_rew=-5.0,
            max_idle_time=30
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

        # flags for sounds and state/action info
        self.show_state = show_state
        self.show_actions = show_actions
        self.sound_effects = sound_effects

        # other variables (mainly for multiplayer mode)
        self.team_name = team_name
        self.window_position = window_position
        self.countdown_seconds = countdown_seconds
        self.color_scheme = color_scheme
        self.max_idle_time = max_idle_time

        # create a random number generator object
        self.rng = random.Random()
        seed = self.seed_rng(seed)
        if verbose: print(f'RNG seed = {seed}')

        # seed the RNG
        if seed is None: self.seed = random.randrange(sys.maxsize)
        else: self.seed = seed
        self.rng.seed(self.seed)

        # show info in terminal
        if verbose:
            print(f'Action mode = {action_mode}')
            print(f'State mode = {state_mode}')
            print(f'Box size = {box_size}x{box_size}')
            print(f'Periodic = {periodic}')
            print(f'Random initial body length = {rand_init_body_length}')
            print(f'Random initial direction = {rand_init_direction}')

    # seed the RNG
    def seed_rng(self, seed=None):
        if seed is None: 
            seed = random.randrange(sys.maxsize)
        self.rng.seed(seed)
        return seed

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
            size = self.rng.randrange(init_size,int(self.box_size/2))
        else:
            size = init_size
        if self.rand_init_direction:
            direction = self.rng.choice(head_dirs)
        else:
            direction = init_direction

        # snake's head initial position
        self.position, self.body = self.initialize_body(direction, size)

        # reset snake direction towards RIGHT
        self.direction = direction
        self.action = 'NO_TURN'

        # sparn food in a random position
        self.spawn_food()

        # reset initial score
        self.score = 0

        # reset counters to check for truncation
        self.old_score = 0
        self.old_direction = None
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
                
    ################################## STATE DEFS ################################## 

    def get_state_simple(self):
        self.compass = self.check_compass(self.food_position)
        return (self.direction, self.compass)

    def get_state_proximity(self):
        self.compass = self.check_compass(self.food_position)
        self.proximity = self.check_proximity()
        return (self.direction, self.compass, self.proximity)

    ################################## LOCOMOTION ##################################

    # spawn food at random locations avoiding overlap with snake body
    def spawn_food(self):
        self.food_position = [self.rng.randrange(1, (self.box_length//self.cell_size)) * self.cell_size, 
                              self.rng.randrange(1, (self.box_height//self.cell_size)) * self.cell_size]
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
            # set the food_eaten flag to true
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
    def step(self, action, check_inactivity=False):
        # set direction based on action
        self.direction = self.get_direction_from_actions(action)

        # advance snake (this method also sets the food_eaten flag)
        self.advance()

        # check if terminal state or truncation was reached
        terminated = self.is_terminal()
        truncated = self.is_truncated(check_inactivity)

        # assign rewards
        if terminated:
            reward = self.lose_rew
        elif truncated:
            reward = self.trun_rew
        elif self.food_eaten:
            reward = self.food_rew
        else:
            reward = self.step_rew
        
        # if food was eaten, reset flag and spawn a new one
        if self.food_eaten:
            self.spawn_food()
            # play sound
            if self.sound_effects:
                self.sound_chomp.play()

        # get reading of new state
        if not terminated:
            next_state = self.get_state()
        else:
            next_state = 'Term'

        return next_state, reward, terminated, truncated

    # check if the snake is stuck in a loop
    def is_truncated(self, check_inactivity=False):
        truncated = False

        # check truncation based on user interaction
        if check_inactivity:
            # initialise timer for the first time
            if not hasattr(self, 'last_direction_change'):
                self.last_direction_change = time.time()

            # if direction changed, rest timer
            if self.direction != self.old_direction:
                self.last_direction_change = time.time()

            # measure time since last direction change
            idle_time = time.time() - self.last_direction_change

            # if direction didn't change for too long, truncate
            if idle_time > self.max_idle_time:
                truncated = True

            # keep direction updated
            self.old_direction = self.direction

        # or based on score changes
        else:
            # if score didn't change, increase counter
            if self.score == self.old_score: self.stuck_counter += 1
            else: self.stuck_counter = 0

            # if the counter is stuck for too long, truncate
            if self.stuck_counter == self.box_size_sq:
                truncated = True

            self.old_score = self.score

        return truncated

    # play with a given policy or interactively
    def play(self, policy=None, render=True, save_video=False):
        if render:
            self.init_render()
            if save_video: self.frames = []  # store frames for the video
            if self.countdown_seconds > 0: self.countdown()

        # reset the game
        state = self.reset()

        # game loop
        escape_pressed = False
        while not escape_pressed:
            # policy=None is interactive mode: check for user keypresses 
            if policy is None:
                if render: action, escape_pressed = read_keys()
                else: raise Warning('Set render=True to play interactively!')
            # policy!=None is non-interactive: use actions provided by policy
            else:
                action = policy[state]
                # if rendering the game, check if ESC key is pressed to stop
                if render: escape_pressed = read_esc()

            # also set a global variable to be used in render function
            self.action = action

            # update snake position
            next_state, reward, terminated, truncated = self.step(action)

            if terminated or truncated:
                if render:
                    self.game_over()
                    if save_video: 
                        self.capture_frame()
                        self.capture_frame()
                pygame.quit()
                return self.score, truncated

            if render:
                self.render_frame()
                if save_video: self.capture_frame()

            # shift state
            state = next_state

        return self.score, truncated

    ############################## RENDERING METHODS ##############################

    # capture the current frame from the Pygame window
    def capture_frame(self):
        # get the current frame as an array
        frame = pygame.surfarray.array3d(pygame.display.get_surface())
        # convert from (width, height, colors) to (height, width, colors)
        frame = frame.transpose([1, 0, 2])
        self.frames.append(frame)

    # save the collected frames as a video using imageio
    def save_video(self, video_path, fps=12):
        import imageio
        with imageio.get_writer(video_path, fps=fps) as video:
            for frame in self.frames:
                video.append_data(frame)
        print(f"Video saved as {video_path}")

    # display a countdown before starting the game
    def countdown(self, delay=None):
        # wait a small delay (in seconds), if provided
        if delay is not None: time.sleep(delay)

        for i in range(self.countdown_seconds, 0, -1):
            # clear screen
            self.game_window.fill((black))
            self.display_team_name()

            # render countdown text
            countdown_text = self.countdown_font.render(str(i), True, white)
            text_rect = countdown_text.get_rect(center=(self.box_length//2, self.box_height//2))
            self.game_window.blit(countdown_text, text_rect)

            # add border
            pygame.draw.rect(self.game_window, white, self.game_window.get_rect(), 1)

            # update the display
            pygame.display.flip()

            # this fixes rendering issues on macOS
            pygame.event.pump()

            # wait for 1 second
            time.sleep(1)

    # initialize rendering environment (pygame)
    def init_render(self):
        # set position of game window
        if self.window_position is not None:
            set_window_position(*self.window_position)  

        # initialise pygame 
        pygame.init()

        # # initialise joystick object
        # pygame.joystick.init()
        # joystick = pygame.joystick.Joystick(0)
        # joystick.init()

        # initialise game window 
        if self.team_name != None: pygame.display.set_caption(self.team_name)
        else: pygame.display.set_caption('Snake')
        self.game_window = pygame.display.set_mode((self.box_length, self.box_height), pygame.NOFRAME)
        
        # FPS (frames per second) controller
        self.fps = pygame.time.Clock()

        # fonts objects
        self.main_font = pygame.font.Font(FONT_PATH, self.box_height//20)
        self.game_over_font = pygame.font.Font(FONT_PATH, self.box_height//10)
        self.countdown_font = pygame.font.Font(FONT_PATH, self.box_height//3)

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
        if self.color_scheme == 'green':
            self.start_color = lightGreen
            self.end_color = green
        elif self.color_scheme == 'blue':
            self.start_color = lightBlue
            self.end_color = blue
        elif self.color_scheme == 'red':
            self.start_color = lightRed
            self.end_color = red
        elif self.color_scheme == 'orange':
            self.start_color = lightOrange
            self.end_color = orange
        elif self.color_scheme == 'purple':
            self.start_color = lightPurple
            self.end_color = purple
        elif self.color_scheme == 'pink':
            self.start_color = lightPink
            self.end_color = pink
        elif self.color_scheme == 'grey':
            self.start_color = lightGrey
            self.end_color = grey
        elif self.color_scheme == 'brown':
            self.start_color = lightBrown
            self.end_color = brown
        else:
            raise Warning('Invalid color scheme')

        # color of the head
        self.head_color = self.start_color

        # # TODO questo da testare su raspberry se l'audio non funziona
        # if pygame.mixer.get_init():
        #     pygame.mixer.quit()

        # initialize audio mixer
        # pygame.mixer.init()

        # load sounds
        if self.sound_effects:
            self.sound_chomp = pygame.mixer.Sound('sound/chomp.mp3')
            self.sound_proximity = pygame.mixer.Sound('sound/prox_beep.wav')
            self.sound_gameover = pygame.mixer.Sound('sound/game_over.wav')

            # adjust volumes
            self.sound_proximity.set_volume(0.5)

        # load the food image 
        self.food_image = pygame.image.load('img/apple.png')

        # resize the image to match the cell size
        self.food_image = pygame.transform.scale(self.food_image, (self.cell_size, self.cell_size))

        # load compass images
        if self.show_state:
            self.compass_images = {
                'N': pygame.image.load('img/north.png'),
                'NE': pygame.image.load('img/north_east.png'),
                'E': pygame.image.load('img/east.png'),
                'SE': pygame.image.load('img/south_east.png'),
                'S': pygame.image.load('img/south.png'),
                'SW': pygame.image.load('img/south_west.png'),
                'W': pygame.image.load('img/west.png'),
                'NW': pygame.image.load('img/north_west.png')
            }

            # resize images
            for key in self.compass_images:
                self.compass_images[key] = pygame.transform.smoothscale(self.compass_images[key], (self.cell_size*4 , self.cell_size*4))

            # load proximity images
            if self.state_mode == 'proximity':
                self.proximity_images = {
                    'f': pygame.image.load('img/prox_f.png'),
                    'l': pygame.image.load('img/prox_l.png'),
                    'r': pygame.image.load('img/prox_r.png'),
                    'fl': pygame.image.load('img/prox_fl.png'),
                    'fr': pygame.image.load('img/prox_fr.png'),
                    'lr': pygame.image.load('img/prox_lr.png'),
                    'flr': pygame.image.load('img/prox_flr.png'),
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

        # load action images
        self.left_turn_img = pygame.image.load('img/relative_turns/left.png').convert_alpha()
        self.no_turn_img = pygame.image.load('img/relative_turns/no_turn_x.png').convert_alpha()
        self.right_turn_img = pygame.image.load('img/relative_turns/right.png').convert_alpha()

        self.left_circle_img = pygame.image.load('img/relative_turns/left_circle.png').convert_alpha()
        self.no_turn_circle_img = pygame.image.load('img/relative_turns/no_turn_circle.png').convert_alpha()
        self.right_circle_img = pygame.image.load('img/relative_turns/right_circle.png').convert_alpha()

        # resize them 
        resize_factor = self.cell_size*1.25
        self.left_turn_img = pygame.transform.smoothscale(self.left_turn_img, (resize_factor, resize_factor))
        self.no_turn_img = pygame.transform.smoothscale(self.no_turn_img, (resize_factor*0.9, resize_factor*0.9))
        self.right_turn_img = pygame.transform.smoothscale(self.right_turn_img, (resize_factor, resize_factor))

        resize_factor *= 1.2
        self.left_circle_img = pygame.transform.smoothscale(self.left_circle_img, (resize_factor, resize_factor))
        self.no_turn_circle_img = pygame.transform.smoothscale(self.no_turn_circle_img, (resize_factor, resize_factor))
        self.right_circle_img = pygame.transform.smoothscale(self.right_circle_img, (resize_factor, resize_factor))

        # transparency values for action images
        self.non_active_alpha = 50
        self.active_alpha = 110 

        # define separation between images
        self.separator = self.cell_size*0.7

        # calculate the total width of the three images plus separators
        total_width = (self.left_turn_img.get_width() + self.no_turn_img.get_width() + 
                self.right_turn_img.get_width() + 2 * self.separator)

        # set x-positions for each image
        self.left_x = (self.box_length - total_width) // 2
        self.center_x = self.left_x + self.left_turn_img.get_width() + self.separator
        self.right_x = self.center_x + self.no_turn_img.get_width() + self.separator

        # calculate the y-position for all images
        self.y_position = self.box_length - self.cell_size//2 - self.left_turn_img.get_height()

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

        # fill the surface with brightRed color
        overlay.fill(brightRed)

        # blit the overlay onto the game window
        self.game_window.blit(overlay, (0, 0))
            
        # create a text surface on which text will be drawn
        self.game_over_surface = self.game_over_font.render('GAME OVER!', True, brightRed)
        if self.score == 1: self.game_over_surface1 = self.game_over_font.render(f'{self.score} PUNTO', True, brightRed)
        else: self.game_over_surface1 = self.game_over_font.render(f'{self.score} PUNTI', True, brightRed)
        
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

        start_time = time.time()

        # wait for user input to return
        if wait_for_user:
            while True:
                # close automatically after a fixed number of seconds
                if time.time() - start_time > 10:
                    return
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
        # self.score_surface.set_alpha(int(0.75 * 255))

        # text_rect = self.score_surface.get_rect(center=(self.cell_size, self.score_surface.get_height() // 2))
        text_rect = self.score_surface.get_rect()
        center_y = self.score_surface.get_height() // 2
        text_rect.topleft = (self.cell_size // 3, center_y - text_rect.height // 2)

        # display text
        self.game_window.blit(self.score_surface, text_rect.topleft)

    # display team name onscreen
    def display_team_name(self):
        # create the surface object 
        self.team_name_surface = self.main_font.render(self.team_name, True, self.end_color)
        # self.team_name_surface.set_alpha(int(0.75 * 255))  

        # calculate the position to center the text
        text_rect = self.team_name_surface.get_rect(center=(self.box_length // 2, self.team_name_surface.get_height() // 2))

        # display text
        self.game_window.blit(self.team_name_surface, text_rect.topleft)

    # display a blinking fast-forward icon (two small triangles)
    def display_ff_icon(self, color=white, blink_interval=0.2):
        if not hasattr(self, '_ff_last_time'):
            # initialize internal timer and state
            self._ff_last_time = time.time()
            self._ff_visible = True

        # toggle visibility if interval passed
        now = time.time()
        if now - self._ff_last_time > blink_interval:
            self._ff_last_time = now
            self._ff_visible = not self._ff_visible

        if self._ff_visible:
            # size and position
            tri_width = self.cell_size // 2
            tri_height = self.cell_size // 1.5
            margin = self.cell_size // 3
            x0 = margin
            y0 = self.game_window.get_height() - tri_height - margin

            # first triangle points (pointing right)
            tri1 = [(x0, y0), (x0, y0 + tri_height), (x0 + tri_width, y0 + tri_height//2)]
            # second triangle points, slightly shifted right
            shift = tri_width + self.cell_size // 10
            tri2 = [(x0 + shift, y0), (x0 + shift, y0 + tri_height), (x0 + shift + tri_width, y0 + tri_height//2)]

            pygame.draw.polygon(self.game_window, color, tri1)
            pygame.draw.polygon(self.game_window, color, tri2)

    # display info about state onscreen
    def display_state_info(self, color, head_rect):
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

    # helper function to set image transparency and blit the circle image for the active action
    def draw_image_with_circle(self, img_surface, x_pos, circle_img, is_active):
        # only draw the circle for the active action
        if is_active:
            # blit the circle image centered behind the action icon
            circle_x = x_pos + (img_surface.get_width() - circle_img.get_width()) // 2
            circle_y = self.y_position + (img_surface.get_height() - circle_img.get_height()) // 2

            # set active alpha
            circle_img.set_alpha(self.active_alpha)
            img_surface.set_alpha(self.active_alpha)

            # blit the image
            self.game_window.blit(circle_img, (circle_x, circle_y))
        else:
            # set non-active alpha for idle action images
            img_surface.set_alpha(self.non_active_alpha)

        # blit the image
        self.game_window.blit(img_surface, (x_pos, self.y_position))

    # function to display the action image
    def display_action(self):
        # draw each action
        self.draw_image_with_circle(self.left_turn_img, self.left_x, self.left_circle_img, self.action == 'LEFT')
        self.draw_image_with_circle(self.no_turn_img, self.center_x, self.no_turn_circle_img, self.action == 'NO_TURN')
        self.draw_image_with_circle(self.right_turn_img, self.right_x, self.right_circle_img, self.action == 'RIGHT')

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

        # draw rest of the body with gradient colors
        for i, pos in enumerate(self.body[1:], start=1):
            factor = i / (self.body_size - 1)  # factor for interpolation
            color = self.interpolate_color(factor)
            body_rect = pygame.Rect(pos[0], pos[1], self.cell_size, self.cell_size)
            pygame.draw.rect(self.game_window, color, body_rect)

        # # draw food
        # # simple version with a square
        # food_rect = pygame.Rect(self.food_position[0], self.food_position[1], self.cell_size, self.cell_size), 
        # pygame.draw.rect(self.game_window, brightRed, food_rect, border_radius=self.food_radius)

        # nicer version with an external image
        food_position = (self.food_position[0], self.food_position[1])
        self.game_window.blit(self.food_image, food_position)
        
        # display stuff on screen
        self.display_score(white)

        if self.show_state:
            self.display_state_info(green, head_rect)

        if self.show_actions:
            self.display_action()

        # display team name
        if self.team_name != None:
            self.display_team_name()

        # display fast forward icon
        if hasattr(self, '_show_fast_forward'):
            self.display_ff_icon()

        # draw window border
        if self.periodic: border_color, border_px = white, 1
        else: border_color, border_px = red, 3
        pygame.draw.rect(self.game_window, border_color, self.game_window.get_rect(), border_px)

        # FPS/refresh Rate (increase speed with score)
        self.fps.tick(self.snake_speed + self.score*0.1)

        # refresh game screen
        pygame.display.flip()

        # this fixes rendering issues on macOS
        pygame.event.pump()
