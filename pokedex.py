from dataclasses import dataclass
import pokebase as pb
import pickle
from os import path

MAX_GEN = 9

def gen_sort(el):
    return int(el.generation.url.split('/')[-2])

@dataclass
class MoveVersionGroup:
    level_learned_at: int
    learn_method: str
    version_group_id: int
    version_group_name: str

    def __init__(self, version_group: pb.APIResource):
        self.level_learned_at = version_group.level_learned_at
        self.learn_method = version_group.move_learn_method.name
        self.version_group_id = version_group.version_group.url.split('/')[-2]
        self.version_group_name = version_group.version_group.name

@dataclass
class Move:
    id: int
    name: str
    version_groups: list[MoveVersionGroup]

    def __init__(self, move: pb.APIResource):
        self.name = move.move.name
        self.id = move.move.url.split('/')[-2]
        self.version_groups = []
        for vg in move.version_group_details:
            new_vg = MoveVersionGroup(vg)
            self.version_groups.append(new_vg)

@dataclass
class Ability:
    id: int
    name: str
    is_hidden: bool
    slot: int

@dataclass
class Pokemon:
    id: int
    name: str
    types: tuple[str, str | None]
    pokemon_species_id: int
    stats: dict[str, int]
    is_default: bool
    abilities: list[str]

    def __init__(self, gen: int, pokemon: pb.APIResource, pokemon_species_id: int, is_default: bool):
        self.pokemon_species_id = pokemon_species_id
        self.name = pokemon.name
        self.types = self.get_types(pokemon, gen)
        self.stats = self.get_stats(pokemon)
        self.abilities = self.get_abilities(pokemon, gen)
        self.moves = self.get_moves(pokemon)
        self.is_default = is_default

    #this is probably wrong lol
    def get_types(self, pokemon: pb.APIResource, gen):
        """
        for past types this goes:
        gen = 3
        1,4,5  data will have 4 as the correct gen, we want to take the first gen that is above or equal to the current gen
        """
        if len(pokemon.past_types):
            pokemon.past_types.sort(key=gen_sort)
            for t in pokemon.past_types:
                if int(t.generation.url.split('/')[-2]) < gen:
                    continue
                else:
                    types = [None, None]
                    for type in t.types:
                        match type.slot:
                            case 1:
                                types[0] = type.type.name
                            case 2:
                                types[1] = type.type.name
                            case _:
                                raise ValueError("unknown type slot")
                    return types
                                
        types = [None, None]
        for type in pokemon.types:
            match type.slot:
                case 1:
                    types[0] = type.type.name
                case 2:
                    types[1] = type.type.name
                case _:
                    raise ValueError("unknown type slot")
        return types

    def get_stats(self, pokemon: pb.APIResource):
        stats = {}
        for stat in pokemon.stats:
            stats[stat.stat.name] = stat.base_stat
        return stats

    def get_abilities(self, pokemon: pb.APIResource, gen):
        abilities = [None, None, None]
        for ability in pokemon.abilities:
            abilities[ability.slot - 1] = ability.ability.name

        pokemon.past_abilities.sort(reverse=True, key=gen_sort)
        for past_abilities in pokemon.past_abilities:
            if int(past_abilities.generation.url.split('/')[-2]) < gen:
                break
            for past_ability in past_abilities.abilities:
                print(past_ability)
                abilities[past_ability.slot - 1] = past_ability.ability.name

        return abilities
        
    def get_moves(self, pokemon: pb.APIResource):
        moves = []
        for move in pokemon.moves:
            new_move = Move(move)
            moves.append(new_move)

@dataclass
class PokemonSpecies:
    id: int
    name: str
    evolution_chain_id: int
    varieties: list[Pokemon]

    def __init__(self, gen, id, name, varieties):
        self.id = id
        self.name = name
        self.varieties = []
        for v in varieties:
            pokemon_name = v.pokemon.name
            mon = pb.pokemon(pokemon_name)
            p = Pokemon(gen, mon, pokemon_species_id=self.id, is_default=v.is_default)
            self.varieties.append(p)

class Pokedex:
    gen: int
    gen_str: str
    is_range: bool
    pokemon_species: dict[str,PokemonSpecies] = {}

    def __init__(self, gen_int, is_range=True, force_update=False):
        self.gen = gen_int
        self.is_range = is_range
        gen_range = range(1, self.gen + 1) if self.is_range else range(self.gen, self.gen + 1)
    
        for gen_idx in gen_range:
            gen = pb.generation(gen_idx)
            gen_str = gen.name
            species = gen.pokemon_species
            for i, s in enumerate(species):
                (n := len(species))
                self.pokemon_species[s.name] = PokemonSpecies(s.id, gen_idx, s.name, s.varieties)
                print(f'gen: {gen_idx}/{gen_range[-1]} | pokemon: {i+1}/{n} {s.name} {len(s.varieties)} variet{"y" if len(s.varieties) == 1 else "ies"}')

    def get_save_path_self(self):
        return Pokedex.get_save_path(self.gen, self.is_range)
    
    @staticmethod
    def get_save_path(gen: int, is_range: bool):
        save_path = path.dirname(path.realpath(__file__))
        return path.join(save_path, 'data', f'dex-gen{gen}{"-range.pickle" if is_range else ".pickle"}')

    def save(self):
        with open(self.get_save_path_self(), 'wb') as f:
            pickle.dump(self, f)
    
    @staticmethod
    def load(gen, is_range):
        try:    
            with open(Pokedex.get_save_path(gen, range), 'rb') as f:
                dex = pickle.load(f)
        except FileNotFoundError as e:
            dex = Pokedex(gen_int=gen, is_range=is_range, force_update=True)
            dex.save()
        return dex

if __name__ == "__main__":
    gen = 3
    is_range = True
    force_update=False

    dex = Pokedex.load(gen, is_range)