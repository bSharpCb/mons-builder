# Pokémon Team Builder for Smogon OU Singles Metagame

This tool generates competitive Pokémon teams with proper defensive coverage against common threats in the Smogon OU singles metagame.

## Features

- Automatically builds balanced teams with proper type coverage
- Ensures teams meet specific defensive requirements:
  - 2 water resists
  - 1-2 fighting resists
  - 1-2 dragon resists (or 1 immunity)
  - 1 flying resist
  - 1-2 electric resists
  - 2 ground resists (or 1 immunity)
  - 1 dark resist
- Selects appropriate builds for each Pokémon from a database
- Outputs a complete team in standard Smogon format
- Allows users to specify Pokémon to include in the team
- Allows users to specify Pokémon to exclude from team generation
- Ensures only one form of Ogerpon is included in a team (following game rules)

## Requirements

- Python 3.6 or higher

## Usage

1. Ensure you have the `mons_db.json` file in the same directory as the script
2. (Optional) Modify the `config.json` file to specify Pokémon to include or exclude
3. Run the script:

```bash
python3 team_builder.py
```

4. The generated team will be saved to `team_output.txt` and also displayed in the console

## Configuration

You can customize team generation by editing the `config.json` file:

```json
{
  "include_pokemon": ["landorus-therian", "heatran"],
  "exclude_pokemon": ["kyurem", "darkrai"]
}
```

- `include_pokemon`: List of Pokémon names that should be included in the team
  - These Pokémon will be prioritized and guaranteed to be in the final team
  - If you specify more than 6 Pokémon, only the first 6 will be used
  - Names are case-insensitive

- `exclude_pokemon`: List of Pokémon names that should never appear in the team
  - These Pokémon will be excluded from team generation
  - Names are case-insensitive

Note: If a Pokémon name in your configuration doesn't match any in the database, it will be ignored with a warning message.

### Special Rules

- **Ogerpon Forms**: Following the game's rules, only one form of Ogerpon can be included in a team. If multiple Ogerpon forms are specified in the `include_pokemon` list, only the first one will be used, and a warning will be displayed.

## How It Works

The team builder uses the following algorithm:

1. Loads Pokémon data from the database
2. Calculates type effectiveness for each Pokémon
3. Builds a team by prioritizing Pokémon that provide resistances to required types
4. Selects a random build for each team member
5. Outputs the complete team

## Customization

You can modify the coverage requirements by editing the `COVERAGE_REQUIREMENTS` dictionary in the script. The keys are attack types, and the values are the number of Pokémon that should resist that type.

You can also modify the type effectiveness chart by editing the `TYPE_CHART` dictionary if you need to adjust how resistances are calculated.

## Example Output

```
Quaquaval @ Assault Vest
Ability: Moxie
EVs: 252 Atk / 4 Def / 252 Spe
Tera Type: Steel
Adamant Nature
- Close Combat
- Aqua Step
- Knock Off
- Rapid Spin

Araquanid @ Custap Berry
Ability: Water Bubble
EVs: 252 HP / 40 Def / 216 SpA
Tera Type: Ghost
Modest Nature
- Sticky Web
- Surf
- Endeavor
- Endure

...
```

## License

This project is open source and available for anyone to use and modify.