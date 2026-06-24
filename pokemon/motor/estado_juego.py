from pokemon.motor.bus_de_eventos import bus_de_eventos_global
from pokemon.models.pokemon import Pokemon
from pokemon.enums.effects import Effects

class EstadoJuego:
    
    def __init__(self):
        self.equipoP1: list[Pokemon] = []
        self.equipoP2: list[Pokemon] = []        
        self.pokemonActivoP1: Pokemon = None
        self.pokemonActivoP2: Pokemon = None
        self.estado_anterior = None
        self.operador = None
        self.esSimulado = False
        self.esTerminal = False
        self.ganaP1 = False
        self.ganaP2 = False
    
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
        
    def getEquipo(self, equipo):
        if (equipo == 1): 
            return self.equipoP1
        else: 
            return self.equipoP2
    
    def pokemonesElegibles(self, equipo = 1):
        equipo_objetivo = self.equipoP1 if equipo == 1 else self.equipoP2
        lista = []
        for index, ref_pokemon in enumerate(equipo_objetivo):
            if ref_pokemon.hp > 0:
                if index != 0:
                    lista.append((index, ref_pokemon))
        return lista
    
    def intercambiarPokemon(self, indicePokemonDentro, equipo=1):
        if indicePokemonDentro == 0: return

        equipo_objetivo = self.equipoP1 if equipo == 1 else self.equipoP2
        saliente = equipo_objetivo[0]

        if saliente.efecto == Effects.TOXIC: 
            saliente.multiplicador_toxico = 1
        saliente.aqua_ring_activo = False
        saliente.protegido = False
        saliente.lock_on_activo = False
        saliente.endure_activo = False
        saliente.protects_seguidos = 0
        saliente.puede_atacar = True

        for stat in saliente.modificadores_stats:
            saliente.modificadores_stats[stat] = 0
            
        temp = equipo_objetivo[0]
        equipo_objetivo[0] = equipo_objetivo[indicePokemonDentro]
        equipo_objetivo[indicePokemonDentro] = temp
        
        if equipo == 1:
            self.pokemonActivoP1 = equipo_objetivo[0]
        else:
            self.pokemonActivoP2 = equipo_objetivo[0]
            
        if not self.esSimulado:
            self._emit(f'El jugador {equipo} envía a {equipo_objetivo[0].name}')
    
    def conteo_vivos(self, equipo=1):
        cuenta = 0
        equipo_objetivo = self.equipoP1 if equipo == 1 else self.equipoP2
        for pokemon in equipo_objetivo:
            if pokemon.hp > 0: 
                cuenta += 1
        return cuenta

    def obtener_acciones_posibles(self, equipo = 1) -> list[dict]:
        acciones = []
        posibles_cambios = self.pokemonesElegibles(equipo)
        pokemonActivo = self.pokemonActivoP1 if equipo == 1 else self.pokemonActivoP2

        if pokemonActivo.hp > 0:
            for movimiento in pokemonActivo.moves:
                acciones.append({
                    "intercambio_index": None,
                    "movimiento": movimiento
                })

        for indice_cambio, ref_pokemon in posibles_cambios:
            acciones.append({
                "intercambio_index": indice_cambio,
                "movimiento": None
            })

        return acciones