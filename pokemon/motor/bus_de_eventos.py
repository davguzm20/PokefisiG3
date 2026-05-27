## Utilizamos el bus de eventos para desacoplar componentes. Es implementación del patrón Observer
## Aquí se reciben los eventos que se disparan de un componente y se le envía la señal al componente suscrito para realizar la acción que necesite


class EventBus:
   
    def __init__(self):
        self.suscripciones = {}

    # (1) entonces se agrega args y kwarg
    def disparar(self, suscripcion, *args, **kwargs): #Publicar
        if suscripcion in self.suscripciones:
            for dirfuncion in self.suscripciones[suscripcion]:
                try:
                    dirfuncion(*args, **kwargs) #Una limitación de este Event Bus es que las funciones se ejecutarán pero retornaran al vacio
                except TypeError:
                    dirfuncion()

    
    def escuchar(self, nombreSuscripcion, dirfuncion): #Suscribir
        if nombreSuscripcion not in self.suscripciones:
            self.suscripciones[nombreSuscripcion] = []

        self.suscripciones[nombreSuscripcion].append(dirfuncion) 
    #Si solo lee lo que hay en direccion de memoria de la función faltaría definir parametros (1)

bus_de_eventos_global = EventBus() #Importen esta instancia, no la clase
print("Inicié el bus de eventos")