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
    juego.configurar_jugador_como_IA(2, 2, pokemones_disponibles, 4, pesos_mock)

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

            hay_ganador = nuevo_juego.iniciar_turno(accionP1, accionP2)
            turno += 1
            if turno == 20:
                juegos = juegos +1

                if juegos == num_juegos: break
                configurar_juego(nuevo_juego)
                turno = 0
                
            if hay_ganador:
                if nuevo_juego.combate.estado_del_equipo.ganaP1:
                    ganadas = ganadas +1
                    juegos = juegos +1

                    if juegos == num_juegos: break
                    configurar_juego(nuevo_juego)
                    turno = 0

                elif nuevo_juego.combate.estado_del_equipo.ganaP2:
                    juegos = juegos +1
                    
                    if juegos == num_juegos: break
                    configurar_juego(nuevo_juego)
                    turno = 0
                
                

            else:
                index_intercambioP1 = 0
                index_intercambioP2 = 0

                if nuevo_juego.combate.hay_intercambioP1:
                    print("La IA está eligiendo un intercambio")
                    #index_intercambioP1 = nuevo_juego.combate.generar_intercambio_aleatorio(1)
                    index_intercambioP1 = nuevo_juego.jugador1.elegir_movimiento_ia(nuevo_juego.combate.estado_del_equipo)
                elif nuevo_juego.combate.hay_intercambioP2:
                    index_intercambioP2 = nuevo_juego.combate.generar_intercambio_aleatorio(2)
                
                nuevo_juego.combate.ejecutar_intercambios_por_debilitamiento(index_intercambioP1, index_intercambioP2)

            fin = time.perf_counter()
            tiempos.append(fin-inicio)
            print(f"Tomo: {fin-inicio} segundos")

        print(ganadas)
        return ganadas/juegos

print(evaluar_fitness(1))

print(tiempos)
