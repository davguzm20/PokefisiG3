import random
import math
from pokemon.motor.estado_juego import EstadoJuego
from pokemon.motor.acciones import calcular_daño

#Esta es una idea sin fundamento por el momento, pero si se puede usar luego entonces genial

#Usarlo para recordar los pokemones y sus movimientos que ya hayan sido usados del oponente
class AgenteP:

    def __init__(self):
        self.conocimiento = {
        }

    #Enviar el nombre del pokemon, no el objeto
    def recordarPokemon(self, pokemonUsado):
        if pokemonUsado not in self.conocimiento:
            self.conocimiento[pokemonUsado] = []
    
    #Enviar el objeto movimiento
    def recordarMovimiento(self, pokemonOponente, movimiento):
        if movimiento not in self.conocimiento[pokemonOponente]:
            self.conocimiento[pokemonOponente].append(movimiento)

#=============== Las siguientes funciones pueden usarse independientemente para los agentes de diferentes niveles. Podrían ser operadores para pasar de un estado a otro

#Este sería el agente de nivel 0
def elegirMovimientoAleatorio(movimientos):
    return movimientos[math.ceil(random.random()*len(movimientos)-1)]
 
#Devuelve daño causado y el objeto movimiento (en ese orden)
def movimiento_en_base_a_mayor_daño(pokemonActivoP1, pokemonActivoP2, movimientos):
    valMax = -999
    actualMov = [valMax, None]
    for movimiento in movimientos:
        valAct = calcular_daño(pokemonActivoP2, pokemonActivoP1, movimiento)
        if valAct > valMax:
            valMax = valAct
            actualMov = [valMax, movimiento]

    return actualMov

#Ej. Agente de nivel 1 con heuristica de daño. 
#La IA elige retirarse dada *una condicion aun mejorable* o atacar con el mayor daño que puede hacer
def movimiento_en_base_a_difHP_generada(estado_juego, movimientos, agenteP):
    if isinstance(agenteP, AgenteP) and isinstance(estado_juego, EstadoJuego):
        movimiento_mas_fuerte_IA = movimiento_en_base_a_mayor_daño(estado_juego.pokemonActivoP1, estado_juego.pokemonActivoP2, movimientos)
        movimiento_mas_fuerte_Player = movimiento_en_base_a_mayor_daño(estado_juego.pokemonActivoP2, estado_juego.pokemonActivoP1, agenteP.conocimiento[estado_juego.pokemonActivoP1])

        hpRestante = estado_juego.pokemonActivoP2.hp - movimiento_mas_fuerte_Player[0]

        if hpRestante < estado_juego.pokemonActivoP1.hp - movimiento_mas_fuerte_IA[0] and hpRestante <= 0:
            estado_juego.intercambiarPokemon(1,2)
        
    return movimiento_mas_fuerte_IA[1]

#Otra versión con diferencia de HP
def movimiento_en_base_a_difHP(estado_juego, movimientos, agenteP):
    if isinstance(agenteP, AgenteP) and isinstance(estado_juego, EstadoJuego):
        hpPlayer = estado_juego.pokemonActivoP1.hp
        hpIA = estado_juego.pokemonActivoP2.hp
        difHP = hpIA - hpPlayer

        #Falta agregar código


    return movimientos[1]

