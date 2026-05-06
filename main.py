from pokemon.pokemon_factory import PokemonFactory
from ui.scenes.scene_manager import SceneManager
from pokemon.motor.juego_interfaz import Juego

def main():
    pokemons = PokemonFactory.load_all_pokemons("pokemon/pokemones.json")
    print(f"Fueron cargados {len(pokemons)} pokemons")
    
    juego = Juego()
    juego.iniciar_en_bus_eventos()

    SceneManager.run()

if __name__ == "__main__":
    main()