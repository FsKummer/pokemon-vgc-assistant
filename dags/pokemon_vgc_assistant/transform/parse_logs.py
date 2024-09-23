import base64
import csv
import pdb
import copy

    # turn = {
    #     'battle_field_state_start': {
    #         'p1': {'a': '', 'b': ''},
    #         'p2': {'a': '', 'b': ''}
    #     },
    #     'moves': [
    #         {
    #             'action': '',
    #             'actor': '',
    #             'target': '',
    #             'move': '',
    #             'abilty': '',
    #             'item': '',
    #             'description': ''
    #         }
    #     ],
    #     'battle_field_state_end': {
    #         'p1': {'a': '', 'b': ''},
    #         'p2': {'a': '', 'b': ''}
    #     }
    # }

class ParseLogs:
    def __init__(self, log: str):
        """
        Initializes the ParseLogs class with the Base64 encoded log.
        """

        self.raw_log = log
        self.turns = {}
        self.team_p1 = []
        self.team_p2 = []
        self.player_1 = ''
        self.player_2 = ''
        self.current_turn = 0
        self.turns[self.current_turn] = {'battle_field_state_start': {}, 'moves': [], 'battle_field_state_end': {}}
        self.lines = self.raw_log.split('\n')
        self.winner = ''

    def parse_player_info(self, line: str):
        """
        Extracts player information from the log.
        """
        parts = line.split('|')
        player = parts[2]
        if player == 'p1':
            self.player_1 = parts[3]
            self.turns[self.current_turn]['battle_field_state_start'][self.player_1] = {'a': '', 'b': ''}
            self.turns[self.current_turn]['battle_field_state_end'][self.player_1] = {'a': '', 'b': ''}
        else:
            self.player_2 = parts[3]
            self.turns[self.current_turn]['battle_field_state_start'][self.player_2] = {'a': '', 'b': ''}
            self.turns[self.current_turn]['battle_field_state_end'][self.player_2] = {'a': '', 'b': ''}

    def parse_team_info(self, line: str):
        """
        Extracts the team information from the log.
        """
        parts = line.split('|')
        player = parts[2]
        pokemon = parts[3].split(',')[0]
        if player == 'p1':
            self.team_p1.append(pokemon)
        else:
            self.team_p2.append(pokemon)

    def parse_switch_info(self, line: str):
        """
        Parses the switch information from the log.
        """
        parts = line.split('|')
        pokemon = parts[3].split(',')[0]

        if self.current_turn == 0:
            if parts[2].startswith('p1a'):
                self.turns[self.current_turn]['battle_field_state_start'][self.player_1]['a'] = pokemon
                self.turns[self.current_turn]['battle_field_state_end'][self.player_1]['a'] = pokemon
            elif parts[2].startswith('p1b'):
                self.turns[self.current_turn]['battle_field_state_start'][self.player_1]['b'] = pokemon
                self.turns[self.current_turn]['battle_field_state_end'][self.player_1]['b'] = pokemon
            elif parts[2].startswith('p2a'):
                self.turns[self.current_turn]['battle_field_state_start'][self.player_2]['a'] = pokemon
                self.turns[self.current_turn]['battle_field_state_end'][self.player_2]['a'] = pokemon
            else:
                self.turns[self.current_turn]['battle_field_state_start'][self.player_2]['b'] = pokemon
                self.turns[self.current_turn]['battle_field_state_end'][self.player_2]['b'] = pokemon
        else:
            if parts[2].startswith('p1a'):
                previous_mon = self.turns[self.current_turn]['battle_field_state_end'][self.player_1]['a']
                self.turns[self.current_turn]['battle_field_state_end'][self.player_1]['a'] = pokemon
                action_player = self.player_1
            elif parts[2].startswith('p1b'):
                previous_mon = self.turns[self.current_turn]['battle_field_state_end'][self.player_1]['b']
                self.turns[self.current_turn]['battle_field_state_end'][self.player_1]['b'] = pokemon
                action_player = self.player_1
            elif parts[2].startswith('p2a'):
                previous_mon = self.turns[self.current_turn]['battle_field_state_end'][self.player_2]['a']
                self.turns[self.current_turn]['battle_field_state_end'][self.player_2]['a'] = pokemon
                action_player = self.player_2
            else:
                previous_mon = self.turns[self.current_turn]['battle_field_state_end'][self.player_2]['b']
                self.turns[self.current_turn]['battle_field_state_end'][self.player_2]['b'] = pokemon
                action_player = self.player_2
            self.turns[self.current_turn]['moves'].append({
                'player': action_player,
                'action': 'switch',
                'actor': pokemon,
                'target': previous_mon,
                'description': f"{action_player} switched {previous_mon} to {pokemon}.",
            })


    def initialize_new_turn(self):
        """
        Initializes a new turn in the turns dictionary.
        """

        old_bf_state = copy.deepcopy(self.turns[self.current_turn]['battle_field_state_end'])
        self.current_turn += 1
        self.turns[self.current_turn] = {'battle_field_state_start': {}, 'moves': [], 'battle_field_state_end': {}}
        self.turns[self.current_turn]['battle_field_state_start'] = copy.deepcopy(old_bf_state)
        self.turns[self.current_turn]['battle_field_state_end'] = copy.deepcopy(old_bf_state)

    def parse_action_info(self, line: str):
        """
        Parses the move information from the log.
        """
        parts = line.split('|')
        if len(parts) <= 1:
            return

        action = parts[1]
        if action == 'move':
            self.parse_move_info(parts)
        elif action == 'switch':
            self.parse_switch_info(line)
        elif action == '-weather':
            self.parse_weather_info(parts)
        elif action == '-fieldstart':
            self.parse_fieldstart_info(parts)
        elif action == '-ability':
            self.parse_ability_info(parts)
        elif action == 'faint':
            self.parse_faint_info(parts)
        elif action == '-terastallize':
            self.parse_terastallize_info(parts)
        elif action == '-enditem':
            self.parse_item_info(parts)
        elif action == '-damage':
            self.parse_damage_info(parts)
        elif action == '-heal':
            self.parse_heal_info(parts)
        elif action in ['-boost', '-unboost']:
            self.parse_boost_info(parts)
        elif action == '-crit':
            self.parse_crit_info(parts)
        elif action == '-status':
            self.parse_status_info(parts)
        elif action == 'cant':
            self.parse_cant_info(parts)
        elif action == '-activate':
            self.parse_activate_info(parts)
        elif action == '-message':
            self.parse_message_info(parts)
        elif action == 'win':
            self.winner = parts[2]
        else:
            pass

    def parse_weather_info(self, parts: list):
        if len(parts) <= 4:
            return
        weather = parts[2]
        ability = ' '.join(parts[3].split()[2:])
        pokemon_spot = parts[4].split()[1]
        if pokemon_spot.startswith('p1'):
            action_player = self.player_1
        else:
            action_player = self.player_2
        pokemon = self.turns[self.current_turn]['battle_field_state_end'][action_player][pokemon_spot[2]]
        self.turns[self.current_turn]['moves'].append(
            {
                'player': action_player,
                'action': 'weather',
                'actor': pokemon,
                'ability': ability,
                'description': f"{pokemon} caused {weather} to appear."
            }
        )


    def parse_fieldstart_info(self, parts: list):
        if len(parts) <= 4:
            return
        field = ' '.join(parts[2].split()[1:])
        ability = ' '.join(parts[3].split()[2:])
        pokemon_spot = parts[4].split()[1]
        if pokemon_spot.startswith('p1'):
            action_player = self.player_1
        else:
            action_player = self.player_2
        pokemon = self.turns[self.current_turn]['battle_field_state_end'][action_player][pokemon_spot[2]]
        self.turns[self.current_turn]['moves'].append(
            {
                'player': action_player,
                'action': 'fieldstart',
                'actor': pokemon,
                'ability': ability,
                'description': f"{pokemon} caused {field} to the battlefield."
            }
        )

    def parse_ability_info(self, parts: list):
        if len(parts) <= 4:
            return

        ability = parts[3]
        pokemon_spot = parts[2].split()[0]
        if pokemon_spot.startswith('p1'):
            action_player = self.player_1
        else:
            action_player = self.player_2
        pokemon = self.turns[self.current_turn]['battle_field_state_end'][action_player][pokemon_spot[2]]
        self.turns[self.current_turn]['moves'].append(
            {
                'player': action_player,
                'action': 'ability',
                'actor': pokemon,
                'ability': ability,
                'description': f"{pokemon} activated {ability}."
            }
        )


    def parse_damage_info(self, parts: list):
        pass

    def parse_heal_info(self, parts: list):
        pass

    def parse_boost_info(self, parts: list):
        pass

    def parse_crit_info(self, parts: list):
        pass

    def parse_status_info(self, parts: list):
        pass

    def parse_faint_info(self, parts: list):
        pokemon_spot = parts[2].split()[0]
        action_player = self.find_player(pokemon_spot)
        pokemon = self.turns[self.current_turn]['battle_field_state_end'][action_player][pokemon_spot[2]]
        self.turns[self.current_turn]['battle_field_state_end'][action_player][pokemon_spot[2]] = ''
        self.turns[self.current_turn]['moves'].append(
            {
                'player': action_player,
                'action': 'faint',
                'actor': pokemon,
                'description': f"{pokemon} fainted."
            }
        )

    def parse_item_info(self, parts: list):
        pokemon_spot = parts[2].split()[0]
        action_player = self.find_player(pokemon_spot)
        pokemon = self.turns[self.current_turn]['battle_field_state_end'][action_player][pokemon_spot[2]]
        item = parts[3]
        self.turns[self.current_turn]['moves'].append(
            {
                'player': action_player,
                'action': 'item',
                'actor': pokemon,
                'item': item,
                'description': f"{pokemon} consumed its {item}."
            }
        )

    def parse_terastallize_info(self, parts: list):
        pokemon_spot = parts[2].split()[0]
        action_player = self.find_player(pokemon_spot)
        pokemon = self.turns[self.current_turn]['battle_field_state_end'][action_player][pokemon_spot[2]]
        type = parts[3]
        self.turns[self.current_turn]['moves'].append(
            {
                'player': action_player,
                'action': 'terastallize',
                'actor': pokemon,
                'type': type,
                'description': f"{pokemon} was terastallized to {type} type."
            }
        )

    def parse_cant_info(self, parts: list):
        pass

    def parse_activate_info(self, parts: list):
        pass

    def parse_message_info(self, parts: list):
        message = parts[2]
        self.turns[self.current_turn]['moves'].append(
            {
                'player': '',
                'action': 'message',
                'description': message
            }
        )

    def parse_move_info(self, parts: list):
            move = parts[3]
            pokemon_spot = parts[2].split()[0]
            action_player = self.find_player(pokemon_spot)
            actor = self.turns[self.current_turn]['battle_field_state_end'][action_player][pokemon_spot[2]]
            target_spot = parts[4].split()
            if target_spot and len(target_spot[0]) > 3 and target_spot[0] != 'null':
                target_spot = target_spot[0]
                if target_spot.startswith('p1'):
                    target_player = self.player_1
                else:
                    target_player = self.player_2

                target = self.turns[self.current_turn]['battle_field_state_end'][target_player][target_spot[2]]
            else:
                target = ''

            self.turns[self.current_turn]['moves'].append({
                'player': action_player,
                'action': 'move',
                'actor': actor,
                'target': target,
                'move': move,
                'description': f"{actor} used {move} on {target}.",
            })

    def find_player(self, pokemon_spot: str) -> str:
        if pokemon_spot.startswith('p1'):
            return self.player_1
        else:
            return self.player_2

    def skip_line(self, line: str):
        return line.startswith(('|t:', '|start', '|j|', '|c|', '|upkeep|', '|l|')) or len(line) <= 1

    def parse_log(self):
        """
        Parses the full log line by line.
        """
        for line in self.lines:
            if self.skip_line(line):
                continue

            if self.current_turn == 0:
                if line.startswith('|player|'):
                    self.parse_player_info(line)
                elif line.startswith('|poke|'):
                    self.parse_team_info(line)
                elif line.startswith('|switch|'):
                    self.parse_switch_info(line)
                elif line.startswith('|turn|'):
                    self.initialize_new_turn()
                else:
                    self.parse_action_info(line)
            else:
                if line.startswith('|turn|'):
                    self.initialize_new_turn()
                else:
                    self.parse_action_info(line)


        return {
            'turns': self.turns,
            'team_p1': self.team_p1,
            'team_p2': self.team_p2,
            'player_1': self.player_1,
            'player_2': self.player_2,
            'winner': self.winner
        }

# csv_path='data/battle_info_1.csv'
# with open(csv_path, 'r') as file:
#     csv_reader = csv.reader(file)
#     next(csv_reader)
#     next(csv_reader)
#     next(csv_reader)
#     row = next(csv_reader)
#     log = row[2]

# logs_parser = ParseLogs(log)
# turns = logs_parser.parse_log()
# print(base64.b64decode(log.encode('utf-8')).decode('utf-8'))
# print(turns)
# print(logs_parser.team_p1)
# print(logs_parser.team_p2)
# print(logs_parser.player_1)
# print(logs_parser.player_2)
# print(f"Winner: {logs_parser.winner}")
# log = "|j|☆speedyturtle87\n|j|☆Warcrie\n|t:|1724040773\n|gametype|doubles\n|player|p1|speedyturtle87|carmine|1217\n|player|p2|Warcrie|blue-masters|1243\n|teamsize|p1|6\n|teamsize|p2|6\n|gen|9\n|tier|[Gen 9] VGC 2024 Reg H\n|rated|\n|rule|Species Clause: Limit one of each Pokémon\n|rule|Item Clause: Limit 1 of each item\n|clearpoke\n|poke|p1|Basculegion, L50, M|\n|poke|p1|Pelipper, L50, M|\n|poke|p1|Ursaluna-Bloodmoon, L50, M|\n|poke|p1|Volbeat, L50, M|\n|poke|p1|Decidueye-Hisui, L50, M|\n|poke|p1|Archaludon, L50, F|\n|poke|p2|Bronzong, L50|\n|poke|p2|Ninetales-Alola, L50, M|\n|poke|p2|Arcanine-Hisui, L50, F|\n|poke|p2|Kilowattrel, L50, M|\n|poke|p2|Garchomp, L50, M|\n|poke|p2|Glaceon, L50, F|\n|teampreview|4\n|inactive|Battle timer is ON: inactive players will automatically lose when time's up. (requested by speedyturtle87)\n|inactive|speedyturtle87 has 60 seconds left.\n|inactive|Warcrie has 60 seconds left.\n|\n|t:|1724040816\n|start\n|switch|p1a: Pelipper|Pelipper, L50, M|100/100\n|switch|p1b: Volbeat|Volbeat, L50, M, shiny|100/100\n|switch|p2a: Bronzong|Bronzong, L50|100/100\n|switch|p2b: Glaceon|Glaceon, L50, F|100/100\n|-weather|RainDance|[from] ability: Drizzle|[of] p1a: Pelipper\n|turn|1\n|\n|t:|1724040830\n|move|p1a: Pelipper|Weather Ball|p2b: Glaceon\n|-damage|p2b: Glaceon|56/100\n|move|p1b: Volbeat|U-turn|p2b: Glaceon\n|-damage|p2b: Glaceon|38/100\n|\n|t:|1724040853\n|switch|p1b: Basculegion|Basculegion, L50, M|100/100|[from] U-turn\n|move|p2b: Glaceon|Freeze-Dry|p1a: Pelipper\n|-supereffective|p1a: Pelipper\n|-enditem|p1a: Pelipper|Focus Sash\n|-damage|p1a: Pelipper|1/100\n|move|p2a: Bronzong|Trick Room|p2a: Bronzong\n|-fieldstart|move: Trick Room|[of] p2a: Bronzong\n|\n|-weather|RainDance|[upkeep]\n|upkeep\n|turn|2\n|\n|t:|1724040870\n|switch|p2b: Ninetales|Ninetales-Alola, L50, M, shiny|100/100\n|-weather|Snow|[from] ability: Snow Warning|[of] p2b: Ninetales\n|move|p1a: Pelipper|Protect|p1a: Pelipper\n|-singleturn|p1a: Pelipper|Protect\n|move|p2a: Bronzong|Gyro Ball|p1a: Pelipper\n|-activate|p1a: Pelipper|move: Protect\n|move|p1b: Basculegion|Last Respects|p2a: Bronzong\n|-supereffective|p2a: Bronzong\n|-damage|p2a: Bronzong|44/100\n|\n|-weather|Snow|[upkeep]\n|-heal|p2a: Bronzong|50/100|[from] item: Leftovers\n|upkeep\n|turn|3\n|\n|t:|1724040893\n|switch|p1a: Archaludon|Archaludon, L50, F|100/100\n|-terastallize|p2a: Bronzong|Water\n|move|p2a: Bronzong|Iron Defense|p2a: Bronzong\n|-boost|p2a: Bronzong|def|2\n|move|p1b: Basculegion|Last Respects|p2b: Ninetales\n|-damage|p2b: Ninetales|72/100\n|move|p2b: Ninetales|Aurora Veil|p2b: Ninetales\n|-sidestart|p2: Warcrie|move: Aurora Veil\n|\n|-weather|Snow|[upkeep]\n|-heal|p2a: Bronzong|56/100|[from] item: Leftovers\n|upkeep\n|turn|4\n|inactive|speedyturtle87 has 30 seconds left.\n|inactive|Warcrie has 30 seconds left.\n|\n|t:|1724040921\n|switch|p1b: Pelipper|Pelipper, L50, M|1/100\n|-weather|RainDance|[from] ability: Drizzle|[of] p1b: Pelipper\n|switch|p2b: Glaceon|Glaceon, L50, F|38/100\n|move|p2a: Bronzong|Gyro Ball|p1b: Pelipper\n|-resisted|p1b: Pelipper\n|-damage|p1b: Pelipper|0 fnt\n|faint|p1b: Pelipper\n|move|p1a: Archaludon|Flash Cannon|p2b: Glaceon\n|-supereffective|p2b: Glaceon\n|-damage|p2b: Glaceon|0 fnt\n|faint|p2b: Glaceon\n|\n|-weather|RainDance|[upkeep]\n|-heal|p2a: Bronzong|61/100|[from] item: Leftovers\n|upkeep\n|\n|t:|1724040938\n|switch|p2b: Ninetales|Ninetales-Alola, L50, M, shiny|72/100\n|switch|p1b: Volbeat|Volbeat, L50, M, shiny|100/100\n|-weather|Snow|[from] ability: Snow Warning|[of] p2b: Ninetales\n|turn|5\n|inactive|Warcrie has 30 seconds left.\n|\n|t:|1724040968\n|move|p2b: Ninetales|Helping Hand|p2a: Bronzong\n|-singleturn|p2a: Bronzong|Helping Hand|[of] p2b: Ninetales\n|move|p1b: Volbeat|Rain Dance|p1b: Volbeat\n|-weather|RainDance\n|move|p2a: Bronzong|Body Press|p1a: Archaludon\n|-supereffective|p1a: Archaludon\n|-damage|p1a: Archaludon|0 fnt\n|faint|p1a: Archaludon\n|\n|-weather|RainDance|[upkeep]\n|-heal|p2a: Bronzong|67/100|[from] item: Leftovers\n|-fieldend|move: Trick Room\n|upkeep\n|\n|t:|1724040978\n|switch|p1a: Basculegion|Basculegion, L50, M|100/100\n|turn|6\n|inactive|Warcrie has 30 seconds left.\n|\n|t:|1724041007\n|move|p1a: Basculegion|Last Respects|p2a: Bronzong\n|-damage|p2a: Bronzong|38/100\n|move|p2b: Ninetales|Icy Wind|p1b: Volbeat|[spread] p1a,p1b\n|-resisted|p1a: Basculegion\n|-damage|p1a: Basculegion|94/100\n|-damage|p1b: Volbeat|90/100\n|-unboost|p1a: Basculegion|spe|1\n|-unboost|p1b: Volbeat|spe|1\n|move|p1b: Volbeat|U-turn|p2b: Ninetales\n|-resisted|p2b: Ninetales\n|-damage|p2b: Ninetales|65/100\n|move|p2a: Bronzong|Gyro Ball|p1a: Basculegion\n|-resisted|p1a: Basculegion\n|-damage|p1a: Basculegion|71/100\n|\n|-weather|RainDance|[upkeep]\n|-heal|p2a: Bronzong|44/100|[from] item: Leftovers\n|upkeep\n|turn|7\n|\n|t:|1724041028\n|move|p1b: Volbeat|Tailwind|p1b: Volbeat\n|-sidestart|p1: speedyturtle87|move: Tailwind\n|move|p1a: Basculegion|Last Respects|p2a: Bronzong\n|-damage|p2a: Bronzong|15/100\n|move|p2b: Ninetales|Icy Wind|p1b: Volbeat|[spread] p1a,p1b\n|-resisted|p1a: Basculegion\n|-damage|p1a: Basculegion|65/100\n|-damage|p1b: Volbeat|79/100\n|-unboost|p1a: Basculegion|spe|1\n|-unboost|p1b: Volbeat|spe|1\n|move|p2a: Bronzong|Gyro Ball|p1a: Basculegion\n|-resisted|p1a: Basculegion\n|-damage|p1a: Basculegion|33/100\n|\n|-weather|RainDance|[upkeep]\n|-heal|p2a: Bronzong|21/100|[from] item: Leftovers\n|-sideend|p2: Warcrie|move: Aurora Veil\n|upkeep\n|turn|8\n|inactive|speedyturtle87 has 30 seconds left.\n|\n|t:|1724041053\n|move|p1a: Basculegion|Last Respects|p2a: Bronzong\n|-damage|p2a: Bronzong|0 fnt\n|faint|p2a: Bronzong\n|move|p2b: Ninetales|Icy Wind|p1b: Volbeat|[spread] p1a,p1b\n|-resisted|p1a: Basculegion\n|-damage|p1a: Basculegion|27/100\n|-damage|p1b: Volbeat|69/100\n|-unboost|p1a: Basculegion|spe|1\n|-unboost|p1b: Volbeat|spe|1\n|move|p1b: Volbeat|U-turn|p2b: Ninetales\n|-resisted|p2b: Ninetales\n|-damage|p2b: Ninetales|53/100\n|\n|-weather|RainDance|[upkeep]\n|upkeep\n|\n|t:|1724041065\n|switch|p2a: Kilowattrel|Kilowattrel, L50, M|100/100\n|turn|9\n|\n|t:|1724041073\n|move|p2b: Ninetales|Helping Hand|p2a: Kilowattrel\n|-singleturn|p2a: Kilowattrel|Helping Hand|[of] p2b: Ninetales\n|move|p1a: Basculegion|Last Respects|p2a: Kilowattrel\n|-enditem|p2a: Kilowattrel|Focus Sash\n|-damage|p2a: Kilowattrel|1/100\n|move|p2a: Kilowattrel|Discharge|p1a: Basculegion|[spread] p2b,p1a,p1b\n|-supereffective|p1a: Basculegion\n|-damage|p2b: Ninetales|15/100\n|-damage|p1a: Basculegion|0 fnt\n|-damage|p1b: Volbeat|33/100\n|-status|p1b: Volbeat|par\n|faint|p1a: Basculegion\n|move|p1b: Volbeat|U-turn|p2a: Kilowattrel\n|-resisted|p2a: Kilowattrel\n|-damage|p2a: Kilowattrel|0 fnt\n|faint|p2a: Kilowattrel\n|\n|-weather|none\n|upkeep\n|turn|10\n|\n|t:|1724041090\n|move|p1b: Volbeat|Encore|p2b: Ninetales\n|-start|p2b: Ninetales|Encore\n|move|p2b: Ninetales|Helping Hand|null|[notarget]\n|-fail|p2b: Ninetales\n|\n|-sideend|p1: speedyturtle87|move: Tailwind\n|upkeep\n|turn|11\n|\n|t:|1724041097\n|move|p2b: Ninetales|Helping Hand|p2: Kilowattrel|[notarget]\n|-fail|p2b: Ninetales\n|cant|p1b: Volbeat|par\n|\n|upkeep\n|turn|12\n|\n|t:|1724041104\n|move|p2b: Ninetales|Helping Hand|p2: Kilowattrel|[notarget]\n|-fail|p2b: Ninetales\n|cant|p1b: Volbeat|par\n|\n|-end|p2b: Ninetales|Encore\n|upkeep\n|turn|13\n|\n|t:|1724041117\n|cant|p1b: Volbeat|par\n|move|p2b: Ninetales|Icy Wind|p1b: Volbeat\n|-damage|p1b: Volbeat|18/100 par\n|-unboost|p1b: Volbeat|spe|1\n|\n|upkeep\n|turn|14\n|\n|t:|1724041124\n|move|p2b: Ninetales|Icy Wind|p1b: Volbeat\n|-damage|p1b: Volbeat|4/100 par\n|-unboost|p1b: Volbeat|spe|1\n|move|p1b: Volbeat|U-turn|p2b: Ninetales\n|-resisted|p2b: Ninetales\n|-damage|p2b: Ninetales|3/100\n|\n|upkeep\n|turn|15\n|\n|t:|1724041132\n|move|p2b: Ninetales|Icy Wind|p1b: Volbeat\n|-damage|p1b: Volbeat|0 fnt\n|faint|p1b: Volbeat\n|\n|win|Warcrie\n|raw|speedyturtle87's rating: 1217 &rarr; <strong>1194</strong><br />(-23 for losing)\n|raw|Warcrie's rating: 1243 &rarr; <strong>1266</strong><br />(+23 for winning)\n|l|☆speedyturtle87\n|player|p1|\n|l|☆Warcrie\n|player|p2|\n"
# logs_parser = ParseLogs(log)
# turns = logs_parser.parse_log()
