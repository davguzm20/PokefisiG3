import threading
import time
from pokemon.agenteP.agenteP import mini_max_recursivo
from pokemon.motor.bus_de_eventos import bus_de_eventos_global

def esperar():
    bus_de_eventos_global.disparar("MENSAJE_COMBATE", "La IA está pensando...")


def mini_max_recursivo_thread(nodo, profundidad, lado_ia, max):
    x = threading.Thread(target=mini_max_recursivo_t, args=(nodo, profundidad, lado_ia, max))
    x.start()
    x.join()


def mini_max_recursivo_t(nodo, profundidad, lado_ia, max):
    print("Minimax se está ejecutando en otro hilo")
    inicio = time.perf_counter()
    raiz = mini_max_recursivo(nodo, profundidad, lado_ia, max)

    fin = time.perf_counter()

    tiempo = fin - inicio
    print(f"Minimax tomó {tiempo} segundos")

    return  raiz
