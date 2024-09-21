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

        ability = ' '.join(parts[3])
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
            target_spot = parts[4].split()[0]
            if target_spot.startswith('p1'):
                target_player = self.player_1
            else:
                target_player = self.player_2
            target = self.turns[self.current_turn]['battle_field_state_end'][target_player][target_spot[2]]

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
