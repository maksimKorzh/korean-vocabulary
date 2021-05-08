##########################################
#
# A script to auto generate voacabulary
#   from the given input Korean text
#
##########################################

# packages
from konlpy.tag import Okt
import requests
from bs4 import BeautifulSoup
import json

# vocabulary
vocabulary = []

'''
# create OKT instance
okt = Okt();

# open input file
with open('korean.txt') as f:
    # init input text
    text = f.read()
    
    # tokenize text
    tokenized_text = okt.pos(text, norm=True, stem=True)
'''

tokenized_text = [('내일', 'Noun'), ('은', 'Josa'), ('오늘', 'Noun'), ('보다', 'Josa'), ('추워지다', 'Verb'), ('수도', 'Noun'), ('있다', 'Adjective'), ('옷', 'Noun'), ('을', 'Josa'), ('따뜻하다', 'Adjective'), ('입다', 'Verb'), ('되다', 'Verb'), ('것', 'Noun'), ('같다', 'Adjective')]

# loop over tokens
for token in tokenized_text:
    # translate.com POST request data payload
    payload = {
        'text_to_translate': token[0],
        'source_lang': 'ko',
        'translated_lang': 'en',
        'use_cache_only': 'false'
    }

    # make HTTP POST request to translate.com
    response = requests.post('https://www.translate.com/translator/ajax_translate', data=payload)

    # parse the response
    translated_text = json.loads(response.text)['translated_text']
    
    # print debug info
    print('Translating...', token[0] + ': ', translated_text, ', Type:', token[1])
    
    # optionally request conjugation details
    if ('다' in token[0]):
        # get conjugation details
        response = requests.get('https://koreanverb.app/?search=' + token[0])

        # parse the content
        content = BeautifulSoup(response.text, 'lxml')

        # extract HTML table
        table = content.find('table')

        # extract table data
        conjugation_details = list(filter(None, [
            ': '.join([col.text.replace('declarative ', '').replace(' informal high', '') for col in row.find_all('td')])
            for row in
            table.find_all('tr')
            if 'declarative present informal high' in row.text or
               'declarative past informal high' in row.text or
               'declarative future informal high' in row.text
        ]))
        
        # print debug info
        print('Conjugationg...', token[0] + ': ', conjugation_details)
    
    # init details
    congation_details = []

    # append token to vocabulary
    vocabulary.append({
        'Word': token[0],
        'Type': token[1],
        'Translation': translated_text
    })

























