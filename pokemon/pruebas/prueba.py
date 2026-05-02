from pokemon.motor.bus_de_eventos import bus_de_eventos_global as EventBus

def funcion_en_cualquier_componente(texto, numero = 10):
    print(texto, numero)

EventBus.escuchar("SOY_UNA_FUNCION", funcion_en_cualquier_componente)

#En otro componente..
EventBus.disparar("SOY_UNA_FUNCION", "tengo que pasar un parametro", numero=42)