import os, json, re
from datetime import date

DIRECTORY = os.path.dirname(__file__) + "/jsons/"
REGEX = "\D*(\d{1,2})\.json$"

class Player:
    def __init__(self, name):
        self.name = name
        self.total_diff = self.rigs = self.rigs_hit = 0
        self.rounds_played = 1
        self.dog = [0]*8
        self.correct_songs = [0]*3
        self.total_songs = [0]*3
        
    def update_total(self, total_songs):
        self.total_songs = [a + b for a, b in zip(self.total_songs, total_songs)]
        
    def update_correct(self, correct_songs):
        self.correct_songs = [a + b for a, b in zip(self.correct_songs, correct_songs)]
        
    def update_dog(self, dog):
        self.dog = [a + b for a, b in zip(self.dog, dog)]
        
    def update_all(self, new):
        self.total_diff += new.total_diff
        self.rigs += new.rigs
        self.rigs_hit += new.rigs_hit
        self.rounds_played += new.rounds_played
        self.update_total(new.total_songs)
        self.update_correct(new.correct_songs)
        self.update_dog(new.dog)
        
        
class Game:
    def __init__(self, file_name, is_list = False):
        self.is_list = is_list
        self.players = []
        self.total_songs = [0]*3
        self.calculate_game(file_name)
        
    def get_all_names(self):
        return [player.name for player in self.players]
        
    def get_player_by_name(self, name):
        for player in self.players:
            if player.name == name:
                return player
        return None
        
    def calculate_game(self, file_name):
        reg_match = re.search(REGEX, file_name)
        if reg_match is None:
            print("invalid file name: {}".format(file_name))
            exit()
        songs_played = int(reg_match.group(1))
        
        with open(DIRECTORY + file_name,encoding="utf8") as f:
            data = json.load(f)
            
        for song in data['songs'][:songs_played]:
            song_type = song["songInfo"]["type"]
            self.total_songs[song_type-1]+=1
            correct_count = int(song['correctCount'])
            
            if self.is_list:
                for player_name in song['listStates']:
                    player = self.get_player_by_name(player_name["name"])
                    if player is None:
                        player = Player(player_name["name"])
                        self.players.append(player)
                    player.rigs+=1
                    if player.name in song['correctGuessPlayers']:
                        player.rigs_hit+=1
                    
            if not correct_count:
                continue
                
            for player_name in song['correctGuessPlayers']:
                player = self.get_player_by_name(player_name)
                if player is None:
                    player = Player(player_name)
                    self.players.append(player)
                player.correct_songs[song_type-1]+=1
                player.dog[correct_count-1]+=1
                if song['songInfo']['animeDifficulty'] != "Unrated":
                    player.total_diff += song['songInfo']['animeDifficulty']
                    
        while len(self.players) < 8:
            print(self.get_all_names())
            player_name = input("[{}] Input missing player name(case sensitive):".format(file_name))
            if player_name in self.get_all_names():
                print("{} is not missing".format(player_name))
                continue
            self.players.append(Player(player_name))
            
        for player in self.players:
            player.update_total(self.total_songs)
            
            
class Tour:
    def __init__(self, is_list = False):
        self.is_list = is_list
        self.players = []
        self.calculate_all_games()
        
    def get_player_by_name(self, name):
        for player in self.players:
            if player.name == name:
                return player
        return None
        
    def calculate_all_games(self):
        for file_name in os.listdir(DIRECTORY):
            game = Game(file_name, self.is_list)
            for player in game.players:
                if self.get_player_by_name(player.name) is None:
                    self.players.append(player)
                else:
                    self.get_player_by_name(player.name).update_all(player)
                    

                    