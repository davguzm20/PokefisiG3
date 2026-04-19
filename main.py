import pygame
from pokemon.pokemon_factory import PokemonFactory

BASE_WIDTH, BASE_HEIGHT, SCALE = 320, 240, 2.5


def main():
    pygame.init()
    running = True

    pokemons = PokemonFactory.load_all_pokemons("pokemon/pokemones.json")
    print(f"Fueron cargados {len(pokemons)} pokemons")

    pygame.display.set_mode((BASE_WIDTH * SCALE, BASE_HEIGHT * SCALE))
    pygame.display.set_caption("POKEFISIG3")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()


if __name__ == "__main__":
    main()