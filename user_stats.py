import sys
import pandas as pd
import nltk
import string
from gensim.utils import simple_preprocess, lemmatize
from gensim import models
from nltk.stem import WordNetLemmatizer 
from gensim.corpora.dictionary import Dictionary

en_stop = set(nltk.corpus.stopwords.words('english'))

lemmatizer = WordNetLemmatizer()
word_rooter = nltk.stem.snowball.PorterStemmer(ignore_stopwords=False).stem

# method for grabbing from csv list
def parse_list_notation(line):
  return line.replace('"', "").replace("'", '').replace(" ", '').replace("[", '').replace("]", '').split(',') 

# to be used for lda model creation and for test user text
def clean_document(text):
  text = [word.translate(str.maketrans('','',string.punctuation)) for word in text]
  text = [word for word in text if word.isalpha()]
  text = [word for word in text if len(word) > 2]
  text = [word for word in text if 'https' not in word]
  text = [word.lower() for word in text if word.lower() not in en_stop]
  text = [lemmatizer.lemmatize(word) for word in text]
  text = [word_rooter(word) for word in text]
  return text

# This method is used to find how many words there are in a topic above
# the decided MINIMUM_RELEVANCE value. 
def topic_scaling(model): 
  MINIMUM_RELEVANCE = 0.0001 
  scales =[]

  for topic in model.show_topics(num_topics=model.num_topics):
    term_count = model.get_topic_terms(topic[0], model.num_terms)  
    relevant_term_count = [term for term in term_count if term[1] > MINIMUM_RELEVANCE]

    scales.append(len(relevant_term_count) / model.num_terms)  
    
  return scales

if len(sys.argv) < 2:
    print("No username provided.\n")
    quit()
else:
    username = sys.argv[1]

import pullUserWords
#Pull 100 user tweets
pullUserWords.pull_to_csv(username)

user_text = pd.read_csv('test_user.csv', encoding= 'macroman')
cleaned_words = clean_document( parse_list_notation( user_text['w'].iloc[0]) )

model_ranges = ['0-20k_16topics','20-40k_18topics','40-60k_18topics','60-80k_34topics','80-100k_20topics','100kplus_24topics']

topic_rankings = []

for range in model_ranges: 
  model = models.LdaModel.load('models/' + 'lda_model_' + range + '.model')
  bow = model.id2word.doc2bow(cleaned_words) # convert to bag of words format first
  doc_topics, word_topics, phi_values = model.get_document_topics(bow, per_word_topics=True) # grab doc topiz

  adjustments = topic_scaling(model) 
  adjusted_doc_topics = []

  for topic in doc_topics:  
    adjusted_doc_topics.append((topic[0], adjustments[topic[0]]*topic[1] + topic[1]))
  
  top_topic = max(adjusted_doc_topics, key=lambda x:x[1]) # get topic tuple with highest probability
  topic_rankings.append((top_topic[0], top_topic[1], range, model.show_topic(top_topic[0], topn = 10))) 

topic_rankings = sorted(topic_rankings, key=lambda x:x[1],reverse=True)
topic_rankings

print('User is most likely to be in the ' + topic_rankings[0][2] + ' income range based on their similarity score of ' + str(topic_rankings[0][1]) + ' to the following topic:')

for word in topic_rankings[0][3]:
  print(word[0])

print('Reference topic #' + str(topic_rankings[0][0] + 1) + ' in the ' + topic_rankings[0][2] + 'graph.')
print()
print('User is second most likely to be in the ' + topic_rankings[1][2] + ' income range based on their similarity score of ' + str(topic_rankings[1][1]) + ' to the following topic:')

for word in topic_rankings[1][3]:
  print(word[0])

print('Reference topic #' + str(topic_rankings[1][0] + 1) + ' in the ' + topic_rankings[1][2] + 'graph.')
print()
print('User is third most likely to be in the ' + topic_rankings[2][2] + ' income range based on their similarity score of ' + str(topic_rankings[2][1]) + ' to the following topic:')

for word in topic_rankings[2][3]:
  print(word[0])

print('Reference topic #' + str(topic_rankings[2][0] + 1) + ' in the ' + topic_rankings[2][2] + 'graph.')
