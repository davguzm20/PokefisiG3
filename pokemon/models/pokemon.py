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

        # ======================

        self.puede_atacar: bool = True
        self.se_hace_daño: bool = True
        self.multiplicador_toxico: int = 1


    def is_alive(self) -> bool:
        return self.hp > 0