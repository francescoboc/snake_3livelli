from pie_chart import *
import subprocess
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--level', choices=['easy', 'medium', 'hard'], default='medium')
    return parser.parse_args()

def read_scores(file_path='scores.csv'):
    if not os.path.exists(file_path):
        return None

    scores_human, scores_ai = [], []
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            scores_human.append(float(row['Umano']))
            scores_ai.append(float(row['AI']))

    return scores_human, scores_ai

def start_screen_loop():
    # initialize pygame
    pygame.init()

    # initialize joystick
    pygame.joystick.init()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    # get total screen size
    display_sizes = pygame.display.get_desktop_sizes()
    WIDTH, HEIGHT = display_sizes[0][0], display_sizes[0][1]

    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)

    # load and scale background image
    bg_image = pygame.image.load("sfondo_snake.jpg")
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

    # parse argument to set level of AI
    args = parse_args()
    level = args.level

    if level == 'easy':
        ai_color = blue

    elif level == 'medium':
        ai_color = orange

    elif level == 'hard':
        ai_color = red

    human_color = green
    draw_color = grey

    while True:
        _, start_pressed = read_joystick(joystick)

        if start_pressed:
            # blackout the screen
            screen.fill(black)
            pygame.display.flip()

            # run human_vs_ai function and freeze loop until termination
            subprocess.run(['python', 'human_vs_ai.py', '--level', level], stderr=subprocess.DEVNULL)
            # subprocess.run(['python', 'human_vs_ai.py', '--level', level])

            # read scores from csv file
            scores_human, scores_ai = read_scores()

            # get id of pygame window and use xdotool to regain focus
            pygame.time.wait(150)
            wid = pygame.display.get_wm_info().get('window')
            subprocess.run(['xdotool', 'windowactivate', str(wid)], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # show results with a pie chart
            draw_pie_chart(screen, joystick, WIDTH, HEIGHT, scores_human, scores_ai, 
                           human_color, ai_color, draw_color, duration=45)

        # redraw the background
        screen.blit(bg_image, (0, 0))
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    start_screen_loop()
