import random, copy
from pokemon.pokemon_factory import PokemonFactory
from pokemon.models.pokemon import Pokemon

class TeamFactory:
    BLUEPRINTS_4VS4 = [
        ["ivysaur", "charmeleon", "wartortle", "kadabra"],
        ["bayleef", "quilava", "croconaw", "chansey"],
        ["gloom", "magmar", "seadra", "porygon"],
        ["weepinbell", "charmeleon", "poliwhirl", "electabuzz"],
        ["quilava", "ivysaur", "magmar", "chansey"],
        ["wartortle", "seadra", "magneton", "gloom"],
        ["rhydon", "graveler", "magneton", "golbat"],
        ["magmar", "seadra", "weepinbell", "clefairy"],
        ["primeape", "machoke", "rhydon", "clefairy"],
        ["kadabra", "haunter", "magneton", "ivysaur"],
        ["dragonair", "croconaw", "golbat", "porygon"],
        ["magmar", "wartortle", "bayleef", "machoke"],
        ["chansey", "haunter", "rhydon", "magneton"],
        ["gloom", "weepinbell", "chansey", "poliwhirl"],
        ["magneton", "clefairy", "togetic", "golbat"],
        ["togetic", "wartortle", "bayleef", "flaaffy"],
        ["pikachu", "haunter", "graveler", "charmeleon"],
        ["kadabra", "machoke", "ivysaur", "croconaw"],
        ["jigglypuff", "dragonair", "electabuzz", "gloom"],
        ["dragonair", "chansey", "charmeleon", "wartortle"]
    ]

    BLUEPRINTS_3VS3 = [
        ["ivysaur", "charmeleon", "wartortle"],     
        ["bayleef", "quilava", "croconaw"],       
        ["kadabra", "chansey", "rhydon"],         
        ["haunter", "magneton", "seadra"],        
        ["gloom", "magmar", "porygon"],           
        ["weepinbell", "poliwhirl", "electabuzz"],
        ["quilava", "ivysaur", "clefairy"],       
        ["wartortle", "magneton", "golbat"],      
        ["graveler", "dragonair", "togetic"],     
        ["primeape", "rhydon", "togetic"],        
        ["machoke", "croconaw", "flaaffy"],       
        ["pikachu", "haunter", "graveler"],       
        ["jigglypuff", "dragonair", "charmeleon"],
        ["chansey", "magneton", "golbat"],        
        ["kadabra", "machoke", "ivysaur"],        
        ["seadra", "magmar", "gloom"],            
        ["croconaw", "quilava", "togetic"],       
        ["dragonair", "chansey", "wartortle"],    
        ["electabuzz", "rhydon", "gloom"],        
        ["porygon", "haunter", "magmar"]          
    ]


    @staticmethod
    def generar_equipo_predefinido(team_number: int, num_pokemones: int) -> list[Pokemon]:
        """
        Elige un equipo de un conjunto predefinido usando el índice (team_number),
        filtrando según el tamaño del equipo (3 o 4), clona los pokémones 
        y les asigna un set óptimo de 2 movimientos de daño y 2 de soporte.
        """
        if not PokemonFactory.pokemons:
            raise ValueError("¡Debes cargar primero los pokémons usando PokemonFactory.load_all_pokemons()!")

        if num_pokemones == 3:
            pool_opciones = TeamFactory.BLUEPRINTS_3VS3
        elif num_pokemones == 4:
            pool_opciones = TeamFactory.BLUEPRINTS_4VS4
        else:
            raise ValueError("El parámetro num_pokemones debe ser estrictamente 3 o 4.")

        blueprint = pool_opciones[team_number % len(pool_opciones)]
        
        db_pokemons = {p.name.lower(): p for p in PokemonFactory.pokemons}
        equipo = []

        for name in blueprint:
            if name not in db_pokemons:
                print(f"No se encontró a '{name}' en el archivo JSON.")
                continue

            p_sel = copy.deepcopy(db_pokemons[name])
            random.shuffle(p_sel.moves)

            movimientos_daño = [m for m in p_sel.moves if m.power is not None]
            movimientos_soporte = [m for m in p_sel.moves if m.power is None]

            set_final = movimientos_daño[:2] + movimientos_soporte[:2]

            if len(set_final) < 4:
                restantes = [m for m in p_sel.moves if m not in set_final]
                set_final += restantes[:(4 - len(set_final))]

            p_sel.moves = set_final[:4]
            equipo.append(p_sel)

        return equipo