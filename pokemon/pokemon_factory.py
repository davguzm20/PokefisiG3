import json
from pokemon.models.pokemon import Pokemon
from pokemon.models.sprites import Sprites
from pokemon.enums.pokemon_type import PokemonType
from pokemon.models.ability import Ability
from pokemon.models.move import Move
from pokemon.enums.damage_class import DamageClass

class PokemonFactory:
    pokemons = None

    @staticmethod
    def create_pokemon(data: dict) -> Pokemon:
        types = [PokemonType(type) for type in data["tipo"]]
        
        abilities = [
            Ability(
                ability["nombre"], 
                ability["descripcion"]
            )
            for ability in data["habilidades"]
        ]
        
        moves = [
            Move(
                accuracy=move["precision"],
                name=move["nombre"],
                damage_class=DamageClass(move["clase_daño"]),
                description=move["descripcion"],
                power=move["poder"],
                power_points=move["pp"],
                type=PokemonType(move["tipo"]),
                priority=move["prioridad"]
            )
            for move in data["movimientos"]
        ]
        
        sprites = Sprites(
            regular=data["sprites"]["regular"],
            back=data["sprites"]["back"],
            shiny=data["sprites"]["shiny"],
            back_shiny=data["sprites"]["back_shiny"],
            mini_regular=data["sprites"]["mini_regular"],
            mini_shiny=data["sprites"]["mini_shiny"]
        )

        return Pokemon(
            name=data["nombre"],
            types=types,
            abilities=abilities,
            hp=data["hp"],
            attack=data["atk"],
            defense=data["def"],
            special_attack=data["spa"],
            special_defense=data["spd"],
            speed=data["speed"],
            weight=data["peso"],
            moves=moves,
            sprites=sprites
        )
        
    @staticmethod
    def load_all_pokemons(filepath: str) -> list[Pokemon]:
        with open(filepath, encoding="utf-8") as file:
            data = json.load(file)
            
        PokemonFactory.pokemons = [PokemonFactory.create_pokemon(pokemon_data) 
                for pokemon_data in data.values()]
        print(f"Fueron cargados {len(PokemonFactory.pokemons)} pokemons")
        return PokemonFactory.pokemons