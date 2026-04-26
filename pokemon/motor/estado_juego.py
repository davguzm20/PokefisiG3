
class EstadoJuego:
    
    def __init__(self):
        self.equipoP1 = []
        self.equipoP2 = []        
        self.pokemonActivoP1 = None
        self.pokemonActivoP2 = None
    
    #La UI debería disparar el evento cuando el equipo es armado
    #Pasar una lista de pokemones. El equipo es 1 del jugador o 2 de la IA
    def setEquipo(self, pokemones, equipo=1):
        if (equipo == 1): 
            self.equipoP1 = pokemones 
            self.pokemonActivoP1 = pokemones[0]

        else: 
            self.equipoP2 = pokemones 
            self.pokemonActivoP2 = pokemones[0]
    
    #Pasale el indice del pokemon al que quieres cambiar. La 
    def intercambiarPokemon(self, indicePokemonDentro, equipo=1):
        if(equipo == 1): 
            temp = self.equipoP1[0]
            self.equipoP1[0] = self.equipoP1[indicePokemonDentro]
            self.equipoP1[indicePokemonDentro] = temp
            
            self.pokemonActivoP1 = self.equipoP1[0]

        else:
            temp = self.equipoP2[0]
            self.equipoP2[0] = self.equipoP2[indicePokemonDentro]
            self.equipoP2[indicePokemonDentro] = temp

            self.pokemonActivoP2 = self.equipoP2[0]
        

        
    