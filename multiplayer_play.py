from multiplayer_tools import *

# GAME MODES:
# demo for one player with no state info OK
# demo for one player with state info OK
# challenge all the policies (demo one game) TODO change snake color
# challenge all the policies with statistics TODO return id_color of winner
# challenge best_policy vs ai TODO receives path to best policy and id_color
# challenge human vs ai OK

def best_policy_vs_ai(policy_folder, policy_name, mode=None, show_state=None):
    # import default variables
    from defaults import box_size, snake_speed, periodic, action_mode, rand_init_body_length, \
        rand_init_direction, state_mode, show_compass, sound_effects, show_state_info, countdown_seconds

    # visual and sound effects
    show_compass = False
    sound_effects = True

    # overwrite default values
    if mode is not None: state_mode = mode
    if show_state is not None: show_compass = show_state

    # put all shared variables into a list for convenience
    shared_vars = [box_size, snake_speed, periodic, action_mode, rand_init_body_length,\
        rand_init_direction, state_mode, show_compass, sound_effects, show_state_info, countdown_seconds]

    # load a saved policy
    n_episodes = int(1e7)
    pi_star = load_policy(periodic, box_size, action_mode, state_mode, n_episodes, verbose=False)

    # load a user policy
    pi_user = load_user_policy(policy_name+'.txt', policy_folder, verbose=False)

    policies, team_names = [pi_user, pi_star], [policy_name, 'AI']

    # run the games in parallel
    scores_dict = human_policy_vs_ai(policies, team_names, shared_vars)

def human_vs_ai(mode=None, show_state=None):
    # import default variables
    from defaults import box_size, snake_speed, periodic, action_mode, rand_init_body_length, \
        rand_init_direction, state_mode, show_compass, sound_effects, show_state_info, countdown_seconds

    # visual and sound effects
    show_compass = False
    sound_effects = True

    # overwrite default values
    if mode is not None: state_mode = mode
    if show_state is not None: show_compass = show_state

    # put all shared variables into a list for convenience
    shared_vars = [box_size, snake_speed, periodic, action_mode, rand_init_body_length,\
        rand_init_direction, state_mode, show_compass, sound_effects, show_state_info, countdown_seconds]

    # load a saved policy
    n_episodes = int(1e7)
    pi_star = load_policy(periodic, box_size, action_mode, state_mode, n_episodes, verbose=False)

    policies, team_names = [None, pi_star], ['Umano', 'AI']

    # run the games in parallel
    scores_dict = run_games_in_parallel(policies, team_names, shared_vars)

# demo for one player 
def one_player(mode=None, show_state=None):
    from defaults import box_size, snake_speed, periodic, action_mode, rand_init_body_length, \
        rand_init_direction, state_mode, show_compass, sound_effects, show_state_info, countdown_seconds

    # overwrite default values
    if mode is not None: state_mode = mode
    if show_state is not None: show_compass = show_state

    # put all shared variables into a list for convenience
    shared_vars = [box_size, snake_speed, periodic, action_mode, rand_init_body_length,\
        rand_init_direction, state_mode, show_compass, sound_effects, show_state_info, countdown_seconds]

    # if policy is None the game is launched in interactive mode
    policy = None

    # run game
    n_teams, team_name = 1, None
    cell_size, window_position = calculate_size_and_positions(n_teams, box_size)
    run_snake_game(policy, team_name, window_position, cell_size, shared_vars)

# challenge all the policies (in .txt format) inside a folder on one game (with rendering)
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

# challenge all the policies (in .txt format) with statistics (no rendering)
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

    import matplotlib.pyplot as plt
    scores = [rank[0] for rank in ranking]
    teams = [rank[1] for rank in ranking]
    plt.bar(teams, scores)
    plt.title('Punteggio medio su 1000 partite')
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print('Please specify one game mode')
    else:
        game_mode = sys.argv[1]

        # behavior for different game modes
        # 'one_player' mode requires flag to show state or not
        if game_mode == 'one_player':
            state_mode = 'simple'
            if len(sys.argv) == 3: 
                if sys.argv[2] == 'show':
                    show_state = True
                    one_player(state_mode, show_state)
                elif sys.argv[2] == 'no_show':
                    show_state = False
                    one_player(state_mode, show_state)
                else:
                    print("Please specify show_state flag ('show' or 'no_show')")
            # if no show_state flag is passed, run game with default values
            else:
                one_player()
        # 'challenge' mode requires path to policies folder as a second argument
        elif game_mode == 'challenge':
            if len(sys.argv) == 3: 
                turn_folder = sys.argv[2]
                challenge(turn_folder)
            else: 
                print('Please specify path to policies folder')
        elif game_mode == 'statistical_challenge':
            if len(sys.argv) == 3: 
                turn_folder = sys.argv[2]
                statistical_challenge(turn_folder)
            else: 
                print('Please specify PATH to policies folder')
        # 'human_vs_ai' mode requires flag to choose state mode
        elif game_mode == 'human_vs_ai':
            show_state = True
            if len(sys.argv) == 3: 
                if sys.argv[2] == 'simple':
                    state_mode = 'simple'
                    show_state = True
                    human_vs_ai(state_mode, show_state)
                elif sys.argv[2] == 'proximity':
                    state_mode = 'proximity'
                    human_vs_ai(state_mode, show_state)
                else:
                    print("Please specify a STATE MODE ('simple' or 'proximity')")
            # if no show_state flag is passed, run game with default values
            else:
                human_vs_ai()
        # 'best_policy_vs_ai' mode requires flag to choose state mode AND path to best policy
        elif game_mode == 'best_policy_vs_ai':
            show_state = True
            if len(sys.argv) == 5: 
                policy_folder = sys.argv[2]
                policy_name = sys.argv[3]
                if sys.argv[4] == 'simple':
                    state_mode = 'simple'
                    show_state = True
                    best_policy_vs_ai(policy_folder, policy_name, state_mode, show_state)
                elif sys.argv[4] == 'proximity':
                    state_mode = 'proximity'
                    best_policy_vs_ai(policy_folder, policy_name, state_mode, show_state)
                else:
                    print("Please specify STATE MODE of AI, then PATH to folder and NAME of best policy")
            elif len(sys.argv) == 4: 
                policy_folder = sys.argv[2]
                policy_name = sys.argv[3]
                best_policy_vs_ai(policy_folder, policy_name)
        else:
            print('Game mode not recognized!')
