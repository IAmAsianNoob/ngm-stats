import sys, Tour, gspread, os
from datetime import date
import os

DEBUG = "DEBUG" in os.environ and os.environ["DEBUG"].lower() == "true"

MAIN_SHEET_RANDOM=0
MAIN_SHEET_WATCHED=599282945
SHEET_PLAYER_IDS=220350629
SHEET_PLAYER_RANKS=120898190
SHEET_EXTRA_STATS=1324663165

# 🐶
dog_weight = [1, 0.8, 0.5, 0.1, 0, 0, 0, 0]

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

def sort_incomplete(e):
    if is_list:
        return e[2]
    return e[3]

def post_to_sheet(tour):
    sheet = gc.open('ngm stats')
    wks = sheet.get_worksheet_by_id(MAIN_SHEET_WATCHED if is_list else MAIN_SHEET_RANDOM)
    sheet_size = len(wks.get_all_values())
    extra_stats_sheet = sheet.get_worksheet_by_id(SHEET_EXTRA_STATS)
    ids_dict = convert_to_dict(sheet.get_worksheet_by_id(SHEET_PLAYER_IDS).get_all_values())
    ranks_dict = convert_to_dict(sheet.get_worksheet_by_id(SHEET_PLAYER_RANKS).get_all_values())
    full_stats = []
    incomplete_stats = []

    for player in tour.players:
        op_rate, ed_rate, in_rate = 0, 0, 0
        guess_rate = round((sum(player.correct_songs) / sum(player.total_songs)) * 100, 3)
        avg_diff = round(player.total_diff / sum(player.correct_songs), 3)
        erigs = player.dog[0]
        dog = round(sum([player.dog[i]*(i+1) for i in range(8)]) / sum(player.correct_songs), 3)
        whats_up_dog = round(sum([player.dog[i]* dog_weight[i] for i in range(8)]) / sum(player.total_songs) * 100, 3)
        rank = "?"
        if player.name in ids_dict:
            if ids_dict[player.name] in ranks_dict:
                rank = ranks_dict[ids_dict[player.name]]
        if player.total_songs[0]:
            op_rate = round((player.correct_songs[0] / player.total_songs[0]) * 100, 3)
        if player.total_songs[1]:
            ed_rate = round((player.correct_songs[1] / player.total_songs[1]) * 100, 3)
        if player.total_songs[2]:
            in_rate = round((player.correct_songs[2] / player.total_songs[2]) * 100, 3)

        player_data = None
        if is_list:
            player_data = [player.name, guess_rate, whats_up_dog, avg_diff, erigs, dog, op_rate, ed_rate, in_rate, player.rigs, player.rigs_hit, sum(player.correct_songs), sum(player.total_songs)]
        else:
            player_data = [rank, player.name, guess_rate, whats_up_dog, avg_diff, erigs, dog, op_rate, ed_rate, in_rate]

        if player.rounds_played < 5:
            player_data.insert(0, f"{player.rounds_played} games")
            incomplete_stats.append(player_data)
        else:
            full_stats.append(player_data)

    full_stats.sort(reverse=True, key=s)
    full_stats.insert(0, [str(date.today())])

    if not DEBUG:
        wks.update(values=full_stats, range_name='A'+str(sheet_size + 2))
    else:
        for row in full_stats:
            print(" ".join([str(e) for e in row]))

    if is_list:
        full_stats.insert(0, ["player name, guess rate, usefullness, avg diff, erigs, avg /8 correct, OP guess rate, ED guess rate, IN guess rate, rigs, rigs hit, correct count, song count"])
    else:
        full_stats.insert(0, ["rank, player name, guess_rate, usefulness, avg_diff, erigs, dog, op_rate, ed_rate, in_rate"])

    if len(incomplete_stats) > 0:
        print("Check the 'Extra Stats' sheet")
        incomplete_stats.sort(reverse=True, key=sort_incomplete)
        # Pad with empty rows to clear the rest
        while len(incomplete_stats) < 10:
            incomplete_stats.append([""] * len(incomplete_stats[0]))
        if is_list:
            extra_stats_sheet.update(values=incomplete_stats, range_name="A4")
        else:
            extra_stats_sheet.update(values=incomplete_stats, range_name="A18")

    if len(tour.top_songs):
        print(f"\nTop {len(tour.top_songs)} played songs")
        for [song, play_count] in tour.top_songs:
            print(f"{song} - {play_count}")
    
    print(f"{wks.url}?range={sheet_size}:{sheet_size}")

def main():
    global is_list
    args = sys.argv[1:]
    if "-l" in args:
        is_list = True
    post_to_sheet(Tour.Tour(is_list, debug=DEBUG))

if __name__ == "__main__":
    main()