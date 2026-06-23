from pokemon.models.move import Move
import random
import math
from pokemon.models.pokemon import Pokemon
from pokemon.motor.acciones import calcular_daño, establecer_vida, obtener_multiplicador_tipos
from pokemon.motor.estado_juego import EstadoJuego
from pokemon.enums.damage_class import DamageClass
from pokemon.enums.effects import Effects
from pokemon.enums.weather import Weather
from pokemon.motor.bus_de_eventos import bus_de_eventos_global

class Combate:
    estado_del_equipo = None

    def __init__(self, estado_juego):
        self.estado_del_equipo: EstadoJuego = estado_juego
        self.es_simulado = estado_juego.esSimulado
        self.hay_intercambioP1 = False
        self.hay_intercambioP2 = False
        self.entorno_activo: Weather = None
        self.entorno_turnos_restantes = 0

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
    def ordenar_acciones(self, pokemonP1: Pokemon, accionElegidaP1, pokemonP2: Pokemon, accionElegidaP2):
        #Si hay intercambios??
        if not isinstance(accionElegidaP1, Move): return [0, 1]
        if not isinstance(accionElegidaP2, Move): return [1, 0]

        #Si hay prioridad?
        if accionElegidaP1.priority > accionElegidaP2.priority:
            return [0, 1]
        
        elif accionElegidaP1.priority < accionElegidaP2.priority:
            return [1, 0]
        
        #Por velocidad?

        if pokemonP1.obtener_stat_efectiva(pokemonP1.speed, "speed") > pokemonP2.obtener_stat_efectiva(pokemonP2.speed, "speed"):
            return [0, 1]
        
        elif pokemonP1.obtener_stat_efectiva(pokemonP1.speed, "speed") < pokemonP2.obtener_stat_efectiva(pokemonP2.speed, "speed"):
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

    def ejecutar_turno_ui(self, pokemonP1, accionElegidaP1: int | Move, pokemonP2, accionElegidaP2: int | Move, tipoP1, tipoP2):
        """
        Función que aplica las consecuencias del comando de lo jugadores y el entorno. Además considera las habilidades y efectos activos en los pokemones.
        La accion elegida puede ser un entero (ejecuta intercambio) o una instancia de Movimiento (ejecuta movimiento).
        \nEl resultado cambia las propiedades del estado por lo que es necesario revisar si el estado devuelto es terminal.
        \nConsiderar que esta función deja pendiente la resolución de intercambios ante debilitamientos.
        """

        orden = self.ordenar_acciones(pokemonP1, accionElegidaP1, pokemonP2, accionElegidaP2)

        contexto = {
            0: {"id_player": 1, "id_rival": 2, "accion": accionElegidaP1, "tipo_rival": tipoP2},
            1: {"id_player": 2, "id_rival": 1, "accion": accionElegidaP2, "tipo_rival": tipoP1}
        }
        pokemon_rival_desvanecido = False

        for indice in orden:
            
            ctx = contexto[indice]           
            #Si el pokemon se desvaneció por el turno anterior
            if pokemon_rival_desvanecido:
                ## Considerando efectos, entornos y habilidades. No olvidar que debería chequearse la consecuencia que tienen sobre este pokemon ========================= !!!!!!!! <===== !!!!!!!! <===== !!!!!!!! <===== !!!!!!!! <=====
                continue

            atacante = self.estado_del_equipo.pokemonActivoP1 if ctx["id_player"] == 1 else self.estado_del_equipo.pokemonActivoP2
            defensor = self.estado_del_equipo.pokemonActivoP2 if ctx["id_player"] == 1 else self.estado_del_equipo.pokemonActivoP1
            atacante.protegido = False
            atacante.puede_atacar = True

            accion = ctx["accion"]
            
            if not isinstance(accion, int): #Verificación para contar adecuadamente los protects
                if accion.name not in ("protect", "detect"): atacante.protects_seguidos = 0
            else:
                atacante.protects_seguidos = 0

            #Si es un movimiento se evalua si es de status o un movimiento que hace daño. De otra manera el movimiento sería para intercambiar pokemon
            if isinstance(accion, Move):
                accion.current_power_points -= 1

                #Revisión de efectos, entornos y habilidades antes del ataque
                self.resolver_efecto_MID(atacante) ### También es posible que hayan habilidades que se ejecuten después de atacar. Pero por el momento no consideremos habilidades
                if not atacante.puede_atacar:
                    continue

                if accion.damage_class != DamageClass.STATUS:
                    
                    if defensor.protegido:
                        self._emit(f"¡{defensor.name} se ha protegido!")
                        continue

                    #Sería mejor si fuera accion.ejecutar()
                    daño = calcular_daño(atacante, defensor, accion)

                    if not self.es_simulado:
                        self._emit(f"¡{atacante.name} usa {accion.name}!")
                        self._emit(f"Hace {round(daño, 2)} de daño a {defensor.name}")
                    
                    vida_previa = defensor.hp
                    nueva_vida_rival = establecer_vida(defensor, daño)
                    atacante.reciente_daño_hecho = vida_previa - nueva_vida_rival #### Añadido para movimientos que roban vida
                    
                    #Si el rival se queda sin pokemones tras el turno ya no hace falta seguir ejecutando movimientos ni intercambios
                    if self.estado_del_equipo.conteo_vivos(ctx["id_rival"]) == 0:
                        if not self.es_simulado:
                            self._emit(f"¡{defensor.name} se ha debilitado!")
                        self.estado_del_equipo.esTerminal = True
                        
                        self.estado_del_equipo.ganaP1 = True if ctx["id_rival"] == 2 else False
                        self.estado_del_equipo.ganaP2 = True if ctx["id_rival"] == 1 else False
                        
                        return   

                    if nueva_vida_rival <= 0 :
                        if not self.es_simulado:
                            self._emit(f"¡{defensor.name} se ha debilitado!")
                        pokemon_rival_desvanecido = True

                        self.hay_intercambioP1 = True if ctx["id_rival"] == 1 else False
                        self.hay_intercambioP2 = True if ctx["id_rival"] == 2 else False                
                else:
 
                    self.resolver_movimiento_de_soporte(accion, atacante, defensor)

                    if not self.es_simulado:
                        self._emit(f"¡{atacante.name} usó {accion.name}, que es un estado!")
            
            else:
                if not self.es_simulado:
                    self._emit(f"El entrenador del Equipo {ctx['id_player']} retira a su Pokémon...")

                self.estado_del_equipo.intercambiarPokemon(ctx["accion"], ctx["id_player"])      

        #Revisión de efectos, entornos y habilidades que tienen consecuencias tardías
        self.resolver_efecto_END(pokemonP1)
        self.resolver_efecto_END(pokemonP2)
        
        if self.estado_del_equipo.esTerminal == True: #Si ya se definio el ganador, las consecuencias de los efectos no deberían impactar en el resultado.
            return
        else:
            if pokemonP1.hp == 0:
                if self.estado_del_equipo.conteo_vivos(1) == 0:
                    self.estado_del_equipo.ganaP2 = True
                    self.estado_del_equipo.esTerminal = True
                else:
                    self.hay_intercambioP1 = True
            if pokemonP2.hp == 0:
                if self.estado_del_equipo.conteo_vivos(2) == 0:
                    self.estado_del_equipo.ganaP1 = True
                    self.estado_del_equipo.esTerminal = True
                else:
                    self.hay_intercambioP2 = True
            
            if self.estado_del_equipo.ganaP2 and self.estado_del_equipo.ganaP1:
                self.estado_del_equipo.ganaP1 = False
                self.estado_del_equipo.ganaP2 = False
                self._emit(f"Es un empate!")
        
    def generar_intercambio_aleatorio(self, equipo: int):
        
        if self.estado_del_equipo.esTerminal:
            print("Este estado es terminal. No se generó un intercambio")
            return

        elegibles = self.estado_del_equipo.pokemonesElegibles(equipo)
        return random.choice(elegibles)[0]

    def ejecutar_intercambio_por_debilitamiento(self, index_relevo, equipo):
        """
        Recibe un indice de relevo para un equipo y solo se aplica si el combate sabe que es necesario hacer un intercambio.  
        \nUtilizar esta función tras terminar un turno y si el turno no es terminal.
        """
        if equipo == 1 and self.hay_intercambioP1:
            self.estado_del_equipo.intercambiarPokemon(index_relevo, 1)
            self.hay_intercambioP1 = False
        if equipo == 2 and self.hay_intercambioP2:
            self.estado_del_equipo.intercambiarPokemon(index_relevo, 2)
            self.hay_intercambioP2 = False

    def ejecutar_intercambios_por_debilitamiento(self, index_relevo_P1, index_relevo_P2):
        """
        Recibe los indices de relevo por equipo y solo se aplica si el combate sabe que es necesario hacer un intercambio.  
        \nUtilizar esta función tras terminar un turno y si el turno no es terminal.
        """

        if self.hay_intercambioP1:
            self.estado_del_equipo.intercambiarPokemon(index_relevo_P1, 1)
            self.hay_intercambioP1 = False
        
        if self.hay_intercambioP2:
            self.estado_del_equipo.intercambiarPokemon(index_relevo_P2, 2)
            self.hay_intercambioP2 = False
                 

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
        pokemon_rival_desvanecido = False

        for indice in orden:

            ctx = contexto[indice]          
            #Si el pokemon se desvaneció por el turno anterior
            if pokemon_rival_desvanecido: 
                return

            atacante = self.estado_del_equipo.pokemonActivoP1 if ctx["id_player"] == 1 else self.estado_del_equipo.pokemonActivoP2
            defensor = self.estado_del_equipo.pokemonActivoP2 if ctx["id_player"] == 1 else self.estado_del_equipo.pokemonActivoP1

            accion = ctx["accion"]

            #Si es un movimiento se evalua si es de status o un movimiento que hace daño. De otra manera el movimiento sería para intercambiar pokemon
            if isinstance(accion, Move):
                accion.current_power_points -= 1

                if accion.damage_class != DamageClass.STATUS:
                    
                    daño = calcular_daño(atacante, defensor, accion)
                    vida_previa = defensor.hp #### Añadido

                    self._emit(f"¡{atacante.name} usa {accion.name}!")
                    self._emit(f"Hace {round(daño, 2)} de daño a {defensor.name}")
                    
                    nueva_vida_rival = establecer_vida(defensor, daño)

                    atacante.reciente_daño_hecho = vida_previa - nueva_vida_rival #### Añadido
                    
                    self.resolver_movimiento_after_exec(accion, atacante)

                    if nueva_vida_rival <= 0 :
                        self._emit(f"¡{defensor.name} se ha debilitado!")
                        pokemon_rival_desvanecido = True

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
    
    def resolver_movimiento_de_soporte(self, movimiento: Move, atacante: Pokemon, defensor: Pokemon):
        """
        En base al nombre del movimiento ejecuta la acción que se espera
        """

        movimiento_nombre = movimiento.name

        match(movimiento_nombre):

            case "tail-whip":
                defensor.aplicar_buff_debuff("defense", -1)
                if not self.es_simulado: self._emit(f"¡La Defensa de {defensor.name} bajó!")

            case "screech":
                defensor.aplicar_buff_debuff("defense", -2)
                if not self.es_simulado: self._emit(f"¡La Defensa de {defensor.name} bajó mucho!")

            case "charm":
                defensor.aplicar_buff_debuff("attack", -2)
                if not self.es_simulado: self._emit(f"¡El Ataque de {defensor.name} bajó mucho!")

            case "fake-tears":
                defensor.aplicar_buff_debuff("special_defense", -2)
                if not self.es_simulado: self._emit(f"¡La Defensa Especial de {defensor.name} bajó mucho!")

            case "captivate":
                defensor.aplicar_buff_debuff("special_attack", -2)
                if not self.es_simulado: self._emit(f"¡El Ataque Especial de {defensor.name} bajó mucho!")

            case "confide":
                defensor.aplicar_buff_debuff("special_attack", -1)
                if not self.es_simulado: self._emit(f"¡El Ataque Especial de {defensor.name} bajó!")

            case "eerie-impulse":
                defensor.aplicar_buff_debuff("special_attack", -2)
                if not self.es_simulado: self._emit(f"¡El Ataque Especial de {defensor.name} bajó mucho!")

            case "flash":
                defensor.aplicar_buff_debuff("accuracy", -1)
                if not self.es_simulado: self._emit(f"¡La Precisión de {defensor.name} bajó!")

            case "thunder-wave":
                if defensor.efecto is None:
                    defensor.efecto = Effects.PARALYSIS
                    if not self.es_simulado:
                        self._emit(f"¡{defensor.name} ha quedado paralizado!")
                elif not self.es_simulado:
                    self._emit(f"¡{defensor.name} ya tiene un problema de estado!")

            case "sleep-powder":
                if defensor.efecto is None:
                    defensor.efecto = Effects.SLEEP
                    defensor.turnos_restantes_estado = random.randint(1, 3)
                    defensor.puede_atacar = False
                    if not self.es_simulado:
                        self._emit(f"¡{defensor.name} se ha quedado dormido!")
                elif not self.es_simulado:
                    self._emit(f"¡{defensor.name} ya tiene un problema de estado!")

            case "confuse-ray" | "sweet-kiss":
                if defensor.efecto is None:
                    defensor.efecto = Effects.CONFUSION
                    defensor.turnos_restantes_estado = random.randint(2, 5)
                    if not self.es_simulado:
                        self._emit(f"¡{defensor.name} se ha confundido!")
                elif not self.es_simulado:
                    self._emit(f"¡{defensor.name} ya tiene un problema de estado!")

            case "swagger":
                defensor.aplicar_buff_debuff("attack", 2)
                if not self.es_simulado:
                    self._emit(f"¡El Ataque de {defensor.name} subió mucho!")
                if defensor.efecto is None:
                    defensor.efecto = Effects.CONFUSION
                    defensor.turnos_restantes_estado = random.randint(2, 5)
                    if not self.es_simulado:
                        self._emit(f"¡{defensor.name} se ha confundido!")

            case "attract":
                if defensor.efecto is None:
                    defensor.efecto = Effects.ATTRACT
                    if not self.es_simulado:
                        self._emit(f"¡{defensor.name} se ha enamorado!")
                elif not self.es_simulado:
                    self._emit(f"¡{defensor.name} ya tiene un problema de estado!")

            case "toxic":
                if defensor.efecto is None:
                    defensor.efecto = Effects.TOXIC
                    defensor.multiplicador_toxico = 1
                    if not self.es_simulado:
                        self._emit(f"¡{defensor.name} ha sido gravemente envenenado!")
                elif not self.es_simulado:
                    self._emit(f"¡{defensor.name} ya tiene un problema de estado!")
            case "dragon-dance":
                atacante.aplicar_buff_debuff("attack", 1)
                atacante.aplicar_buff_debuff("speed", 1)
                if not self.es_simulado: 
                    print(f"El ataque de {atacante.name} aumentó")
                    print(f"La velocidad de {atacante.name} aumentó")

            case "swords-dance":
                atacante.aplicar_buff_debuff("attack", 2)
                if not self.es_simulado: print(f"El ataque de {atacante.name} subió drasticamente")

            case "amnesia":
                atacante.aplicar_buff_debuff("special_defense", 2)
                if not self.es_simulado: print(f"La defensa especial de {atacante.name} subió drasticamente")
            
            case "barrier":
                atacante.aplicar_buff_debuff("defense", 2)
                if not self.es_simulado: print(f"La defensa de {atacante.name} subió drasticamente")

            case "charge":
                atacante.aplicar_buff_debuff("special_defense", 1)
                if not self.es_simulado: print(f"La defensa especial de {atacante.name} aumentó")
            
            case "double-team":
                atacante.aplicar_buff_debuff("evasion", 1)
                if not self.es_simulado: print(f"La evasión de {atacante.name} aumentó")

            case "growl":
                defensor.aplicar_buff_debuff("attack", -1)
                if not self.es_simulado: self._emit(f"¡El Ataque de {defensor.name} bajó!")

            case "protect" | "detect":
                rn = random.random()
                prob_fail = atacante.protects_seguidos * 1/3

                if rn > prob_fail:
                    atacante.protects_seguidos += 1
                    atacante.protegido = True
                else:
                    atacante.protects_seguidos = 0
                    atacante.protegido = False

            case "wish":
                atacante.vida_pendiente_wish = atacante.max_hp // 2

            case "synthesis":
                match(self.entorno_activo):
                    case Weather.SUNNY:
                        atacante.hp = min(atacante.max_hp, atacante.hp + round(atacante.max_hp*2/3,2))
                    
                    case Weather.SANDSTORM | Weather.HAIL | Weather.RAIN:
                        atacante.hp = min(atacante.max_hp, atacante.hp + atacante.max_hp/4)

                    case _:
                        atacante.hp = min(atacante.max_hp, atacante.hp + atacante.max_hp/2)

                    
            
            case "aqua-ring":
                atacante.aqua_ring_activo = True
            
            case "rest":
                atacante.hp = atacante.max_hp
                atacante.efecto = Effects.SLEEP
                atacante.turnos_restantes_estado = 2
                atacante.multiplicador_toxico = 1
            
            case "heal-pulse":
                defensor.hp = min(defensor.max_hp, defensor.hp + defensor.max_hp/2)
            
            case "refresh":
                atacante.efecto = None
                atacante.multiplicador_toxico = 1

            case _:
                #print(f"El movimiento {movimiento_nombre} no está soportado")
                return

    def resolver_efecto_MID(self, afectado: Pokemon):
        """
        En base al nombre del efecto se ejecuta consecuencias sobre el afectado justo antes de atacar
        """

        efecto_nombre = afectado.efecto

        match(efecto_nombre):
            case Effects.SLEEP:
                afectado.turnos_restantes_estado -= 1

                if afectado.turnos_restantes_estado == 0:
                    afectado.efecto = None
                    afectado.puede_atacar = True
                else:
                    if not self.es_simulado: print(f"{afectado.name} Está durmiendo y no puede atacar")
                    afectado.puede_atacar = False

            #Agregar para los demás casos
            case Effects.CONFUSION:
                afectado.turnos_restantes_estado -= 1

                if afectado.turnos_restantes_estado == 0:
                    if not self.es_simulado: print(f"{afectado.name} salió de la confusión")
                    afectado.efecto = None
                    afectado.puede_atacar = True
                else:
                    rn = random.random()
                    if rn > 1/3:
                        afectado.puede_atacar = False
                        daño_confusion = round(afectado.max_hp/3, 2)
                        establecer_vida(afectado, daño_confusion)

                        if not self.es_simulado: print(f"{afectado.name} Está confundido y se hace daño a sí mismo")
            
            case Effects.PARALYSIS:
                rn = random.random()
                if rn > 0.125:
                    afectado.puede_atacar = False
                    if not self.es_simulado: print(f"{afectado.name} Está paralizado y no puede atacar")
                    
            case Effects.ATTRACT:
                rn = random.random()
                if rn < 0.5:
                    afectado.puede_atacar = False
                    if not self.es_simulado: print(f"{afectado.name} está enamorado y no puede atacar")

            case _:
                #print(f"El efecto: {efecto_nombre} no está soportado")
                return

    def resolver_efecto_END(self, afectado: Pokemon):
        """
        En base al nombre del efecto se ejecuta consecuencias sobre el afectado antes de finalizar el turno
        """

        if afectado.hp == 0: return

        if afectado.aqua_ring_activo:
            vida_recuperada = round(afectado.max_hp/16,2)
            establecer_vida(afectado, -vida_recuperada)

        if afectado.vida_pendiente_wish > 0:
            establecer_vida(afectado, -afectado.vida_pendiente_wish)
            afectado.vida_pendiente_wish = 0

        efecto_nombre = afectado.efecto

        match(efecto_nombre):
            case Effects.POISON:
                daño_veneno = round(afectado.max_hp/8, 2)
                establecer_vida(afectado, daño_veneno)
                if not self.es_simulado: print(f"{afectado.name} Recibió daño por envenenamiento")
                #Falta algo que actualize la vida en la UI

            case Effects.TOXIC:
                daño_veneno = round(afectado.max_hp/16, 2)
                daño_veneno = daño_veneno * afectado.multiplicador_toxico
                establecer_vida(afectado, daño_veneno)
                afectado.multiplicador_toxico += 1
                if not self.es_simulado: print(f"{afectado.name} Recibió daño por envenenamiento")

            case _:
                #print(f"El efecto: {efecto_nombre} no está soportado")
                return
            
    def resolver_movimiento_after_exec(self, movimiento: Move, atacante:Pokemon):

        nombre_movimiento = movimiento.name

        match(nombre_movimiento):
            case "absorb" | "draining-kiss":
                if atacante.reciente_daño_hecho == 0: return

                vida_robada = atacante.reciente_daño_hecho/2
                if not self.es_simulado: print(f"{atacante.name} Recuperó algo de vida")
                establecer_vida(atacante, -vida_robada)

            