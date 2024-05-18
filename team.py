from pokedex import Pokedex, Pokemon

class Restrictions:
    def __init__(self, allow_repeat: bool):
        self.allow_repeat: bool = allow_repeat

"""
here's my thinking, we can create a library of all viable pokemon + movesets which pass through a filter
 - we can filter by a lambda that gets passed in or a default filter

 no... we can deal with the filter later, lets first fix the pokemon varieties that don't exist in the current gen and types
 todo...
"""

class Team:
    def init_random_team(self):
        self.pokemon: list[Pokemon] = []
        pass

    def __init__(self, pokedex: Pokedex, max_team_size: int = 6, restrictions: Restrictions = Restrictions(False)):
        self.max_team_size: int = max_team_size
        self.pokedex: Pokedex = pokedex
        self.restrictions: Restrictions = restrictions
        self.init_random_team()
    
    def __str__(self):
        r = ""
        for p in self.pokemon:
            r += p.name + f" [{p.types[0]}|{p.types[1]}] | "
        return r[0:-3] if len(self.pokemon) else "Empty team"

if __name__ == "__main__":
    gen = 3
    is_range = True
    dex = Pokedex.load(gen, is_range)

    print(dex)
    team = Team(dex)
    print(team)