from pokemon.enums.pokemon_type import PokemonType
from pokemon.models.ability import Ability
from pokemon.models.move import Move
from pokemon.models.sprites import Sprites
from pokemon.enums.effects import Effects

class Pokemon:
    def __init__(self, name: str, types: list[PokemonType], abilities: list[Ability],
                    hp: int, attack: int, defense: int, special_attack: int, 
                    special_defense: int, speed: int, weight: int, moves: list[Move],
                    sprites: Sprites):
        self.name = name
        self.types = types
        self.abilities = abilities
        self.moves = moves
        self.hp = hp
        self.max_hp = hp
        self.attack = attack
        self.defense = defense
        self.special_attack = special_attack
        self.special_defense = special_defense
        self.speed = speed
        self.weight = weight
        self.sprites = sprites
        self.efecto: Effects = None
        self.turnos_restantes_estado = 0 #-1 Es infinito

        # ====================== Atributos extra

        self.reciente_daño_hecho = 0

        self.modificadores_stats = {
            "attack": 0,
            "defense": 0,
            "special_attack": 0,
            "special_defense": 0,
            "speed": 0,
            "accuracy": 0,
            "evasion": 0
        }

        self.aqua_ring_activo: bool = True
        self.puede_atacar: bool = True
        self.se_hace_daño: bool = True
        self.protects_seguidos: int = 0
        self.multiplicador_toxico: int = 1
        self.protegido: bool = False
        self.vida_pendiente_wish = 0
        self.vida_pendiente = 0

    def aplicar_buff_debuff(self, stat: str, cantidad: int):
        self.modificadores_stats[stat] = max(-6 ,min(6, self.modificadores_stats[stat]+cantidad))

    def obtener_stat_efectiva(self, stat_base:int, stat: str) -> float:
        """
        Obtener el valor de un stat considerando buffs y debuffs
        """
        nivel = self.modificadores_stats[stat]

        if nivel >= 0:
            multiplicador = (2 + nivel) / 2
        else:
            multiplicador = 2 / (2-nivel)
        
        return stat_base*multiplicador

    def is_alive(self) -> bool:
        return self.hp > 0