from tools import *

def draw_pie_chart(screen, joystick, WIDTH, HEIGHT, scores_human, scores_ai, human_color, ai_color, draw_color, duration):

    # font sizes
    FONT_TITLE = pygame.font.Font(FONT_PATH, HEIGHT//15)
    FONT_LABEL   = pygame.font.Font(FONT_PATH, HEIGHT//40)
    FONT_HINT = pygame.font.Font(FONT_PATH, HEIGHT//60)
    FONT_SUBTITLE = pygame.font.Font(FONT_PATH, HEIGHT//25)
    FONT_AVG = pygame.font.Font(FONT_PATH, HEIGHT//32)

    title_text = 'Statistiche'
    subtitle_top = 'Vittorie:'
    subtitle_bottom = 'Punteggi medi:'
    hint_text = 'Premi il pulsante per continuare'

    # ---------- cosmetic parameters ----------
    title_pos = (WIDTH//2, HEIGHT//11)
    title_color = white
    hint_color = white
    subtitle_color = white

    pie_radius = min(WIDTH, HEIGHT)//4.5
    pie_center = (WIDTH//2, HEIGHT//2.2)  

    radial_line_length = 50
    hor_segment_length = 50
    label_offset = 10
    border_width = 4
    lines_width = 3
    label_spacing = HEIGHT//40

    colors = {'Umano': human_color, 'AI': ai_color, 'Pareggio': draw_color}

    # ---------- calculate statistics ----------
    wins_human = sum(h > a for h, a in zip(scores_human, scores_ai))
    wins_ai    = sum(a > h for h, a in zip(scores_human, scores_ai))
    draws      = len(scores_human) - wins_human - wins_ai
    total      = len(scores_human)

    fractions = {
        'Umano':    wins_human / total,
        'AI':       wins_ai / total,
        'Pareggio': draws / total
    }

    eps = 1e-6
    frac_filtered = {k: v for k, v in fractions.items() if v > eps}

    # average scores
    avg_human = sum(scores_human) / len(scores_human)
    avg_ai = sum(scores_ai) / len(scores_ai)

    # ---------- draw ----------
    screen.fill(black)

    # title
    title_surface = FONT_TITLE.render(title_text, True, title_color)
    title_rect = title_surface.get_rect(center=title_pos)
    screen.blit(title_surface, title_rect)

    # --- subtitle above the pie ---
    sub_top_surface = FONT_SUBTITLE.render(subtitle_top, True, subtitle_color)
    sub_top_rect = sub_top_surface.get_rect(center=(WIDTH//2, pie_center[1] - pie_radius - HEIGHT//9))
    screen.blit(sub_top_surface, sub_top_rect)

    # pie chart
    current_angle = -90
    for label, p in frac_filtered.items():
        end_angle = current_angle + 360 * p
        angles = np.arange(current_angle, end_angle+0.1, 0.1)

        # slice
        points = [
            pie_center,
            *[
                (
                    int(pie_center[0] + pie_radius * np.cos(np.radians(a))),
                    int(pie_center[1] + pie_radius * np.sin(np.radians(a)))
                )
                for a in angles
            ],
        ]
        pygame.draw.polygon(screen, colors[label], points)

        if len(frac_filtered) > 1:
            pygame.draw.polygon(screen, black, points, width=border_width)

        # mid angle
        mid_angle = np.radians((current_angle + end_angle)/2)
        dir_x, dir_y = np.cos(mid_angle), np.sin(mid_angle)
        current_angle = end_angle

        # radial line + horizontal segment
        line_start = (
            int(pie_center[0] + 0.5*pie_radius * dir_x),
            int(pie_center[1] + 0.5*pie_radius * dir_y)
        )
        line_mid = (
            int(pie_center[0] + (pie_radius + radial_line_length) * dir_x),
            int(pie_center[1] + (pie_radius + radial_line_length) * dir_y)
        )

        if dir_x >= 0:
            line_end = (line_mid[0] + hor_segment_length, line_mid[1])
            align = 'left'
        else:
            line_end = (line_mid[0] - hor_segment_length, line_mid[1])
            align = 'right'

        pygame.draw.line(screen, colors[label], line_start, line_mid, width=lines_width)
        pygame.draw.line(screen, colors[label], line_mid, line_end, width=lines_width)

        # # --- label (single line) ---
        # perc = (p*100)
        # text = f'{label}: {perc:.1f}%'
        # text_surface = FONT_LABEL.render(text, True, colors[label])

        # if align == 'left':
        #     text_rect = text_surface.get_rect(midleft=(line_end[0] + label_offset, line_end[1]))
        # else:
        #     text_rect = text_surface.get_rect(midright=(line_end[0] - label_offset, line_end[1]))

        # screen.blit(text_surface, text_rect)

        # --- label (two lines) ---
        perc = p * 100
        line1 = label
        line2 = f"{perc:.1f}%"

        surf1 = FONT_LABEL.render(line1, True, colors[label])
        surf2 = FONT_LABEL.render(line2, True, colors[label])

        # align both lines to same cetral point
        if align == 'left':
            r1 = surf1.get_rect(midleft=(line_end[0] + label_offset, line_end[1] - label_spacing//2))
            r2 = surf2.get_rect(midleft=(line_end[0] + label_offset, line_end[1] + label_spacing//2))
        else:
            r1 = surf1.get_rect(midright=(line_end[0] - label_offset, line_end[1] - label_spacing//2))
            r2 = surf2.get_rect(midright=(line_end[0] - label_offset, line_end[1] + label_spacing//2))

        screen.blit(surf1, r1)
        screen.blit(surf2, r2)

    # --- subtitle below pie ---
    sub_bottom_surface = FONT_SUBTITLE.render(subtitle_bottom, True, subtitle_color)
    sub_bottom_rect = sub_bottom_surface.get_rect(center=(WIDTH//2, pie_center[1] + pie_radius + HEIGHT//7))
    screen.blit(sub_bottom_surface, sub_bottom_rect)

    # --- average scores text ---
    avg_human_surface = FONT_AVG.render(f"Umano: {avg_human:.1f} punti", True, colors['Umano'])
    avg_ai_surface = FONT_AVG.render(f"AI: {avg_ai:.1f} punti", True, colors['AI'])

    avg_h_rect = avg_human_surface.get_rect(center=(WIDTH//2, sub_bottom_rect.bottom + HEIGHT//25))
    avg_ai_rect = avg_ai_surface.get_rect(center=(WIDTH//2, avg_h_rect.bottom + HEIGHT//35))

    screen.blit(avg_human_surface, avg_h_rect)
    screen.blit(avg_ai_surface, avg_ai_rect)

    # hint text at the bottom
    hint_surface = FONT_HINT.render(hint_text, True, hint_color)
    hint_rect = hint_surface.get_rect(midbottom=(WIDTH//2, HEIGHT - 20))
    screen.blit(hint_surface, hint_rect)

    pygame.display.flip()

    # ---------- exit loop ----------
    start_time = time.time()
    pressed_once = False

    while True:
        _, button_pressed = read_joystick(joystick)

        if button_pressed:
            pressed_once = True
            break

        if (time.time() - start_time) >= duration:
            break

        pygame.time.delay(10)

    # wait for button to be relased
    if pressed_once:
        release_start = time.time()
        while True:
            _, button_pressed = read_joystick(joystick)
            if not button_pressed:
                break
            if time.time() - release_start > 0.5:
                break
            pygame.time.delay(10)
