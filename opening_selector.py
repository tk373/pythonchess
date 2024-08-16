import pygame

def select_opening(openings):
    pygame.init()
    opening_selected = None
    font = pygame.font.Font(None, 36)
    select_screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption('Select Opening')

    while opening_selected is None:
        select_screen.fill((255, 255, 255))
        y = 50

        for opening_name in openings:  # Directly iterate over the dict_keys object
            text = font.render(opening_name, True, (0, 0, 0))
            select_screen.blit(text, (50, y))
            y += 50

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                selected_index = (y - 50) // 50
                if 0 <= selected_index < len(openings):
                    opening_selected = list(openings)[selected_index]

    return opening_selected
