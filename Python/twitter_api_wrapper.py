import datetime
import tweepy
import unidecode
import pandas as pd
import numpy as np


class TwitterParser:
    def __init__(self, twitter_credentials_arg):
        auth = tweepy.OAuthHandler(twitter_credentials_arg["consumer_key"], twitter_credentials_arg["consumer_secret"])
        auth.set_access_token(twitter_credentials_arg["access_token"], twitter_credentials_arg["access_token_secret"])
        self.api = tweepy.API(auth)

    def get_tweets_from_user(self, screen_name, start_date_arg, num_items=1000):
        all_statuses = tweepy.Cursor(self.api.user_timeline,
                                     id=screen_name,
                                     until=start_date_arg[::-1],
                                     tweet_mode='extended',
                                     wait_on_rate_limit=True,
                                     wait_on_rate_limit_notify=True).items(num_items)
        return all_statuses


havent_written = True
should_write_batch = False
output_df_list = []


def write_batch():
    print('at top of write')
    global havent_written
    global output_df_list
    global output_csv
    global should_write_batch
    output_df = pd.DataFrame(output_df_list)
    output_df.to_csv(output_csv, mode='a', sep=',', encoding='utf-8', index=False, header=havent_written)
    output_df_list = []
    havent_written = False
    should_write_batch = False
    print('wrote batch')


if __name__ == "__main__":
    twitter_credentials = {
        "consumer_key": "wkfvHMlqea3Xh7cQIvqN0akcb",
        "consumer_secret": "xSTZPNtnlWW8KAqMF7LeRdMDSjqSmaNt9Jbl3BM6j1arvHzc1x",
        "access_token": "1282852132610285569-Q35U3wPpXMbHvOZdCaD1i8rhZEpxg5",
        "access_token_secret": "HJMIwOhbtdqQ0QmPUVRb46OHTgPBgLvmDoHhrEdHnktKD"
    }

    tp = TwitterParser(twitter_credentials)

    input_csv = './Candidates2020_all_id_pt.csv'
    # input_csv = './Candidates2018_all_id.csv'
    output_csv = './Candidates2020_tweets_3accts_{0}.csv'.format(datetime.datetime.now().strftime("%H%M%S_%m%d%Y"))

    id_from = 1260
    id_to = 1399
    start_date = '11-03-2019'  # MM-DD-YYYY
    end_date = '11-03-2020'  # MM-DD-YYYY
    # start_date = '11-06-2017'  # MM-DD-YYYY
    # end_date = '11-06-2018'  # MM-DD-YYYY

    start_date_obj = datetime.datetime.strptime(start_date, "%m-%d-%Y")
    end_date_obj = datetime.datetime.strptime(end_date, "%m-%d-%Y")

    candidates_df = pd.read_csv(input_csv)

    consec_exceptions_count = 0
    for i in range(id_from, id_to + 1):
        if (i + 1) % 10 == 0:
            should_write_batch = True

        try:
            candidate_row = candidates_df.loc[candidates_df['id'] == i].to_dict('records')[0]
        except IndexError:
            break  # exit loop if i val is greater than number of rows in df

        for twitter_type in ['campaign_twitter', 'official_twitter', 'personal_twitter']:
            username = candidate_row[twitter_type]
            if not username or type(username) == float and np.isnan(username):
                print('{0}: no {1} for {2} ({3})'.format(i, twitter_type, candidate_row['name'],
                                                         candidate_row['state']))
                continue
            print('{0}: getting {1} [{2}: {3}] ({4})'.format(i, candidate_row['name'], twitter_type, username,
                                                             candidate_row['state']))
            try:
                # twitter date takes form YYYY-MM-DD so we reverse it here
                tweets = tp.get_tweets_from_user(username, start_date_arg=start_date, num_items=1000)

                num_tweets = 0
                for tweet in tweets:
                    tweet_date = tweet.created_at
                    if not start_date_obj < tweet_date < end_date_obj or tweet.full_text[:2] == 'RT':  # RETWEETS
                        continue

                    new_row = {
                        'candidate_id': candidate_row['id'],
                        'candidate_name': candidate_row['name'],
                        'candidate_gender': candidate_row['gender'],
                        'candidate_state': candidate_row['state'],
                        'candidate_tenure': candidate_row['tenure'],
                        'candidate_ballotpedia': candidate_row['ballotpedia_url'],  # include on new balotpedia csvs
                        'tweet_text': str(unidecode.unidecode(tweet.full_text)),
                        'tweet_link': "http://twitter.com/anyuser/status/{0}".format(tweet.id),  # link to tweet
                        'tweet_username': username,
                        'tweet_name': tweet.user.name,
                        'tweet_timestamp': str(tweet.created_at),
                        'tweet_favorites': tweet.favorite_count,
                        'tweet_retweets': tweet.retweet_count,
                        'tweet_is_quote': str(tweet.is_quote_status),
                        'twitter_type': twitter_type,
                    }

                    output_df_list.append(new_row)
                    num_tweets += 1
                    consec_exceptions_count = 0
                print('{0}: retrieved {1} [{2}: {3}] ({4} tweets) ({5})'.format(i, candidate_row['name'], twitter_type,
                                                                                username, num_tweets,
                                                                                candidate_row['state']))

                if should_write_batch:
                    write_batch()

            except tweepy.TweepError as e:
                print(e)
                consec_exceptions_count += 1
                print(
                    "Problem getting tweets for {0}. Consecutive exceptions: {1}".format(username, consec_exceptions_count))
                if consec_exceptions_count >= 10:
                    print('Too many consecutive exceptions. Terminating')
                    write_batch()
                    exit(-1)
                else:
                    continue

    write_batch()
