from pokemon.pokemon_factory import PokemonFactory
from ui.scenes.scene_manager import SceneManager

def main():
    pokemons = PokemonFactory.load_all_pokemons("pokemon/pokemones.json")
    print(f"Fueron cargados {len(pokemons)} pokemons")

    SceneManager.run()

if __name__ == "__main__":
    main()