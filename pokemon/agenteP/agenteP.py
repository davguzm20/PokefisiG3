import random, copy
from pokemon.motor.estado_juego import EstadoJuego
from pokemon.motor.acciones import calcular_daño, obtener_multiplicador_tipos, establecer_vida
from pokemon.models.pokemon import Pokemon
from pokemon.models.pokemon import Move
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

def heuristica_diff_HP(estado_juego, movimientos, lado):

    if not isinstance(estado_juego, EstadoJuego) and not movimientos:
        return
    
    atacante, defensor, hp_poke_ia, hp_poke_oponente = resolver_lados(estado_juego, lado)

    for movimiento in movimientos:
        danio = calcular_daño(atacante, defensor, movimiento)


#Inicio de Heuristica avanzada para nivel 3
#funcion base para considerar pesos

def heuristica_avanzada(estado_juego, movimiento, pesos):
    if isinstance(movimiento, dict):
        indice_intercambio = movimiento["intercambio"]
        movimiento = movimiento["movimiento"] if movimiento["movimiento"] else movimiento
        

    # Normalizar cada componente entre 0 y 1
    if isinstance(estado_juego, EstadoJuego):
        hp_ratio = (estado_juego.pokemonActivoP2.hp - estado_juego.pokemonActivoP1.hp) / max(estado_juego.pokemonActivoP2.hp + estado_juego.pokemonActivoP1.hp, 1)
        velocidad = (estado_juego.pokemonActivoP1.speed - estado_juego.pokemonActivoP2.speed) / max(estado_juego.pokemonActivoP1.speed + estado_juego.pokemonActivoP2.speed, 1)
        if isinstance(movimiento, Move):
            ventaja_tipo = obtener_multiplicador_tipos(movimiento, estado_juego.pokemonActivoP1, estado_juego.pokemonActivoP2)
        else: ventaja_tipo = 0.2
        pokemons_vivos = estado_juego.conteo_vivos(2) - estado_juego.conteo_vivos(1) / max(len(estado_juego.equipoP1), len(estado_juego.equipoP2), 1)

    return (
        pesos["hp"] * hp_ratio +
        pesos["velocidad"] * velocidad +
        pesos["tipo"] * ventaja_tipo +
        pesos["vivos"] * pokemons_vivos
    )


def tasa_de_especialización(pokemon_lado_ia, pokemon_lado_oponente):

    if not isinstance(pokemon_lado_oponente, Pokemon) and not isinstance(pokemon_lado_ia, Pokemon):
        return
    
    spec_oponente = pokemon_lado_oponente.attack - pokemon_lado_oponente.special_attack
    spec_def_oponente = pokemon_lado_oponente.defense - pokemon_lado_oponente.special_defense
    
    spec_def_ia = pokemon_lado_ia.defense - pokemon_lado_ia.special_defense
    spec_ia = pokemon_lado_ia.attack - pokemon_lado_ia.special_attack

    ##Si sale negativo se especializa en fisico, si no en especial. ¿Pero qué tanto se especializa?
    
    magnitud_de_especializacion_oponente = spec_oponente/ ( pokemon_lado_oponente.attack + pokemon_lado_oponente.special_attack) #¿Por qué la suma de ambos?

    #Si el ataque fisico del oponente es *magnitud* mayor que mi defensa fisica, significa que soy debil ante él. ¿Pero qué tan débil?
    

    return




def funcion_heuristica_avanzada(estado_juego, estado_anterior, movimiento, pesos, lado_ia):
    
    # Para hacer una heuristica necesito saber información de un estado que me ayude a evaluar qué tan cerca estoy de una meta
    # En este caso nuestra meta sería obtener un estado donde el oponente 

    # Esto será implementado con minimax
    # Ya que es una función de utilidad que será usada con algoritmo evolutivo los valores que devuelva deben ser de 0 a 1
    
    # Necesito: definir heuristicas, evaluar el estado en base a ellas, y cuantificar eso en un rango de 0 a 1

    # Heurística 1: Si soy suficientemente rápido para pegar este movimiento que sería letal, lo mejor es atacar
    
    # Heurística 2: Si mi pokemon es capaz de resistir bastante bien los ataques del pokemon oponente no hace falta cambiar. 
    # Si es al revés hace falta buscar un pokemon que sea capaz de resistir los ataques del oponente
    
    # Generalmente los pokemones se especializan en fisico, magico, y a veces balanceados. Puedo evaluar eso con una tasa de especialización. Tasa de especialización en defensa y ataque
    # Mientras mayor diferencia haya entre su tipo de daño especializado y mi defensa que lo soporta más riesgo hay
    
    # Una mayor tasa de especialización

    ant_pokemon_lado_ia, ant_pokemon_lado_oponente, ant_hp_poke_ia, ant_hp_poke_oponente = resolver_lados(estado_anterior, lado_ia)
    pokemon_lado_ia, pokemon_lado_oponente, hp_poke_ia, hp_poke_oponente = resolver_lados(estado_juego, lado_ia)


    # Normalizar cada componente entre 0 y 1
    if isinstance(estado_juego, EstadoJuego):
        danio_hecho = ant_hp_poke_oponente - hp_poke_oponente ## Puedo hacer tanto daño con el operador que me llevó a este estado
        danio_recibido = ant_hp_poke_ia - hp_poke_ia ## Puedo resistir tanto daño con la acción del oponente que me llevó a este estado
        velocidad = (pokemon_lado_ia.speed - pokemon_lado_oponente.speed) / max(pokemon_lado_ia.speed + pokemon_lado_oponente.speed, 1) ## Ejecutar mis acciones más rapido que el oponente me da cierta magnitud de ventaja. Qué es una magnitud mayor cuando el oponente esta bajo de vida

        hp_ratio = (hp_poke_ia - hp_poke_oponente) / max(hp_poke_ia + hp_poke_oponente, 1) 
        ventaja_tipo_movimiento = obtener_multiplicador_tipos(movimiento, pokemon_lado_ia, pokemon_lado_oponente)
        pokemons_vivos = estado_juego.conteo_vivos(2) - estado_juego.conteo_vivos(1) / max(len(estado_juego.equipoP1), len(estado_juego.equipoP2), 1)
    
    return (
        pesos["hp"] * hp_ratio +
        pesos["velocidad"] * velocidad +
        pesos["tipo"] * ventaja_tipo_movimiento +
        pesos["vivos"] * pokemons_vivos
    )
 
#----------------------------------------------------------------------------------- Mini Max == Preferiblemente hasta 4 de profundidad?

pesos_mock = {
    "hp": 0.3,
    "velocidad": 0.2,
    "tipo": 0.3,
    "vivos": 0.2
}
operadores = {
    "intercambiar_pokemon": [1,2,3,4],
    "elegir_movimiento": [1,2,3,4]
}
global mejor_movimiento

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

#Retorna si el nodo debe ser podado o no
def poda_alfa_beta(nodo): #Un padre visita las hojas y actualiza
    if not isinstance(nodo, Nodo):
        return
    
    if not nodo.padre: return False
    # Al principio, los nodos no tienen ni alfa ni beta. Los valores de alfa y beta se van heredando de los padres
    if not nodo.alfa: nodo.alfa = nodo.padre.alfa
    if not nodo.beta: nodo.beta = nodo.padre.beta

    #Pero lo principal en la poda es obtener el puntaje asociado a un nodo dependiendo de si el turno es de Min o Max
    #En este caso las hojas actualizan al padre, entonces el turno actual es el del padre
    if nodo.puntaje:
        if nodo.padre.turnoDeMax: #Max elegirá el mayor valor disponible, reemplazará a alfa
            if nodo.puntaje > nodo.padre.alfa:
                nodo.padre.alfa = nodo.puntaje
                print(f'AAAAAAAAAAAAAAAAAAAAAAAAAAAA {nodo.operador}')
                mejor_movimiento = nodo.operador
                if nodo.padre.profundidad == 0:
                    mejor_movimiento = nodo.operador
                    print(mejor_movimiento)
                    
            if nodo.padre.alfa >= nodo.padre.beta:
                return True
        elif not nodo.padre.turnoDeMax:
            if nodo.puntaje < nodo.padre.beta:
                mejor_movimiento = nodo.operador
                print(f'AAAAAAAAAAAAAAAAAAAAAAAAAAAA {nodo.operador}')
                nodo.padre.beta = nodo.puntaje

            if nodo.padre.beta <= nodo.padre.alfa:
                return True
    
    return False

def Mini_Max(estado_juego, profundidad, lado_ia):

    pila = []
    nodo_estado = Nodo(estado_juego, 0)

    lado_max = lado_ia
    lado_min = 2 if lado_ia == 1 else 1
    pila.append(nodo_estado)
    
    alfa = -float('inf') #No puede disminuir
    beta = float('inf') #No puede aumentar 
    nodo_estado.alfa = alfa
    nodo_estado.beta = beta

    while pila:
        #Esto es una búsqueda, solo que en un caso es turno de Max y en otro de Min, y además no se siguen generando hijos hasta cierta profundidad
        print(f'Nueva pila: {pila}')
        nodo_actual = pila.pop()
        estado_actual = nodo_actual.estado

        #(3)... Los estados visitados deben ser podados dependiendo del puntaje y si el turno es de Min o Max
        fue_podado = poda_alfa_beta(nodo_actual)
        if fue_podado:
            while pila and pila[-1].padre == nodo_actual.padre:
                pila.pop()
            continue

        #()Los estados generados dependen de si un turno es de Min o Max
        lado_actual = lado_max if nodo_actual.turnoDeMax else lado_min

        if nodo_actual.turnoDeMax: print("========================= Es turno de Max =======================")
        else: print("========================= Es turno de Min =======================")

        print(f'Se tomó un elemento de la pila: {nodo_actual}')
        #Entonces generar sucesores depende de si el equipo es de min o max, información que brinda lado_actual
        sucesores = generar_sucesores(estado_actual, lado_actual)

        #(2)... (Backtracking) Necesito volver a visitar al padre después de haber visitado los sucesores para poder seguir el proceso de MiniMax y poda. Entonces lo pondré en la pila. Saldrá al final de los sucesores por ser LIFO
        if nodo_actual.sucesores_no_generados and nodo_actual.profundidad != profundidad: 
            pila.append(nodo_actual)
        
        #Se va generando un arbol en base a min y a max. Donde los sucesores están encapsulados en un nodo que permite generar el arbol correctamente
        if nodo_actual.profundidad != profundidad and nodo_actual.sucesores_no_generados:
            nodo_actual.sucesores_no_generados = False
            for sucesor in sucesores:
                print(sucesor.equipoP1[0].name)
                nodo_sucesor = Nodo(sucesor, nodo_actual.profundidad + 1, not nodo_actual.turnoDeMax)
                
                nodo_sucesor.padre = nodo_actual #Apunto al padre porque necesito actualizar los puntajes y accederlos. No se guardan en la pila una vez se generaron los sucesores.

                pila.append(nodo_sucesor)
        
        
        #Aquí se califica el estado. Calificar el estado permitirá que cuando se visite un nodo este pueda ser podado
        if nodo_actual.profundidad == profundidad: #Solo las hojas son calificadas

            nodo_actual.puntaje = heuristica_avanzada(estado_actual, estado_actual.operador, pesos_mock)
            print(f"califique este estado con {nodo_actual.puntaje}")
        
        #Cómo se supone que devuelva el movimiento? (2)..
        
    if nodo_actual.profundidad == 0 and not nodo_actual.sucesores_no_generados:
            print(f'El mejor movimiento es: {mejor_movimiento}')
            return mejor_movimiento
    return None



def poda_alfa_betav2(nodo):
    if not isinstance(nodo, Nodo):
        return 


    return 0


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
                hijoMax = hijo.estado
        else:
            if hijo.puntaje < valMin:
                valMin = hijo.puntaje
                hijoMin = hijo.estado

    return [(hijoMax,valMax),(hijoMin,valMin)]
        

def minimax(nodo, profundidad, lado_ia):
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

        lado_actual = lado_max if nodo.turnoMax else lado_min
        if nodo_actual.turnoMax: print("========================= Es turno de Max =======================")
        else: print("========================= Es turno de Min =======================")
        

        # ====== (2) .. Cuando se vuelva al padre despues de puntuar sus hijos (y que existan) es el momento de elegir Min_Max
        if nodo_actual.profundidad != profundidad and nodo_actual.hijos:
            
            indice_hijo_elegido = 0 if nodo_actual.turnoMax else 1
            hijo_elegido = evaluarminmax(nodo_actual.hijos, nodo_actual.turnoMax)
            
            nodo_actual.puntaje = hijo_elegido[indice_hijo_elegido][1]
            nodo_actual.operador = hijo_elegido[indice_hijo_elegido][0].operador


        # ====== Se va generando sucesores solo si el nodo no es una hoja. En este caso eso depende de: la profundidad del nodo actual es la maxima, o si en este nodo el estado devuelve un juego terminado
        print(f"Profundidad de: {nodo_actual.profundidad}")
        if nodo_actual.profundidad != profundidad and not nodo_actual.hijos:
            sucesores = generar_sucesores(estado_actual, lado_actual)
            hijos = []

            #El nodo actual debe de apilarse para volver a él y poder elegir de sus hijos
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

        if nodo_actual.profundidad == 0 and nodo_actual.operador:
            print(f'Con un puntaje de {nodo_actual.puntaje}')
            if nodo_actual.operador["movimiento"]:
                print(f'El movimiento elegido es: {nodo_actual.operador["movimiento"].name}')
            if nodo_actual.operador["intercambio"]:
                print(f'Se hizo un intercambio con: {nodo_actual.operador["intercambio"]}')
            

    