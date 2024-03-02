import sys, Tour, gspread, os
from datetime import date

is_list = False
DIRECTORY = os.path.dirname(__file__)
gc = gspread.oauth(
        credentials_filename=DIRECTORY + '/credentials/credentials.json',
        authorized_user_filename=DIRECTORY + '/credentials/authorized_user.json'
    )

def convert_to_dict(a):
    new_dict = {}
    for i in a:
        new_dict[i[0]] = i[1]
    return new_dict
    
def s(e):
    if is_list:
        return e[1]
    return e[2]

def post_to_sheet(tour):
    sheet = gc.open('ngm stats')
    wks = sheet.get_worksheet(int(is_list))
    ids_dict = convert_to_dict(sheet.get_worksheet(2).get_all_values())
    ranks_dict = convert_to_dict(sheet.get_worksheet(3).get_all_values())
    full_stats = []
    for player in tour.players:
        if player.rounds_played < 5:
            continue
        rank = "?"
        if player.name in ids_dict:
            if ids_dict[player.name] in ranks_dict:
                rank = ranks_dict[ids_dict[player.name]]
        op_rate, ed_rate, in_rate = 0, 0, 0
        guess_rate = round((sum(player.correct_songs) / sum(player.total_songs)) * 100, 3)
        avg_diff = round(player.total_diff / sum(player.correct_songs), 3)
        erigs = player.dog[0]
        dog = round(sum([player.dog[i]*(i+1) for i in range(8)]) / sum(player.correct_songs), 3)
        if player.total_songs[0]:
            op_rate = round((player.correct_songs[0] / player.total_songs[0]) * 100, 3)
        if player.total_songs[1]:
            ed_rate = round((player.correct_songs[1] / player.total_songs[1]) * 100, 3)
        if player.total_songs[2]:
            in_rate = round((player.correct_songs[2] / player.total_songs[2]) * 100, 3)
        if is_list:
            full_stats.append([player.name, guess_rate, avg_diff, erigs, dog, op_rate, ed_rate, in_rate, player.rigs, player.rigs_hit, sum(player.correct_songs), sum(player.total_songs)])
        else:
            full_stats.append([rank, player.name, guess_rate, avg_diff, erigs, dog, op_rate, ed_rate, in_rate])    
    full_stats.sort(reverse=True, key=s)
    full_stats.insert(0, [str(date.today())])
    wks.update(values=full_stats, range_name='A'+str(len(wks.get_all_values())+2))
            
    

def main():
    global is_list
    args = sys.argv[1:]
    if "-l" in args:
        is_list = True
    post_to_sheet(Tour.Tour(is_list))
    

if __name__ == "__main__":
    main()