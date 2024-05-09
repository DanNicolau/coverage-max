from dataclasses import dataclass
import pokebase as pb

MAX_POKEDEX_ID = 1025
MAX_EVOLUTION_CHAIN = 549

#we are doing this to format the data to our interests
@dataclass
class Stats:
    hp: int = 0
    attack: int = 0
    defense: int = 0
    special_attack: int = 0
    special_defense: int = 0
    speed: int = 0

@dataclass
class Move:
    id: int
    name: str
    level_learned_at: int
    damage_class: int
    type: str

@dataclass
class Pokemon:
    id: int = 0
    name: str = None
    types: tuple[str, str] = (None, None)
    abilities: list[str] = None
    # we maybe just skip mons not in final evolution
    stats: Stats = None
    is_final_evolution: bool = False
    moveset: list[Move] = None
    natural_moveset: list[Move] = None
    other_immunities: list[str] = None
    #post process with what weak or resilient to etc.
    def __str__(self):
        return f'{self.id}: {self.name}{" (f)" if self.is_final_evolution else ""} | [{self.types[0]}|{self.types[1]}]'

class Pokedex:
    pokemon: dict[str, Pokemon] = {}
    type_chart: list[list[float]]

    def add_pokemon(self, p: Pokemon):
        self.pokemon[p.name] = p
        return p
    
    def print(self):
        for p in self.pokemon.values():
            print(p)

def generate_pokedex() -> Pokedex:
    """
    We want to cache the pokedex locally since even in between runs this takes so long to run. The first run of the program will just generate the dex of the stats we are interested in with a flag at run if we want to update the dex. We will store the dex into a pickle.
    """
    pokedex = Pokedex()

    # num_mons = 151
    total_mons = pb.APIResourceList('pokemon').count
    num_mons = 9

    for i in range(1, num_mons + 1):
        print(f'{i}/{num_mons}')
        new_mon = Pokemon(id=i)
        r_mon = pb.pokemon(i)

        new_mon.name = r_mon.name
        new_mon.stats = get_stats(r_mon)
        new_mon.types = get_types(r_mon)
        new_mon.abilities = get_abilities(r_mon)
        
        pokedex.add_pokemon(new_mon)

    update_is_final_evolution(pokedex)

    pokedex.print()

    raise NotImplementedError()

def update_final_evolution_recur(chain, pokedex: Pokedex):
    if len(chain.evolves_to) == 0:
        pokedex.pokemon[chain.species.name].is_final_evolution = True
    else:
        for et in chain.evolves_to:
            update_final_evolution_recur(et, pokedex)


def update_is_final_evolution(pokedex: Pokedex):
    for evo_id in range(1, 4): # MAX_EVOLUTION_CHAIN + 1):
        chain = pb.evolution_chain(evo_id).chain
        update_final_evolution_recur(chain, pokedex)


def get_abilities(r_mon) -> list[str]:
    r = []
    for a in r_mon.abilities:
        r.append(a.ability.name)

def get_types(r_mon) -> tuple[str, str]:
    types = [None, None]
    for t in r_mon.types:
        match t.slot:
            case 1:
                types[0] = t.type.name
            case 2:
                types[1] = t.type.name
            case _:
                raise ValueError(f'got strange type slot: {t.slot} | {t.type.name}')

    return tuple(types)

def get_stats(r_mon):
    new_stats = Stats()
    for stat in r_mon.stats:
        match stat.stat.name:
            case 'hp':
                new_stats.hp = stat.base_stat
            case 'attack':
                new_stats.attack = stat.base_stat
            case 'defense':
                new_stats.defense = stat.base_stat
            case 'special-attack':
                new_stats.special_attack = stat.base_stat
            case 'special-defense':
                new_stats.special_defense = stat.base_stat
            case 'speed':
                new_stats.speed = stat.base_stat
            case _:
                raise ValueError(f'Not sure what that stat is: {stat.stat.name}.')
    return new_stats

if __name__ == "__main__":
    # print(pb.APIResourceList('pokemon').count)
    generate_pokedex()