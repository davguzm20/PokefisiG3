from ui.scenes.scene_manager import SceneManager
from pokemon.pokemon_factory import PokemonFactory
from pokemon.motor.juego_interfaz import Juego
import sys

def main():
    PokemonFactory.load_all_pokemons("pokemon/pokemones.json")

    juego = Juego()
    juego.iniciar_en_bus_eventos()
    sys.setswitchinterval(0.0005) #Se usan hilos, entonces para que no se vea tan lageado, se concurre de hilo en hilo en este intervalo

    SceneManager.run(juego)

if __name__ == "__main__":
    main()
