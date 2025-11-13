#!/usr/bin/env python3
"""
Script to filter the Pokémon database to create separate files for each playstyle.
"""

import json

# Define all playstyles
PLAYSTYLES = [
    "offense",
    "hyper offense",
    "bulky offense",
    "balance",
    "rain",
    "sun",
    "stall"
]

# Load the original database
with open("mons_db.json", "r") as f:
    data = json.load(f)

# Process each playstyle
for playstyle in PLAYSTYLES:
    # Filter Pokémon with builds for this playstyle
    filtered_pokemon = []
    for pokemon in data:
        # Check if any build has this playstyle in its teamFit array
        filtered_builds = []
        for build in pokemon["builds"]:
            if isinstance(build, dict) and "teamFit" in build and playstyle in build["teamFit"]:
                filtered_builds.append(build)
        
        # If there are matching builds, add the Pokémon to the filtered list
        if filtered_builds:
            # Create a copy of the Pokémon with only matching builds
            filtered_pokemon.append({
                "name": pokemon["name"],
                "types": pokemon["types"],
                "builds": filtered_builds
            })
    
    # Save the filtered database
    filename = f"{playstyle.replace(' ', '_')}_db.json"
    with open(filename, "w") as f:
        json.dump(filtered_pokemon, f, indent=2)
    
    print(f"Created {filename} with {len(filtered_pokemon)} Pokémon that have builds for {playstyle} teams.")