from pokemon.motor.bus_de_eventos import bus_de_eventos_global

class EstadoJuego:
    
    def __init__(self):
        self.equipoP1 = []
        self.equipoP2 = []        
        self.pokemonActivoP1 = None
        self.pokemonActivoP2 = None
    
    #La UI debería disparar el evento cuando el equipo es armado
    #Pasar una lista de pokemones. El equipo es 1 del jugador o 2 de la IA
    def _emit(self, text):
        print(text)
        bus_de_eventos_global.disparar("MENSAJE_COMBATE", text)

    def setEquipo(self, pokemones, equipo=1):
        if (equipo == 1): 
            self.equipoP1 = pokemones 
            self.pokemonActivoP1 = pokemones[0]

        else: 
            self.equipoP2 = pokemones 
            self.pokemonActivoP2 = pokemones[0]
    
    def pokemonesElegibles(self, equipo = 1):
        equipo_objetivo = self.equipoP1 if equipo == 1 else self.equipoP2

        return [(i, p) for i, p in enumerate(equipo_objetivo) if p.hp > 0]
    
    #Pasale el indice del pokemon al que quieres cambiar. La 
    def intercambiarPokemon(self, indicePokemonDentro, equipo=1):
        equipo_objetivo = self.equipoP1 if equipo == 1 else self.equipoP2
        
        temp = equipo_objetivo[0]
        equipo_objetivo[0] = equipo_objetivo[indicePokemonDentro]
        equipo_objetivo[indicePokemonDentro] = temp
        
        if equipo == 1:
            self.pokemonActivoP1 = equipo_objetivo[0]
        else:
            self.pokemonActivoP2 = equipo_objetivo[0]
        
        self._emit(f'El jugador {equipo}  envía a {equipo_objetivo[0].name}')
    
    def conteo_vivos(self, equipo=1):
        cuenta = 0
        
        if(equipo==1):
            for pokemon in self.equipoP1:
                if pokemon.hp != 0: cuenta = cuenta + 1
        else:
            for pokemon in self.equipoP2:
                if pokemon.hp != 0: cuenta = cuenta + 1

        return cuenta

        
    