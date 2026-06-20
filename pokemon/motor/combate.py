from pokemon.models.move import Move
import random
import math
from pokemon.models.pokemon import Pokemon
from pokemon.motor.acciones import calcular_daño, establecer_vida, obtener_multiplicador_tipos
from pokemon.motor.estado_juego import EstadoJuego
from pokemon.enums.damage_class import DamageClass
from pokemon.motor.bus_de_eventos import bus_de_eventos_global

class Combate:
    estado_del_equipo = None

    def __init__(self, estado_juego):
        self.estado_del_equipo = estado_juego
        self.es_simulado = estado_juego.esSimulado
    
    def _emit(self, text):
        print(text)
        bus_de_eventos_global.disparar("MENSAJE_COMBATE", text)

    def elegir_intercambio(self, elegibles):
        for i, (idx_real, pokemon) in enumerate(elegibles):
            print(f"{i + 1}. {pokemon.name} (HP: {pokemon.hp})")

        while True:
            try:
                seleccion = int(input("Elige el número de la opción: ")) - 1
                if 0 <= seleccion < len(elegibles):
                    return elegibles[seleccion][0] 
                else:
                    print("Esa opción no está en la lista.")
            except ValueError:
                print("Escribe un número por favor")

    #La UI debe disparar un evento que envie pokemonP1, accionelegidaP1, pokemonP2, P2accionElegida. Envia la referencia de la funcion o el nombre del movimiento
    def ordenar_acciones(self, pokemonP1, accionElegidaP1, pokemonP2, accionElegidaP2):
        #Si hay intercambios??
        if not isinstance(accionElegidaP1, Move): return [0, 1]
        if not isinstance(accionElegidaP2, Move): return [1, 0]

        #Si hay prioridad?
        if accionElegidaP1.priority > accionElegidaP2.priority:
            return [0, 1]
        
        elif accionElegidaP1.priority < accionElegidaP2.priority:
            return [1, 0]
        
        #Por velocidad?

        if pokemonP1.speed > pokemonP2.speed:
            return [0, 1]
        
        elif pokemonP1.speed < pokemonP2.speed:
            return [1, 0]

        #Nada que los diferencie?
        else:
            rng = math.ceil(random.random()*2)
            if rng == 1: return [0, 1]
            else: return [1, 0]

    def resolver_intercambio_ui(self, ctx):
        if self.estado_del_equipo.conteo_vivos(ctx["id_rival"]) == 0:
            return 
        
        elegibles = self.estado_del_equipo.pokemonesElegibles(ctx["id_rival"])

        if ctx["tipo_rival"] == 1: # Humano
            idx_nuevo = bus_de_eventos_global.disparar("ELEGIR_INTERCAMBIO", elegibles, ctx["id_rival"])
        else: # IA
            idx_nuevo = random.choice(elegibles)[0]
            self.estado_del_equipo.intercambiarPokemon(idx_nuevo, ctx["id_rival"])
        
       

    def ejecutar_turno_ui(self, pokemonP1, accionElegidaP1, pokemonP2, accionElegidaP2, tipoP1, tipoP2):
        orden = self.ordenar_acciones(pokemonP1, accionElegidaP1, pokemonP2, accionElegidaP2)

        contexto = {
            0: {"id_player": 1, "id_rival": 2, "accion": accionElegidaP1, "tipo_rival": tipoP2},
            1: {"id_player": 2, "id_rival": 1, "accion": accionElegidaP2, "tipo_rival": tipoP1}
        }
        pokemonDesvanecido = False

        for indice in orden:

            ctx = contexto[indice]           
            #Si el pokemon se desvaneció por el turno anterior
            if pokemonDesvanecido: 
                return

            atacante = self.estado_del_equipo.pokemonActivoP1 if ctx["id_player"] == 1 else self.estado_del_equipo.pokemonActivoP2
            defensor = self.estado_del_equipo.pokemonActivoP2 if ctx["id_player"] == 1 else self.estado_del_equipo.pokemonActivoP1

            accion = ctx["accion"]

            #Si es un movimiento se evalua si es de status o un movimiento que hace daño. De otra manera el movimiento sería para intercambiar pokemon
            if isinstance(accion, Move):
                accion.current_power_points -= 1

                if accion.damage_class != DamageClass.STATUS:
                    
                    daño = calcular_daño(atacante, defensor, accion)
                    if not self.es_simulado:
                        self._emit(f"¡{atacante.name} usa {accion.name}!")
                        self._emit(f"Hace {round(daño, 2)} de daño a {defensor.name}")
                    
                    nueva_vida_rival = establecer_vida(defensor, daño)

                    if nueva_vida_rival <= 0 :
                        if not self.es_simulado:
                            self._emit(f"¡{defensor.name} se ha debilitado!")
                        pokemonDesvanecido = True

                        self.resolver_intercambio_ui(ctx)

                    #Si el rival se queda sin pokemones tras el turno ya no hace falta seguir ejecutando movimiento
                    if self.estado_del_equipo.conteo_vivos(ctx["id_rival"]) == 0:
                        return   
                                
                else:

                    self.resolver_movimiento_de_status(accion, atacante, defensor)

                    if not self.es_simulado:
                        self._emit(f"¡{atacante.name} usó {accion.name}, que es un estado!")
            
            else:
                if not self.es_simulado:
                    self._emit(f"El entrenador del Equipo {ctx['id_player']} retira a su Pokémon...")

                elegibles = self.estado_del_equipo.pokemonesElegibles(ctx["id_player"])
                tipo_player = tipoP1 if ctx["id_player"] == 1 else tipoP2
                
                if tipo_player == 1:
                    self.estado_del_equipo.intercambiarPokemon(ctx["accion"], ctx["id_player"])

                else:
                    idx_nuevo = random.choice(elegibles)[0]
                    self.estado_del_equipo.intercambiarPokemon(idx_nuevo, ctx["id_player"])
                
                

    def resolver_intercambio(self, ctx):
        if self.estado_del_equipo.conteo_vivos(ctx["id_rival"]) == 0:
            return 
        
        elegibles = self.estado_del_equipo.pokemonesElegibles(ctx["id_rival"])

        if ctx["tipo_rival"] == 1: # Humano
            idx_nuevo = self.elegir_intercambio(elegibles)
        else: # IA
            idx_nuevo = random.choice(elegibles)[0]
        
        self.estado_del_equipo.intercambiarPokemon(idx_nuevo, ctx["id_rival"])
    
    def ejecutar_turno(self, pokemonP1, accionElegidaP1, pokemonP2, accionElegidaP2, tipoP1, tipoP2):
        orden = self.ordenar_acciones(pokemonP1, accionElegidaP1, pokemonP2, accionElegidaP2)

        contexto = {
            0: {"id_player": 1, "id_rival": 2, "accion": accionElegidaP1, "tipo_rival": tipoP2},
            1: {"id_player": 2, "id_rival": 1, "accion": accionElegidaP2, "tipo_rival": tipoP1}
        }
        pokemonDesvanecido = False

        for indice in orden:

            ctx = contexto[indice]          
            #Si el pokemon se desvaneció por el turno anterior
            if pokemonDesvanecido: 
                return

            atacante = self.estado_del_equipo.pokemonActivoP1 if ctx["id_player"] == 1 else self.estado_del_equipo.pokemonActivoP2
            defensor = self.estado_del_equipo.pokemonActivoP2 if ctx["id_player"] == 1 else self.estado_del_equipo.pokemonActivoP1

            accion = ctx["accion"]

            #Si es un movimiento se evalua si es de status o un movimiento que hace daño. De otra manera el movimiento sería para intercambiar pokemon
            if isinstance(accion, Move):
                accion.current_power_points -= 1

                if accion.damage_class != DamageClass.STATUS:
                    
                    daño = calcular_daño(atacante, defensor, accion)
                    self._emit(f"¡{atacante.name} usa {accion.name}!")
                    self._emit(f"Hace {round(daño, 2)} de daño a {defensor.name}")
                    
                    nueva_vida_rival = establecer_vida(defensor, daño)

                    if nueva_vida_rival <= 0 :
                        self._emit(f"¡{defensor.name} se ha debilitado!")
                        pokemonDesvanecido = True

                        self.resolver_intercambio(ctx, atacante, defensor)

                    #Si el rival se queda sin pokemones tras el turno ya no hace falta seguir ejecutando movimiento
                    if self.estado_del_equipo.conteo_vivos(ctx["id_rival"]) == 0:
                        return   
                                
                else:
                    self._emit(f"¡{atacante.name} usó {accion.name}, que es un estado!")
            
            else:
                self._emit(f"El entrenador del Equipo {ctx['id_player']} retira a su Pokémon...")
                elegibles = self.estado_del_equipo.pokemonesElegibles(ctx["id_player"])
                tipo_player = tipoP1 if ctx["id_player"] == 1 else tipoP2
                
                if tipo_player == 1:
                    idx_nuevo = self.elegir_intercambio(elegibles)
                else:
                    idx_nuevo = random.choice(elegibles)[0]
                
                self.estado_del_equipo.intercambiarPokemon(idx_nuevo, ctx["id_player"])
    
    def verificar_ganador(self):
        estado_juego = None
        if isinstance(self.estado_del_equipo, EstadoJuego):
            estado_juego = self.estado_del_equipo
        
        if estado_juego.conteo_vivos(2) == 0:
            self._emit("¡El Jugador 1 gana!")
            return True
        elif estado_juego.conteo_vivos(1) == 0:
            self._emit("¡El Jugador 2 gana!")
            return True

        return False
    
    def resolver_movimiento_de_status(movimiento: Move, atacante: Pokemon, defensor: Pokemon):
        """
        En base al nombre del movimiento ejecuta la acción que se espera
        """

        movimiento_nombre = movimiento.name

        match(movimiento_nombre):
            case "curse":
                
                ## Aquí poner la lógica del movimiento curse

                print("Curse")
            #Agregar para los demás casos
            
            case _:
                print("Este movimiento no está soportado")