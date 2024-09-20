import base64

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
        self.raw_log = base64.b64decode(log.encode('utf-8')).decode('utf-8')
        self.turns = {}
        self.team_p1 = []
        self.team_p2 = []
        self.player_1 = ''
        self.player_2 = ''
        self.current_turn = 0
        self.turns[self.current_turn] = {'battle_field_state_start': {}, 'moves': []}
        self.lines = self.raw_log.split('\n')

    def parse_player_info(self, line: str):
        """
        Extracts player information from the log.
        """
        parts = line.split('|')
        player = parts[2]
        if player == 'p1':
            self.player_1 = parts[3]
            self.turns[self.current_turn]['battle_field_state_start'][self.player_1] = {'a': '', 'b': ''}
        else:
            self.player_2 = parts[3]
            self.turns[self.current_turn]['battle_field_state_start'][self.player_2] = {'a': '', 'b': ''}

    def parse_team_info(self, line: str):
        """
        Extracts the team information from the log.
        """
        parts = line.split('|')
        player = parts[2]
        pokemon = parts[3]
        if player == 'p1':
            self.team_p1.append(pokemon)
        else:
            self.team_p2.append(pokemon)

    def parse_switch_info(self, line: str):
        """
        Parses the switch information from the log.
        """
        parts = line.split('|')
        pokemon = parts[2].split(',')[0]
        if parts[1].startswith('p1a'):
            self.turns[self.current_turn]['battle_field_state_start'][self.player_1]['a'] = pokemon
        elif parts[1].startswith('p1b'):
            self.turns[self.current_turn]['battle_field_state_start'][self.player_1]['b'] = pokemon
        elif parts[1].startswith('p2a'):
            self.turns[self.current_turn]['battle_field_state_start'][self.player_2]['a'] = pokemon
        else:
            self.turns[self.current_turn]['battle_field_state_start'][self.player_2]['b'] = pokemon

    def initialize_new_turn(self):
        """
        Initializes a new turn in the turns dictionary.
        """
        self.current_turn += 1
        self.turns[self.current_turn] = {'battle_field_state_start': {}, 'moves': []}
        self.turns[self.current_turn]['battle_field_state_start'][self.player_1] = {'a': '', 'b': ''}
        self.turns[self.current_turn]['battle_field_state_start'][self.player_2] = {'a': '', 'b': ''}

    def parse_move_info(self, line: str):
        pass


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
                    self.parse_move_info(line)
            else:
                if line.startswith('|turn|'):
                    self.initialize_new_turn()
                else:
                    self.parse_move_info(line)


        return self.turns
