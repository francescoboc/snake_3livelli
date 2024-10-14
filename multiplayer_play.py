from multiplayer_tools import *

def best_policy_vs_ai(turn_folder, team_name, mode=None, show_state=None, seed=None):
    # import default variables
    from defaults import box_size, snake_speed, periodic, action_mode, rand_init_body_length, \
        rand_init_direction, state_mode, show_compass, sound_effects, show_state_info, countdown_seconds

    # overwrite default values
    show_compass = False
    sound_effects = True

    # this is important! the policies are all defined with 3 actions
    action_mode = 3

    # overwrite default values
    if mode is not None: state_mode = mode
    if show_state is not None: show_compass = show_state

    # put all shared variables into a list for convenience
    shared_vars = [box_size, snake_speed, periodic, action_mode, rand_init_body_length,\
        rand_init_direction, state_mode, show_compass, sound_effects, show_state_info, countdown_seconds]

    # load a saved policy
    n_episodes = int(1e7)
    pi_star = load_policy(periodic, action_mode, state_mode, n_episodes, verbose=False)

    # load a user policy from a turn folder
    policy_folder = turn_folder + '/strategie'
    policy_name = team_name + '.txt'
    pi_user = load_user_policy(policy_name, policy_folder, verbose=False)

    policies, team_names = [pi_user, pi_star], [team_name, 'AI']

    # map team_name to corresponding color by loading the list of teams
    policy_folder, team_names_folder = load_policies_from_folder(policy_folder)
    color_mapping = {team_names_folder[i]:color_schemes[i] for i in range(len(team_names_folder))}
    color_scheme = color_mapping[team_name]

    # run the games in parallel
    scores_dict = human_policy_vs_ai(policies, team_names, shared_vars, seed, color_scheme)

def human_vs_ai(mode=None, show_state=None):
    # import default variables
    from defaults import box_size, snake_speed, periodic, action_mode, rand_init_body_length, \
        rand_init_direction, state_mode, show_compass, sound_effects, show_state_info, countdown_seconds

    # overwrite default values
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
    action_mode = 3
    pi_star = load_policy(periodic, action_mode, state_mode, n_episodes, verbose=False)

    policies, team_names = [None, pi_star], ['Umano', 'AI']

    # pass the same seed to all the games
    seed = random.randrange(sys.maxsize)
    seeds = [seed for t in range(len(team_names))]

    # run the games in parallel
    scores_dict = run_games_in_parallel(policies, team_names, shared_vars, seeds)

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

    # overwrite default values
    show_compass = True
    sound_effects = False

    # put all shared variables into a list for convenience
    shared_vars = [box_size, snake_speed, periodic, action_mode, rand_init_body_length,\
        rand_init_direction, state_mode, show_compass, sound_effects, show_state_info, countdown_seconds]

    # all the policies are inside a subfolder 'strategie'
    policies_folder = f'{turn_folder}/strategie'

    # load policies and team names
    policies, team_names = load_policies_from_folder(policies_folder)

    # pass the same seed to all the games
    seed = random.randrange(sys.maxsize)
    seeds = [seed for t in range(len(team_names))]

    # run the games in parallel
    scores_dict = run_games_in_parallel(policies, team_names, shared_vars, seeds)

    # get team ranking
    ranking = sorted(zip(scores_dict.values(), scores_dict.keys()), reverse=True)
    winner_score, winner_name = ranking[0][0], ranking[0][1]

# show the challenge but with the best run of each game
def challenge_best_seeds(turn_folder):
    # import default variables
    from defaults import box_size, snake_speed, periodic, action_mode, rand_init_body_length, \
        rand_init_direction, state_mode, show_compass, sound_effects, show_state_info, countdown_seconds

    # overwrite default values
    show_compass = True
    sound_effects = False

    # put all shared variables into a list for convenience
    shared_vars = [box_size, snake_speed, periodic, action_mode, rand_init_body_length,\
        rand_init_direction, state_mode, show_compass, sound_effects, show_state_info, countdown_seconds]

    # all the policies are inside a subfolder 'strategie'
    policies_folder = f'{turn_folder}/strategie'

    # load policies and team names
    policies, team_names = load_policies_from_folder(policies_folder)

    # load ranking file (these are dictionaries)
    mean_scores, best_seeds = load_ranking(turn_folder)

    # the seeds list needs to be arranged as team_names
    ordered_seeds = [best_seeds[team_name] for team_name in team_names]

    # run the games in parallel
    scores_dict = run_games_in_parallel(policies, team_names, shared_vars, ordered_seeds)

    # get team ranking
    ranking = sorted(zip(scores_dict.values(), scores_dict.keys()), reverse=True)
    winner_score, winner_name = ranking[0][0], ranking[0][1]

# challenge all the policies (in .txt format) with statistics (no rendering)
def statistical_challenge(turn_folder):
    # import default variables
    from defaults import box_size, snake_speed, periodic, action_mode, rand_init_body_length, \
        rand_init_direction, state_mode, show_compass, sound_effects, show_state_info, countdown_seconds

    # overwrite default values
    sound_effects = False

    # put all shared variables into a list for convenience
    shared_vars = [box_size, snake_speed, periodic, action_mode, rand_init_body_length,\
        rand_init_direction, state_mode, show_compass, sound_effects, show_state_info, countdown_seconds]

    # number of test games
    n_games = 1000

    # all the policies are inside a subfolder 'strategie'
    policies_folder = f'{turn_folder}/strategie'

    # load policies and team names
    policies, team_names = load_policies_from_folder(policies_folder)

    # team_names list is ordered as color_schemes, so we can use it to map names to colors
    color_mapping = {team_names[i]:color_schemes_rgb[i].normalize() for i in range(len(team_names))}

    # test policies in parallel
    print('Valutazione strategie in corso...')
    scores_dict, seeds_dict = test_policies_in_parallel(policies, team_names, shared_vars, n_games)

    # get team ranking
    ranking = sorted(zip(scores_dict.values(), scores_dict.keys()), reverse=True)

    # save ranking dictionary to file in turn folder
    save_path = f'{turn_folder}/ranking.txt'
    with open(save_path, 'w') as file:
        for score, team_name in ranking:
            # get the corresponding seed for the team
            seed = seeds_dict[team_name]  
            file.write(f"{score:.3f}\t{team_name}\t{seed}\n")

    ########## PLOT BARS TO SHOW AVERAGE SCORES ########## 

    import matplotlib.pyplot as plt
    from matplotlib.widgets import Button

    # function to add average score text on top of each bar
    def add_scores_to_bars(bars, scores):
        for bar, score in zip(bars, scores):
            height = bar.get_height()  # get bar height
            ax.text(
                bar.get_x() + bar.get_width() / 2,  # x position (centered on bar)
                height,  # y position (top of bar)
                f'{score:.2f}',  # text (formatted score)
                ha='center', va='bottom',  # horizontal and vertical alignment
                fontsize=12,
                weight = 'bold'
            )

    # create scores and teams lists
    scores = [rank[0] for rank in ranking]
    teams = [rank[1] for rank in ranking]

    # create ordered colors list
    colors = [color_mapping[team] for team in teams]

    # disable the toolbar
    plt.rcParams['toolbar'] = 'none'

    plot_title = 'Punteggio medio su 1000 partite'
    pi_star_simple_label = 'AI'
    pi_star_proximity_label = 'AI avanzata'

    pi_star_simple_color = grey.normalize()
    pi_star_proximity_color = brown.normalize()

    fig, ax = plt.subplots(figsize=(8,5.5))
    fig.tight_layout(pad=2)
    fig.canvas.manager.set_window_title('Sfida')
    bars = ax.bar(teams, scores, color=colors)
    add_scores_to_bars(bars, scores)
    ax.set_title(plot_title, weight='bold')

    # rotate x-tick labels
    ax.set_xticks(range(len(teams)))
    ax.set_xticklabels(teams, rotation=45, ha='right', fontsize=12, weight='bold')

    # remove y-ticks
    ax.set_yticks([])

    # adjust layout to make room for the team names
    plt.subplots_adjust(bottom=0.17)

    # # load and test learned policies
    # n_episodes = int(1e7)
    # state_mode = 'simple'
    # action_mode = 3
    # policy = load_policy(periodic, action_mode, state_mode, n_episodes, verbose=False)
    # pi_star_simple_score, _ = test_policy(action_mode, state_mode, box_size, periodic, 
    #         rand_init_body_length, rand_init_direction, n_games, policy, verbose=False, use_tqdm=False)
    # state_mode = 'proximity'
    # policy = load_policy(periodic, action_mode, state_mode, n_episodes, verbose=False)
    # pi_star_proximity_score, _ = test_policy(action_mode, state_mode, box_size, periodic, 
    #         rand_init_body_length, rand_init_direction, n_games, policy, verbose=False, use_tqdm=False)

    # no need to re-evaluate the learned policies everytime!
    pi_star_simple_score = 46.11
    pi_star_proximity_score = 56.08

    # prepare pi_star_bars dictionary with all info for the new score bars
    pi_star_bars = {
        pi_star_simple_label: {'score': pi_star_simple_score, 
            'color': pi_star_simple_color, 'show': False},
        pi_star_proximity_label: {'score': pi_star_proximity_score, 
            'color': pi_star_proximity_color, 'show': False}
    }

    # function to reveal score bars dynamically
    def reveal_pi_star_bar(label):
        if pi_star_bars[label]['show'] is False:
            # append the new bar label, score and color to the existing lists
            new_score = pi_star_bars[label]['score']
            new_color = pi_star_bars[label]['color']
            teams.append(label)
            scores.append(new_score)
            colors.append(new_color)

            # clear the existing plot and redraw everything
            ax.clear()  
            bars = ax.bar(teams, scores, color=colors)
            add_scores_to_bars(bars, scores)
            ax.set_title(plot_title, weight='bold')

            # rotate x-tick labels
            ax.set_xticks(range(len(teams)))
            ax.set_xticklabels(teams, rotation=45, ha='right', fontsize=12, weight='bold')

            # remove y-ticks
            ax.set_yticks([])

            # adjust layout to make room for the team names
            plt.subplots_adjust(bottom=0.17)

            # mark the bar as revealed (so button becomes inactive)
            pi_star_bars[label]['show'] = True  

            # redraw the plot
            plt.draw()

    # create buttons 
    button_ax_simple = plt.axes([0.91, 0.01, 0.037, 0.04])
    button_simple = Button(button_ax_simple, 'AI')
    button_simple.on_clicked(lambda event: reveal_pi_star_bar(pi_star_simple_label))

    button_ax_proximity = plt.axes([0.955, 0.01, 0.037, 0.04])
    button_proximity = Button(button_ax_proximity, 'AI+')
    button_proximity.on_clicked(lambda event: reveal_pi_star_bar(pi_star_proximity_label))

    plt.show()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print('Please specify one game mode')
        print('Game modes:\n \
        one_player\n \
        challenge\n \
        statistical_challenge\n \
        challenge_best\n \
        human_vs_ai\n \
        best_policy_vs_ai')

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
                    raise Warning("Please specify show_state FLAG ('show' or 'no_show')")
            # if no show_state flag is passed, run game with default values
            else:
                one_player()

        # 'challenge' mode requires path to policies folder as a second argument
        elif game_mode == 'challenge':
            if len(sys.argv) == 3: 
                turn_folder = sys.argv[2]
                challenge(turn_folder)
            else: 
                raise Warning('Please specify PATH to policies folder')

        # similar to challenge but there's no render of the games, only a bar plot of statistics
        elif game_mode == 'statistical_challenge':
            if len(sys.argv) == 3: 
                turn_folder = sys.argv[2]
                statistical_challenge(turn_folder)
            else: 
                raise Warning('Please specify PATH to policies folder')

        # same as challenge mode but uses best seeds (to do AFTER statistical_challenge)
        elif game_mode == 'challenge_best':
            if len(sys.argv) == 3: 
                turn_folder = sys.argv[2]
                challenge_best_seeds(turn_folder)
            else: 
                raise Warning('Please specify PATH to policies folder')

        # 'human_vs_ai' mode requires flag to choose state mode
        elif game_mode == 'human_vs_ai':
            show_state = True
            if len(sys.argv) == 3: 
                if sys.argv[2] == 'simple':
                    state_mode = 'simple'
                elif sys.argv[2] == 'proximity':
                    state_mode = 'proximity'
                else:
                    raise Warning("Please specify a STATE MODE ('simple' or 'proximity')")
                human_vs_ai(state_mode, show_state)
            # if no state_mode flag is passed, run game with default values
            else:
                human_vs_ai()

        # 'best_policy_vs_ai' mode reads the best team from ranking file and asks for state mode
        elif game_mode == 'best_policy_vs_ai':
            show_state = True
            if len(sys.argv) == 4 or len(sys.argv) == 5:
                turn_folder = sys.argv[2]
                if sys.argv[3] == 'simple':
                    state_mode = 'simple'
                elif sys.argv[3] == 'proximity':
                    state_mode = 'proximity'
                else:
                    raise Warning("Please specify a STATE MODE ('simple' or 'proximity')")
                # load ranking file
                mean_scores, best_seeds = load_ranking(turn_folder)
                # select which ranking position to challenge
                if len(sys.argv) == 5: position = int(sys.argv[4])
                else: position = 1
                if position > len(mean_scores):
                    raise Warning(f'Position {position} does not exist in this ranking file!')
                team_name =  list(mean_scores.keys())[position-1]
                # seed = best_seeds[team_name]
                seed = random.randrange(sys.maxsize)
                best_policy_vs_ai(turn_folder, team_name, state_mode, show_state, seed)
            else:
                raise Warning("Please specify PATH to turn folder, STATE MODE of AI, ranking POSITION")

        else:
            print('Please specify one game mode')
            print('Game modes:\n \
            one_player\n \
            challenge\n \
            statistical_challenge\n \
            challenge_best\n \
            human_vs_ai\n \
            best_policy_vs_ai')
