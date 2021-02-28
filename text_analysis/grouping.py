import numpy as np
import pandas as pd
import topics as t



def main():
    topics = t.get_topics()
    tweets_info_df = pd.read_csv('letsseebig.csv')
    val_counts = tweets_info_df['candidate_id'].value_counts().to_dict()

    # tweets_info_df = tweets_info_df[['candidate_id', 'candidate_name', 'category', 'tweet_text']]
    # tweets_info_df = tweets_info_df.groupby(['candidate_id', 'candidate_name', 'category']).count().reset_index()
    # tweets_info_df.columns = ['candidate_id', 'candidate_name', 'category', 'count']

    tweets_info_df = tweets_info_df[['candidate_id', 'candidate_name', 'category', 'tweet_favorites', 'tweet_retweets', 'tweet_text']]
    tweets_info_df = tweets_info_df.groupby(['candidate_id', 'candidate_name', 'category']).agg(['count', 'mean', 'sum'])
    tweets_info_df.columns = tweets_info_df.columns.map('{0[0]}_{0[1]}'.format)
    tweets_info_df = tweets_info_df.reset_index()
    tweets_info_df.drop(['tweet_retweets_count'], axis=1, inplace=True)
    tweets_info_df.columns = ['candidate_id', 'candidate_name', 'category', 'count',
                              'tweet_favorites_mean', 'tweet_favorites_sum', 'tweet_retweets_mean',
                              'tweet_retweets_sum']

    candidates_df = pd.read_csv('Candidates2020_all_id_pt.csv')
    for topic in topics:
        candidates_df[topic + '_count'] = 0
        candidates_df[topic + '_average_favorites'] = 0
        candidates_df[topic + '_average_retweets'] = 0

    candidates_df['total_tweets'] = 0
    for candidate_id in val_counts.keys():
        candidates_df.loc[candidates_df['id'] == candidate_id, ['total_tweets']] = val_counts[candidate_id]

    candidate_ids = list(candidates_df['id'].unique())

    for id in candidate_ids:
        for topic in topics:
            rows = tweets_info_df.loc[(tweets_info_df['candidate_id'] == int(id)) & (tweets_info_df['category'] == topic)]
            if len(rows) > 0:
                count = int(rows.iloc[0]['count'])
                avg_fav = int(rows.iloc[0]['tweet_favorites_mean'])
                avg_rt = int(rows.iloc[0]['tweet_retweets_mean'])
                candidates_df.loc[candidates_df['id'] == id, [topic + '_count']] = count
                candidates_df.loc[candidates_df['id'] == id, [topic + '_average_favorites']] = avg_fav
                candidates_df.loc[candidates_df['id'] == id, [topic + '_average_retweets']] = avg_rt

    candidates_df.to_csv('candidates_counts2.csv')


if __name__ == '__main__':
    main()