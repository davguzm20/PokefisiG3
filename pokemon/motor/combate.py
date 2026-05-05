from pokemon.models.move import Move
import random
import math
from pokemon.motor.acciones import calcular_daño, establecer_vida, obtener_multiplicador_tipos
from pokemon.motor.estado_juego import EstadoJuego
from pokemon.enums.damage_class import DamageClass

class Combate:
    estado_del_equipo = None

    def __init__(self, estado_juego):
        self.estado_del_equipo = estado_juego
    
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

    #Esto debería disparar eventos a la interfaz y devolver un nuevo estado. Los parametros entregarlos de estado_juego
    def ejecutar_turno(self, pokemonP1, accionElegidaP1, pokemonP2, accionElegidaP2, tipoP1, tipoP2):
        orden = self.ordenar_acciones(pokemonP1, accionElegidaP1, pokemonP2, accionElegidaP2)
        
        contexto = {
            0: {"id_propio": 1, "id_rival": 2, "accion": accionElegidaP1, "tipo_rival": tipoP2},
            1: {"id_propio": 2, "id_rival": 1, "accion": accionElegidaP2, "tipo_rival": tipoP1}
        }

        for indice in orden:
            ctx = contexto[indice]
            
            atacante = self.estado_del_equipo.pokemonActivoP1 if ctx["id_propio"] == 1 else self.estado_del_equipo.pokemonActivoP2
            defensor = self.estado_del_equipo.pokemonActivoP2 if ctx["id_propio"] == 1 else self.estado_del_equipo.pokemonActivoP1
            
            # Si el atacante muere pierde su turno
            if atacante is None or atacante.hp <= 0:
                continue 

            accion = ctx["accion"]

            if isinstance(accion, Move):
                if accion.damage_class != DamageClass.STATUS:
                    daño = calcular_daño(atacante, defensor, accion)
                    print(f"¡{atacante.name} usa {accion.name}!")
                    print(f"Hace {daño} de daño a {defensor.name}")
                    
                    nueva_vida_rival = establecer_vida(defensor, daño)

                    if nueva_vida_rival <= 0:
                        print(f"¡{defensor.name} se ha debilitado!")
                        
                        #Si se queda sin pokemones el rival tras mi turno
                        if self.estado_del_equipo.conteo_vivos(ctx["id_rival"]) == 0:
                            return 

                        elegibles = self.estado_del_equipo.pokemonesElegibles(ctx["id_rival"])
                        
                        if ctx["tipo_rival"] == 1: # Humano
                            idx_nuevo = self.elegir_intercambio(elegibles)
                        else: # IA
                            idx_nuevo = random.choice(elegibles)[0]
                        
                        self.estado_del_equipo.intercambiarPokemon(idx_nuevo, ctx["id_rival"])
                else:
                    print(f"¡{atacante.name} usó {accion.name}, que es un estado!")
            
            else:
                print(f"El entrenador del Equipo {ctx['id_propio']} retira a su Pokémon...")
                elegibles = self.estado_del_equipo.pokemonesElegibles(ctx["id_propio"])
                
                tipo_jugador = tipoP1 if ctx["id_propio"] == 1 else tipoP2
                
                if tipo_jugador == 1:
                    idx_nuevo = self.elegir_intercambio(elegibles)
                else:
                    idx_nuevo = random.choice(elegibles)[0]
                
                self.estado_del_equipo.intercambiarPokemon(idx_nuevo, ctx["id_propio"])
    
    def verificar_ganador(self):
        estado_juego = None
        if isinstance(self.estado_del_equipo, EstadoJuego):
            estado_juego = self.estado_del_equipo
        
        if estado_juego.conteo_vivos(2) == 0:
            print("El jugador gana")
            return True
        elif estado_juego.conteo_vivos(1) == 0:
            print("El oponente gana")
            return True

        return False