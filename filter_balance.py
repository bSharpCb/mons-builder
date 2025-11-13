#!/usr/bin/env python3
"""
Script to filter the Pokémon database to only include Pokémon with builds for "balance" teams.
"""

import json

# Load the original database
with open("mons_db.json", "r") as f:
    data = json.load(f)

# Filter Pokémon with builds for "balance" teams
balance_pokemon = []
for pokemon in data:
    # Check if any build has "balance" in its teamFit array
    balance_builds = []
    for build in pokemon["builds"]:
        if isinstance(build, dict) and "teamFit" in build and "balance" in build["teamFit"]:
            balance_builds.append(build)
    
    # If there are balance builds, add the Pokémon to the filtered list
    if balance_builds:
        # Create a copy of the Pokémon with only balance builds
        balance_pokemon.append({
            "name": pokemon["name"],
            "types": pokemon["types"],
            "builds": balance_builds
        })

# Save the filtered database
with open("balance_db.json", "w") as f:
    json.dump(balance_pokemon, f, indent=2)

print(f"Created balance_db.json with {len(balance_pokemon)} Pokémon that have builds for balance teams.")