#!/usr/bin/env python3
"""
Pokémon Team Builder for Smogon OU Singles Metagame

This tool generates competitive Pokémon teams with proper defensive coverage
against common threats in the Smogon OU metagame.
"""

import json
import random
from typing import Dict, List, Set, Tuple, Optional

# Type effectiveness chart
# Values: 0 = immune, 0.5 = resistant, 1 = neutral, 2 = weak
TYPE_CHART = {
    "normal": {"ghost": 0, "rock": 0.5, "steel": 0.5, "fighting": 2},
    "fire": {"fire": 0.5, "water": 2, "grass": 0.5, "ice": 0.5, "bug": 0.5, "rock": 2, 
             "dragon": 0.5, "steel": 0.5, "ground": 2},
    "water": {"fire": 0.5, "water": 0.5, "grass": 2, "electric": 2, "ice": 0.5, "steel": 0.5},
    "electric": {"water": 0.5, "electric": 0.5, "flying": 0.5, "ground": 2, "dragon": 0.5},
    "grass": {"fire": 2, "water": 0.5, "grass": 0.5, "poison": 2, "ground": 0.5, 
              "flying": 2, "bug": 2, "ice": 2, "dragon": 0.5, "steel": 2},
    "ice": {"fire": 2, "ice": 0.5, "fighting": 2, "rock": 2, "steel": 2},
    "fighting": {"normal": 0.5, "ice": 0.5, "poison": 0.5, "flying": 2, "psychic": 2, 
                 "bug": 0.5, "rock": 0.5, "dark": 0.5, "steel": 0.5, "fairy": 2},
    "poison": {"grass": 0.5, "poison": 0.5, "ground": 2, "psychic": 2, "bug": 0.5, 
               "fairy": 0.5, "steel": 0},
    "ground": {"fire": 0.5, "electric": 0, "grass": 2, "poison": 0.5, "flying": 0, 
               "bug": 0.5, "rock": 0.5, "water": 2, "ice": 2},
    "flying": {"electric": 2, "grass": 0.5, "fighting": 0.5, "bug": 0.5, "rock": 2, 
               "ice": 2, "ground": 0},
    "psychic": {"fighting": 0.5, "psychic": 0.5, "bug": 2, "ghost": 2, "dark": 2},
    "bug": {"fire": 2, "grass": 0.5, "fighting": 0.5, "poison": 0.5, "flying": 2, 
            "rock": 2, "steel": 0.5, "fairy": 0.5},
    "rock": {"normal": 0.5, "fire": 0.5, "water": 2, "grass": 2, "fighting": 2, 
             "poison": 0.5, "ground": 2, "flying": 0.5, "steel": 2},
    "ghost": {"normal": 0, "fighting": 0, "poison": 0.5, "bug": 0.5, "ghost": 2, "dark": 2},
    "dragon": {"dragon": 2, "steel": 0.5, "fairy": 2, "ice": 2},
    "dark": {"fighting": 2, "psychic": 0, "bug": 2, "ghost": 0.5, "dark": 0.5, "fairy": 2},
    "steel": {"normal": 0.5, "fire": 2, "grass": 0.5, "ice": 0.5, "fighting": 2, 
              "poison": 0, "ground": 2, "flying": 0.5, "psychic": 0.5, "bug": 0.5, 
              "rock": 0.5, "dragon": 0.5, "steel": 0.5, "fairy": 0.5},
    "fairy": {"fighting": 0.5, "poison": 2, "bug": 0.5, "dragon": 0, "dark": 0.5, 
              "steel": 2}
}

# Team coverage requirements
COVERAGE_REQUIREMENTS = {
    "water": 2,      # 2 water resists
    "fighting": 2,   # 1-2 fighting resists
    "dragon": 2,     # 1-2 dragon resists (or 1 immunity)
    "flying": 1,     # 1 flying resist
    "electric": 2,   # 1-2 electric resists
    "ground": 2,     # 2 ground resists, or 1 immunity
    "dark": 1        # 1 dark resist
}

class Pokemon:
    """Class representing a Pokémon with its types and builds."""
    
    def __init__(self, name: str, types: List[str], builds: List[str]):
        self.name = name
        self.types = types
        self.builds = builds
    
    def __str__(self) -> str:
        return f"{self.name.capitalize()} ({'/'.join(t.capitalize() for t in self.types)})"
    
    def get_random_build(self) -> str:
        """Return a random build for this Pokémon."""
        return random.choice(self.builds)
    
    def resists_type(self, attack_type: str) -> float:
        """
        Calculate how this Pokémon resists a given attack type.
        Returns:
            0 for immune
            0.25 or 0.5 for resistant
            1 for neutral
            2 or 4 for weak
        """
        effectiveness = 1.0
        
        for poke_type in self.types:
            if poke_type in TYPE_CHART and attack_type in TYPE_CHART[poke_type]:
                type_effect = TYPE_CHART[poke_type][attack_type]
                effectiveness *= type_effect
        
        return effectiveness


class TeamBuilder:
    """Class to build competitive Pokémon teams with proper type coverage."""
    
    def __init__(self, pokemon_db_path: str):
        """Initialize with the path to the Pokémon database JSON file."""
        self.pokemon_list = self._load_pokemon(pokemon_db_path)
        
    def _load_pokemon(self, db_path: str) -> List[Pokemon]:
        """Load Pokémon data from the JSON database."""
        with open(db_path, 'r') as f:
            data = json.load(f)
        
        pokemon_list = []
        for entry in data:
            # Skip Pokémon with missing types (like Excadrill in the dataset)
            if not entry.get("types"):
                continue
                
            pokemon = Pokemon(
                name=entry["name"],
                types=entry["types"],
                builds=entry["builds"]
            )
            pokemon_list.append(pokemon)
        
        return pokemon_list
    
    def get_pokemon_with_resistance(self, attack_type: str, team: List[Pokemon] = None) -> List[Pokemon]:
        """
        Get all Pokémon that resist or are immune to the given attack type.
        
        Args:
            attack_type: The type to check resistance against
            team: Optional list of Pokémon already on the team (to exclude)
            
        Returns:
            List of Pokémon that resist or are immune to the attack type
        """
        resistant_pokemon = []
        team_names = [p.name for p in team] if team else []
        
        for pokemon in self.pokemon_list:
            if pokemon.name in team_names:
                continue
                
            effectiveness = pokemon.resists_type(attack_type)
            if effectiveness < 1:  # Resistant or immune
                resistant_pokemon.append(pokemon)
        
        return resistant_pokemon
    
    def get_pokemon_with_immunity(self, attack_type: str, team: List[Pokemon] = None) -> List[Pokemon]:
        """
        Get all Pokémon that are immune to the given attack type.
        
        Args:
            attack_type: The type to check immunity against
            team: Optional list of Pokémon already on the team (to exclude)
            
        Returns:
            List of Pokémon that are immune to the attack type
        """
        immune_pokemon = []
        team_names = [p.name for p in team] if team else []
        
        for pokemon in self.pokemon_list:
            if pokemon.name in team_names:
                continue
                
            effectiveness = pokemon.resists_type(attack_type)
            if effectiveness == 0:  # Immune
                immune_pokemon.append(pokemon)
        
        return immune_pokemon
    
    def build_team(self) -> List[Pokemon]:
        """
        Build a competitive team with proper defensive coverage.
        
        Returns:
            List of 6 Pokémon forming a balanced team
        """
        team = []
        coverage = {type_name: 0 for type_name in COVERAGE_REQUIREMENTS}
        
        # Try to fulfill all coverage requirements
        while len(team) < 6:
            # Determine which coverage requirements are not yet met
            unfulfilled = {
                t: count for t, count in COVERAGE_REQUIREMENTS.items() 
                if coverage[t] < count
            }
            
            if not unfulfilled:
                # All requirements met, add random Pokémon to fill the team
                remaining_pokemon = [p for p in self.pokemon_list if p.name not in [t.name for t in team]]
                if not remaining_pokemon:
                    break
                    
                new_pokemon = random.choice(remaining_pokemon)
                team.append(new_pokemon)
                
                # Update coverage with the new Pokémon
                for attack_type in coverage:
                    effectiveness = new_pokemon.resists_type(attack_type)
                    if effectiveness == 0:  # Immune
                        coverage[attack_type] = COVERAGE_REQUIREMENTS[attack_type]  # Immunity fulfills requirement
                    elif effectiveness < 1:  # Resistant
                        coverage[attack_type] += 1
            else:
                # Prioritize types with the largest gap in coverage
                priority_type = max(unfulfilled.items(), key=lambda x: x[1] - coverage[x[0]])[0]
                
                # Check if we need immunity for this type
                if priority_type == "ground" and coverage[priority_type] == 0:
                    # For ground, try to get an immunity first
                    immune_pokemon = self.get_pokemon_with_immunity(priority_type, team)
                    if immune_pokemon:
                        new_pokemon = random.choice(immune_pokemon)
                        team.append(new_pokemon)
                        coverage[priority_type] = COVERAGE_REQUIREMENTS[priority_type]  # Immunity fulfills requirement
                        continue
                
                # Get Pokémon that resist this type
                resistant_pokemon = self.get_pokemon_with_resistance(priority_type, team)
                
                if not resistant_pokemon:
                    # If no resistant Pokémon available, try another type
                    del unfulfilled[priority_type]
                    if not unfulfilled:
                        # No more unfulfilled types, add a random Pokémon
                        remaining_pokemon = [p for p in self.pokemon_list if p.name not in [t.name for t in team]]
                        if not remaining_pokemon:
                            break
                            
                        new_pokemon = random.choice(remaining_pokemon)
                        team.append(new_pokemon)
                        
                        # Update coverage with the new Pokémon
                        for attack_type in coverage:
                            effectiveness = new_pokemon.resists_type(attack_type)
                            if effectiveness == 0:  # Immune
                                coverage[attack_type] = COVERAGE_REQUIREMENTS[attack_type]
                            elif effectiveness < 1:  # Resistant
                                coverage[attack_type] += 1
                    continue
                
                # Add a Pokémon that resists the priority type
                new_pokemon = random.choice(resistant_pokemon)
                team.append(new_pokemon)
                
                # Update coverage with the new Pokémon
                for attack_type in coverage:
                    effectiveness = new_pokemon.resists_type(attack_type)
                    if effectiveness == 0:  # Immune
                        coverage[attack_type] = COVERAGE_REQUIREMENTS[attack_type]  # Immunity fulfills requirement
                    elif effectiveness < 1:  # Resistant
                        coverage[attack_type] += 1
        
        return team
    
    def generate_team_output(self) -> str:
        """
        Generate a complete team with builds and return as formatted text.
        
        Returns:
            String containing the full team with builds
        """
        team = self.build_team()
        output = []
        
        for pokemon in team:
            build = pokemon.get_random_build()
            output.append(build)
        
        return "\n\n".join(output)


def main():
    """Main function to run the team builder."""
    builder = TeamBuilder("mons_db.json")
    team_output = builder.generate_team_output()
    
    # Write to output file
    with open("team_output.txt", "w") as f:
        f.write(team_output)
    
    print("Team generated successfully! Check team_output.txt for the result.")
    print("\nTeam preview:")
    print(team_output)


if __name__ == "__main__":
    main()