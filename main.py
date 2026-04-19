import pygame

BASE_WIDTH, BASE_HEIGHT, SCALE = 320, 240, 2.5

def main():
    pygame.init()
    running = True

    pygame.display.set_mode((BASE_WIDTH * SCALE, BASE_HEIGHT * SCALE))
    pygame.display.set_caption("POKEFISIG3")
    

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()

if __name__ == "__main__":
    main()