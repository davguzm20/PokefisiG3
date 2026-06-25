import random, copy
from pokemon.motor.estado_juego import EstadoJuego
from pokemon.motor.acciones import calcular_daño, obtener_multiplicador_tipos, establecer_vida
from pokemon.models.pokemon import Pokemon
from pokemon.models.pokemon import Move
from pokemon.motor.combate import Combate
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

#-----------------------------------------------------------------------------------
def movimiento_en_base_a_mayor_daño(pokemonActivoP1, pokemonActivoP2, movimientos):
    valMax = -999
    actualMov = [valMax, None]
    for movimiento in movimientos:
        valAct = calcular_daño(pokemonActivoP2, pokemonActivoP1, movimiento)
        if valAct > valMax:
            valMax = valAct
            actualMov = [valMax, movimiento]

    return actualMov

#Niv 1
#Ajuste para eleccion random en base a la lista de movimientos
def elegirMovimientoAleatorio(movimientos):
    return random.choice(movimientos)

#Niv 2
#Heuristica inicial basada en diferencia de HP
#maximizar diferencia a favor de IA

    #Devuelve el pokemon activo de la IA, el pokemon activo del jugador, y sus HP respectivamente
    # dependiendo de qué lado controle la IA. El lado 2 es el que se ve de frente y el lado 1 el que se ve de espaldas
def resolver_lados(estado_juego, ia_side):
    if not isinstance(estado_juego, EstadoJuego):
        print("estado_juego debe ser instacia de EstadoJuego")
        return
        
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
    atacante, defensor, hp_ia, hp_player = resolver_lados(estado_juego, ia_side)
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

def elegir_movimiento_con_minimax(estado, profundidad, agente_ia):
    
    copia_estado = copiar_estado(estado)
    nodo = NodoV2(copia_estado, profundidad=0)

    raiz = mini_max_recursivo(nodo, profundidad, agente_ia.num_jugador)

    if raiz.hijo_escogido.operador["movimiento"]: print(f'El movimiento escogido es: {raiz.hijo_escogido.operador["movimiento"].name}')
    
    if raiz.hijo_escogido.operador["intercambio"]:print(f'Se hizo un intercambio con el pokemon de indice: {raiz.hijo_escogido.operador["intercambio"]}')

def heuristica_avanzada(estado_juego, movimiento, pesos):

    if isinstance(movimiento, dict):
        indice_intercambio = movimiento["intercambio"]
        movimiento = movimiento["movimiento"] if movimiento["movimiento"] else movimiento
        
    # Normalizar cada componente entre 0 y 1
    if isinstance(estado_juego, EstadoJuego):

        hp_ratio = (estado_juego.pokemonActivoP2.hp - estado_juego.pokemonActivoP1.hp) / max(estado_juego.pokemonActivoP2.hp + estado_juego.pokemonActivoP1.hp, 1)
        velocidad = (estado_juego.pokemonActivoP1.speed - estado_juego.pokemonActivoP2.speed) / max(estado_juego.pokemonActivoP1.speed + estado_juego.pokemonActivoP2.speed, 1)

        if isinstance(movimiento, Move):
            if ventaja_tipo.power == 0: return 0
            ventaja_tipo = obtener_multiplicador_tipos(movimiento, estado_juego.pokemonActivoP1, estado_juego.pokemonActivoP2)

        else: ventaja_tipo = 0.05

        pokemons_vivos = estado_juego.conteo_vivos(2) - estado_juego.conteo_vivos(1) / max(len(estado_juego.equipoP1), len(estado_juego.equipoP2), 1)
    
        

    return +(
        pesos["hp"] * hp_ratio +
        pesos["velocidad"] * velocidad +
        pesos["tipo"] * ventaja_tipo +
        pesos["vivos"] * pokemons_vivos
    )


#La función heuristica se usa con minimax. Pero siempre debe centrarse en valorar el equipo de Max, porque se está valorando en qué posición queda Max parado
def funcion_heuristica_avanzada(estado_juego, operador, pesos, lado_ia, estado_anterior = None):
    
    if isinstance(operador, dict):
        movimiento = operador["movimiento"] if operador["movimiento"] else None
    
    pokemon_lado_ia, pokemon_lado_oponente, hp_poke_ia, hp_poke_oponente = resolver_lados(estado_juego, lado_ia)

    # Normalizar cada componente entre 0 y 1
    if isinstance(estado_juego, EstadoJuego):
        velocidad = (pokemon_lado_ia.speed - pokemon_lado_oponente.speed) / max(pokemon_lado_ia.speed + pokemon_lado_oponente.speed, 1)
        hp_ratio = (hp_poke_ia - hp_poke_oponente) / max(hp_poke_ia + hp_poke_oponente, 1)

        if isinstance(movimiento, Move):
            if movimiento.power == 0: return 0.0 #Por ahora no hay movs de soporte 
            multiplicador = obtener_multiplicador_tipos(movimiento, estado_juego.pokemonActivoP1, estado_juego.pokemonActivoP2)
            if multiplicador > 2:
                ventaja_tipo = 2
            elif multiplicador > 1:
                ventaja_tipo = 1
            elif multiplicador == 1:
                ventaja_tipo = 0
            elif multiplicador > 0.5:
                ventaja_tipo = -1
            else:
                ventaja_tipo = -2
        else:
            ventaja_tipo = 0.5

        pokemons_vivos = (estado_juego.conteo_vivos(2) - estado_juego.conteo_vivos(1)) / max(len(estado_juego.equipoP1), len(estado_juego.equipoP2), 1)
    
    return (
        pesos["hp"] * hp_ratio +
        pesos["velocidad"] * velocidad +
        pesos["tipo"] * ventaja_tipo +
        pesos["vivos"] * pokemons_vivos
    )
 
#----------------------------------------------------------------------------------- Mini Max == Preferiblemente hasta 4 de profundidad?

pesos_mock = {
    "hp": 0.3,
    "velocidad": 0.2,
    "tipo": 0.3,
    "vivos": 0.2
}

class Nodo:

    def __init__(self, estado_juego, profundidad, turnoDeMax = True):
        self.estado = estado_juego
        self.profundidad = profundidad
        self.puntaje = 0 #Del 0 al 1
        self.turnoDeMax = turnoDeMax
        self.padre = None
        self.operador = None
        self.alfa = None
        self.beta = None
        self.sucesores_no_generados = True

def copiar_estado(estado_juego):
    if not isinstance(estado_juego, EstadoJuego):
        print("estado_juego debe ser instacia de EstadoJuego")
        return
    
    estado_copia = EstadoJuego()
    estado_copia.setEquipo(copy.deepcopy(estado_juego.equipoP1), 1)
    estado_copia.setEquipo(copy.deepcopy(estado_juego.equipoP2), 2)
    estado_copia.estado_anterior = copy.deepcopy(estado_juego)
    
    return estado_copia
    
def generar_sucesores(estado_juego, lado_ia):

    if not isinstance(estado_juego, EstadoJuego):
        print("estado_juego debe ser instacia de EstadoJuego")
        return
    
    estado_actual = copiar_estado(estado_juego)
    equipo_objetivo = estado_actual.equipoP1 if lado_ia == 1 else estado_actual.equipoP2

    sucesores = []
    
    # Los turnos de min y max en este caso suceden en una única secuencia en lugar de ordenarse, por lo que un pokemon podría ser debilitado antes de que el agente pueda realmente ejecutar su movimiento. El estado sería evaluable pero en el juego la decisión podría no suceder como se espera
    # Así que por otro lado la función de evaluación debería valorar también la magnitud en la que un pokemon puede ejecutar sus movimientos

    # También es posible que uno de los estados evaluados devuelva un pokemon con 0hp.
    # En ese caso, en el siguiente turno en el estado se habrá elegido tanto un intercambio como un movimiento

    if equipo_objetivo[0].hp == 0:
        for i in range(1, len(equipo_objetivo)):
            if equipo_objetivo[i].hp != 0:
                
                for movimiento in equipo_objetivo[i].moves:
                    estado_sucesor = copiar_estado(estado_juego)
                    estado_juego.intercambiarPokemon(i, lado_ia)

                    equipo_actual = estado_sucesor.equipoP1 if lado_ia == 1 else estado_sucesor.equipoP2
                    equipo_opuesto = estado_sucesor.equipoP2 if lado_ia == 1 else estado_sucesor.equipoP1

                    danio_final = calcular_daño(equipo_actual[0], equipo_opuesto[0], movimiento)

                    establecer_vida(equipo_opuesto[0], danio_final)

                    estado_sucesor.operador = {
                        "movimiento": movimiento,
                        "intercambio": i
                    }

                    sucesores.append(estado_sucesor)

    else:
        #Los posibles intercambios
        for i in range(1, len(equipo_objetivo)):
            if equipo_objetivo[i].hp != 0:
                estado_sucesor = copiar_estado(estado_juego)
                estado_sucesor.intercambiarPokemon(i, lado_ia)
                estado_sucesor.operador = {
                    "movimiento": None,
                    "intercambio": i
                }

                sucesores.append(estado_sucesor)
        
        #Los posibles movimientos
        for movimiento in equipo_objetivo[0].moves:
            estado_sucesor = copiar_estado(estado_juego)
            equipo_opuesto = estado_sucesor.equipoP2 if lado_ia == 1 else estado_sucesor.equipoP1

            #print(f'se estaría usando el movimiento {movimiento.name} sobre {equipo_opuesto[0].name} con hp: {equipo_opuesto[0].hp}')

            danio_final = calcular_daño(equipo_objetivo[0], equipo_opuesto[0], movimiento)

            establecer_vida(equipo_opuesto[0], danio_final)
            estado_sucesor.operador = {
                "movimiento": movimiento,
                "intercambio": None
            }
            #print(equipo_opuesto[0].hp)
            sucesores.append(estado_sucesor)

    print(f'sucesores generados: {sucesores}')
    list.reverse(sucesores)

    return sucesores

class NodoV2:
    def __init__(self, estado = None, padre = None, turnoMax = True, profundidad = 0):
        self.altura = 0 #No se esta usando
        self.estado = estado
        self.padre = padre
        self.profundidad = profundidad
        self.turnoMax = turnoMax
        self.puntaje = None
        self.hijos = None
        self.operador = None
        self.hijo_escogido = None
        self.alfa = -float('inf')
        self.beta = float('inf')
        self.hay_poda = False


##### ==================== La siguiente es una versión de minimax sin poda. Es más facil de explicar que el de arriba. Y en caso se quiera rehacer el mini_max con poda se puede partir de aquí

def evaluarminmax(hijos, turnoMax):
    
    valMax = -float('inf')
    valMin = float('inf')
    hijoMax = None
    hijoMin = None

    for hijo in hijos:
        if not isinstance(hijo, NodoV2):
            raise Exception("hijos debe tener instancias de Nodo")
        if turnoMax:
            if hijo.puntaje > valMax:
                valMax = hijo.puntaje
                hijoMax = hijo.estado.operador
        else:
            if hijo.puntaje < valMin:
                valMin = hijo.puntaje
                hijoMin = hijo.estado.operador

    return [(hijoMax,valMax),(hijoMin,valMin)]

## Siempre terminar con turno de Max, osea profundidad debe ser multiplo de 2
def minimax2(nodo, profundidad, lado_ia):
    if not isinstance(nodo, NodoV2):
        raise Exception("El parametro debe ser una instancia de Nodo")
    
    lado_max = lado_ia
    lado_min = 2 if lado_ia == 1 else 1

    pila = []
    pila.append(nodo)

    while pila:
        #Debo llegar hasta una altura de 1 para calificar, pero por el momento he de generar sucesores
    
        # ===== Recoger datos
        nodo_actual = pila.pop() ###
        if not isinstance(nodo_actual, NodoV2): raise Exception("Nodo apilado no es instancia de nodo")

        estado_actual = nodo_actual.estado ###
        if not isinstance(estado_actual, EstadoJuego): raise Exception("El valor contenido en el nodo no es un estado")

        lado_actual = lado_max if nodo_actual.turnoMax else lado_min
        if nodo_actual.turnoMax: print("========================= Es turno de Max =======================")
        else: print("========================= Es turno de Min =======================")
        

        # ====== (2) .. Cuando se vuelva al padre despues de puntuar sus hijos (y que existan) es el momento de elegir Min_Max para uno de los padres. Es como si ya hubieran visto a (todos) sus hijos
        if nodo_actual.profundidad != profundidad and nodo_actual.hijos:

            #(3)... En este punto un arbol suficiente para hacer poda habría sido generado, para que sea más facil de implementar se guardó a los hijos
            indice_hijo_elegido = 0 if nodo_actual.turnoMax else 1
            hijo_elegido = evaluarminmax(nodo_actual.hijos, nodo_actual.turnoMax)
            
            nodo_actual.puntaje = hijo_elegido[indice_hijo_elegido][1]
            nodo_actual.operador = hijo_elegido[indice_hijo_elegido][0].operador


        # ====== Se va generando sucesores solo si el nodo no es una hoja. En este caso eso depende de: la profundidad del nodo actual es la maxima, o si en este nodo el estado devuelve un juego terminado (Esto último falta programarlo)
        print(f"Profundidad de: {nodo_actual.profundidad}")
        if nodo_actual.profundidad != profundidad and not nodo_actual.hijos:
            sucesores = generar_sucesores(estado_actual, lado_actual)
            hijos = []

            #El nodo actual debe de apilarse para volver a él y poder elegir de sus hijos el puntaje que corresponda
            nodo_actual.hijos = hijos
            pila.append(nodo_actual)  

            # Como los sucesores son estados en este caso se tiene que recorrer de nuevo la lista y volverlos nodos, con las atributos correspondientes
            for sucesor in sucesores:
                sucesor_actual = sucesor
                if not isinstance(sucesor_actual, EstadoJuego): raise Exception("El sucesor no es un estado")

                nodo_sucesor = NodoV2(estado=sucesor_actual, padre=nodo_actual, turnoMax = not nodo_actual.turnoMax, profundidad= nodo_actual.profundidad+1)
                hijos.append(nodo_sucesor)
                pila.append(nodo_sucesor)
            
              


        # ====== Las hojas se puntuan
        if nodo_actual.profundidad == profundidad:

            nodo_actual.puntaje = heuristica_avanzada(estado_actual, estado_actual.operador, pesos_mock)
            print(f'Puntaje de {nodo_actual.puntaje} realizando: {estado_actual.operador}')

        # ====== (2) .. Retorna el mejor movimiento. El nodo raiz solo tendrá operador cuando haya llegado al final de min_max
        if nodo_actual.profundidad == 0 and nodo_actual.operador:
            print(f'Con un puntaje de {nodo_actual.puntaje}')

            if nodo_actual.operador["movimiento"]:
                print(f'El movimiento elegido es: {nodo_actual.operador["movimiento"].name}')
            if nodo_actual.operador["intercambio"]:
                print(f'Se hizo un intercambio con: {nodo_actual.operador["intercambio"]}')


# ============================ Mini max con poda ======================================

## Debe retornar un nodo del cual se devolverá su operador. Para ello recursivamente va a generar sucesores.
def mini_max_recursivo(nodo, profundidad, lado_ia, max, pesos):
    
    if not isinstance(nodo, NodoV2):
        print("padre debe ser instacia de Nodo")
        return
    
    if not isinstance(nodo.estado, EstadoJuego):
        print("el estado de nodo debe ser instacia de EstadoJuego")
        return
    
    estado_actual = copiar_estado(nodo.estado)
    estado_actual.esSimulado = True

    equipo_ia = estado_actual.equipoP1 if lado_ia == 1 else estado_actual.equipoP2

    # ========================================================= Divide el trabajo
    
    #Primero hay que evaluar si es hoja para que no siga generando sucesores.
    if nodo.profundidad == profundidad or nodo.estado.conteo_vivos(1) == 0 or nodo.estado.conteo_vivos(2) == 0:
        nodo.puntaje = funcion_heuristica_avanzada(nodo.estado, nodo.estado.operador, pesos, max)

        #El padre se actualiza los alfas y betas
        if not isinstance(nodo.padre, NodoV2):
            print("padre debe ser instacia de Nodo")
        
        if nodo.padre.turnoMax:
            if nodo.puntaje >= nodo.padre.beta:
                print("hay poda")
                return True

            if nodo.puntaje > nodo.padre.alfa:
                nodo.padre.alfa = nodo.puntaje
                
        else:
            if nodo.puntaje <= nodo.padre.alfa:
                print("hay poda")
                return True

            if nodo.puntaje < nodo.padre.beta:
                nodo.padre.beta = nodo.puntaje
                
        
        #Sin embargo si la poda se hace en el primer elemento, el padre no tendrá hijo escogido. Pero no hay problema porque de todas maneras siempre lo tendría en su primera búsqueda dx

        return False

    # ======================================= Conquista
    
    #Hay que generar sucesores y a cada uno de los sucesores ha de aplicarsele el minimax
    
    if nodo.turnoMax: print("========================= Es turno de Max =======================")
    else: print("========================= Es turno de Min =======================")

    print(f'Con profundidad: {nodo.profundidad}')

    if nodo.profundidad != profundidad:
        
        # #Los posibles intercambios
        # for i in range(1, len(equipo_ia)):
        #     if equipo_ia[i].hp != 0:
        #         if nodo.hay_poda:
        #             break
        #         estado_sucesor = copiar_estado(estado_actual)
        #         estado_sucesor.esSimulado = True
               
        #         estado_sucesor.operador = {
        #             "movimiento": None,
        #             "intercambio": i
        #         }

        #         nodo_sucesor = NodoV2(estado_sucesor, nodo, not nodo.turnoMax, nodo.profundidad +1)
          
        #         #En la poda, en bajada, alfa y beta se pasan tal cual a los hijos. (Propagación de alfa y beta en bajada)
        #         nodo_sucesor.alfa = nodo.alfa
        #         nodo_sucesor.beta = nodo.beta
        #         nodo_sucesor.operador = estado_sucesor.operador

        #         if nodo.turnoMax:
        #             equipo_actual = estado_sucesor.equipoP1 if lado_ia == 1 else estado_sucesor.equipoP2
        #             equipo_opuesto = estado_sucesor.equipoP2 if lado_ia == 1 else estado_sucesor.equipoP1
        #             lado_atacante = lado_ia
        #         else:
        #             equipo_actual = estado_sucesor.equipoP2 if lado_ia == 1 else estado_sucesor.equipoP1
        #             equipo_opuesto = estado_sucesor.equipoP1 if lado_ia == 1 else estado_sucesor.equipoP2
        #             lado_atacante = 2 if lado_ia == 1 else 1
                
        #         #print(f'se estaría intercambiando el pokemon con {equipo_actual[i].name}')
        #         estado_sucesor.intercambiarPokemon(i, lado_atacante)
                
                
        #         #Parte de la conquista
        #         nodo.hay_poda = mini_max_recursivo(nodo_sucesor, profundidad, lado_atacante, max, pesos)
        
        #Los posibles movimientos

        movimientos_ordenados = sorted(equipo_ia[0].moves, key=lambda x: x.power if x.power is not None else 0, reverse=True)
        for movimiento in movimientos_ordenados:
            if nodo.hay_poda:
                break
            estado_sucesor = copiar_estado(estado_actual)
            estado_sucesor.esSimulado = True
            
            if nodo.turnoMax:
                equipo_actual = estado_sucesor.equipoP1 if lado_ia == 1 else estado_sucesor.equipoP2
                equipo_opuesto = estado_sucesor.equipoP2 if lado_ia == 1 else estado_sucesor.equipoP1
                lado_atacante = lado_ia
            else:
                equipo_actual = estado_sucesor.equipoP2 if lado_ia == 1 else estado_sucesor.equipoP1
                equipo_opuesto = estado_sucesor.equipoP1 if lado_ia == 1 else estado_sucesor.equipoP2
                lado_atacante = 2 if lado_ia == 1 else 1

            print(f'se estaría usando el movimiento {movimiento.name} sobre {equipo_opuesto[0].name} con hp: {equipo_opuesto[0].hp}')

            danio_final = calcular_daño(equipo_ia[0], equipo_opuesto[0], movimiento)

            establecer_vida(equipo_opuesto[0], danio_final)
            estado_sucesor.operador = {
                "movimiento": movimiento,
                "intercambio": None
            }

            #print(equipo_opuesto[0].hp)
            nodo_sucesor = NodoV2(estado_sucesor, nodo, not nodo.turnoMax, nodo.profundidad +1)
            nodo_sucesor.operador = estado_sucesor.operador
            #En la poda, en bajada, alfa y beta se pasan tal cual a los hijos. (Propagación de alfa y beta en bajada)
            nodo_sucesor.alfa = nodo.alfa
            nodo_sucesor.beta = nodo.beta
            
            
            #Parte de la conquista
            nodo.hay_poda = mini_max_recursivo(nodo_sucesor, profundidad, lado_atacante, max, pesos)
    
    #print("Se exploraron todos los nodos de este estado aplicado poda")
    # =================================== Combina .. (?)

    #Si no es la raiz debe actualizar los alfa y betas del padre (Propagación de alfa y beta en subida) Esto sucede cuando ya se vieron los hijos no podados del nodo
    if nodo.profundidad != profundidad and not nodo.hay_poda:  
        nodo.puntaje = nodo.alfa if nodo.turnoMax else nodo.beta

    if nodo.padre:
        if nodo.padre.turnoMax:
            if nodo.puntaje > nodo.padre.alfa:
                nodo.padre.alfa = nodo.puntaje
                if nodo.profundidad == 1:
                    nodo.padre.hijo_escogido = nodo
        else:
            if nodo.puntaje < nodo.padre.beta:
                nodo.padre.beta = nodo.puntaje
                if nodo.profundidad == 1:
                    nodo.padre.hijo_escogido = nodo
    
    if not nodo.padre:
        return nodo
    

    return nodo.alfa > nodo.beta


ayuda ={
    
}

def poda_alfa_beta(puntaje, nodo):
    if not isinstance(nodo, NodoV2):
        #print("nodo debe ser instacia de Nodo")
        return
    
    if not isinstance(nodo.padre, NodoV2):
        print("padre del nodo debe ser instacia de Nodo")
        
    
    if nodo.padre.turnoMax:
        if puntaje >= nodo.padre.beta:
            #print(f"{'  ' * nodo.profundidad} >>>> PODA <<<< | Alfa ({puntaje}) >= Beta ({nodo.beta})")
            nodo.padre.puntaje = puntaje
            return True
        if puntaje > nodo.padre.alfa:
            nodo.padre.alfa = puntaje
            nodo.padre.puntaje = puntaje

    else:
        if puntaje <= nodo.padre.alfa: #Si hay poda no actualizas nada
            nodo.padre.puntaje = puntaje
            #print(f"{'  ' * nodo.profundidad} >>>> PODA <<<< Alfa ({nodo.alfa}) >= Beta ({puntaje})")
            return True
        if puntaje < nodo.padre.beta: # Aquí hay un problema. La poda puede suceder después de revisar uno de los hijos y sería necesario revertir el cambio. Porque el nodo ascenderá al padre y lo cambiará
            nodo.padre.beta = puntaje
            nodo.padre.puntaje = puntaje

    return False




def minimax_recursivov2(nodo, profundidad, lado_ia, max, pesos):

    # if not isinstance(nodo, NodoV2):
    #     #print("nodo debe ser instacia de Nodo")
    #     return
    
    # if not isinstance(nodo.estado, EstadoJuego):
    #     #print("el estado de nodo debe ser instacia de EstadoJuego")
    #     return
    
    estado_actual = copiar_estado(nodo.estado)
    estado_actual.esSimulado = True
    
    equipo_ia, equipo_oponente = (estado_actual.equipoP1, estado_actual.equipoP2)  if lado_ia == 1 else (estado_actual.equipoP2, estado_actual.equipoP1)
    
    print(f"{'  ' * nodo.profundidad}====> Entrando a Nodo Prof: {nodo.profundidad} | TurnoMax: {nodo.turnoMax} | Alfa: {nodo.alfa} | Beta: {nodo.beta} | poda: {nodo.hay_poda}")

    beta_antes_de_la_poda = nodo.beta
    alfa_antes_de_la_poda = nodo.alfa
    
    if nodo.profundidad % 2 == 0 and nodo.profundidad != 0: #Las siguientes condiciones solo pueden suceder en un estado donde tanto Max como Min hayan elegido una acción
        if estado_actual.conteo_vivos(1) == 0:
            
            if lado_ia == 1: #Si el equipo de esta IA murió debería de dejarse de generar hijos.
                nodo.puntaje = -99999
            else:
                nodo.puntaje = 999999
            
            print(f"{'  ' * nodo.profundidad}<==== Saliendo de Nodo Prof: {nodo.profundidad} | Puntaje asignado: {nodo.puntaje}")
            return poda_alfa_beta(nodo.puntaje, nodo)
            
        if estado_actual.conteo_vivos(2) == 0:
            if lado_ia == 1: #Si el equipo del oponente murió igualmente debería dejarse de generar hijos.
                nodo.puntaje = 999999
            else:
                nodo.puntaje = -99999
            
            print(f"{'  ' * nodo.profundidad}<==== Saliendo de Nodo Prof: {nodo.profundidad} | Puntaje asignado: {nodo.puntaje}")
            return poda_alfa_beta(nodo.puntaje, nodo)

    if nodo.profundidad == profundidad:
        nodo.puntaje = funcion_heuristica_avanzada(nodo.estado, nodo.estado.operador, pesos, max)

        #El padre se actualiza los alfas y betas
        if not isinstance(nodo.padre, NodoV2):
            print("padre debe ser instacia de Nodo")
        print(f"{'  ' * nodo.profundidad}<==== Saliendo de Nodo Prof: {nodo.profundidad} | Puntaje asignado: {nodo.puntaje}")
        return poda_alfa_beta(nodo.puntaje, nodo)
        
    if nodo.profundidad != profundidad:

        # for i in range(1, len(equipo_ia)):
        #     if equipo_ia[i].hp != 0:
        #         if nodo.hay_poda:
        #             break
        #         estado_sucesor = copiar_estado(estado_actual)
        #         estado_sucesor.esSimulado = True
               
        #         estado_sucesor.operador = {
        #             "movimiento": None,
        #             "intercambio": i
        #         }

        #         nodo_sucesor = NodoV2(estado_sucesor, nodo, not nodo.turnoMax, nodo.profundidad +1)
          
        #         #En la poda, en bajada, alfa y beta se pasan tal cual a los hijos. (Propagación de alfa y beta en bajada)
        #         nodo_sucesor.alfa = nodo.alfa
        #         nodo_sucesor.beta = nodo.beta
        #         nodo_sucesor.operador = estado_sucesor.operador

        #         if nodo.turnoMax:
        #             equipo_actual = estado_sucesor.equipoP1 if lado_ia == 1 else estado_sucesor.equipoP2
        #             equipo_opuesto = estado_sucesor.equipoP2 if lado_ia == 1 else estado_sucesor.equipoP1
        #             lado_atacante = lado_ia
        #         else:
        #             equipo_actual = estado_sucesor.equipoP2 if lado_ia == 1 else estado_sucesor.equipoP1
        #             equipo_opuesto = estado_sucesor.equipoP1 if lado_ia == 1 else estado_sucesor.equipoP2
        #             lado_atacante = 2 if lado_ia == 1 else 1
                
        #         #print(f'se estaría intercambiando el pokemon con {equipo_actual[i].name}')
        #         estado_sucesor.intercambiarPokemon(i, lado_atacante)
                
                
        #         #Parte de la conquista
        #         nodo.hay_poda = mini_max_recursivo(nodo_sucesor, profundidad, lado_atacante, max, pesos)

        if nodo.turnoMax:
            equipoAtacante = equipo_ia
        else:
            equipoAtacante = equipo_oponente

        movimientos_ordenados = sorted(equipoAtacante[0].moves, key=lambda x: x.power if x.power is not None else 0, reverse=True)
        print(movimientos_ordenados)
        for movimiento in movimientos_ordenados: # =====================
            #print(movimiento.name)
            if nodo.hay_poda:
                break
            estado_sucesor = copiar_estado(estado_actual)
            estado_sucesor.esSimulado = True
            
            if nodo.turnoMax:
                equipo_atacante = estado_sucesor.getEquipo(lado_ia)
                equipo_defensor = estado_sucesor.getEquipo(lado_ia - 1)
            else:
                equipo_atacante = estado_sucesor.getEquipo(lado_ia - 1)
                equipo_defensor = estado_sucesor.getEquipo(lado_ia)

            print(f'se estaría usando el movimiento {movimiento.name} sobre {equipo_defensor[0].name} con hp: {equipo_defensor[0].hp}')

            danio_final = calcular_daño(equipo_atacante[0], equipo_defensor[0], movimiento)

            establecer_vida(equipo_defensor[0], danio_final)

            if equipo_defensor[0].hp == 0:
                indices_pokemons = estado_sucesor.pokemonesElegibles(lado_ia -1 if nodo.turnoMax else lado_ia)

                if not indices_pokemons: # Si no hay pokemones elegibles este también es un nodo terminal dx
                    if nodo.turnoMax:
                        nodo.puntaje = 999999
                        
                    else:
                        nodo.puntaje = -99999
                    if nodo.profundidad == 1:
                        if nodo.padre.turnoMax:
                            if nodo.puntaje >= nodo.padre.beta:
                                nodo.padre.hijo_escogido = nodo.estado
                                print(f"{'  ' * nodo.profundidad}<==== Saliendo de Nodo Prof: {nodo.profundidad} | Puntaje asignado: {nodo.puntaje} | {nodo.padre.hijo_escogido} | {nodo.estado.operador}")
                                return True
                            if nodo.puntaje > nodo.padre.alfa:
                                nodo.padre.alfa = nodo.puntaje
                                nodo.padre.hijo_escogido = nodo.estado

                        else:
                            if nodo.puntaje <= nodo.padre.alfa:
                                nodo.padre.hijo_escogido = nodo.estado
                                print(f"{'  ' * nodo.profundidad}<==== Saliendo de Nodo Prof: {nodo.profundidad} | Puntaje asignado: {nodo.puntaje} | {nodo.padre.hijo_escogido} | {nodo.estado}")
                                return True
                            if nodo.puntaje < nodo.padre.beta:
                                nodo.padre.beta = nodo.puntaje
                                nodo.padre.hijo_escogido = nodo.estado
                            print(f"{'  ' * nodo.profundidad}<==== Saliendo de Nodo Prof: {nodo.profundidad} | Puntaje asignado: {nodo.puntaje} | {nodo.padre.hijo_escogido} | {nodo.estado}")
                        return False
                    if nodo.profundidad == 0: #Aquí espera que el movimiento escogido genere la baja del rival. Sin embargo que gane, al final depende de la velocidad de su pokemon
                        nodo.hijo_escogido = estado_actual
                        estado_actual.operador = {
                            "movimiento": movimiento,
                            "intercambio": None
                        }
                        return nodo
                    print(f"{'  ' * nodo.profundidad}<==== Saliendo de Nodo Prof: {nodo.profundidad} | Puntaje asignado: {nodo.puntaje} | {nodo.padre.hijo_escogido} | {nodo.estado}")
                    return poda_alfa_beta(nodo.puntaje, nodo)


                for indice, pokemon in indices_pokemons:
                    if nodo.hay_poda:
                        break

                    print(f"Este sucesor para el nodo en prof:{nodo.profundidad+1} resulta del intercambio ante debilitamiento. Pokemon debilitado: {equipo_defensor[0].name} Pokemon entrante: {pokemon.name} usando el movimiento: {movimiento.name}")

                    cambios_estado_sucesor = copiar_estado(estado_sucesor)
                    cambios_estado_sucesor.esSimulado = True
                    cambios_estado_sucesor.intercambiarPokemon(indice, lado_ia -1 if nodo.turnoMax else lado_ia) #Turno Max altera el equipo de turno min

                    cambios_estado_sucesor.operador = {
                        "movimiento": movimiento,
                        "intercambio": None
                    }

                    cambios_nodo_sucesor = NodoV2(cambios_estado_sucesor, nodo, not nodo.turnoMax, nodo.profundidad +1)
                    cambios_nodo_sucesor.alfa = nodo.alfa
                    cambios_nodo_sucesor.beta = nodo.beta

                    nodo.hay_poda = minimax_recursivov2(cambios_nodo_sucesor, profundidad, lado_ia, max, pesos)
                
                break

            estado_sucesor.operador = {
                "movimiento": movimiento,
                "intercambio": None
            }

            ##print(equipo_opuesto[0].hp)
            nodo_sucesor = NodoV2(estado_sucesor, nodo, not nodo.turnoMax, nodo.profundidad +1)
            #En la poda, en bajada, alfa y beta se pasan tal cual a los hijos. (Propagación de alfa y beta en bajada)
            nodo_sucesor.alfa = nodo.alfa
            nodo_sucesor.beta = nodo.beta
            
            
            #Parte de la conquista
            nodo.hay_poda = minimax_recursivov2(nodo_sucesor, profundidad, lado_ia, max, pesos)
            
    
    # Un nodo que puede generar sucesores habrá recorrido los válidos con o sin poda.
    # Este nodo es un hijo de un padre también. Por lo que también debería evaluar la poda
    # En este punto el nodo entregará su alfa o beta al padre dependiendo de si hubo poda cuando este nodo reviso sus hijos.
    # Si hubo poda lo único que tiene que entregar el nodo al padre es el puntaje del nodo donde hubo poda. Porque el padre necesita ese dato para realizar su poda en como esta planteado este algoritmo
    if nodo.profundidad != 0 and nodo.hay_poda:
        print(f"Hubo poda entonces necesito arreglar el alfa/beta de este Nodo Prof: {nodo.profundidad} ALFA: {nodo.alfa} | Beta: {nodo.beta}")
        if nodo.turnoMax:
            nodo.alfa = alfa_antes_de_la_poda
        else: #En un turno Min si hubo poda es posible que se haya actualizado el beta de este nodo, es necesario evitar ese camboi
            nodo.beta = beta_antes_de_la_poda

    #Independientemente de si hay poda o no, los nodos tendrán que actualizar el alfa y beta del padre. Eso se logra con la función poda_alfa_beta

    #Muchas veces sucedía que al entrar al primer hijo de un nodo había poda. Lo que significa que se perdía el puntaje que se supone se asignaría al padre para la poda, haciendo que falle. Aquí se le asigna el puntaje 
    if nodo.profundidad != 0 and not nodo.hay_poda:
        print(f"{nodo.puntaje} | ALFA: {nodo.alfa} | Beta: {nodo.beta}  | turno: {"ia" if nodo.turnoMax else "oponente"} | movimiento con el que se llegó aquí: {nodo.estado.operador["movimiento"].name} | {nodo.estado.conteo_vivos(1)} | {nodo.estado.conteo_vivos(2)} | Poke: {nodo.estado.pokemonActivoP1.name} hp:{nodo.estado.pokemonActivoP1.hp} | Poke: {nodo.estado.pokemonActivoP2.name} hp:{nodo.estado.pokemonActivoP2.hp}")
        if nodo.profundidad != 1:
            if nodo.turnoMax:
                nodo.puntaje = nodo.alfa
            else:
                nodo.puntaje = nodo.beta
            print(f"{'  ' * nodo.profundidad}<==== Saliendo de Nodo Prof: {nodo.profundidad} | ALFA: {nodo.alfa} | Beta: {nodo.beta} | Puntaje asignado: {nodo.puntaje}")
            return poda_alfa_beta(nodo.puntaje, nodo)
    
    # Si hay poda, la poda del hijo de este nodo se habrá encargado de darle el puntaje necesario (a excepción de si la poda ocurre con el primer hijo) para que el padre de este nodo evalue su poda
    if nodo.profundidad != 0:
        if nodo.profundidad != 1:
            print(f"{nodo.puntaje} | ALFA: {nodo.alfa} | Beta: {nodo.beta}")
            print(f"{'  ' * nodo.profundidad}<==== Saliendo de Nodo Prof: {nodo.profundidad} | ALFA: {nodo.alfa} | Beta: {nodo.beta} | Puntaje asignado: {nodo.puntaje}") ##Por qué el puntaje que se entrega es infinito??
            return poda_alfa_beta(nodo.puntaje, nodo)

    if nodo.profundidad == 1: #Cuando se está en hijos de profundidad 1 la poda es diferente porque en este punto minimax tomará la decisión. Lo importante para el padre es saber el operador
        #print(nodo.estado.operador, nodo.padre.profundidad, nodo.padre.turnoMax, nodo.padre.hijo_escogido, nodo.padre.alfa, nodo.padre.beta, nodo.puntaje)
        if nodo.puntaje == 999999 or nodo.puntaje == -99999: nodo.padre.hijo_escogido = nodo.estado
        if nodo.padre.turnoMax:
            if nodo.puntaje >= nodo.padre.beta:
                nodo.padre.hijo_escogido = nodo.estado
                print(f"{'  ' * nodo.profundidad}<==== Saliendo de Nodo Prof: {nodo.profundidad} | Puntaje asignado: {nodo.puntaje} | {nodo.padre.hijo_escogido} | {nodo.estado.operador}")
                return True
                
            if nodo.puntaje > nodo.padre.alfa:
                nodo.padre.alfa = nodo.puntaje
                nodo.padre.hijo_escogido = nodo.estado

        else:
            if nodo.puntaje <= nodo.padre.alfa:
                nodo.padre.hijo_escogido = nodo.estado
                print(f"{'  ' * nodo.profundidad}<==== Saliendo de Nodo Prof: {nodo.profundidad} | Puntaje asignado: {nodo.puntaje} | {nodo.padre.hijo_escogido} | {nodo.estado}")
                return True
            if nodo.puntaje < nodo.padre.beta:
                nodo.padre.beta = nodo.puntaje
                nodo.padre.hijo_escogido = nodo.estado
        print(f"{'  ' * nodo.profundidad}<==== Saliendo de Nodo Prof: {nodo.profundidad} | Puntaje asignado: {nodo.puntaje} | {nodo.padre.hijo_escogido} | {nodo.estado.operador}")
        return False
        
    if nodo.profundidad == 0:
        #print(nodo.hijo_escogido.operador)
        return nodo
        
    if nodo.profundidad == 0:
        print(nodo.hijo_escogido.operador)
        return nodo

# ======================= Minimax de libro

def resolver_accion(acciones, lado_ia):
    accion_ia = None
    accion_oponente = None

    ia_intercambio = acciones["accion_ia"]["intercambio_index"]
    ia_movimiento = acciones["accion_ia"]["movimiento"]
    
    oponente_intercambio = acciones["accion_oponente"]["intercambio_index"]
    oponente_movimiento = acciones["accion_oponente"]["movimiento"]

    if ia_intercambio is None:
        accion_ia = ia_movimiento
    else:
        accion_ia = ia_intercambio
    
    if oponente_intercambio is None:
        accion_oponente = oponente_movimiento
    else:
        accion_oponente = oponente_intercambio
    
    if lado_ia == 1:
        return (accion_ia, accion_oponente)
    else:
        return (accion_oponente, accion_ia)

def minimax_simplificado(nodo: NodoV2, profundidad, acciones, lado_ia, alfa, beta, pesos):
    """
    Minimax con poda simula todos los estados convenientes de simular según la profundidad, tratando de elegir en base a un criterio la mejor acción a realizar.
    El número de turnos simulados es la profundidad/2.
    Puntua el estado de un combate dependiendo de la profundidad o si es terminal.
    El criterio está dado por funcion_heuristica_avanzada()

    Retorna un diccionario
    {"intercambio_index": int, "movimiento": Move}
    """

    estado_actual = copiar_estado(nodo.estado)
    estado_actual.esSimulado = True
    mejor_accion = None

    id_ia = lado_ia
    id_oponente = lado_ia - 1
    
    #print(nodo.profundidad, alfa, beta, acciones)
    
    if estado_actual.conteo_vivos(id_oponente) == 0:
        #print(f"------ > Este nodo fue puntuado con: 99999")
        return 99999
    if estado_actual.conteo_vivos(id_ia) == 0:
        #print(f"------ > Este nodo fue puntuado con: -99999")
        return -99999
    
    if nodo.profundidad == profundidad:
        
        operador = {
            "movimiento": acciones["accion_ia"] if acciones else None,
            #No hace falta considerar intercambio pues el estado ya contendrá la información del intercambio
        }
        puntaje = funcion_heuristica_avanzada(nodo.estado, operador, pesos, lado_ia)
        #print(f"------ > Este nodo fue puntuado con: {puntaje}")
        return puntaje
    

    if nodo.turnoMax:
        mejor_valor = -float('inf')

        for accion in estado_actual.obtener_acciones_posibles():

            nodo_resultante = NodoV2(nodo.estado, None, not nodo.turnoMax, nodo.profundidad + 1)
            
            valor = minimax_simplificado(nodo_resultante, profundidad,
                                         {"accion_ia": accion,
                                          "accion_oponente": None},
                                           lado_ia, alfa, beta, pesos)
            
            mejor_valor = max(mejor_valor, valor)

            if nodo.profundidad == 0:
                ###print(f"Rama explorada para max es: {mejor_accion} con {valor}")
                if mejor_valor == valor:
                    ###print("Se encontro algun nuevo candidato para Max")
                    mejor_accion = accion
            
            alfa = max (alfa, mejor_valor)

            if beta <= alfa:
                break
        
        if nodo.profundidad == 0:
            #print(f"Puntaje final escogido es: {mejor_valor}")
            return mejor_accion
        return mejor_valor
    
    else:
        mejor_valor = float('inf')

        for accion in estado_actual.obtener_acciones_posibles():

            estado_resultante = copiar_estado(estado_actual)
            estado_resultante.esSimulado = True

            acciones["accion_oponente"] = accion
            accion_p1, accion_p2 = resolver_accion(acciones, lado_ia)

            nuevo_combate = Combate(estado_resultante)
            nuevo_combate.ejecutar_turno_ui(estado_resultante.pokemonActivoP1, accion_p1, estado_resultante.pokemonActivoP2, accion_p2, 2, 2)

            estado_resultante = nuevo_combate.estado_del_equipo
            
            hubo_caida = False
            poda_activada = False

            #Caso 0: Se debilitaron ambos pokemones
            if estado_resultante.pokemonActivoP1.hp == 0 and estado_resultante.pokemonActivoP2.hp == 0:
                hubo_caida = True
                #La lógica del combate determinará quien gana dependiendo de la ejecución del turno
                if nuevo_combate.estado_del_equipo.esTerminal:
                    if nuevo_combate.estado_del_equipo.ganaP1:
                        valor = 99999 if lado_ia == 1 else -99999
                        mejor_valor = min(mejor_valor, valor)
                        beta = min(beta, mejor_valor)

                        if beta <= alfa:
                            poda_activada = True
                            #print(f"(!!!!!) Hay poda (!!!!!) con puntaje: {mejor_valor}")
                            break

                    elif nuevo_combate.estado_del_equipo.ganaP2:
                        valor = 99999 if lado_ia == 2 else -99999
                        mejor_valor = min(mejor_valor, valor)
                        beta = min(beta, mejor_valor)

                        if beta <= alfa:
                            poda_activada = True
                            #print(f"(!!!!!) Hay poda (!!!!!) con puntaje: {mejor_valor}")
                            break
                #Si no es terminal ambos jugadores deberán elegir un pokemon de relevo
                else:
                    elegiblesP1 = estado_resultante.pokemonesElegibles(1)
                    elegiblesP2 = estado_resultante.pokemonesElegibles(2)

                    for id_pokemonP1, pokemonP1 in elegiblesP1:
                        for id_pokemonP2, pokemonP2 in elegiblesP2:
                            nuevo_estado = copiar_estado(estado_resultante)
                            nuevo_estado.esSimulado = True
                            
                            nuevo_combate.estado_del_equipo = nuevo_estado
                            nuevo_combate.ejecutar_intercambios_por_debilitamiento(id_pokemonP1, id_pokemonP2)
                            
                            nodo_resultante = NodoV2(nuevo_estado, None, not nodo.turnoMax, nodo.profundidad + 1)

                            valor = minimax_simplificado(nodo_resultante, profundidad, acciones, lado_ia, alfa, beta, pesos)
                            mejor_valor = min(mejor_valor, valor)
                            beta = min(beta, mejor_valor)

                            if beta <= alfa:
                                poda_activada = True
                                break
                        if beta <= alfa:
                            poda_activada = True
                            break
                    if poda_activada:
                        #print(f"(!!!!!) Hay poda (!!!!!) con puntaje: {mejor_valor}")
                        break
            
            # Caso 1: Se debilitó el Pokémon del Jugador 1.
            elif estado_resultante.pokemonActivoP1.hp == 0:
                hubo_caida = True

                elegibles = estado_resultante.pokemonesElegibles(1)
                
                if elegibles:
                    for id_pokemon, pokemon in elegibles:
                        #Se crea nuevos estados pues la acción abrió la posibilidad a distintas elecciones de intercambio
                        nuevo_estado = copiar_estado(estado_resultante)
                        nuevo_estado.esSimulado = True
                        nuevo_estado.intercambiarPokemon(id_pokemon, 1)


                        nodo_resultante = NodoV2(nuevo_estado, None, not nodo.turnoMax, nodo.profundidad + 1)

                        valor = minimax_simplificado(nodo_resultante, profundidad, acciones, lado_ia, alfa, beta, pesos)
                        mejor_valor = min(mejor_valor, valor)
                        beta = min(beta, mejor_valor)

                        if beta <= alfa:
                            poda_activada = True
                            break
                    if poda_activada:
                        #print(f"(!!!!!) Hay poda (!!!!!) con puntaje: {mejor_valor}")
                        break

                else: #Lista vacia entonces no hay intercambio. Estado es terminal.
                    nodo_resultante = NodoV2(estado_resultante, None, not nodo.turnoMax, nodo.profundidad + 1)

                    valor = minimax_simplificado(nodo_resultante, profundidad, acciones, lado_ia, alfa, beta, pesos) 
                    mejor_valor = min(mejor_valor, valor)
                    beta = min(beta, mejor_valor)

                    if beta <= alfa:
                        #print(f"(!!!!!) Hay poda (!!!!!) con puntaje: {mejor_valor}")
                        break    

            # Caso 2: Se debilitó el Pokémon del Jugador 2
            elif estado_resultante.pokemonActivoP2.hp == 0:
                hubo_caida = True

                elegibles = estado_resultante.pokemonesElegibles(2)
                
                if elegibles:
                    for id_pokemon, pokemon in elegibles:
                        #Se crea nuevos estados pues la acción abrió la posibilidad a distintas elecciones de intercambio
                        nuevo_estado = copiar_estado(estado_resultante)
                        nuevo_estado.esSimulado = True
                        nuevo_estado.intercambiarPokemon(id_pokemon, 2)


                        nodo_resultante = NodoV2(nuevo_estado, None, not nodo.turnoMax, nodo.profundidad + 1)

                        valor = minimax_simplificado(nodo_resultante, profundidad, acciones, lado_ia, alfa, beta, pesos)
                        mejor_valor = min(mejor_valor, valor)
                        beta = min(beta, mejor_valor)

                        if beta <= alfa:
                            poda_activada = True
                            break
                    if poda_activada:
                        #print(f"(!!!!!) Hay poda (!!!!!) con puntaje: {mejor_valor}")
                        break

                else: #Lista vacia entonces no hay intercambio. Estado es terminal.
                    nodo_resultante = NodoV2(estado_resultante, None, not nodo.turnoMax, nodo.profundidad + 1)

                    valor = minimax_simplificado(nodo_resultante, profundidad, acciones, lado_ia, alfa, beta, pesos) 
                    mejor_valor = min(mejor_valor, valor)
                    beta = min(beta, mejor_valor)

                    if beta <= alfa:
                        #print(f"(!!!!!) Hay poda (!!!!!) con puntaje: {mejor_valor}")
                        break


            # Caso 3: Ningún Pokémon se debilitó
            if not hubo_caida:
                nodo_resultante = NodoV2(estado_resultante, None, not nodo.turnoMax, nodo.profundidad + 1)
                
                valor = minimax_simplificado(nodo_resultante, profundidad, acciones, lado_ia, alfa, beta, pesos)
                mejor_valor = min(mejor_valor, valor)
                beta = min(beta, mejor_valor)

                if beta <= alfa:
                    #print(f"(!!!!!) Hay poda (!!!!!) con puntaje: {mejor_valor}")
                    break
        
        return mejor_valor