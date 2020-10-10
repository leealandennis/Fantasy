import time
import requests
import re
import sys
import csv
import os
from fuzzywuzzy import process

QBS_AWS_LINK = 'https://s3-us-west-1.amazonaws.com/fftiers/out/text_QB.txt'
RBS_AWS_LINK = 'https://s3-us-west-1.amazonaws.com/fftiers/out/text_RB-HALF.txt'
WRS_AWS_LINK = 'https://s3-us-west-1.amazonaws.com/fftiers/out/text_WR-HALF.txt'
TES_AWS_LINK = 'https://s3-us-west-1.amazonaws.com/fftiers/out/text_TE-HALF.txt'
FLEX_AWS_LINK = 'https://s3-us-west-1.amazonaws.com/fftiers/out/text_FLX-HALF.txt'

TYPE_QB = 'QB'
TYPE_RB = 'RB'
TYPE_WR = 'WR'
TYPE_TE = 'TE'
TYPE_FLEX = 'FLEX'

TYPES_TO_URLS = {
    TYPE_QB: QBS_AWS_LINK,
    TYPE_RB: RBS_AWS_LINK,
    TYPE_WR: WRS_AWS_LINK,
    TYPE_TE: TES_AWS_LINK,
    TYPE_FLEX: FLEX_AWS_LINK
}

CSV_FILE_PATH = sys.argv[1]
CSV_FILE_PATH_OPTIMIZED = re.sub(r'.csv', '_optimized.csv', CSV_FILE_PATH)

roster_by_position = {}
roster_slot_numbers = {}
optimized_roster = {}
available_players = []


def request_get_helper(path: str,
                       timeout: int = 60,
                       retries: int = -1,
                       show_error: bool = True):

    while retries > 0 or retries < 0:
        try:
            return requests.get(path)
        except requests.ConnectionError as err:
            if show_error:
                print(str(err))
                print('THERE WAS AN ERROR')

            time.sleep(timeout)

            return request_get_helper(path, timeout, retries - 1, show_error)


def get_data_arrays(position_type: str) -> list:
    boris_response = request_get_helper(TYPES_TO_URLS[position_type])
    position_text = boris_response.text
    position_text = re.sub(
        r', ', ',',
        re.sub(r'\n', ',', re.sub(r'Tier [\d]+: ', '', position_text)))
    position_text_length = len(position_text)

    if position_text[position_text_length - 1] == ',':
        position_text = position_text[0:position_text_length - 1]

    return position_text.split(',')


def read_csv():
    if not os.path.exists(CSV_FILE_PATH):
        print('Path does not exist')
        sys.exit()

    with open(CSV_FILE_PATH_OPTIMIZED, 'w') as csv_file_optimized:
        csv_writer = csv.writer(csv_file_optimized)
        csv_writer.writerow(['slot', 'name', 'position'])

    with open(CSV_FILE_PATH) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        is_first_row = True
        for row in csv_reader:
            if is_first_row:
                is_first_row = False
                continue

            position = row[2]
            roster_slot = row[0]
            player_name = row[1]

            if position in roster_by_position and player_name:
                roster_by_position[position].append(player_name)
            elif player_name:
                roster_by_position[position] = [player_name]

            if roster_slot in roster_slot_numbers:
                roster_slot_numbers[
                    roster_slot] = roster_slot_numbers[roster_slot] + 1
            else:
                roster_slot_numbers[roster_slot] = 1
            if player_name:
                available_players.append(player_name)


def find_players_position(player_name: str):
    for position, players in roster_by_position.items():
        if player_name in players:
            return position


def optimize_roster_for_position(slot_type: str, position_ratings_array):

    if slot_type == TYPE_FLEX:
        position_players_in_my_roster = roster_by_position[
            TYPE_RB] + roster_by_position[TYPE_WR] + roster_by_position[TYPE_TE]
        position = None
    else:
        position_players_in_my_roster = roster_by_position[slot_type]
        position = slot_type

    optimized_roster[slot_type] = []
    num_roster_slots_filled = 0
    player_found = False

    with open(CSV_FILE_PATH_OPTIMIZED, 'a') as csv_file_optimized:

        csv_writer = csv.writer(csv_file_optimized)

        while num_roster_slots_filled != roster_slot_numbers[slot_type]:

            for player in position_ratings_array:
                player_found = False
                result = process.extractOne(player,
                                            position_players_in_my_roster)
                name = result[0]
                ratio = result[1]

                if ratio > 85 and name in available_players:

                    if not position:
                        position = find_players_position(name)

                    optimized_roster[slot_type].append(name)
                    available_players.remove(name)
                    num_roster_slots_filled += 1
                    player_found = True
                    csv_writer.writerow([slot_type, name, position])
                    break

            if not player_found:
                csv_writer.writerow([slot_type, '', ''])
                break


def write_bench_players_to_csv():
    with open(CSV_FILE_PATH_OPTIMIZED, 'a') as csv_file_optimized:
        csv_writer = csv.writer(csv_file_optimized)

        for player in available_players:
            position = find_players_position(player)

            if position == 'K' or position == 'DEF':
                slot = position
            else:
                slot = 'BN'

            csv_writer.writerow([slot, player, position])


read_csv()
qb_ratings_array = get_data_arrays(TYPE_QB)
rb_ratings_array = get_data_arrays(TYPE_RB)
wr_ratings_array = get_data_arrays(TYPE_WR)
te_ratings_array = get_data_arrays(TYPE_TE)
flex_ratings_array = get_data_arrays(TYPE_FLEX)

optimize_roster_for_position(TYPE_QB, qb_ratings_array)

optimize_roster_for_position(TYPE_RB, rb_ratings_array)
optimize_roster_for_position(TYPE_WR, wr_ratings_array)
optimize_roster_for_position(TYPE_TE, te_ratings_array)
optimize_roster_for_position(TYPE_FLEX, flex_ratings_array)
print(optimized_roster)
write_bench_players_to_csv()
