#!/usr/bin/python3
import pokebase as pb
from dataclasses import dataclass
import utils

class Team:
    team: list[pb.APIResource] #pokemon id

    def __init__(self, ids: list[int]) -> None:
        for id in ids:
            print(pb.pokemon(id).base_experience)

if __name__ == "__main__":
    dex = utils.generate_pokedex()

    team = Team([1,2,3])