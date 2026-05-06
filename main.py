from ui.scenes.scene_manager import SceneManager
from pokemon.pokemon_factory import PokemonFactory
from pokemon.motor.juego_interfaz import Juego

def main():
    PokemonFactory.load_all_pokemons("pokemon/pokemones.json")

    juego = Juego()
    juego.iniciar_en_bus_eventos()

    SceneManager.run(juego)

if __name__ == "__main__":
    main()
