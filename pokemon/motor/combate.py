from pokemon.models.move import Move
import random
import math
from pokemon.models.pokemon import Pokemon
from pokemon.motor.acciones import calcular_daño, establecer_vida, obtener_multiplicador_tipos
from pokemon.motor.estado_juego import EstadoJuego
from pokemon.enums.damage_class import DamageClass
from pokemon.enums.effects import Effects
from pokemon.enums.weather import Weather
from pokemon.enums.pokemon_type import PokemonType
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

    def _modificar_stat(self, pokemon: Pokemon, stat: str, cantidad: int) -> bool:
        """
        Modifica un modificador de estadística entre -6 y +6 de forma segura.
        Maneja los límites superiores e inferiores emitiendo los comentarios oficiales.
        """
        stat_nombres_es = {
            "attack": "Ataque",
            "defense": "Defensa",
            "special_attack": "Ataque Especial",
            "special_defense": "Defensa Especial",
            "speed": "Velocidad",
            "accuracy": "Precisión",
            "evasion": "Evasión"
        }
        
        nombre_stat = stat_nombres_es.get(stat, stat)
        actual = pokemon.modificadores_stats.get(stat, 0)

        if cantidad > 0:
            if actual >= 6:
                if not self.es_simulado:
                    self._emit(f"¡El {nombre_stat} de {pokemon.name} no puede subir más!")
                return False
            nueva_cantidad = min(6, actual + cantidad)
            pokemon.modificadores_stats[stat] = nueva_cantidad
            cambio_real = nueva_cantidad - actual
            
            if not self.es_simulado and cambio_real > 0:
                if cambio_real == 1:
                    self._emit(f"¡El {nombre_stat} de {pokemon.name} subió!")
                elif cambio_real == 2:
                    self._emit(f"¡El {nombre_stat} de {pokemon.name} subió mucho!")
                else:
                    self._emit(f"¡El {nombre_stat} de {pokemon.name} subió drásticamente!")
            return True

        elif cantidad < 0:
            if actual <= -6:
                if not self.es_simulado:
                    self._emit(f"¡La {nombre_stat} de {pokemon.name} no puede bajar más!")
                return False
            nueva_cantidad = max(-6, actual + cantidad)
            pokemon.modificadores_stats[stat] = nueva_cantidad
            cambio_real = actual - nueva_cantidad
            
            if not self.es_simulado and cambio_real > 0:
                if cambio_real == 1:
                    self._emit(f"¡La {nombre_stat} de {pokemon.name} bajó!")
                elif cambio_real == 2:
                    self._emit(f"¡La {nombre_stat} de {pokemon.name} bajó mucho!")
                else:
                    self._emit(f"¡La {nombre_stat} de {pokemon.name} bajó drásticamente!")
            return True
            
        return False

    def elegir_intercambio(self, elegibles):
        for i, (idx_real, pokemon) in enumerate(elegibles):
            print(f"{i + 1}. {pokemon.name} (HP: {pokemon.hp})")

        while True:
            try:
                seleccion = int(input("Elige el número de la option: ")) - 1
                if 0 <= seleccion < len(elegibles):
                    return elegibles[seleccion][0] 
                else:
                    print("Esa opción no está en la lista.")
            except ValueError:
                print("Escribe un número por favor")

    def ordenar_acciones(self, pokemonP1: Pokemon, accionElegidaP1, pokemonP2: Pokemon, accionElegidaP2):
        if not isinstance(accionElegidaP1, Move): return [0, 1]
        if not isinstance(accionElegidaP2, Move): return [1, 0]

        if accionElegidaP1.priority > accionElegidaP2.priority:
            return [0, 1]
        elif accionElegidaP1.priority < accionElegidaP2.priority:
            return [1, 0]

        if pokemonP1.obtener_stat_efectiva(pokemonP1.speed, "speed") > pokemonP2.obtener_stat_efectiva(pokemonP2.speed, "speed"):
            return [0, 1]
        elif pokemonP1.obtener_stat_efectiva(pokemonP1.speed, "speed") < pokemonP2.obtener_stat_efectiva(pokemonP2.speed, "speed"):
            return [1, 0]
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
        self.estado_del_equipo.pokemonActivoP1.protegido = False
        self.estado_del_equipo.pokemonActivoP1.endure_activo = False
        self.estado_del_equipo.pokemonActivoP2.protegido = False
        self.estado_del_equipo.pokemonActivoP2.endure_activo = False

        orden = self.ordenar_acciones(pokemonP1, accionElegidaP1, pokemonP2, accionElegidaP2)

        contexto = {
            0: {"id_player": 1, "id_rival": 2, "accion": accionElegidaP1, "tipo_rival": tipoP2},
            1: {"id_player": 2, "id_rival": 1, "accion": accionElegidaP2, "tipo_rival": tipoP1}
        }
        pokemon_rival_desvanecido = False

        for indice in orden:
            ctx = contexto[indice]           
            if pokemon_rival_desvanecido:
                continue

            atacante = self.estado_del_equipo.pokemonActivoP1 if ctx["id_player"] == 1 else self.estado_del_equipo.pokemonActivoP2
            defensor = self.estado_del_equipo.pokemonActivoP2 if ctx["id_player"] == 1 else self.estado_del_equipo.pokemonActivoP1
            atacante.protegido = False
            atacante.puede_atacar = True
            atacante.endure_activo = False

            accion = ctx["accion"]
            
            if not isinstance(accion, int): 
                if accion.name not in ("protect", "detect", "endure"): atacante.protects_seguidos = 0
            else:
                atacante.protects_seguidos = 0

            if isinstance(accion, Move):
                accion.current_power_points -= 1

                self.resolver_efecto_MID(atacante) 
                if not atacante.puede_atacar:
                    continue

                if accion.damage_class != DamageClass.STATUS:
                    if defensor.protegido:
                        if not self.es_simulado:
                            self._emit(f"¡{defensor.name} se ha protegido!")
                        continue
                    
                    if atacante.lock_on_activo:
                        acierta = True
                        atacante.lock_on_activo = False
                    else:
                        probabilidad_acierto = atacante.calcular_probabilidad_acierto(accion, defensor)
                        acierta = random.random() < probabilidad_acierto
                    
                    if not acierta:
                        if not self.es_simulado:
                            self._emit(f"¡{atacante.name} usó {accion.name}, pero falló!")
                        continue

                    daño = calcular_daño(atacante, defensor, accion)

                    if not self.es_simulado:
                        self._emit(f"¡{atacante.name} usa {accion.name}!")
                        self._emit(f"Hace {round(daño, 2)} de daño a {defensor.name}")
                    
                    vida_previa = defensor.hp
                    nueva_vida_rival = establecer_vida(defensor, daño)

                    if defensor.endure_activo and nueva_vida_rival <= 0:
                        nueva_vida_rival = 1
                        defensor.hp = 1
                        defensor.endure_activo = False
                        if not self.es_simulado:
                            self._emit(f"¡{defensor.name} resistió el golpe con Aguante!")
                        

                    atacante.reciente_daño_hecho = vida_previa - nueva_vida_rival 
                    self.resolver_movimiento_after_exec(accion, atacante)

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
                    probabilidad_acierto = atacante.calcular_probabilidad_acierto(accion, defensor)
                    acierta = random.random() < probabilidad_acierto
                    
                    if not acierta:
                        if not self.es_simulado:
                            self._emit(f"¡{atacante.name} usó {accion.name}, pero falló!")
                        continue
                    
                    if acierta:
                        if not self.es_simulado:
                            self._emit(f"¡{atacante.name} usó {accion.name}!")

                    self.resolver_movimiento_de_soporte(accion, atacante, defensor)
            else:
                if not self.es_simulado:
                    self._emit(f"El entrenador del Equipo {ctx['id_player']} retira a su Pokémon...")
                self.estado_del_equipo.intercambiarPokemon(ctx["accion"], ctx["id_player"])      

        self.resolver_efecto_END(pokemonP1)
        self.resolver_efecto_END(pokemonP2)
        self.resolver_entorno_END(pokemonP1)
        self.resolver_entorno_END(pokemonP2)
        
        if self.estado_del_equipo.esTerminal:
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
                self._emit(f"¡Es un empate!")
        
    def generar_intercambio_aleatorio(self, equipo: int):
        if self.estado_del_equipo.esTerminal:
            print("Este estado es terminal. No se generó un intercambio")
            return 0 
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
        if ctx["tipo_rival"] == 1:
            idx_nuevo = self.elegir_intercambio(elegibles)
        else:
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
            if pokemon_rival_desvanecido: 
                return

            atacante = self.estado_del_equipo.pokemonActivoP1 if ctx["id_player"] == 1 else self.estado_del_equipo.pokemonActivoP2
            defensor = self.estado_del_equipo.pokemonActivoP2 if ctx["id_player"] == 1 else self.estado_del_equipo.pokemonActivoP1
            accion = ctx["accion"]

            if isinstance(accion, Move):
                accion.current_power_points -= 1

                if accion.damage_class != DamageClass.STATUS:
                    daño = calcular_daño(atacante, defensor, accion)
                    vida_previa = defensor.hp

                    if not self.es_simulado:
                        self._emit(f"¡{atacante.name} usa {accion.name}!")
                        self._emit(f"Hace {round(daño, 2)} de daño a {defensor.name}")
                    
                    nueva_vida_rival = establecer_vida(defensor, daño)
                    atacante.reciente_daño_hecho = vida_previa - nueva_vida_rival 
                    
                    self.resolver_movimiento_after_exec(accion, atacante)

                    if nueva_vida_rival <= 0 :
                        if not self.es_simulado: self._emit(f"¡{defensor.name} se ha debilitado!")
                        pokemon_rival_desvanecido = True
                        self.resolver_intercambio(ctx, atacante, defensor)

                    if self.estado_del_equipo.conteo_vivos(ctx["id_rival"]) == 0:
                        return   
                else:
                    if not self.es_simulado: self._emit(f"¡{atacante.name} usó {accion.name}, que es un estado!")
                    self.resolver_movimiento_de_soporte(accion, atacante, defensor)
            else:
                if not self.es_simulado: self._emit(f"El entrenador del Equipo {ctx['id_player']} retira a su Pokémon...")
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
        movimiento_nombre = movimiento.name

        match(movimiento_nombre):
            case "lock-on":
                atacante.lock_on_activo = True
                if not self.es_simulado:
                    self._emit(f"¡{atacante.name} fijó el blanco!")

            case "venom-drench":
                if defensor.efecto in (Effects.POISON, Effects.TOXIC):
                    self._modificar_stat(defensor, "attack", -1)
                    self._modificar_stat(defensor, "special_attack", -1)
                    self._modificar_stat(defensor, "speed", -1)
                elif not self.es_simulado:
                    self._emit(f"¡No tuvo efecto en {defensor.name}!")

            case "endure":
                rn = random.random()
                prob_fail = atacante.protects_seguidos * (1/3)
                if rn > prob_fail:
                    atacante.endure_activo = True
                    atacante.protects_seguidos += 1
                    if not self.es_simulado:
                        self._emit(f"¡{atacante.name} se preparó para resistir!")
                else:
                    atacante.protects_seguidos = 0
                    atacante.endure_activo = False
                    if not self.es_simulado:
                        self._emit(f"¡Falló el aguante de {atacante.name}!")

            case "haze":
                p1 = self.estado_del_equipo.pokemonActivoP1
                p2 = self.estado_del_equipo.pokemonActivoP2
                for stat in p1.modificadores_stats:
                    p1.modificadores_stats[stat] = 0
                    p2.modificadores_stats[stat] = 0
                if not self.es_simulado:
                    self._emit("¡Se eliminaron todos los cambios de estadísticas!")

            case "power-swap":
                p1 = self.estado_del_equipo.pokemonActivoP1
                p2 = self.estado_del_equipo.pokemonActivoP2
                p1.modificadores_stats["attack"], p2.modificadores_stats["attack"] = \
                    p2.modificadores_stats["attack"], p1.modificadores_stats["attack"]
                p1.modificadores_stats["special_attack"], p2.modificadores_stats["special_attack"] = \
                    p2.modificadores_stats["special_attack"], p1.modificadores_stats["special_attack"]
                if not self.es_simulado:
                    self._emit(f"¡{atacante.name} intercambió cambios de Ataque con {defensor.name}!")

            case "guard-split":
                p1 = self.estado_del_equipo.pokemonActivoP1
                p2 = self.estado_del_equipo.pokemonActivoP2
                promedio_def = round((p1.defense + p2.defense) / 2)
                promedio_spdef = round((p1.special_defense + p2.special_defense) / 2)
                p1.defense = p2.defense = promedio_def
                p1.special_defense = p2.special_defense = promedio_spdef
                if not self.es_simulado:
                    self._emit(f"¡{atacante.name} compartió su Defensa con {defensor.name}!")

            case "rain-dance":
                self.entorno_activo = Weather.RAIN
                self.entorno_turnos_restantes = 5
                if not self.es_simulado:
                    self._emit("¡Empezó a llover!")

            case "sunny-day":
                self.entorno_activo = Weather.SUNNY
                self.entorno_turnos_restantes = 5
                if not self.es_simulado:
                    self._emit("¡El sol empezó a brillar con fuerza!")

            case "sandstorm":
                self.entorno_activo = Weather.SANDSTORM
                self.entorno_turnos_restantes = 5
                if not self.es_simulado:
                    self._emit("¡Se desató una tormenta de arena!")

            case "hail":
                self.entorno_activo = Weather.HAIL
                self.entorno_turnos_restantes = 5
                if not self.es_simulado:
                    self._emit("¡Empezó a granizar!")

            case "tail-whip":
                self._modificar_stat(defensor, "defense", -1)

            case "screech":
                self._modificar_stat(defensor, "defense", -2)

            case "charm":
                self._modificar_stat(defensor, "attack", -2)

            case "fake-tears":
                self._modificar_stat(defensor, "special_defense", -2)

            case "captivate":
                self._modificar_stat(defensor, "special_attack", -2)

            case "confide":
                self._modificar_stat(defensor, "special_attack", -1)

            case "eerie-impulse":
                self._modificar_stat(defensor, "special_attack", -2)

            case "flash":
                self._modificar_stat(defensor, "accuracy", -1)

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
                self._modificar_stat(defensor, "attack", 2)
                if defensor.efecto is None:
                    defensor.efecto = Effects.CONFUSION
                    defensor.turnos_restantes_estado = random.randint(2, 5)
                    if not self.es_simulado:
                        self._emit(f"¡{defensor.name} se ha confundido!")
                elif not self.es_simulado:
                    self._emit(f"¡{defensor.name} ya estaba confundido!")

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
                self._modificar_stat(atacante, "attack", 1)
                self._modificar_stat(atacante, "speed", 1)

            case "swords-dance":
                self._modificar_stat(atacante, "attack", 2)

            case "amnesia":
                self._modificar_stat(atacante, "special_defense", 2)
            
            case "barrier":
                self._modificar_stat(atacante, "defense", 2)

            case "charge":
                self._modificar_stat(atacante, "special_defense", 1)
            
            case "double-team":
                self._modificar_stat(atacante, "evasion", 1)

            case "growl":
                self._modificar_stat(defensor, "attack", -1)

            case "protect" | "detect":
                rn = random.random()
                prob_fail = atacante.protects_seguidos * 1/3

                if rn > prob_fail:
                    atacante.protects_seguidos += 1
                    atacante.protegido = True
                    if not self.es_simulado:
                        self._emit(f"¡{atacante.name} se va a proteger!")
                else:
                    atacante.protects_seguidos = 0
                    atacante.protegido = False
                    if not self.es_simulado: 
                        self._emit(f"¡El movimiento de protección de {atacante.name} falló!")

            case "wish":
                atacante.vida_pendiente_wish = atacante.max_hp // 2
                if not self.es_simulado:
                    self._emit(f"¡{atacante.name} pidió un deseo!")

            case "synthesis":
                match(self.entorno_activo):
                    case Weather.SUNNY:
                        atacante.hp = min(atacante.max_hp, atacante.hp + round(atacante.max_hp*2/3,2))
                    case Weather.SANDSTORM | Weather.HAIL | Weather.RAIN:
                        atacante.hp = min(atacante.max_hp, atacante.hp + atacante.max_hp/4)
                    case _:
                        atacante.hp = min(atacante.max_hp, atacante.hp + atacante.max_hp/2)
                if not self.es_simulado:
                    self._emit(f"¡{atacante.name} restauró sus PS mediante síntesis!")
            
            case "aqua-ring":
                atacante.aqua_ring_activo = True
                if not self.es_simulado:
                    self._emit(f"¡Un velo de agua rodea a {atacante.name}!")
            
            case "rest":
                atacante.hp = atacante.max_hp
                atacante.efecto = Effects.SLEEP
                atacante.turnos_restantes_estado = 2
                atacante.multiplicador_toxico = 1
                if not self.es_simulado:
                    self._emit(f"¡{atacante.name} se durmió y recuperó toda su salud!")
            
            case "heal-pulse":
                defensor.hp = min(defensor.max_hp, defensor.hp + defensor.max_hp/2)
                if not self.es_simulado:
                    self._emit(f"¡Un pulso curativo restauró los PS de {defensor.name}!")
            
            case "refresh":
                atacante.efecto = None
                atacante.multiplicador_toxico = 1
                if not self.es_simulado:
                    self._emit(f"¡{atacante.name} se ha curado de sus problemas de estado!")

            case _:
                return

    def resolver_efecto_MID(self, afectado: Pokemon):
        efecto_nombre = afectado.efecto

        match(efecto_nombre):
            case Effects.SLEEP:
                afectado.turnos_restantes_estado -= 1
                if afectado.turnos_restantes_estado == 0:
                    afectado.efecto = None
                    afectado.puede_atacar = True
                    if not self.es_simulado: 
                        self._emit(f"¡{afectado.name} se ha despertado!")
                else:
                    if not self.es_simulado: 
                        self._emit(f"¡{afectado.name} está profundamente dormido!")
                    afectado.puede_atacar = False

            case Effects.CONFUSION:
                afectado.turnos_restantes_estado -= 1
                if afectado.turnos_restantes_estado == 0:
                    if not self.es_simulado: 
                        self._emit(f"¡{afectado.name} salió de la confusión!")
                    afectado.efecto = None
                    afectado.puede_atacar = True
                else:
                    if not self.es_simulado:
                        self._emit(f"¡{afectado.name} está confundido...!")
                    rn = random.random()
                    if rn > 1/3:
                        afectado.puede_atacar = False
                        daño_confusion = round(afectado.max_hp/3, 2)
                        establecer_vida(afectado, daño_confusion)
                        if not self.es_simulado: 
                            self._emit(f"¡Tan confundido que se hirió a sí mismo!")
            
            case Effects.PARALYSIS:
                rn = random.random()
                if rn < 0.25: # Probabilidad competitiva oficial (25%)
                    afectado.puede_atacar = False
                    if not self.es_simulado: 
                        self._emit(f"¡{afectado.name} está paralizado y no se puede mover!")
                    
            case Effects.ATTRACT:
                if not self.es_simulado:
                    self._emit(f"¡{afectado.name} está enamorado!")
                rn = random.random()
                if rn < 0.5:
                    afectado.puede_atacar = False
                    if not self.es_simulado: 
                        self._emit(f"¡La inmovilidad del amor le impide atacar!")

            case _:
                return

    def resolver_efecto_END(self, afectado: Pokemon):
        if afectado.hp == 0: return

        if afectado.aqua_ring_activo:
            vida_recuperada = round(afectado.max_hp/16,2)
            establecer_vida(afectado, -vida_recuperada)
            if not self.es_simulado:
                self._emit(f"¡Acua Aro recuperó salud de {afectado.name}!")

        if afectado.vida_pendiente_wish > 0:
            establecer_vida(afectado, -afectado.vida_pendiente_wish)
            afectado.vida_pendiente_wish = 0
            if not self.es_simulado:
                self._emit(f"¡El deseo de {afectado.name} se cumplió!")

        efecto_nombre = afectado.efecto

        match(efecto_nombre):
            case Effects.POISON:
                daño_veneno = round(afectado.max_hp/8, 2)
                establecer_vida(afectado, daño_veneno)
                if not self.es_simulado: 
                    self._emit(f"¡{afectado.name} recibe daño por el veneno!")

            case Effects.TOXIC:
                daño_veneno = round(afectado.max_hp/16, 2)
                daño_veneno = daño_veneno * afectado.multiplicador_toxico
                establecer_vida(afectado, daño_veneno)
                afectado.multiplicador_toxico += 1
                if not self.es_simulado: 
                    self._emit(f"¡{afectado.name} recibe daño por el veneno grave!")

            case _:
                return
            
    def resolver_movimiento_after_exec(self, movimiento: Move, atacante: Pokemon):
        nombre_movimiento = movimiento.name

        match(nombre_movimiento):
            case "absorb" | "draining-kiss" | "giga-drain":
                if atacante.reciente_daño_hecho <= 0: return
                vida_robada = atacante.reciente_daño_hecho / 2
                if not self.es_simulado: 
                    self._emit(f"¡{atacante.name} absorbió energía de su oponente!")
                establecer_vida(atacante, -vida_robada)
    
    def resolver_entorno_END(self, pokemon: Pokemon):
        # Descontar el turno de clima únicamente al evaluar el primer Pokémon activo de la ronda
        if self.entorno_activo is not None and pokemon == self.estado_del_equipo.pokemonActivoP1:
            self.entorno_turnos_restantes -= 1
            if self.entorno_turnos_restantes <= 0:
                if not self.es_simulado:
                    self._emit("¡El clima volvió a la normalidad!")
                self.entorno_activo = None
        
        if self.entorno_activo is None or pokemon.hp == 0: 
            return
        
        match(self.entorno_activo):
            case Weather.SANDSTORM:
                if PokemonType.STEEL not in pokemon.types and PokemonType.GROUND not in pokemon.types and PokemonType.ROCK not in pokemon.types:
                    daño_entorno = round(pokemon.max_hp/16, 2)
                    establecer_vida(pokemon, daño_entorno)
                    if not self.es_simulado: 
                        self._emit(f"¡La tormenta de arena castiga a {pokemon.name}!")

            case Weather.HAIL:
                if PokemonType.ICE not in pokemon.types:
                    daño_entorno = round(pokemon.max_hp/16, 2)
                    establecer_vida(pokemon, daño_entorno)
                    if not self.es_simulado: 
                        self._emit(f"¡El granizo golpea a {pokemon.name}!")