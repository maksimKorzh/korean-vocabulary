##########################################
#
# A script to auto generate voacabulary
#   from the given input Korean text
#
##########################################

# print debug info
print('Loading...')
    
# packages
from konlpy.tag import Okt
import requests
from bs4 import BeautifulSoup
from jinja2 import Environment
import json
import csv

# vocabulary
vocabulary = []

# print debug info
print('Creating tokenizer instance...')

# create OKT instance
okt = Okt();

korean_text = ''

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

# word count
count = 0

# loop over tokens
for token in tokenized_text:
    try:
        # translate.com POST request data payload
        payload = {
            'text_to_translate': token[0],
            'source_lang': 'ko',
            'translated_lang': 'en',
            'use_cache_only': 'false'
        }

        # make HTTP POST request to translate.com
        response = requests.post(
            'https://www.translate.com/translator/ajax_translate',
            headers={'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}, # change to any if daily dose of requests is exhausted
            data=payload
        )

        # parse the response
        translated_text = json.loads(response.text)['translated_text']
        
        # print debug info
        count += 1
        print('Translating...', token[0] + ': ',
               translated_text, ', Type:',
               token[1], ', word',
               count,
               'out of', len(tokenized_text),
               ' words')
        
        # init details
        congation_details = []
        
        # optionally request conjugation details
        if (token[1] in ['Verb', 'Adverb', 'Adjective']):
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
            print('Conjugating...', token[0] + ': ', conjugation_details)
        
        # skip punctuation, foreign words and duplicates
        try:
            if (token[1] == 'Punctuation' or token[1] == 'Foreign'):
                # print debug info
                print('Skipping garbage...')
                continue
        except Exception as e:
            print('Error skipping token:', e)

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
            if (token[1] in ['Verb', 'Adverb', 'Adjective']):
                vocabulary[-1]['Present tense'] = conjugation_details[0].split(': ')[-1]
                vocabulary[-1]['Past tense'] = conjugation_details[1].split(': ')[-1]
                vocabulary[-1]['Future tense'] = conjugation_details[2].split(': ')[-1]
        
        except:
            pass

    except:
        print('Failed to translate: ', token)

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
    
    <!-- Analytics -->
    <script type="text/javascript">
      if (window.location.href.includes('github')) {
        $.post('https://maksimkorzh.pythonanywhere.com/analytics/api/post', {
          date: new Date,
          url: window.location.href
        });
      }
    </script>

  </head>
  <body>
    <div class="card">
      <div class="card-header text-center">
        <h5 class="font-weight-bold">Auto generated vocabulary</h5>
        <small>Made with ??? by Code Monkey King</small>
      </div>
      <div class="card-body">
        <div class="row m-0 p-0">
          <div class="col m-0 p-0" style="width: 730px;">
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
          
          <!-- Screen keyboard -->
          <div id="keyboard" class="col-5 m-0 p-0 ml-4">
            <!-- Word order hint -->
            <div class="mb-3 ml-4 text-center" style="width: 495px;">
              <span class="badge badge-danger">Subject</span>
              <span class="badge badge-warning">Time</span>
              <span class="badge badge-secondary">Place</span>
              <span class="badge badge-success">Object</span>
              <span class="badge badge-info">Adverb</span>
              <span class="badge badge-primary">Verb</span>
            </div>
            
            <textarea autofocus class="ml-4" id="hangul-text" style="width: 495px; height: 215px; font-size: 30px;" onkeydown="physicalKeyboardInput();" placeholder=" Build your Korean sentence here..."></textarea>
            <div class="row m-0 p-0" style="width: 550px;">
              <div class="btn-group mt-2 mx-auto">
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary mr-1" style="width: 42px;">1</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1" style="width: 42px;">2</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1" style="width: 42px;">3</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1" style="width: 42px;">4</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1" style="width: 42px;">5</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1" style="width: 42px;">6</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1" style="width: 42px;">7</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1" style="width: 42px;">8</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1" style="width: 42px;">9</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1" style="width: 42px;">0</button>
              </div>
              <div class="btn-group mt-2 mx-auto">
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary mr-1">???</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1">???</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1">???</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1">???</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1">???</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1">???</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1">???</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1" style="width: 42px;">-</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1" style="width: 42px;">:</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1" style="width: 42px;">"</button>
              </div>
              <div class="btn-group mt-2 mx-auto">
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary mr-1">???</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1">???</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1">???</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1">???</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1">???</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1">???</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1">???</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1">???</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1">???</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1">???</button>
              </div>
              <div class="btn-group mt-2 mx-auto">
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary mr-1">???</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1">???</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1">???</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1">???</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1">???</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1">???</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1">???</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1">???</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1">???</button>
                      <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1" style="width: 42px;">!</button>
              </div>
              <div class="btn-group mt-2 mx-auto">
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary mr-1">???</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1">???</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1">???</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1">???</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1">???</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1">???</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1">???</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1" style="width: 42px;">,</button>
                <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1" style="width: 42px;">.</button>
                      <button onclick="screenKeyboardInput(this);" class="btn btn-outline-secondary ml-1 mr-1" style="width: 42px;">?</button>
              </div>
              <div class="btn-group mt-2 mx-auto" style="width: 500px;">
                <button onclick="screenKeyboardInput(this);" class="col btn btn-outline-secondary ml-1 mr-1">Space</button>
                <button onclick="screenKeyboardBackspace(this);" class="col btn btn-outline-secondary ml-1 mr-1">Backspace</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="card-footer text-center">
        <strong>Original Korean text:</strong><br>
        {{ korean_text }}
        <hr>
        <strong>English translation:</strong><br>
        {{ full_translation }}
        <hr>
        <small>freesoft.for.people@gmail.com</small>
      </div>
    </div>
  </body>
  <script type="text/javascript">
    $('#vocabulary').dataTable({
      "bSort": false
    });
  </script>
  
  <!-- Hangul.js library -->
  <script src="https://unpkg.com/hangul-js" type="text/javascript"></script>

  <!-- Main script -->
  <script>
    const HANGUL = {
      'q': '???',
      'w': '???',
      'e': '???',
      'r': '???',
      't': '???',
      'y': '???',
      'u': '???',
      'i': '???',
      'o': '???',
      'p': '???',
      'a': '???',
      's': '???',
      'd': '???',
      'f': '???',
      'g': '???',
      'h': '???',
      'j': '???',
      'k': '???',
      'l': '???',
      'z': '???',
      'x': '???',
      'c': '???',
      'v': '???',
      'b': '???',
      'n': '???',
      'm': '???',
      'Q': '???',
      'W': '???',
      'E': '???',
      'R': '???',
      'T': '???',
      'O': '???',
      'P': '???',
    };
    
    // always type text at cursor position
    function insertAtCursor(textArea, userInput) {
      if (textArea.selectionStart || textArea.selectionStart == '0') {
        var startPos = textArea.selectionStart;
        var endPos = textArea.selectionEnd;
        textArea.value = textArea.value.substring(0, startPos)
          + userInput
          + textArea.value.substring(endPos, textArea.value.length);
      }

      return endPos;
    }
    
    // handle user input from physical keyboard
    function physicalKeyboardInput() {
      // extract pressed key
      let key = window.event.key;
      
      // if corresponding character exists
      if (HANGUL[key] && window.event.ctrlKey == false) {
        // hack to avoid printing roman letters
        window.event.preventDefault();
        
        // extract textarea DOM element
        let text = document.getElementById('hangul-text');
        
        // input hangul characters instead of roman characters
        let pos = insertAtCursor(text, HANGUL[key]);
        
        // disassemble characters
        let parsed = Hangul.disassemble(text.value);

        // assemble characters
        text.value = Hangul.assemble(parsed);
        
        // adjust cursor position
        if (text.value.length - pos > 1)
          text.selectionEnd = text.value[pos] == ' ' ? pos : pos + 1;
      }
    }
    
    // handle user input from screen keyboard
    function screenKeyboardInput(button) {
      // extract button character
      let key = button.innerHTML.replace('Space', ' ');
      
      // extract textarea DOM element
      let text = document.getElementById('hangul-text');

      // force focus on textarea
      text.focus();
      
      // input hangul characters from screen keyboard
      let pos = insertAtCursor(text, key);

      // disassemble characters
      let parsed = Hangul.disassemble(text.value);

      // assemble characters
      text.value = Hangul.assemble(parsed);
      
      // adjust cursor position
      if (text.value.length - pos > 1)
        text.selectionEnd = (text.value[pos] == ' ' && button.innerHTML != 'Space') ? pos : pos + 1;
    }
    
    // handle backspace
    function screenKeyboardBackspace() {
      // extract textarea DOM element
      let text = document.getElementById('hangul-text');

      // force focus on textarea
      text.focus();
      
      // current cursor position
      var startPos = text.selectionStart;
      var endPos = text.selectionEnd;
        
      // erase character
      text.value = text.value = text.value.substring(0, startPos - 1) +
                                    text.value.substring(endPos, text.value.length);
      
      // adjust cursor position
      text.selectionEnd = startPos - 1;
    }
  </script>
</html>'''

# render HTML template
html_output = Environment().from_string(html_template).render(
    results=vocabulary,
    fieldnames=[col for col in vocabulary[0].keys()],
    korean_text=korean_text.replace('\n', '<br>'),
    full_translation=vocabulary[-1]['Translation'].replace('.', '.<br>').replace(',', ',<br>'),
    len=len
)

# write HTML file
with open('./html/vocabulary.html', 'w') as f:
    f.write(html_output)





















