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
    policy = None

    # run game
    n_teams, team_name = 1, 'super pazzi'
    cell_size, window_position = calculate_size_and_positions(n_teams, box_size)
    run_snake_game(policy, team_name, window_position, cell_size, shared_vars, seed=None)

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
    policy = None

    # run game
    n_teams, team_name = 1, None
    cell_size, window_position = calculate_size_and_positions(n_teams, box_size)
    run_snake_game(policy, team_name, window_position, cell_size, shared_vars, seed=None)

# challenge all the policies (in .txt format) inside a folder
def challenge(path_to_folder):
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

    # get team ranking
    ranking = sorted(zip(scores_dict.values(), scores_dict.keys()), reverse=True)
    winner_score, winner_name = ranking[0][0], ranking[0][1]

# challenge all the policies (in .txt format) inside a folder
def statistical_challenge(path_to_folder):
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
    sound_effects = False
    show_state_info = False

    # put all shared variables into a list for convenience
    shared_vars = [box_size, snake_speed, periodic, action_mode, rand_init_body_length,\
        rand_init_direction, state_mode, show_compass, sound_effects, show_state_info]

    # number of test games
    n_games = 1000

    policies, team_names = [], []
    for filename in sorted(os.listdir(path_to_folder)):
        policies.append(load_user_policy(filename, path_to_folder))
        team_names.append(filename.replace('.txt',''))

    # run the games in parallel
    scores_dict = test_policies_in_parallel(policies, team_names, shared_vars, n_games)

    # get team ranking
    ranking = sorted(zip(scores_dict.values(), scores_dict.keys()), reverse=True)
    # winner_score, winner_name = ranking[0][0], ranking[0][1]

    # TODO display histogram
    save_path = f'{path_to_folder}/ranking.txt'
    with open(save_path, 'w') as file:
        for score, team_name in ranking:
            file.write(f"{score:.3f}\t{team_name}\n")

    # TODO evita il file ranking.txt dalle policy!
    # oppure, meglio: passa come path solo il main math, e poi aggiungi la cartella "strategie", in questo modo ho accesso alla cartella precedente

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
        elif game_mode == 'statistical_challenge':
            if len(sys.argv) == 3: 
                path_to_folder = sys.argv[2]
                statistical_challenge(path_to_folder)
            else: 
                print('Please specify path to policies folder')
        else:
            print('Game mode not recognized!')

        # TODO add a countdown in snake!

        # sfida tra squadre <- path cartella CAMBIA COLORE!
        # nome suadra + id_colore <- valuta policies <- path cartella (ion)
        # sfida ai <- path a policy vincente + id_colore
        # sfida umano vs ai (sempre grigia)
