from pokemon.pokemon_factory import PokemonFactory
#from pokemon.motor.maquina_de_estados import maquina_de_estados
from pokemon.motor.acciones import calcular_daño
from pokemon.motor.acciones import establecer_vida
from pokemon.motor.combate import Combate
from pokemon.motor.estado_juego import EstadoJuego

import math
import random


pokemones_disponibles = PokemonFactory.load_all_pokemons("pokemon/pokemones.json")

for p in pokemones_disponibles:
    p.hp *= 2

estado = EstadoJuego()
estado.setEquipo([pokemones_disponibles[0], pokemones_disponibles[1]], equipo=1) # P1
estado.setEquipo([pokemones_disponibles[5], pokemones_disponibles[6]], equipo=2) # P2

motor = Combate(estado)

print(f"--- INICIO DEL DUELO: {estado.pokemonActivoP1.name} vs {estado.pokemonActivoP2.name} ---")

turno = 1
while True:
    print(f"\n>>> TURNO {turno}")
    
    accionP1 = estado.pokemonActivoP1.moves[0]
    accionP2 = estado.pokemonActivoP2.moves[0]

    print(accionP2.damage_class)

    motor.ejecutar_turno(
        estado.pokemonActivoP1, accionP1, 
        estado.pokemonActivoP2, accionP2
    )
    
    print(estado.pokemonActivoP1.hp, estado.pokemonActivoP2.hp )

    resultado = motor.verificar_ganador()
    if resultado: 
        break
    
    turno += 1
    if turno > 50: 
        print("Empate por agotamiento técnico.")
        break
