from pokemon.enums.pokemon_type import PokemonType
from pokemon.models.ability import Ability
from pokemon.models.move import Move
from pokemon.models.sprites import Sprites

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

    def is_alive(self) -> bool:
        return self.hp > 0