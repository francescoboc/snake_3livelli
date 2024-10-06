from multiplayer_tools import *

# demo for 1 player to play the game with no state info
def oneplayer_nostate():
    from defaults import box_size, snake_speed, periodic, action_mode, rand_init_body_length, \
        rand_init_direction, state_mode, show_compass, sound_effects, show_state_info, countdown_seconds

    # put all shared variables into a list for convenience
    shared_vars = [box_size, snake_speed, periodic, action_mode, rand_init_body_length,\
        rand_init_direction, state_mode, show_compass, sound_effects, show_state_info, countdown_seconds]

    # if policy is None the game is launched in interactive mode
    policy = None

    # run game
    n_teams, team_name = 1, None
    cell_size, window_position = calculate_size_and_positions(n_teams, box_size)
    run_snake_game(policy, team_name, window_position, cell_size, shared_vars)

# demo for 1 player to play the game with state info
def oneplayer_showstate():
    # import default variables
    from defaults import box_size, snake_speed, periodic, action_mode, rand_init_body_length, \
        rand_init_direction, state_mode, show_compass, sound_effects, show_state_info, countdown_seconds

    # don't show state
    show_compass = True

    # put all shared variables into a list for convenience
    shared_vars = [box_size, snake_speed, periodic, action_mode, rand_init_body_length,\
        rand_init_direction, state_mode, show_compass, sound_effects, show_state_info, countdown_seconds]

    # if policy is None the game is launched in interactive mode
    policy = None

    # run game
    n_teams, team_name = 1, None
    cell_size, window_position = calculate_size_and_positions(n_teams, box_size)
    run_snake_game(policy, team_name, window_position, cell_size, shared_vars)

# challenge all the policies (in .txt format) inside a folder
def challenge(turn_folder):
    # import default variables
    from defaults import box_size, snake_speed, periodic, action_mode, rand_init_body_length, \
        rand_init_direction, state_mode, show_compass, sound_effects, show_state_info, countdown_seconds

    # visual and sound effects
    show_compass = True
    sound_effects = False

    # put all shared variables into a list for convenience
    shared_vars = [box_size, snake_speed, periodic, action_mode, rand_init_body_length,\
        rand_init_direction, state_mode, show_compass, sound_effects, show_state_info, countdown_seconds]

    policies, team_names = [], []
    # all the policies are inside a subfolder 'strategie'
    policies_folder = f'{turn_folder}/strategie'
    for filename in sorted(os.listdir(policies_folder)):
        policies.append(load_user_policy(filename, policies_folder))
        team_names.append(filename.replace('.txt',''))

    # run the games in parallel
    scores_dict = run_games_in_parallel(policies, team_names, shared_vars)

    # get team ranking
    ranking = sorted(zip(scores_dict.values(), scores_dict.keys()), reverse=True)
    winner_score, winner_name = ranking[0][0], ranking[0][1]

# challenge all the policies (in .txt format) inside a folder
def statistical_challenge(turn_folder):
    # import default variables
    from defaults import box_size, snake_speed, periodic, action_mode, rand_init_body_length, \
        rand_init_direction, state_mode, show_compass, sound_effects, show_state_info, countdown_seconds

    # visual and sound effects
    sound_effects = False

    # put all shared variables into a list for convenience
    shared_vars = [box_size, snake_speed, periodic, action_mode, rand_init_body_length,\
        rand_init_direction, state_mode, show_compass, sound_effects, show_state_info, countdown_seconds]

    # number of test games
    n_games = 1000

    policies, team_names = [], []
    # all the policies are inside a subfolder 'strategie'
    policies_folder = f'{turn_folder}/strategie'
    for filename in sorted(os.listdir(policies_folder)):
        policies.append(load_user_policy(filename, policies_folder))
        team_names.append(filename.replace('.txt',''))

    # run the games in parallel
    scores_dict = test_policies_in_parallel(policies, team_names, shared_vars, n_games)

    # get team ranking
    ranking = sorted(zip(scores_dict.values(), scores_dict.keys()), reverse=True)

    # save ranking dictionary to file in turn folder
    save_path = f'{turn_folder}/ranking.txt'
    with open(save_path, 'w') as file:
        for score, team_name in ranking:
            file.write(f"{score:.3f}\t{team_name}\n")

    return ranking

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
                turn_folder = sys.argv[2]
                challenge(turn_folder)
            else: 
                print('Please specify path to policies folder')
        elif game_mode == 'statistical_challenge':
            if len(sys.argv) == 3: 
                turn_folder = sys.argv[2]
                ranking = statistical_challenge(turn_folder)
                import matplotlib.pyplot as plt
                scores = [rank[0] for rank in ranking]
                teams = [rank[1] for rank in ranking]
                plt.bar(teams, scores)
                plt.title('Punteggio medio su 1000 partite')
                plt.show()
            else: 
                print('Please specify path to policies folder')
        else:
            print('Game mode not recognized!')

        # sfida tra squadre <- path cartella CAMBIA COLORE!
        # nome suadra + id_colore <- valuta policies <- path cartella 
        # sfida ai <- path a policy vincente + id_colore
        # sfida umano vs ai (sempre grigia)
