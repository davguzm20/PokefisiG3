from pokemon.pokemon_factory import PokemonFactory
#from pokemon.motor.maquina_de_estados import maquina_de_estados
from pokemon.motor.acciones import calcular_daño
from pokemon.motor.acciones import establecer_vida
from pokemon.motor.combate import Combate
from pokemon.motor.estado_juego import EstadoJuego
from pokemon.agenteP.agenteP import AgenteP, elegirMovimientoAleatorio, movimiento_en_base_a_mayor_daño

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
    
    accionP1 = elegirMovimientoAleatorio(estado.pokemonActivoP1.moves)
    accionP2 = movimiento_en_base_a_mayor_daño(estado.pokemonActivoP1, estado.pokemonActivoP2, estado.pokemonActivoP2.moves)[1] #Cuidado aquí

    print(accionP2.damage_class)

    motor.ejecutar_turno(
        estado.pokemonActivoP1, accionP1, 
        estado.pokemonActivoP2, accionP2
    )
    print(f'Jugador 1 usa: {accionP1.name}')
    print(f'Jugador 2 usa: {accionP2.name}')
    print(f'{estado.pokemonActivoP1.name}: {estado.pokemonActivoP1.hp} ||||| {estado.pokemonActivoP1.name}: {estado.pokemonActivoP2.hp}')

    resultado = motor.verificar_ganador()
    if resultado: 
        break
    
    turno += 1
    if turno > 50: 
        print("Empate por agotamiento técnico.")
        break
