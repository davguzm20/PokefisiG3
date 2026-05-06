import copy
import random
from pokemon.motor.combate import Combate
from pokemon.motor.estado_juego import EstadoJuego
from pokemon.motor.bus_de_eventos import bus_de_eventos_global
##IA
from pokemon.agenteP.agenteP import AgenteP, elegirMovimientoAleatorio, movimiento_en_base_a_mayor_daño, heuristica_difHP

#Instancien una única vez esta clase
class IA:
    def __init__(self, tipo_IA, num_jugador):
        self.nivel_IA = tipo_IA
        self.num_jugador = num_jugador
    
    def elegir_movimiento_ia(self, estado):
        if self.nivel_IA == 2:
            if self.num_jugador == 1:
                return heuristica_difHP(estado, estado.pokemonActivoP1.moves, ia_side=1)
            return heuristica_difHP(estado, estado.pokemonActivoP2.moves, ia_side=2)
        return elegirMovimientoAleatorio(estado.pokemonActivoP1.moves if self.num_jugador == 1 else estado.pokemonActivoP2.moves)

class Juego:
    def __init__(self):
        self.jugador1 = 0
        self.jugador2 = 0
        self.estado = EstadoJuego()
        self.combate = None
        self.num_pokemones = 3

    def iniciar_en_bus_eventos(self):
        bus_de_eventos_global.escuchar("INICIAR_TURNO", self.iniciar_turno)
        bus_de_eventos_global.escuchar("ESTABLECER_NUM_POKEMONES", self.set_num_pokemones)
        bus_de_eventos_global.escuchar("ESTABLECER_JUGADOR_COMO_IA", self.configurar_jugador_como_IA)
        bus_de_eventos_global.escuchar("ESTABLECER_JUGADOR_COMO_HUMANO", self.configurar_jugador_como_humano)
        bus_de_eventos_global.escuchar("INICIALIZAR_COMBATE", self.inicializar_combate)

    #Número de pokemones que tendrán los jugadores
    def set_num_pokemones(self, num_pokemones):
        self.num_pokemones = num_pokemones
    
    # Configura un jugador a IA o Humano: num_jugador se refiere a si es Jugador 1 o Jugador 2. 
    #tipo_jugador se refiere a si es una IA: 2 para IA, 1 para humano
    #nivel_ia se maneja como 1: (movimiento aleatorio) 2: (heurística de diferencia de HP) 3: Minimax
    def configurar_jugador_como_IA(self, num_jugador, nivel_ia, pokemones_disponibles):
        equipo = []

        for i in range(self.num_pokemones):
            p_sel = copy.deepcopy(random.choice(pokemones_disponibles))
            random.shuffle(p_sel.moves)
            p_sel.moves = p_sel.moves[:4]
            equipo.append(p_sel)
        
            print(f"IA {num_jugador} eligió a {p_sel.name} con movimientos aleatorios.")
        print(f"Nivel de IA seleccionado: {nivel_ia}")

        self.estado.setEquipo(equipo, num_jugador)
        if num_jugador == 1:
            self.jugador1 = IA(nivel_ia, num_jugador)
        else:
            self.jugador2 = IA(nivel_ia, num_jugador)

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
        accion_P1, accion_P2 = self.generar_acciones_IA()

        if accionP1 is not None: accion_P1 = accionP1
        if accionP2 is not None: accion_P2 = accionP2

        tipo_P1 = 1
        tipo_P2 = 1
        if isinstance(self.jugador1,IA): tipo_P1 = 2
        if isinstance(self.jugador2,IA): tipo_P2 = 2

        self.combate.ejecutar_turno(self.combate.estado_del_equipo.pokemonActivoP1, accion_P1, self.combate.estado_del_equipo.pokemonActivoP2, accion_P2, tipo_P1, tipo_P2)
        
        bus_de_eventos_global.disparar("TURNO_FINALIZADO", self.combate.estado_del_equipo)

        return self.combate.verificar_ganador()
        
    def generar_acciones_IA(self):
        accionP1 = None
        accionP2 = None

        if isinstance(self.jugador1,IA):
            accionP1 = self.jugador1.elegir_movimiento_ia(self.combate.estado_del_equipo)

        if isinstance(self.jugador2,IA):
            accionP2 = self.jugador2.elegir_movimiento_ia(self.combate.estado_del_equipo)

        return accionP1, accionP2

        