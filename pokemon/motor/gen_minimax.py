import random
import copy
import time
import threading

from pokemon.motor.juego_interfaz import Juego, IA
from pokemon.pokemon_factory import PokemonFactory

pokemones_disponibles = PokemonFactory.load_all_pokemons("pokemon/pokemones.json")

def funcion_normalizadora(lista):
    sum = 0
    for gen in lista:
        #print(gen)
        sum = sum + gen

    for i in range(0,len(lista)):
        lista[i] = round(lista[i]/sum, 3)
        
def generar_individuos(n_individuos):

    lista = []
    for i in range(0,n_individuos):
        nuevo_individuo = Individuo()
        nuevo_individuo.generar_cromosoma()
        lista.append(nuevo_individuo)

    return lista

def imprimir_generacion(lista):
    for i in range(0, len(lista)):
        print(f"El individuo {i+1} tiene el cromosoma: {lista[i].cromosoma}")

class Generacion:
    def __init__(self, num_generacion = 1, individuos=[]):
        self.num_generacion = num_generacion
        self.individuos = individuos

    def generar_siguiente_generacion():
        return
        
    
        
class Individuo:
    def __init__(self, numgenes = 4):
        self.aptitud = 0
        self.numgenes = numgenes
        self.cromosoma = []
        self.fitness = None
    
    def generar_cromosoma(self):
        
        max = 10

        for i in range(0, self.numgenes):

            if i != self.numgenes -1:
                act = random.randint(0,max)
                max= max-act
                self.cromosoma.append(act)
            else:
                act = max
                self.cromosoma.append(act)

        funcion_normalizadora(self.cromosoma)
    
    def traducir_pesos_de_cromosoma(self):
        return {
            "hp": self.cromosoma[0],
            "velocidad": self.cromosoma[1],
            "tipo": self.cromosoma[2],
            "vivos": self.cromosoma[3]
        }


    def evaluar_fitness(self, num_juegos): #obtener el win rate de 30 partidas
        nuevo_juego = Juego()
        nuevo_juego.inicializar_combate()

        juegos = 0
        ganadas = 0

        nuevo_juego.configurar_jugador_como_IA(1, 3, pokemones_disponibles, 4, self.traducir_pesos_de_cromosoma())
        nuevo_juego.configurar_jugador_como_IA(2, 2, pokemones_disponibles)
        
        turno = 0
        while True:
            inicio = time.perf_counter()
            accionP1, accionP2 = nuevo_juego.generar_acciones_IA()

            nuevo_juego.iniciar_turno(accionP1, accionP2)

            #Revisión de ganador y creación de nuevo juego
            turno += 1
            if turno >= 20:
                nuevo_juego.configurar_jugador_como_IA(1, 3, pokemones_disponibles, 4, self.traducir_pesos_de_cromosoma())
                nuevo_juego.configurar_jugador_como_IA(2, 2, pokemones_disponibles)
                juegos = juegos +1
                turno = 0
                if juegos == num_juegos:
                    break

                
                
            if nuevo_juego.combate.estado_del_equipo.conteo_vivos(1) == 0:
                
                juegos = juegos +1

                if juegos == num_juegos:
                    break

                turno = 0
                nuevo_juego.configurar_jugador_como_IA(1, 3, pokemones_disponibles, 4, self.traducir_pesos_de_cromosoma())
                nuevo_juego.configurar_jugador_como_IA(2, 2, pokemones_disponibles)

            elif nuevo_juego.combate.estado_del_equipo.conteo_vivos(2) == 0:

                ganadas = ganadas +1
                juegos = juegos +1

                if juegos == num_juegos:
                    break

                turno = 0
                nuevo_juego.configurar_jugador_como_IA(1, 3, pokemones_disponibles, 4, self.traducir_pesos_de_cromosoma())
                nuevo_juego.configurar_jugador_como_IA(2, 2, pokemones_disponibles)

            fin = time.perf_counter()
            print(f"Tomo: {fin-inicio} segundos")

           
        #print(ganadas)
        #print(juegos)
        
        self.aptitud = ganadas/juegos
        return ganadas/juegos
                


def seleccion_torneo(individuos):

    random_number = random.randint(0,len(individuos) - 1)

    #Generar un segundo indice que sea diferente al anterior
    random_number_B = random_number
    while random_number_B == random_number:
        random_number_B = random.randint(0,len(individuos) - 1)

    mejor_candidato = None

    #Elegir el mejor de ambos
    if individuos[random_number].aptitud > individuos[random_number_B].aptitud:
        mejor_candidato = {
            "aptitud": individuos[random_number].aptitud,
            "individuo": individuos[random_number]
        }
    else:
        mejor_candidato = {
            "aptitud": individuos[random_number_B].aptitud,
            "individuo": individuos[random_number_B]
        }
    
    return mejor_candidato["individuo"]

def seleccion(individuos, n_parejas):
    parejas = []

    for _ in range(0, n_parejas):
        
        padre_A = seleccion_torneo(individuos)
        padre_B = seleccion_torneo(individuos)
        
        #Los dos indices acceden a dos individuos a agrupar en parejas
        parejas.append(
            (padre_A, padre_B)
        )


    return parejas

def mutar(individuo, probabilidad_de_mutar):
    cromosoma = individuo.cromosoma
    
    for i in range(0, len(cromosoma)):
        probabilidad = random.uniform(0,1)

        if probabilidad <= probabilidad_de_mutar:
            cromosoma[i] += random.choice([-0.05, 0.05])
            cromosoma[i] = round(max(0, cromosoma[i]),3)
            
        
def ajustar(individuo):
    funcion_normalizadora(individuo.cromosoma)


def cruce(pareja, probabilidad_de_cruce):
    padre_A, padre_B = pareja
    
    tamaño_cromosoma = len(padre_A.cromosoma)

    hijo_A = Individuo()
    hijo_B = Individuo()

    probabilidad = random.uniform(0,1)
    p_cruce = random.randint(1, tamaño_cromosoma - 1)

    if probabilidad <= probabilidad_de_cruce:
        hijo_A.cromosoma = padre_A.cromosoma[:p_cruce] + padre_B.cromosoma[p_cruce:]
        hijo_B.cromosoma = padre_B.cromosoma[:p_cruce] + padre_A.cromosoma[p_cruce:]

    else:
        hijo_A.cromosoma = padre_A.cromosoma.copy()
        hijo_B.cromosoma = padre_B.cromosoma.copy()
    
    mutar(hijo_A, 0.05)
    mutar(hijo_B, 0.05)

    ajustar(hijo_A)
    ajustar(hijo_B)

    return (hijo_A, hijo_B)
    


# =================== Algoritmo genético 
generacion_inicial = Generacion(individuos= generar_individuos(10))
generacion = 1

mejor_individuo = {
    "aptitud": 0,
    "individuo": None
}

historial = []

while True:
    inicio = time.perf_counter()
    generacion_actual = generacion_inicial if generacion == 1 else nueva_generacion
    
    max_aptitud_generacion = -1
    mejor_de_generacion = None
    #Evaluar fitness de los individuos y retener el mejor
    for i in range(0, len(generacion_actual.individuos)):
        generacion_actual.individuos[i].evaluar_fitness(20)
        
        print(f" ========================== Individuo {i} de la generación {generacion} evaluado. Fitness {generacion_actual.individuos[i].aptitud} ==========================")
        if generacion_actual.individuos[i].aptitud > max_aptitud_generacion:
            mejor_de_generacion = generacion_actual.individuos[i]
            max_aptitud_generacion = generacion_actual.individuos[i].aptitud

        if generacion_actual.individuos[i].aptitud > mejor_individuo["aptitud"]:
            mejor_individuo["aptitud"] = generacion_actual.individuos[i].aptitud
            mejor_individuo["individuo"] = copy.deepcopy(generacion_actual.individuos[i])
    
    historial.append({
        "generacion": generacion,
        "individuos": [(ind.traducir_pesos_de_cromosoma(), ind.aptitud) for ind in generacion_actual.individuos]
    })

    if generacion == 20 or mejor_individuo["aptitud"] == 1.0: break # La estructura hace necesario que el algoritmo se detenga justo en este momento, después de calcular el fitness de la siguiente generación

    #Seleccion por torneo
    seleccionados = seleccion(generacion_actual.individuos, 5) #Lista de tuplas

    #Realizar el cruce (Cruce y mutación se dan a la vez)

    nuevos_individuos = []
    for i in range(0, len(seleccionados)):
        hijo_A, hijo_B = cruce(seleccionados[i], 0.7)

        nuevos_individuos.append(hijo_A)
        nuevos_individuos.append(hijo_B)
    
    #Elitismo
    ya_paso_el_padre = any(hijo.cromosoma == mejor_de_generacion.cromosoma for hijo in nuevos_individuos)
    if not ya_paso_el_padre:
        nuevos_individuos[0] = copy.deepcopy(mejor_de_generacion)

    nueva_generacion = Generacion(num_generacion= generacion +1, individuos= nuevos_individuos)

    print(nueva_generacion.individuos)
    #Continuar a la siguiente generación

    fin = time.perf_counter()
    print(f"Tomo: {fin-inicio} segundos")
    generacion += 1

print(f"El mejor individuo encontrado es: {mejor_individuo['individuo']} con una aptitud de {mejor_individuo['aptitud']}")
print(f"Su cromosoma es {mejor_individuo['individuo'].cromosoma}")

for entrada in historial:
    print(entrada)