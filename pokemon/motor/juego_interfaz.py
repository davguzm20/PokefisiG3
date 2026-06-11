import copy
import random
from pokemon.motor.combate import Combate
from pokemon.motor.estado_juego import EstadoJuego
from pokemon.motor.bus_de_eventos import bus_de_eventos_global
##IA
from pokemon.agenteP.agenteP import AgenteP, elegirMovimientoAleatorio, movimiento_en_base_a_mayor_daño, heuristica_difHP, minimax_recursivov2, copiar_estado, NodoV2

import threading
import time

pesos_mock = {
    "hp": 0.3,
    "velocidad": 0.2,
    "tipo": 0.3,
    "vivos": 0.2
}

pesos_optimizados = {
    "hp": 0.65,
    "velocidad": 0.242,
    "tipo": 0.0,
    "vivos": 0.151
}

#Instancien una única vez esta clase
class IA:
    def __init__(self, tipo_IA, num_jugador, profundidad_minimax, pesos = pesos_mock):
        self.nivel_IA = tipo_IA
        self.num_jugador = num_jugador
        self.profundidad_minimax = profundidad_minimax
        self.pesos_heuristicos = pesos
    
    def elegir_movimiento_ia(self, estado):

        if self.nivel_IA == 1:
            return elegirMovimientoAleatorio(estado.pokemonActivoP1.moves if self.num_jugador == 1 else estado.pokemonActivoP2.moves)
        
        if self.nivel_IA == 2:
            if self.num_jugador == 1:
                return heuristica_difHP(estado, estado.pokemonActivoP1.moves, ia_side=1)
            return heuristica_difHP(estado, estado.pokemonActivoP2.moves, ia_side=2)
        
        if self.nivel_IA == 3:
            return self.elegir_movimiento_con_minimax(estado)
                

    def elegir_movimiento_con_minimax(self, estado):
    
        copia_estado = copiar_estado(estado)
        copia_estado.esSimulado = True
        nodo = NodoV2(copia_estado)

        raiz = minimax_recursivov2(nodo, self.profundidad_minimax, self.num_jugador, self.num_jugador, self.pesos_heuristicos)
        
        print("La elección de minimax es:")
        if raiz.hijo_escogido.operador["movimiento"] is not None: 
            print(f'# Usar: {raiz.hijo_escogido.operador["movimiento"].name}')
            return raiz.hijo_escogido.operador["movimiento"]
        
        if raiz.hijo_escogido.operador["intercambio"] is not None:
            print(f'# Intercambiar el pokemon con el de indice: {raiz.hijo_escogido.operador["intercambio"]}')
            return raiz.hijo_escogido.operador["intercambio"]
        

class Acciones:
    def __init__(self):
        self.accionP1 = None
        self.accionP2 = None
        self.acciones_escogidas = False        


class Juego:
    def __init__(self):
        self.jugador1 = 0
        self.jugador2 = 0
        self.estado = EstadoJuego()
        self.combate = None
        self.num_pokemones = 3
        self.pesos_funcionh = None

    def iniciar_en_bus_eventos(self):
        bus_de_eventos_global.escuchar("INICIAR_TURNO", self.iniciar_turno)
        bus_de_eventos_global.escuchar("ESTABLECER_NUM_POKEMONES", self.set_num_pokemones)
        bus_de_eventos_global.escuchar("ESTABLECER_JUGADOR_COMO_IA", self.configurar_jugador_como_IA)
        bus_de_eventos_global.escuchar("ESTABLECER_JUGADOR_COMO_HUMANO", self.configurar_jugador_como_humano)
        bus_de_eventos_global.escuchar("INICIALIZAR_COMBATE", self.inicializar_combate)
        bus_de_eventos_global.escuchar("GENERAR_ACCIONES_IA", self.generar_acciones_IA_thread)

    #Número de pokemones que tendrán los jugadores
    def set_num_pokemones(self, num_pokemones):
        self.num_pokemones = num_pokemones
    
    # Configura un jugador a IA o Humano: num_jugador se refiere a si es Jugador 1 o Jugador 2. 
    #tipo_jugador se refiere a si es una IA: 2 para IA, 1 para humano
    #nivel_ia se maneja como 1: (movimiento aleatorio) 2: (heurística de diferencia de HP) 3: Minimax
    def configurar_jugador_como_IA(self, num_jugador, nivel_ia, pokemones_disponibles, profundidad = 4, pesos = pesos_mock):
        equipo = []

        for i in range(self.num_pokemones):
            p_sel = copy.deepcopy(random.choice(pokemones_disponibles))
            random.shuffle(p_sel.moves)

            cuenta_movimientos_de_daño = 0
            was_index = 0

            movimientos = []
            for i in range(0, len(p_sel.moves)):
                if p_sel.moves[i].power is not None:
                    
                    movimientos.append(p_sel.moves[i])
                    cuenta_movimientos_de_daño += 1

                    if cuenta_movimientos_de_daño == 2:
                        was_index = i
                        break
            
            if was_index+2 >= len(p_sel.moves):
                p_sel.moves = movimientos + p_sel.moves[was_index-3:was_index-1]
            else:
                p_sel.moves = movimientos + p_sel.moves[was_index+1:was_index+3]

            equipo.append(p_sel)
        
            print(f"IA {num_jugador} eligió a {p_sel.name} con movimientos aleatorios.")
        print(f"Nivel de IA seleccionado: {nivel_ia}")

        self.estado.setEquipo(equipo, num_jugador)
        if num_jugador == 1:
            self.jugador1 = IA(nivel_ia, num_jugador, profundidad_minimax = profundidad, pesos= pesos)
        else:
            self.jugador2 = IA(nivel_ia, num_jugador, profundidad_minimax = profundidad, pesos= pesos)

    def configurar_jugador_como_IA_con_equipo(self, num_jugador, nivel_ia, equipo, profundidad = 4, pesos = pesos_mock):

        self.estado.setEquipo(equipo, num_jugador)
        if num_jugador == 1:
            self.jugador1 = IA(nivel_ia, num_jugador, profundidad_minimax = profundidad, pesos= pesos)
        else:
            self.jugador2 = IA(nivel_ia, num_jugador, profundidad_minimax = profundidad, pesos= pesos)

    def configurar_jugador_como_humano(self, num_jugador, equipo_elegido):
        self.estado.setEquipo(equipo_elegido, num_jugador)
    
    #Usar cuando ambos equipos estén ya armados
    def inicializar_combate(self):
        #Sería buena práctica aplicar consistencia aquí
        self.combate = Combate(self.estado)
        
    #Devuelve la instancia para poder usar sus métodos. Visiten la clase combate. Deberían estar usando los métodos: ejecutar_turno y verificar_ganador en la UI
    def get_combate(self):
        if self.combate == None:
            raise Exception("Falta iniciar el combate")
        return self.combate
    

    #La UI debe identificar si se espera la entrada de un jugador durante el combate. Cuando no se espere más entradas se asume que inicia el combate
    #La UI recibirá si ya existe un ganador
    def iniciar_turno(self, accionP1 = None, accionP2 = None):

        if accionP1 is not None: accion_P1 = accionP1
        if accionP2 is not None: accion_P2 = accionP2

        tipo_P1 = 1
        tipo_P2 = 1
        if isinstance(self.jugador1,IA): tipo_P1 = 2
        if isinstance(self.jugador2,IA): tipo_P2 = 2

        self.combate.ejecutar_turno_ui(self.combate.estado_del_equipo.pokemonActivoP1, accion_P1, self.combate.estado_del_equipo.pokemonActivoP2, accion_P2, tipo_P1, tipo_P2)
        
        bus_de_eventos_global.disparar("TURNO_FINALIZADO", self.combate.estado_del_equipo)

        return self.combate.verificar_ganador()
    
    #============================================================================================
    def iniciar_turno_desacoplado(self, accionP1 = None, accionP2 = None):

        if accionP1 is not None: accion_P1 = accionP1
        if accionP2 is not None: accion_P2 = accionP2

        tipo_P1 = 1
        tipo_P2 = 1
        if isinstance(self.jugador1,IA): tipo_P1 = 2
        if isinstance(self.jugador2,IA): tipo_P2 = 2

        self.combate.ejecutar_turno_ui(self.combate.estado_del_equipo.pokemonActivoP1, accion_P1, self.combate.estado_del_equipo.pokemonActivoP2, accion_P2, tipo_P1, tipo_P2)
        
        #El combate habrá modificado el estado. Solo lo extraemos y lo copiamos??

        return 

    def generar_acciones_IA_thread(self, acciones, ref):
        bus_de_eventos_global.disparar("MENSAJE_COMBATE", "IA pensando...")
        x = threading.Thread(target=self.generar_acciones_IA_asincrono, args=(acciones, ref))
        x.start()
    
    def generar_acciones_IA_asincrono(self, acciones, ref):

        if not isinstance(acciones, Acciones):
            return
        
        if isinstance(self.jugador1,IA):
            accionP1 = self.jugador1.elegir_movimiento_ia(copiar_estado(self.combate.estado_del_equipo))
            acciones.accionP1 = accionP1

        if isinstance(self.jugador2,IA):
            accionP2 = self.jugador2.elegir_movimiento_ia(copiar_estado(self.combate.estado_del_equipo))
            acciones.accionP2 = accionP2

        acciones.acciones_escogidas = True
        ref.generando_acciones = False

    def generar_acciones_IA(self):
        accionP1 = None
        accionP2 = None

        if isinstance(self.jugador1,IA):
            accionP1 = self.jugador1.elegir_movimiento_ia(self.combate.estado_del_equipo)

        if isinstance(self.jugador2,IA):
            accionP2 = self.jugador2.elegir_movimiento_ia(self.combate.estado_del_equipo)

        return accionP1, accionP2

        