class EstadoEquipo:
    
    def __init__(self):
        self.equipoP1 = []
        self.equipoP2 = []        
        self.pokemonActivoP1 = None
        self.pokemonActivoP2 = None
    
    #La UI debería disparar el evento cuando el equipo es armado
    #El equipo es 1 o 2
    def setEquipo(self, pokemones, equipo=1):
        if (equipo == 1): 
            self.equipoP1 = pokemones 
            self.pokemonActivoP1 = pokemones[0]

        else: 
            self.equipoP2 = pokemones 
            self.pokemonActivoP2 = pokemones[0]
    
    
    