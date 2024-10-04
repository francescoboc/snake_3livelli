from multiplayer_tools import *

# demo for 1 player to play the game with no state info
def oneplayer_nostate():
    # snake parameters
    box_size = 30
    snake_speed = 10

    # game parameters
    periodic = True
    action_mode = 3
    rand_init_body_length = False
    rand_init_direction = False

    # state mode
    state_mode = 'simple'
    # state_mode = 'proximity'

    # visual and sound effects
    show_compass = False
    sound_effects = True
    show_state_info = False

    # put all shared variables into a list for convenience
    shared_vars = [box_size, snake_speed, periodic, action_mode, rand_init_body_length,\
        rand_init_direction, state_mode, show_compass, sound_effects, show_state_info]

    # if policy is None the game is launched in interactive mode
    policies, team_names = [None], [None] 

    # run the games in parallel
    run_games_in_parallel(policies, team_names, shared_vars)

# demo for 1 player to play the game with state info
def oneplayer_showstate():
    # snake parameters
    box_size = 30
    snake_speed = 10

    # game parameters
    periodic = True
    action_mode = 3
    rand_init_body_length = False
    rand_init_direction = False

    # state mode
    state_mode = 'simple'
    # state_mode = 'proximity'

    # visual and sound effects
    show_compass = True
    sound_effects = True
    show_state_info = False

    # put all shared variables into a list for convenience
    shared_vars = [box_size, snake_speed, periodic, action_mode, rand_init_body_length,\
        rand_init_direction, state_mode, show_compass, sound_effects, show_state_info]

    # if policy is None the game is launched in interactive mode
    policies, team_names = [None], [None] 

    # run the games in parallel
    run_games_in_parallel(policies, team_names, shared_vars)

# challenge all the policies (in .txt format) inside a folder
def challenge(path_to_folder):
    # snake parameters
    box_size = 30
    snake_speed = 100

    # game parameters
    periodic = True
    action_mode = 3
    rand_init_body_length = False
    rand_init_direction = False

    # state mode
    state_mode = 'simple'
    # state_mode = 'proximity'

    # visual and sound effects
    show_compass = True
    sound_effects = False
    show_state_info = False

    # put all shared variables into a list for convenience
    shared_vars = [box_size, snake_speed, periodic, action_mode, rand_init_body_length,\
        rand_init_direction, state_mode, show_compass, sound_effects, show_state_info]

    policies, team_names = [], []
    for filename in sorted(os.listdir(path_to_folder)):
        policies.append(load_user_policy(filename, path_to_folder))
        team_names.append(filename.replace('.txt',''))

    # run the games in parallel
    scores_dict = run_games_in_parallel(policies, team_names, shared_vars)

    # find winners
    ranking = sorted(zip(scores_dict.values(), scores_dict.keys()), reverse=True)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print('Please specify one game mode')
    else:
        game_mode = sys.argv[1]

        # behavior for different game modes
        if game_mode == 'oneplayer_nostate':
            oneplayer_nostate()
        elif game_mode == 'oneplayer_showstate':
            oneplayer_showstate()
        # 'challenge' mode requires another argument: path to policies folder
        elif game_mode == 'challenge':
            if len(sys.argv) == 3: 
                path_to_folder = sys.argv[2]
                challenge(path_to_folder)
            else: 
                print('Please specify path to policies folder')
        else:
            print('Game mode not recognized!')

        # TODO add a countdown in snake!

        # sfida tra squadre <- path cartella CAMBIA COLORE!
        # nome suadra + id_colore <- valuta policies <- path cartella (ion)
        # sfida ai <- path a policy vincente + id_colore
        # sfida umano vs ai (sempre grigia)
