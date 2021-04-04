# takes a CSV of candidates tweet data and looks for topics within each tweet

import time
import numpy as np
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
from nltk.corpus import wordnet

import topics as t

nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('punkt')
nltk.download('stopwords')
stopwords = stopwords.words('english')
sw_append_list = ['amp', 'im']
stopwords.extend(sw_append_list)
lemmatizer = WordNetLemmatizer()


def remove_handles_urls_punct(text):
    text = re.sub(r'\b(?:(?:https?|ftp)://)?\w[\w-]*(?:\.[\w-]+)+\S*', '', text.lower())
    text = re.sub('@[^\s]+', '', text)
    text = re.sub(r"[^\w\s]+", '', text)
    text = re.sub(" \d+", " ", text)
    return text


def tokenize(text):
    tokenized_text = word_tokenize(text)
    return tokenized_text


def remove_stopwords(tokenized_text):
    tokens_without_sw = [word for word in tokenized_text if not word in stopwords]
    return tokens_without_sw


def lemmatize(tokenized_text):
    def get_wordnet_pos(treebank_tag):
        if treebank_tag.startswith('J'):
            return wordnet.ADJ
        elif treebank_tag.startswith('V'):
            return wordnet.VERB
        elif treebank_tag.startswith('N'):
            return wordnet.NOUN
        elif treebank_tag.startswith('R'):
            return wordnet.ADV
        else:
            return None

    pos_text = pos_tag(tokenized_text)
    # lemmatized_tokens = [lemmatizer.lemmatize(i[0], i[1]) for i in pos_text]
    lemmatized_tokens = [lemmatizer.lemmatize(a[0], pos=get_wordnet_pos(a[1])) if get_wordnet_pos(a[1]) else a[0] for a
                         in pos_text]
    return lemmatized_tokens


def clean_data(tweets_df):
    # lowercase tweet text
    tweets_df['cleaned_text'] = tweets_df['tweet_text'].astype(str)
    tweets_df['cleaned_text'] = tweets_df['cleaned_text'].str.lower()
    tweets_df['cleaned_text'] = tweets_df['cleaned_text'].apply(remove_handles_urls_punct)
    # tweets_df['cleaned_text'] = tweets_df['cleaned_text'].str.replace('^[a-z]', '')
    tweets_df['cleaned_text'] = tweets_df['cleaned_text'].apply(tokenize)
    tweets_df['cleaned_text'] = tweets_df['cleaned_text'].apply(remove_stopwords)
    tweets_df['cleaned_text'] = tweets_df['cleaned_text'].apply(lemmatize)


def really_in(big, little):
    if little not in big:
        return False
    if len(little) == len(big):
        return True
    phrase_index = big.index(little)
    if phrase_index == 0 and big[phrase_index + len(little)] == ' ':
        return True
    if phrase_index + len(little) == len(big) and big[phrase_index - 1] == ' ':
        return True
    if big[phrase_index - 1] == ' ' and big[phrase_index + len(little)] == ' ':
        return True
    return False


def main():
    only_max_topics = False  # true for only selecting max topic(s), false otherwise for all topics present
    skip_officials = False   # make true to not include official twitters in analysis

    threshold_percent = 0.1
    input_csv = 'C:\\Users\\Eleanor\\Dropbox\\Honors Research\\Tweets\\TwitterAPIWrapper\\tweets_2018.csv'
    # input_csv = 'sample_tweets.csv'
    output_csv = '2018_categorized_tweets_all_2.csv'

    topics = t.get_topics()

    start = time.time()
    print('reading')
    tweets_df = pd.read_csv(input_csv)
    print('cleaning')
    clean_data(tweets_df)

    if skip_officials:
        tweets_df = tweets_df[tweets_df['twitter_type'] != 'official_twitter']

    tweets_df['category'] = ''
    tweets_df['category_word_matches'] = ''
    tweets_df['category_topic_percent'] = 0

    for topic in topics:
        tweets_df[topic] = 0

    print('processing')
    for index, row in tweets_df.iterrows():
        if index % 1000 == 0:
            print(index)

        counter = {topic: 0 for topic in topics.keys()}
        counter_words = {topic: [] for topic in topics.keys()}
        for topic in topics:
            for phrase in topics[topic]:
                if ' ' in phrase:
                    joined_clean_text = ' '.join(row['cleaned_text'])
                    if phrase in joined_clean_text:
                        if ' ' in phrase and not really_in(joined_clean_text, phrase):
                            continue
                        counter[topic] += 1
                        counter_words[topic].append(phrase)
                else:
                    if phrase in row['cleaned_text']:
                        counter[topic] += 1
                        counter_words[topic].append(phrase)

        if only_max_topics:
            max_topic = max(counter, key=lambda val: counter[val])
            max_topic_phrases = counter_words[max_topic]
            max_topic_percent = counter[max_topic] / len(row['cleaned_text']) if len(row['cleaned_text']) != 0 else 0
        else:
            max_topic = ''
            max_topic_phrases = []
            max_topic_percent = 1.0001 * threshold_percent

        if max_topic_percent <= threshold_percent:
            continue
        for topic in topics.keys():
            if topic == max_topic:
                continue
            topic_percent = counter[topic] / len(row['cleaned_text']) if len(row['cleaned_text']) != 0 else 0
            if topic_percent >= max_topic_percent:
                max_topic += ',' + topic
                max_topic_phrases += counter_words[topic]

        if max_topic == '':
            continue
        elif max_topic[0] == ',':
            max_topic = max_topic[1:]

        tweets_df.loc[index, ['category']] = max_topic
        tweets_df.loc[index, ['category_word_matches']] = str(max_topic_phrases)
        tweets_df.loc[index, ['category_topic_percent']] = max_topic_percent

        for topic in max_topic.split(','):
            tweets_df.loc[index, [topic.strip()]] = 1

    print('writing')
    tweets_df.to_csv(output_csv)
    print(time.time() - start)


if __name__ == '__main__':
    main()
