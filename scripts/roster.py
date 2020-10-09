from bs4 import BeautifulSoup
import time
import requests
import re

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
    TYPE_QB : QBS_AWS_LINK,
    TYPE_RB: RBS_AWS_LINK,
    TYPE_WR: WRS_AWS_LINK,
    TYPE_TE: TES_AWS_LINK,
    TYPE_FLEX: FLEX_AWS_LINK
}

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


def get_data_arrays(type: str) -> list :
    boris_response = request_get_helper(TYPES_TO_URLS[type])
    position_text = boris_response.text
    position_text = re.sub(r', ', ',', re.sub(r'\n', ',', re.sub(r'Tier \d: ', '', position_text)))
    position_text_length = len(position_text)

    if position_text[position_text_length - 1] == ',':
        position_text = position_text[0:position_text_length - 1]

    return position_text.split(',')

print(get_data_arrays(TYPE_QB))
print()
print(get_data_arrays(TYPE_RB))
print()
print(get_data_arrays(TYPE_WR))
print()
print(get_data_arrays(TYPE_TE))
print()
print(get_data_arrays(TYPE_FLEX))






