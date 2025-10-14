from pie_chart import *
import human_vs_ai
# import subprocess

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
    pygame.init()

    # get total screen size
    display_sizes = pygame.display.get_desktop_sizes()
    WIDTH, HEIGHT = display_sizes[0][0], display_sizes[0][1]

    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)

    # set retro style font, colors, and background
    font_title_height = HEIGHT//10
    font_sub_height = font_title_height//2
    font_title = pygame.font.Font(FONT_PATH, font_title_height)
    font_sub = pygame.font.Font(FONT_PATH, font_sub_height)

    bg_color = black
    border_color = yellow

    title_color = white
    title_string = "sfida l'AI a snake!"

    prompt_color = yellow
    prompt_string = 'premi spazio per giocare'

    # TODO usa questi stessi colori anche per il serpente
    human_color = green
    ai_color = red
    draw_color = yellow

    spacing = font_title_height

    title_surface = font_title.render(title_string, True, title_color)
    prompt_surface = font_sub.render(prompt_string, True, prompt_color)

    title_rect = title_surface.get_rect(center=(WIDTH//2, HEIGHT//2))
    prompt_rect = prompt_surface.get_rect(center=(WIDTH//2, HEIGHT//2 + spacing))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_SPACE:

                    # # blackout the screen to reduce flashing when the game windows are closed
                    # screen.fill(bg_color)
                    # pygame.display.flip()

                    # # run human_vs_ai function and freeze loop until termination
                    # # subprocess.run(['python', 'human_vs_ai.py'])
                    # process = subprocess.Popen(['python', 'human_vs_ai.py'])
                    # process.wait()
                    human_vs_ai.main()

                    # read scores from csv file
                    scores_human, scores_ai = read_scores()

                    # TODO close and reopen display to regain focus (dirty)
                    pygame.display.quit()
                    pygame.display.init()
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)

                    # # TODO get id of pygame window and use xdotool to regain focus
                    # # pygame.time.wait(150)
                    # wid = pygame.display.get_wm_info().get('window')
                    # subprocess.run(['xdotool', 'windowactivate', str(wid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                    # show results with a pie chart
                    draw_pie_chart(screen, scores_human, scores_ai, font_title, 
                            font_sub, human_color, ai_color, draw_color, duration=3000)

        screen.fill(bg_color)
        screen.blit(title_surface, title_rect)
        screen.blit(prompt_surface, prompt_rect)

        pygame.display.flip()

if __name__ == "__main__":
    start_screen_loop()
