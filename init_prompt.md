Build a tool that can generate competitive Pokemon teams for the Smogon OU singles metagame. 

Building a team requires selecting 6 pokemon, carefully selecting a combination that provides defensive coverage against the most common offensive threats in the Smogon OU Metagame. 

The potential members to choose from can be found in the mons_db.json file in this project folder. Each pokemon included in this list has its typing listed, as well as example builds. Ultimately the output should look like a textfile with 6 builds separated by newlines (each build should reflect a different pokemon)


When considering potential members, this tool should aim to pick 6 pokemon that collectively cover the following type resistances or immunities:


**Type resistance requirements**
Every team should have at least the following:
- 2 water resists
- 1-2 fighting resists
- 1-2 dragon resists (or 1 immunity)
- 1 flying resist
- 1-2 electric resists
- 2 ground resists, or 1 immunity
- 1 dark resist