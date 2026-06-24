from pokemon.enums.damage_class import DamageClass
from pokemon.enums.pokemon_type import PokemonType
from pokemon.models.pokemon import Pokemon

efectividad_base = {
    PokemonType.NORMAL: {PokemonType.ROCK: 0.5, PokemonType.GHOST: 0.0, PokemonType.STEEL: 0.5},
    PokemonType.FIRE: {PokemonType.FIRE: 0.5, PokemonType.WATER: 0.5, PokemonType.GRASS: 2.0, PokemonType.ICE: 2.0, PokemonType.BUG: 2.0, PokemonType.ROCK: 0.5, PokemonType.DRAGON: 0.5, PokemonType.STEEL: 2.0},
    PokemonType.WATER: {PokemonType.FIRE: 2.0, PokemonType.WATER: 0.5, PokemonType.GRASS: 0.5, PokemonType.GROUND: 2.0, PokemonType.ROCK: 2.0, PokemonType.DRAGON: 0.5},
    PokemonType.ELECTRIC: {PokemonType.WATER: 2.0, PokemonType.ELECTRIC: 0.5, PokemonType.GRASS: 0.5, PokemonType.GROUND: 0.0, PokemonType.FLYING: 2.0, PokemonType.DRAGON: 0.5},
    PokemonType.GRASS: {PokemonType.FIRE: 0.5, PokemonType.WATER: 2.0, PokemonType.GRASS: 0.5, PokemonType.POISON: 0.5, PokemonType.GROUND: 2.0, PokemonType.FLYING: 0.5, PokemonType.BUG: 0.5, PokemonType.ROCK: 2.0, PokemonType.DRAGON: 0.5, PokemonType.STEEL: 0.5},
    PokemonType.ICE: {PokemonType.FIRE: 0.5, PokemonType.WATER: 0.5, PokemonType.GRASS: 2.0, PokemonType.ICE: 0.5, PokemonType.GROUND: 2.0, PokemonType.FLYING: 2.0, PokemonType.DRAGON: 2.0, PokemonType.STEEL: 0.5},
    PokemonType.FIGHTING: {PokemonType.NORMAL: 2.0, PokemonType.ICE: 2.0, PokemonType.POISON: 0.5, PokemonType.FLYING: 0.5, PokemonType.PSYCHIC: 0.5, PokemonType.BUG: 0.5, PokemonType.ROCK: 2.0, PokemonType.GHOST: 0.0, PokemonType.DARK: 2.0, PokemonType.STEEL: 2.0, PokemonType.FAIRY: 0.5},
    PokemonType.POISON: {PokemonType.GRASS: 2.0, PokemonType.POISON: 0.5, PokemonType.GROUND: 0.5, PokemonType.ROCK: 0.5, PokemonType.GHOST: 0.5, PokemonType.STEEL: 0.0, PokemonType.FAIRY: 2.0},
    PokemonType.GROUND: {PokemonType.FIRE: 2.0, PokemonType.ELECTRIC: 2.0, PokemonType.GRASS: 0.5, PokemonType.POISON: 2.0, PokemonType.FLYING: 0.0, PokemonType.BUG: 0.5, PokemonType.ROCK: 2.0, PokemonType.STEEL: 2.0},
    PokemonType.FLYING: {PokemonType.ELECTRIC: 0.5, PokemonType.GRASS: 2.0, PokemonType.FIGHTING: 2.0, PokemonType.BUG: 2.0, PokemonType.ROCK: 0.5, PokemonType.STEEL: 0.5},
    PokemonType.PSYCHIC: {PokemonType.FIGHTING: 2.0, PokemonType.POISON: 2.0, PokemonType.PSYCHIC: 0.5, PokemonType.DARK: 0.0, PokemonType.STEEL: 0.5},
    PokemonType.BUG: {PokemonType.FIRE: 0.5, PokemonType.GRASS: 2.0, PokemonType.FIGHTING: 0.5, PokemonType.POISON: 0.5, PokemonType.FLYING: 0.5, PokemonType.PSYCHIC: 2.0, PokemonType.GHOST: 0.5, PokemonType.DARK: 2.0, PokemonType.STEEL: 0.5, PokemonType.FAIRY: 0.5},
    PokemonType.ROCK: {PokemonType.FIRE: 2.0, PokemonType.ICE: 2.0, PokemonType.FIGHTING: 0.5, PokemonType.GROUND: 0.5, PokemonType.FLYING: 2.0, PokemonType.BUG: 2.0, PokemonType.STEEL: 0.5},
    PokemonType.GHOST: {PokemonType.NORMAL: 0.0, PokemonType.PSYCHIC: 2.0, PokemonType.GHOST: 2.0, PokemonType.DARK: 0.5},
    PokemonType.DRAGON: {PokemonType.DRAGON: 2.0, PokemonType.STEEL: 0.5, PokemonType.FAIRY: 0.0},
    PokemonType.STEEL: {PokemonType.FIRE: 0.5, PokemonType.WATER: 0.5, PokemonType.ELECTRIC: 0.5, PokemonType.ICE: 2.0, PokemonType.ROCK: 2.0, PokemonType.STEEL: 0.5, PokemonType.FAIRY: 2.0},
    PokemonType.DARK: {PokemonType.FIGHTING: 0.5, PokemonType.PSYCHIC: 2.0, PokemonType.GHOST: 2.0, PokemonType.DARK: 0.5, PokemonType.FAIRY: 0.5},
    PokemonType.FAIRY: {PokemonType.FIRE: 0.5, PokemonType.FIGHTING: 2.0, PokemonType.POISON: 0.5, PokemonType.DRAGON: 2.0, PokemonType.STEEL: 0.5, PokemonType.DARK: 2.0}
}

def obtener_multiplicador_tipos(tipo_ataque, tipos_defensor, tipos_atacante):
    multiplicador = 1.0
    
    if tipo_ataque not in efectividad_base:
        return multiplicador

    tabla_atacante = efectividad_base[tipo_ataque]

    for t_def in tipos_defensor:
        if t_def in tabla_atacante:
            multiplicador *= tabla_atacante[t_def]
    
    if tipo_ataque in tipos_atacante: multiplicador *= 1.5
    return multiplicador

def calcular_daño(atacante: Pokemon, defensor: Pokemon, movimiento):
    if movimiento.damage_class == DamageClass.PHYSICAL:
        ataque = atacante.obtener_stat_efectiva(atacante.attack, "attack")
        defensa = defensor.obtener_stat_efectiva(defensor.defense, "defense")
    elif movimiento.damage_class == DamageClass.SPECIAL:
        ataque = atacante.obtener_stat_efectiva(atacante.special_attack, "special_attack")
        defensa = defensor.obtener_stat_efectiva(defensor.special_defense, "special_defense")

    poder = movimiento.power
    nivel = 50  #Esto podría ponerse en otro lugar
    
    if not poder: #Pequeño parche para evitar por el momento que un movimiento de status trabe el programa
       return 0

    daño_base = ((( (2 * nivel / 5) + 2 ) * poder * (ataque / defensa)) / 50) + 2
    multiplicador = obtener_multiplicador_tipos(movimiento.type, defensor.types, atacante.types)

    daño_final = round(daño_base*multiplicador, 3)

    return daño_final

def establecer_vida(defensor, dañofinal):
    defensor.hp = defensor.hp - dañofinal
    if defensor.hp < 0: defensor.hp = 0
    return defensor.hp
