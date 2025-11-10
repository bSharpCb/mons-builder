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

## Requirements

- Python 3.6 or higher

## Usage

1. Ensure you have the `mons_db.json` file in the same directory as the script
2. Run the script:

```bash
python3 team_builder.py
```

3. The generated team will be saved to `team_output.txt` and also displayed in the console

## How It Works

The team builder uses the following algorithm:

1. Loads Pokémon data from the database
2. Calculates type effectiveness for each Pokémon
3. Builds a team by prioritizing Pokémon that provide resistances to required types
4. Selects a random build for each team member
5. Outputs the complete team

## Customization

You can modify the coverage requirements by editing the `COVERAGE_REQUIREMENTS` dictionary in the script. The keys are attack types, and the values are the number of Pokémon that should resist that type.

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