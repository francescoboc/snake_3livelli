from tools import *

def draw_pie_chart(screen, scores_human, scores_ai, font_title, font_sub, human_color, ai_color, draw_color, duration=5000):
    WIDTH, HEIGHT = screen.get_size()

    # cosmetic parameters
    title_text = 'statistica vittorie'
    title_pos = (WIDTH//2, HEIGHT//7)
    title_color = white
    pie_radius = min(WIDTH, HEIGHT)//5
    pie_center = (WIDTH//2, 1.2*(HEIGHT//2))
    radial_line_length = 50
    hor_segment_length = 75
    label_offset = 10
    border_width = 4
    lines_width = 3

    # set colors
    colors = {'Umano': human_color, 'AI': ai_color, 'Pareggio': draw_color}

    # compute fraction of victories
    wins_human = sum(h > a for h, a in zip(scores_human, scores_ai))
    wins_ai = sum(a > h for h, a in zip(scores_human, scores_ai))
    draws = len(scores_human) - wins_human - wins_ai
    total = len(scores_human)

    fractions = {'Umano': wins_human / total, 'AI': wins_ai / total, 'Pareggio': draws / total}

    # filtra le entry con percentuale (quasi) zero
    eps = 1e-6
    frac_filtered = {k: v for k, v in fractions.items() if v > eps}

    # draw title
    title_surface = font_title.render(title_text, True, title_color)
    title_rect = title_surface.get_rect(center=title_pos)
    screen.fill(black)
    screen.blit(title_surface, title_rect)

    # draw pie slices and labels
    current_angle = -90
    for label, p in frac_filtered.items():
        end_angle = current_angle + 360 * p
        angles = np.arange(current_angle, end_angle+0.1, 0.1)
        points = [pie_center] + [
            (int(pie_center[0] + pie_radius * np.cos(np.radians(a))),
             int(pie_center[1] + pie_radius * np.sin(np.radians(a)))) 
            for a in angles
        ]
    
        # draw slice
        pygame.draw.polygon(screen, colors[label], points)

        if len(frac_filtered.items())>1:
            pygame.draw.polygon(screen, black, points, width=border_width)
    
        # compute mid angle
        mid_angle = np.radians((current_angle + end_angle) / 2)
        dir_x, dir_y = np.cos(mid_angle), np.sin(mid_angle)
        current_angle = end_angle
    
        # draw radial lines with horizontal segments
        line_start = (int(pie_center[0] + 0.5*pie_radius * dir_x),
                      int(pie_center[1] + 0.5*pie_radius * dir_y))
        line_mid = (int(pie_center[0] + (pie_radius + radial_line_length) * dir_x),
                    int(pie_center[1] + (pie_radius + radial_line_length) * dir_y))
    
        if dir_x >= 0:  
            line_end = (line_mid[0] + hor_segment_length, line_mid[1])
            text_anchor = (line_end[0] + label_offset, line_end[1])
            align = 'left'
        else:  
            line_end = (line_mid[0] - hor_segment_length, line_mid[1])
            text_anchor = (line_end[0] - label_offset, line_end[1])
            align = 'right'
        
        pygame.draw.line(screen, colors[label], line_start, line_mid, width=lines_width)
        pygame.draw.line(screen, colors[label], line_mid, line_end, width=lines_width)

        # add labels
        text = f'{label}: {(p * 100):.1f}%'
        text_surface = font_sub.render(text, True, colors[label])
        text_rect = (
            text_surface.get_rect(midleft=text_anchor)
            if align == 'left'
            else text_surface.get_rect(midright=text_anchor)
        )
        screen.blit(text_surface, text_rect)
        
        # # label border
        # pygame.draw.rect(screen, black, text_rect.inflate(10, 6))
        # pygame.draw.rect(screen, colors[label], text_rect.inflate(10, 6), width=2)
    
    pygame.display.flip()
    pygame.time.wait(duration)
