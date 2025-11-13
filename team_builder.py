#!/usr/bin/env python3
"""
Pokémon Team Builder for Smogon OU Singles Metagame

This tool generates competitive Pokémon teams with proper defensive coverage
against common threats in the Smogon OU metagame.

Features:
- Ensures proper type coverage against common threats
- Allows users to specify Pokémon to include in the team
- Allows users to specify Pokémon to exclude from team generation
"""

import json
import random
import os
import sys
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
    
    def has_matching_playstyle(self, team_playstyle: str) -> bool:
        """
        Check if this Pokémon has any builds that match the specified team playstyle.
        
        Args:
            team_playstyle: The team playstyle to check for
            
        Returns:
            True if at least one build matches the playstyle, False otherwise
        """
        if not team_playstyle:
            return True
            
        for build in self.builds:
            if isinstance(build, dict) and "teamFit" in build and team_playstyle in build["teamFit"]:
                return True
                
        return False
    
    def get_random_build(self, team_playstyle: Optional[str] = None) -> str:
        """
        Return a random build for this Pokémon.
        
        If team_playstyle is specified, only builds that match the playstyle will be considered.
        """
        # Filter builds based on team playstyle if specified
        valid_builds = self.builds
        
        if team_playstyle:
            # Filter builds that have the specified team playstyle in their teamFit array
            valid_builds = [
                build for build in self.builds
                if isinstance(build, dict) and
                "teamFit" in build and
                team_playstyle in build["teamFit"]
            ]
        
        build_choice = random.choice(valid_builds)
        
        # Handle both string builds (old format) and object builds (new format)
        if isinstance(build_choice, dict):
            return build_choice["build"]
        return build_choice
    
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
    
    def get_pokemon_with_resistance(self, attack_type: str, team: List[Pokemon] = None, team_playstyle: Optional[str] = None) -> List[Pokemon]:
        """
        Get all Pokémon that resist or are immune to the given attack type.
        
        Args:
            attack_type: The type to check resistance against
            team: Optional list of Pokémon already on the team (to exclude)
            team_playstyle: Optional team playstyle to filter Pokémon by
            
        Returns:
            List of Pokémon that resist or are immune to the attack type
        """
        resistant_pokemon = []
        team_names = [p.name for p in team] if team else []
        
        for pokemon in self.pokemon_list:
            if pokemon.name in team_names:
                continue
                
            # Skip Pokémon that don't match the team playstyle
            if team_playstyle and not pokemon.has_matching_playstyle(team_playstyle):
                continue
                
            effectiveness = pokemon.resists_type(attack_type)
            if effectiveness < 1:  # Resistant or immune
                resistant_pokemon.append(pokemon)
        
        return resistant_pokemon
    
    def get_pokemon_with_immunity(self, attack_type: str, team: List[Pokemon] = None, team_playstyle: Optional[str] = None) -> List[Pokemon]:
        """
        Get all Pokémon that are immune to the given attack type.
        
        Args:
            attack_type: The type to check immunity against
            team: Optional list of Pokémon already on the team (to exclude)
            team_playstyle: Optional team playstyle to filter Pokémon by
            
        Returns:
            List of Pokémon that are immune to the attack type
        """
        immune_pokemon = []
        team_names = [p.name for p in team] if team else []
        
        for pokemon in self.pokemon_list:
            if pokemon.name in team_names:
                continue
                
            # Skip Pokémon that don't match the team playstyle
            if team_playstyle and not pokemon.has_matching_playstyle(team_playstyle):
                continue
                
            effectiveness = pokemon.resists_type(attack_type)
            if effectiveness == 0:  # Immune
                immune_pokemon.append(pokemon)
        
        return immune_pokemon
    
    def build_team(self, team_playstyle: Optional[str] = None) -> List[Pokemon]:
        """
        Build a competitive team with proper defensive coverage.
        
        Args:
            team_playstyle: Optional team playstyle to filter Pokémon by
            
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
                    immune_pokemon = self.get_pokemon_with_immunity(priority_type, team, team_playstyle)
                    if immune_pokemon:
                        new_pokemon = random.choice(immune_pokemon)
                        team.append(new_pokemon)
                        coverage[priority_type] = COVERAGE_REQUIREMENTS[priority_type]  # Immunity fulfills requirement
                        continue
                
                # Get Pokémon that resist this type
                resistant_pokemon = self.get_pokemon_with_resistance(priority_type, team, team_playstyle)
                
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
    
    def generate_team_output(self, team_playstyle: Optional[str] = None) -> str:
        """
        Generate a complete team with builds and return as formatted text.
        
        Args:
            team_playstyle: Optional team playstyle to filter Pokémon by
            
        Returns:
            String containing the full team with builds
        """
        team = self.build_team(team_playstyle)
        output = []
        
        for pokemon in team:
            build = pokemon.get_random_build(team_playstyle)
            output.append(build)
        
        return "\n\n".join(output)


class ConfigManager:
    """Class to manage user configuration for team building."""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize with the path to the config file."""
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load configuration from the JSON file."""
        if not os.path.exists(self.config_path):
            # Create default config if it doesn't exist
            default_config = {
                "include_pokemon": [],
                "exclude_pokemon": [],
                "team_playstyle": None
            }
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
        
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error: {self.config_path} is not a valid JSON file.")
            return {"include_pokemon": [], "exclude_pokemon": [], "team_playstyle": None}
    
    def get_included_pokemon(self) -> List[str]:
        """Get the list of Pokémon to include in team generation."""
        return self.config.get("include_pokemon", [])
    
    def get_excluded_pokemon(self) -> List[str]:
        """Get the list of Pokémon to exclude from team generation."""
        return self.config.get("exclude_pokemon", [])
    
    def get_team_playstyle(self) -> Optional[str]:
        """Get the team playstyle preference if specified."""
        return self.config.get("team_playstyle")


def is_ogerpon_form(pokemon_name: str) -> bool:
    """Check if a Pokémon is any form of Ogerpon."""
    return "ogerpon" in pokemon_name.lower()


def main():
    """Main function to run the team builder."""
    # Load configuration
    config_manager = ConfigManager()
    included_pokemon = config_manager.get_included_pokemon()
    excluded_pokemon = config_manager.get_excluded_pokemon()
    team_playstyle = config_manager.get_team_playstyle()
    
    # Initialize team builder with the appropriate database
    db_path = "mons_db.json"
    if team_playstyle:
        # Convert playstyle to filename format (replace spaces with underscores)
        playstyle_filename = team_playstyle.replace(" ", "_")
        playstyle_db_path = f"{playstyle_filename}_db.json"
        
        # Check if the playstyle-specific database exists
        if os.path.exists(playstyle_db_path):
            db_path = playstyle_db_path
            print(f"Using {db_path} for {team_playstyle} playstyle")
        
    builder = TeamBuilder(db_path)
    
    # Print team playstyle if specified
    if team_playstyle:
        print(f"Building team with '{team_playstyle}' playstyle...")
    
    # Validate included Pokémon
    all_pokemon_names = [p.name.lower() for p in builder.pokemon_list]
    invalid_includes = [p for p in included_pokemon if p.lower() not in all_pokemon_names]
    if invalid_includes:
        print(f"Warning: The following Pokémon in your include list are not in the database: {', '.join(invalid_includes)}")
        included_pokemon = [p for p in included_pokemon if p.lower() in all_pokemon_names]
    
    # Modify the team building process based on user preferences
    if included_pokemon:
        # Pre-select the included Pokémon
        team = []
        has_ogerpon = False
        
        for name in included_pokemon:
            for pokemon in builder.pokemon_list:
                if pokemon.name.lower() == name.lower():
                    # Check if this is an Ogerpon form and if we already have one
                    if is_ogerpon_form(pokemon.name) and has_ogerpon:
                        print(f"Warning: Multiple Ogerpon forms detected in include list. Only using the first one.")
                        continue
                    
                    team.append(pokemon)
                    
                    # Mark that we have an Ogerpon if this is one
                    if is_ogerpon_form(pokemon.name):
                        has_ogerpon = True
                    
                    break
        
        # Fill the rest of the team
        remaining_slots = 6 - len(team)
        if remaining_slots > 0:
            # Exclude both the already included Pokémon and user-specified exclusions
            excluded = [p.lower() for p in excluded_pokemon] + [p.name.lower() for p in team]
            
            # Filter the available Pokémon
            available_pokemon = [p for p in builder.pokemon_list if p.name.lower() not in excluded]
            
            # If we already have an Ogerpon, exclude all other Ogerpon forms
            if has_ogerpon:
                available_pokemon = [p for p in available_pokemon if not is_ogerpon_form(p.name)]
            
            # Build the rest of the team
            builder.pokemon_list = available_pokemon
            remaining_team = builder.build_team(team_playstyle)
            
            # Take only what we need to fill the team
            team.extend(remaining_team[:remaining_slots])
        
        # Generate output with the custom team
        output = []
        for pokemon in team:
            build = pokemon.get_random_build(team_playstyle)
            output.append(build)
        
        team_output = "\n\n".join(output)
    else:
        # Normal team building, just exclude specified Pokémon
        if excluded_pokemon:
            # Filter out excluded Pokémon
            builder.pokemon_list = [p for p in builder.pokemon_list if p.name.lower() not in [name.lower() for name in excluded_pokemon]]
        
        # Generate a team normally, but ensure only one Ogerpon form
        team = []
        has_ogerpon = False
        
        # Keep building until we have 6 Pokémon
        while len(team) < 6:
            # Get the next Pokémon
            remaining_pokemon = [p for p in builder.pokemon_list if p.name not in [t.name for t in team]]
            
            # If we already have an Ogerpon, exclude all other Ogerpon forms
            if has_ogerpon:
                remaining_pokemon = [p for p in remaining_pokemon if not is_ogerpon_form(p.name)]
            
            # If no more Pokémon available, break
            if not remaining_pokemon:
                break
                
            # Get the next Pokémon based on coverage requirements
            builder.pokemon_list = remaining_pokemon
            next_pokemon = builder.build_team(team_playstyle)[0]  # Get just one Pokémon
            team.append(next_pokemon)
            
            # Check if this is an Ogerpon form
            if is_ogerpon_form(next_pokemon.name):
                has_ogerpon = True
        
        # Generate output with the team
        output = []
        for pokemon in team:
            build = pokemon.get_random_build(team_playstyle)
            output.append(build)
        
        team_output = "\n\n".join(output)
    
    # Write to output file
    with open("team_output.txt", "w") as f:
        f.write(team_output)
    
    print("Team generated successfully! Check team_output.txt for the result.")
    print("\nTeam preview:")
    print(team_output)


if __name__ == "__main__":
    main()