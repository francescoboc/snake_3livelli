import pygame
import subprocess
import sys

def start_screen_loop():
    pygame.init()
    WIDTH, HEIGHT = 600, 400
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
    pygame.display.set_caption("Snake Challenge")

    font_title = pygame.font.Font(None, 72)
    font_sub = pygame.font.Font(None, 40)

    title_text = font_title.render("Snake Challenge", True, (255, 255, 255))
    prompt_text = font_sub.render("PREMI SPAZIO PER COMINCIARE", True, (200, 255, 200))
    quit_text = font_sub.render("Premi ESC per uscire", True, (180, 180, 180))

    clock = pygame.time.Clock()
    game_process = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_SPACE:
                    # blocca il menu finché il gioco non termina
                    subprocess.run(["python", "human_vs_ai.py"])

                    # RI-inizializza il display per riprendere il focus
                    pygame.display.quit()
                    pygame.display.init()
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
                    pygame.display.set_caption("Snake Challenge")

        screen.fill((20, 20, 20))
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 100))
        screen.blit(prompt_text, (WIDTH//2 - prompt_text.get_width()//2, 230))
        screen.blit(quit_text, (WIDTH//2 - quit_text.get_width()//2, 300))

        pygame.display.flip()
        clock.tick(60)

start_screen_loop()
