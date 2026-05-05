from pokemon.pokemon_factory import PokemonFactory
from pokemon.motor.acciones import calcular_daño
from pokemon.motor.acciones import establecer_vida, obtener_multiplicador_tipos
from pokemon.motor.combate import Combate
from pokemon.motor.estado_juego import EstadoJuego
from pokemon.agenteP.agenteP import AgenteP, elegirMovimientoAleatorio, movimiento_en_base_a_mayor_daño, heuristica_difHP
import copy, random

def configurar_entidad(num_jugador, disponible):
    print(f"\n--- Configurando Jugador {num_jugador} ---")
    print("1. Humano")
    print("2. IA")
    tipo = int(input("Seleccione tipo: "))
    
    equipo = []
    nivel_ia = None
    
    if tipo == 2:
        print("\nSeleccione nivel de IA:")
        print("1. Nivel 1 (movimiento aleatorio)")
        print("2. Nivel 2 (heurística de diferencia de HP)")
        try:
            nivel_ia = int(input("Nivel de IA: "))
        except ValueError:
            nivel_ia = 1
        if nivel_ia not in (1, 2):
            nivel_ia = 1

    for i in range(n_pokes):

        if tipo == 1: 
            print(f"\nSeleccione su Pokémon {i+1}:")
            for idx, p in enumerate(disponible):
                print(f"{idx+1}. {p.name}")
            p_sel = copy.deepcopy(disponible[int(input("Número: ")) - 1])
            
            print(f"Configure movimientos para {p_sel.name} (Máx 4):")
            todos_movs = p_sel.moves
            mis_movs = []
            
            for j in range(4):
                for idx, m in enumerate(todos_movs):
                    print(f"{idx+1}. {m.name}")
                m_sel = todos_movs.pop(int(input(f"Movimiento {j+1}: ")) - 1)
                mis_movs.append(m_sel)
            p_sel.moves = mis_movs
            equipo.append(p_sel)
        
        else: 
            p_sel = copy.deepcopy(random.choice(disponible))
            random.shuffle(p_sel.moves)
            p_sel.moves = p_sel.moves[:4]
            equipo.append(p_sel)
            print(f"IA {num_jugador} eligió a {p_sel.name} con movimientos aleatorios.")
            print(f"Nivel de IA seleccionado: {nivel_ia}")
            
    return tipo, equipo, nivel_ia

def elegir_equipo(pokemones_disponibles):
    for i, pokemon in enumerate(pokemones_disponibles):
        print(f"{i + 1}. {pokemon.name}")
    
    while True:
        try:
            seleccion = int(input("Elige un pokemon (número): ")) - 1
            if 0 <= seleccion < len(pokemones_disponibles):
                return pokemones_disponibles[seleccion]
            else:
                print("Selección inválida. Intenta de nuevo.")
        except ValueError:
            print("Por favor, ingresa un número válido.")

def elegir_movimiento_jugador(pokemon):
    for i, move in enumerate(pokemon.moves):
        print(f"{i + 1}. {move.name} (Tipo: {move.type} | Poder: {move.power})")
    
    while True:
        try:
            seleccion = int(input("Elige un movimiento (número): ")) - 1
            if 0 <= seleccion < len(pokemon.moves):
                return pokemon.moves[seleccion]
            else:
                print("Selección inválida. Intenta de nuevo.")
        except ValueError:
            print("Por favor, ingresa un número válido.")


def elegir_movimiento_ia(estado, jugador, nivel_ia):
    if nivel_ia == 2:
        if jugador == 1:
            return heuristica_difHP(estado, estado.pokemonActivoP1.moves, ia_side=1)
        return heuristica_difHP(estado, estado.pokemonActivoP2.moves, ia_side=2)
    return elegirMovimientoAleatorio(estado.pokemonActivoP1.moves if jugador == 1 else estado.pokemonActivoP2.moves)

#============================ Juego

pokemones_disponibles = PokemonFactory.load_all_pokemons("pokemon/pokemones.json")

n_pokes = 3 if int(input("1. 3vs3\n2. 4vs4\nSelección: ")) == 1 else 4

for p in pokemones_disponibles:
    p.hp *= 3

tipoP1, equipoP1, nivelP1 = configurar_entidad(1, pokemones_disponibles)
tipoP2, equipoP2, nivelP2 = configurar_entidad(2, pokemones_disponibles)


estado = EstadoJuego()
estado.setEquipo(equipoP1, equipo=1) 
estado.setEquipo(equipoP2, equipo=2) 

motor = Combate(estado)

turno = 1
while True:
    print(f"\n>>> TURNO {turno} | {estado.pokemonActivoP1.name}({estado.pokemonActivoP1.hp}hp) vs {estado.pokemonActivoP2.name}({estado.pokemonActivoP2.hp}hp)")

    if tipoP1 == 1:
        accionP1 = elegir_movimiento_jugador(estado.pokemonActivoP1)
    else:
        accionP1 = elegir_movimiento_ia(estado, 1, nivelP1)

    if tipoP2 == 1:
        accionP2 = elegir_movimiento_jugador(estado.pokemonActivoP2)
    else:
        accionP2 = elegir_movimiento_ia(estado, 2, nivelP2)

    motor.ejecutar_turno(estado.pokemonActivoP1, accionP1, estado.pokemonActivoP2, accionP2, tipoP1, tipoP2)

    if motor.verificar_ganador(): 
        break
    
    turno += 1
    if turno > 50: 
        print("Empate por agotamiento técnico.")
        break