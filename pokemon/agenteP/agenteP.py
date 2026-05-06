import random
import math
from pokemon.motor.estado_juego import EstadoJuego
from pokemon.motor.acciones import calcular_daño, obtener_multiplicador_tipos

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

#-----------------------------------------------------------------------------------


#Niv 1
#Ajuste para eleccion random en base a la lista de movimientos
def elegirMovimientoAleatorio(movimientos):
    return random.choice(movimientos)

#Niv 2
#Heuristica inicial basada en diferencia de HP
#maximizar diferencia a favor de IA

    #Devuelve el pokemon activo de la IA, el pokemon activo del jugador, y sus HP respectivamente
    # dependiendo de qué lado controle la IA.
def _resolver_lados(estado_juego, ia_side):
    
    if ia_side == 2:
        return (
            estado_juego.pokemonActivoP2,
            estado_juego.pokemonActivoP1,
            estado_juego.pokemonActivoP2.hp,
            estado_juego.pokemonActivoP1.hp,
        )

    return (
        estado_juego.pokemonActivoP1,
        estado_juego.pokemonActivoP2,
        estado_juego.pokemonActivoP1.hp,
        estado_juego.pokemonActivoP2.hp,
    )

    #La funcion evalua cada mov en base a:
    # si produce KO, cuánto HP restante deja y cuánto HP tiene la IA en ese momento
    #Retorna el mov con mayor valor heurístico
def heuristica_difHP(estado_juego, movimientos, ia_side=1):

    # Valida que el estado del juego sea válido y que haya movimientos disponibles.
    # Si no, retorna None para evitar errores.
    if not isinstance(estado_juego, EstadoJuego) or not movimientos:
        return None

    # Obtiene los pokémon activos y sus HP según qué lado controle la IA.
    atacante, defensor, hp_ia, hp_player = _resolver_lados(estado_juego, ia_side)
    max_hp = max(hp_ia, hp_player, 1)

    mejor = None
    mejor_valor = -float("inf")

    # Evalúa cada movimiento disponible.
    for movimiento in movimientos:

        # Calcula el daño que infligiría este movimiento y hp del defensortras recibirlo.
        dano_ia = calcular_daño(atacante, defensor, movimiento)
        hp_player_restante = max(0, hp_player - dano_ia)

        # Si el ataque hace KO, es la mejor opción posible, así que le damos un mayor valor.
        if hp_player_restante == 0:
            valor = 2.0 + (hp_ia / max_hp)
        else:
            # Si no hay KO, puntúa la ventaja de vida neta para la IA.
            valor = (hp_ia - hp_player_restante) / max_hp

        # Si el mov tiene valor mayor que el actual, se convierte en el mejor candidato.
        if valor > mejor_valor:
            mejor_valor = valor
            mejor = movimiento

    return mejor

#Inicio de Heuristica avanzada para nivel 3
#funcion base para considerar pesos

def heuristica_avanzada(estado_juego, movimiento, pesos):
    # Normalizar cada componente entre 0 y 1
    if isinstance(estado_juego, EstadoJuego):
        hp_ratio = (estado_juego.pokemonActivoP2.hp - estado_juego.pokemonActivoP1.hp) / max(estado_juego.pokemonActivoP2.hp + estado_juego.pokemonActivoP1.hp, 1)
        velocidad = (estado_juego.pokemonActivoP1.speed - estado_juego.pokemonActivoP2.speed) / max(estado_juego.pokemonActivoP1.speed + estado_juego.pokemonActivoP2.speed, 1)
        ventaja_tipo = obtener_multiplicador_tipos(movimiento, estado_juego.pokemonActivoP1, estado_juego.pokemonActivoP2, )
        pokemons_vivos = estado_juego.conteo_vivos(2) - estado_juego.conteo_vivos(1) / max(len(estado_juego.equipoP1), len(estado_juego.equipoP2), 1)

    return (
        pesos["hp"] * hp_ratio +
        pesos["velocidad"] * velocidad +
        pesos["tipo"] * ventaja_tipo +
        pesos["vivos"] * pokemons_vivos
    )

