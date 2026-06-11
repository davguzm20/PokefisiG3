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


pesos_optimos = {
    "hp": 0.242,
    "velocidad": 0.607,
    "tipo": 0.0,
    "vivos": 0.151
}


def configurar_juego(juego):
    juego.configurar_jugador_como_IA(1, 3, pokemones_disponibles, 4, pesos_optimos)
    juego.configurar_jugador_como_IA(2, 1, pokemones_disponibles, 4, pesos_mock)

tiempos = []

def evaluar_fitness(num_juegos): #obtener el win rate de 30 partidasS
        nuevo_juego = Juego()
        nuevo_juego.inicializar_combate()

        juegos = 0
        ganadas = 0

        configurar_juego(nuevo_juego)
        
        turno = 0
        while True:
            inicio = time.perf_counter()
            accionP1, accionP2 = nuevo_juego.generar_acciones_IA()

            nuevo_juego.iniciar_turno(accionP1, accionP2)

            fin = time.perf_counter()
            tiempos.append(fin-inicio)
            print(f"Tomo: {fin-inicio} segundos")

            #Revisión de ganador y creación de nuevo juego
            turno += 1
            if turno >= 20:
                configurar_juego(nuevo_juego)
                juegos = juegos +1
                turno = 0
                if juegos == num_juegos:
                    break
     
            if nuevo_juego.combate.estado_del_equipo.conteo_vivos(1) == 0:
                
                juegos = juegos +1

                if juegos == num_juegos:
                    break

                turno = 0
                configurar_juego(nuevo_juego)

            elif nuevo_juego.combate.estado_del_equipo.conteo_vivos(2) == 0:

                ganadas = ganadas +1
                juegos = juegos +1

                if juegos == num_juegos:
                    break

                turno = 0
                configurar_juego(nuevo_juego)

            

        
        print(ganadas)
        return ganadas/juegos

print(evaluar_fitness(25))

print(tiempos)