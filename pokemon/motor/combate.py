from pokemon.models.move import Move
import random
import math
from pokemon.motor.acciones import calcular_daño, establecer_vida
from pokemon.motor.estado_juego import EstadoJuego
from pokemon.enums.damage_class import DamageClass

class Combate:
    estado_del_equipo = None
    estado_combate = None

    def __init__(self, estado_juego):
        self.estado_del_equipo = estado_juego

    #En el combate, se espera las entradas de los jugadores
    #Se procesan ordenando las acciones
    #Se ejecuta el turno. Y pues se generaría un nuevo estado y se esperarian las entradas nuevamente

    #La UI debe disparar un evento que envie pokemonP1, accionelegidaP1, pokemonP2, P2accionElegida. Envia la referencia de la funcion o el nombre del movimiento
    def ordenar_acciones(self, pokemonP1, accionElegidaP1, pokemonP2, accionElegidaP2):
        #Si hay intercambios??
        if not isinstance(accionElegidaP1, Move): return [0, 1]
        if not isinstance(accionElegidaP2, Move): return [1, 0]

        #Si hay prioridad???
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
    #Tal vez si devuelvo el orden de los indices? P1 = 0, P2 = 1

    #Esto debería disparar eventos a la interfaz y devolver un nuevo estado. Los parametros entregarlos de estado_juego
    def ejecutar_turno(self, pokemonP1, accionElegidaP1, pokemonP2, accionElegidaP2):
        orden = self.ordenar_acciones(pokemonP1, accionElegidaP1, pokemonP2, accionElegidaP2)
        
        if isinstance(self.estado_del_equipo, EstadoJuego):
            nuevo_estado_juego = self.estado_del_equipo

        for indice in orden:
            
            if indice == 0 and pokemonP1.hp != 0:
                if not isinstance(accionElegidaP1, Move):
                    print("Disparar evento para que la UI haga la animación de intercambio") 

                if isinstance(accionElegidaP1, Move):
                    if accionElegidaP1.damage_class != DamageClass.STATUS:
                        daño = calcular_daño(pokemonP1, pokemonP2, accionElegidaP1)
                        print("Disparar evento para el efecto de daño")       
                        vidaRestante = establecer_vida(pokemonP2, daño)
                        print("Disparar evento para cambiar la vida en la UI") 

                        if vidaRestante == 0:
                            print("Disparar evento de desvanecer pokemon") 
                            print("Disparar evento para que la UI pase a la pantalla de seleccionar pokemon")
                            nuevo_estado_juego.intercambiarPokemon(1, 2) #El evento tiene que retornar el pokemon en reemplazo. Aqui se asume que entra el segundo



                        
            if indice == 1 and pokemonP2.hp != 0:
                if not isinstance(accionElegidaP2, Move):
                    print("Disparar evento para que la UI haga la animación de intercambio")
                
                if isinstance(accionElegidaP2, Move):
                    if accionElegidaP2.damage_class != DamageClass.STATUS:
                        daño = calcular_daño(pokemonP2, pokemonP1, accionElegidaP2)
                        print("Disparar evento para el efecto de daño") 
                        vidaRestante = establecer_vida(pokemonP1, daño)
                        print("Disparar evento para cambiar la vida en la UI") 

                        if vidaRestante == 0:
                            print("Disparar evento de desvanecer pokemon") 
                            print("Disparar evento para que la UI pase a la pantalla de seleccionar pokemon")
                            nuevo_estado_juego.intercambiarPokemon(1, 1) 
        #Falta manejar status
    
    def verificar_ganador(self):
        estado_juego = None
        if isinstance(self.estado_del_equipo, EstadoJuego):
            estado_juego = self.estado_del_equipo
        
        cuentaP1 = 0
        cuentaP2 = 0
        for pokemon in estado_juego.equipoP1:
            if pokemon.hp == 0: cuentaP1 = cuentaP1+1

        for pokemon in estado_juego.equipoP2:
            if pokemon.hp == 0: cuentaP2 = cuentaP2+1
        
        if cuentaP1 == len(estado_juego.equipoP1): 
            print("El jugador gana")
            return True
        elif cuentaP2 == len(estado_juego.equipoP2):
            print("El oponente gana")
            return True

        return False