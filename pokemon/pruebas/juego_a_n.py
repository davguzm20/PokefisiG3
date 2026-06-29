import random
import copy
import time
import threading

from pokemon.motor.juego_interfaz import Juego, IA
from pokemon.pokemon_factory import PokemonFactory
from pokemon.enums.effects import Effects

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


def configurar_juego(juego: Juego):
    juego.configurar_jugador_como_IA(1, 3, pokemones_disponibles, 6, pesos_mock)
    juego.configurar_jugador_como_IA(2, 2, pokemones_disponibles, 4, pesos_mock)

    juego.configurar_equipo_aleatoriamente(1, pokemones_disponibles)
    juego.configurar_equipo_aleatoriamente(2, pokemones_disponibles)

    juego.inicializar_combate()
    juego.estado.esTerminal = False
    juego.estado.ganaP1 = False
    juego.estado.ganaP2 = False

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
            if turno == 50:
                juegos = juegos +1

                if juegos == num_juegos: break
                configurar_juego(nuevo_juego)
                turno = 0
                continue
                
            if hay_ganador:
                juegos = juegos +1
                if nuevo_juego.combate.estado_del_equipo.ganaP1:
                    ganadas = ganadas +1
                    

                    if juegos == num_juegos: break
                    configurar_juego(nuevo_juego)
                    turno = 0
                    continue

                elif nuevo_juego.combate.estado_del_equipo.ganaP2:
                    
                    if juegos == num_juegos: break

                    configurar_juego(nuevo_juego)
                    turno = 0
                    continue
                
            else:
                index_intercambioP1 = 0
                index_intercambioP2 = 0
                necesita_intercambio = False
                
                print("REVISANDO SI HAY INTERCAMBIOS")

                if nuevo_juego.combate.hay_intercambioP1:
                    necesita_intercambio = True
                    if nuevo_juego.jugador1.nivel_IA == 3:

                        decision = nuevo_juego.jugador1.elegir_movimiento_ia(nuevo_juego.combate.estado_del_equipo)
                        index_intercambioP1 = decision
                    else:
                        index_intercambioP1 = nuevo_juego.combate.generar_intercambio_aleatorio(1)

                if nuevo_juego.combate.hay_intercambioP2:
                    necesita_intercambio = True
                    if nuevo_juego.jugador2.nivel_IA == 3:

                        decision = nuevo_juego.jugador2.elegir_movimiento_ia(nuevo_juego.combate.estado_del_equipo)
                        index_intercambioP2 = decision
                    else:
                        index_intercambioP2 = nuevo_juego.combate.generar_intercambio_aleatorio(2)

                if necesita_intercambio:
                    nuevo_juego.combate.ejecutar_intercambios_por_debilitamiento(index_intercambioP1, index_intercambioP2)

            fin = time.perf_counter()
            tiempos.append(fin-inicio)
            print(f"Tomo: {fin-inicio} segundos")

        print(ganadas)
        return ganadas/juegos

print(evaluar_fitness(10))

it = 0
sum = 0
for tiempo in tiempos:
    sum += tiempo
    it += 1

print(f"Tiempo promedio de {sum/it}")