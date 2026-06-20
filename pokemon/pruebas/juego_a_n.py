import random
import copy
import time
import threading

from pokemon.motor.juego_interfaz import Juego, IA
from pokemon.pokemon_factory import PokemonFactory

pokemones_disponibles = PokemonFactory.load_all_pokemons("pokemon/pokemones.json")

pesos_mock = {
    "hp": 0.3,
    "velocidad": 0.2,
    "tipo": 0.3,
    "vivos": 0.2
}
def evaluar_fitness(num_juegos): #obtener el win rate de 30 partidasS
        nuevo_juego = Juego()
        nuevo_juego.inicializar_combate()

        juegos = 0
        ganadas = 0

        nuevo_juego.configurar_jugador_como_IA(1, 3, pokemones_disponibles, 4, pesos_mock)
        nuevo_juego.configurar_jugador_como_IA(2, 2, pokemones_disponibles)
        
        turno = 0
        while True:
            inicio = time.perf_counter()
            accionP1, accionP2 = nuevo_juego.generar_acciones_IA()

            nuevo_juego.iniciar_turno(accionP1, accionP2)

            #Revisión de ganador y creación de nuevo juego
            turno += 1
            if turno >= 20:
                nuevo_juego.configurar_jugador_como_IA(1, 3, pokemones_disponibles, 4, pesos_mock)
                nuevo_juego.configurar_jugador_como_IA(2, 2, pokemones_disponibles)
                juegos = juegos +1
                turno = 0
                if juegos == num_juegos:
                    break

                
                
            if nuevo_juego.combate.estado_del_equipo.conteo_vivos(1) == 0:
                
                juegos = juegos +1

                if juegos == num_juegos:
                    break

                turno = 0
                nuevo_juego.configurar_jugador_como_IA(1, 3, pokemones_disponibles, 4, pesos_mock)
                nuevo_juego.configurar_jugador_como_IA(2, 2, pokemones_disponibles)

            elif nuevo_juego.combate.estado_del_equipo.conteo_vivos(2) == 0:

                ganadas = ganadas +1
                juegos = juegos +1

                if juegos == num_juegos:
                    break

                turno = 0
                nuevo_juego.configurar_jugador_como_IA(1, 3, pokemones_disponibles, 4, pesos_mock)
                nuevo_juego.configurar_jugador_como_IA(2, 2, pokemones_disponibles)

            fin = time.perf_counter()
            print(f"Tomo: {fin-inicio} segundos")

        
        
        return ganadas/juegos

evaluar_fitness(1)