##########################################
#
# A script to auto generate voacabulary
#   from the given input Korean text
#
##########################################

# packages
from konlpy.tag import Okt
import json

# vocabulary
vocabulary = []



# create OTK instance
okt = Okt();

# open input file
with open('korean.txt') as f:
    # init input text
    text = f.read()
    
    # tokenize text
    tokenized_text = okt.pos(text, norm=True, stem=True)

#tokenized_text = [('내일', 'Noun'), ('은', 'Josa'), ('오늘', 'Noun'), ('보다', 'Josa'), ('추워지다', 'Verb'), ('수도', 'Noun'), ('있다', 'Adjective'), ('옷', 'Noun'), ('을', 'Josa'), ('따뜻하다', 'Adjective'), ('입다', 'Verb'), ('되다', 'Verb'), ('것', 'Noun'), ('같다', 'Adjective')]

# loop over tokens
for token in tokenized_text:
    # append token to vocabulary
    vocabulary.append({
        'Word': token[0],
        'Type': token[1]
    })

print(vocabulary)
#print(json.dumps(vocabulary, indent=2))



