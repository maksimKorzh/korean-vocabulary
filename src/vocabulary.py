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
from jinja2 import Environment
import json

# vocabulary
vocabulary = []

# print debug info
print('Creating tokenizer instance...')

# create OKT instance
okt = Okt();

# open input file
with open('korean.txt') as f:
    # init input text
    korean_text = f.read()
    
    # print debug info
    print('Tokenizing Korean text...', end='')

    # tokenize text
    tokenized_text = okt.pos(korean_text, norm=True, stem=True)
    
    # print debug info
    print('Done')

# append full sentence to the list of tokens
tokenized_text.append((korean_text, 'Full sentence'))

'''
korean_text = '내일은 오늘보다 추워질 수도 있으니까 옷을 따뜻하게 입어야 될 것 같아요'
tokenized_text = [
    ('내일', 'Noun'),
    ('은', 'Josa'),
    ('오늘', 'Noun'),
    ('보다', 'Josa'),
    ('추워지다', 'Verb'),
    ('수도', 'Noun'),
    ('있다', 'Adjective'),
    ('옷', 'Noun'),
    ('을', 'Josa'),
    ('따뜻하다', 'Adjective'),
    ('입다', 'Verb'),
    ('되다', 'Verb'),
    ('것', 'Noun'),
    ('같다', 'Adjective'),
    ('내일은 오늘보다 추워질 수도 있으니까 옷을 따뜻하게 입어야 될 것 같아요', 'Full sentence')
]
'''

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
    if ('다' in token[0] and token[1] != 'Full sentence'):
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
        'Translation': translated_text,
        'Present tense': '',
        'Past tense': '',
        'Future tense': ''
    })
    
    try:
        vocabulary[-1]['Present tense'] = conjugation_details[0].split(': ')[-1]
        vocabulary[-1]['Past tense'] = conjugation_details[1].split(': ')[-1]
        vocabulary[-1]['Future tense'] = conjugation_details[2].split(': ')[-1]
    except:
        pass

# output HTML file template
html_template = '''
<!DOCTYPE html>

<html>
  <head>
    <!-- JQuery -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>

    <!-- Bootstrap -->
    <link rel="stylesheet" type="text/css" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
    <script type = "text/javascript"  src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js"></script>
    <script type = "text/javascript" src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"></script>
    <script type = "text/javascript"  src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.bundle.min.js"></script>

    <!-- Datatable -->
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.20/css/jquery.dataTables.min.css">
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/responsive/2.2.3/css/responsive.dataTables.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.11.2/moment.min.js"></script>
    <script type = "text/javascript"  src="https://cdn.datatables.net/1.10.20/js/jquery.dataTables.min.js"></script>
    <script type = "text/javascript"  src="https://cdn.datatables.net/responsive/2.2.3/js/dataTables.responsive.min.js"></script>
    <script type = "text/javascript"  src="https://cdn.datatables.net/plug-ins/1.10.15/dataRender/datetime.js"></script>
  </head>
  <body>
    <div class="card">
      <div class="card-header text-center">
        <h5 class="font-weight-bold">Auto generated vocabulary
          <small>
          <hr>
            <strong>Original Korean text:</strong>
            <br>
            {{ korean_text }}
          <hr>
            <strong>English translation:</strong>
            <br>
            {{ full_translation }}
          </small>
        </h5>
      </div>
      <div class="card-body">
        <div class="mt-4">
          <table id="vocabulary" class="display table nowrap responsive" style="width: 100%">
            <thead>
              <tr>
                {% for header in results[0].keys() %}
                  <th>{{ header }}</th>
                {% endfor %}
              </tr>
            </thead>
            <tbody>
              {% for row in results[0: -1] %}
                <tr>
                  {% for index in range(0, len(fieldnames)) %}
                    <td>{{row[fieldnames[index]]}}</td>
                  {% endfor %}
                </tr>
              {% endfor %}
            </tbody>
          </table>

        </div>
      </div>
    </div>
  </body>
  <script type="text/javascript">
    $('#vocabulary').DataTable();
  </script>
  
</html>'''

# render HTML template
html_output = Environment().from_string(html_template).render(
    results=vocabulary,
    fieldnames=[col for col in vocabulary[0].keys()],
    korean_text=korean_text,
    full_translation=vocabulary[-1]['Translation'],
    len=len
)

# write HTML file
with open('./html/vocabulary.html', 'w') as f:
    f.write(html_output)























