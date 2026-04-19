from pokemon.enums.damage_class import DamageClass
from pokemon.enums.pokemon_type import PokemonType

class Move:
    def __init__(self, accuracy: int, name: str, damage_class: DamageClass, description: str, 
                    power: int, power_points: int, type: PokemonType, priority: int):
        self.accuracy = accuracy
        self.name = name
        self.damage_class = damage_class
        self.description = description
        self.power = power
        self.power_points = power_points
        self.current_power_points = power_points
        self.type = type
        self.priority = priority

    def is_usable(self) -> bool:
        return self.current_power_points > 0