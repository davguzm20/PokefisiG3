import random
import copy
import time
from pokemon.motor.juego_interfaz import Juego
from pokemon.pokemon_factory import PokemonFactory

pokemones_disponibles = PokemonFactory.load_all_pokemons("pokemon/pokemones.json")

pesos_manuales = {
    "hp": 0.3,
    "velocidad": 0.2,
    "tipo": 0.3,
    "vivos": 0.2
}

def jugar_partida(nivel_ia1, nivel_ia2, pesos1=None, pesos2=None):
    juego = Juego()
    juego.configurar_jugador_como_IA(1, nivel_ia1, pokemones_disponibles, 4, pesos1)
    juego.configurar_jugador_como_IA(2, nivel_ia2, pokemones_disponibles, 4, pesos2)
    juego.inicializar_combate()
    while True:
        accionP1, accionP2 = juego.generar_acciones_IA()
        juego.iniciar_turno(accionP1, accionP2)
        if juego.combate.verificar_ganador():
            if juego.combate.estado_del_equipo.conteo_vivos(1) == 0:
                return 2
            elif juego.combate.estado_del_equipo.conteo_vivos(2) == 0:
                return 1

def evaluar_fitness(nivel_ia1, nivel_ia2, pesos1, pesos2, num_partidas=30):
    ganadas_j1 = 0
    for i in range(num_partidas):
        ganador = jugar_partida(nivel_ia1, nivel_ia2, pesos1, pesos2)
        if ganador == 1:
            ganadas_j1 += 1
        print(f"Partida {i+1}/{num_partidas}: ganó Jugador {ganador}")
    return ganadas_j1 / num_partidas

if __name__ == "__main__":
    # Cambia aquí los niveles y pesos según la prueba
    wr = evaluar_fitness(3, 2, pesos_manuales, None, num_partidas=30)
    print(f"\nWin rate IA nivel 3 (pesos manuales) vs IA nivel 2: {wr*100:.2f}%")