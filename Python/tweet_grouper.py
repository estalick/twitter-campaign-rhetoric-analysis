import pandas as pd
from topics import get_topics


class CandidateGrouper:

    @staticmethod
    def get_engagement_df(categorized_tweets_df):
        # get total favorites and retweets per candidate
        engagement_total_df = categorized_tweets_df[['candidate_id', 'tweet_favorites', 'tweet_retweets']].groupby(
            'candidate_id').sum()
        engagement_total_df.rename(columns={'tweet_favorites': 'total_candidate_favorites',
                                            'tweet_retweets': 'total_candidate_retweets'}, inplace=True)
        engagement_mean_df = categorized_tweets_df[['candidate_id', 'tweet_favorites', 'tweet_retweets']].groupby(
            'candidate_id').mean()

        count_df = categorized_tweets_df[['candidate_id', 'tweet_favorites']].groupby('candidate_id').count().reset_index()
        count_df.columns = ['candidate_id', 'total_tweets']

        engagement_mean_df.rename(columns={'tweet_favorites': 'mean_candidate_favorites',
                                           'tweet_retweets': 'mean_candidate_retweets'}, inplace=True)
        engagement_df = engagement_total_df.merge(engagement_mean_df, on='candidate_id')
        engagement_df = engagement_df.merge(count_df, on='candidate_id')
        return engagement_df

    @staticmethod
    def group(categorized_tweets_csv_filename, candidates_csv_filename, output_filename):
        topics = get_topics()
        categorized_tweets_df = pd.read_csv(categorized_tweets_csv_filename)

        cols = ['candidate_id', 'tweet_favorites', 'tweet_retweets', 'category']
        new_tweets_df = pd.DataFrame(columns=cols)

        for index, row in categorized_tweets_df.iterrows():
            if index % 500 == 0:
                print(index)
            for topic in topics:
                if row[topic] == 1:
                    new_row = {
                        'candidate_id': row['candidate_id'],
                        'tweet_favorites': row['tweet_favorites'],
                        'tweet_retweets': row['tweet_retweets'],
                        'category': topic
                    }
                    new_tweets_df = new_tweets_df.append(new_row, ignore_index=True)

        new_tweets_df['tweet_favorites'] = new_tweets_df['tweet_favorites'].astype(int)
        new_tweets_df['tweet_retweets'] = new_tweets_df['tweet_retweets'].astype(int)

        new_tweets_df = new_tweets_df.groupby(['candidate_id', 'category']).agg(['count', 'mean', 'sum'])
        new_tweets_df.columns = new_tweets_df.columns.map('{0[0]}_{0[1]}'.format)
        new_tweets_df = new_tweets_df.reset_index()
        new_tweets_df.drop(['tweet_retweets_count'], axis=1, inplace=True)
        new_tweets_df.columns = ['candidate_id', 'category', 'count',
                                 'tweet_favorites_mean', 'tweet_favorites_sum', 'tweet_retweets_mean',
                                 'tweet_retweets_sum']

        cols = ['candidate_id']
        for topic in topics:
            cols.append(topic + '_count')
            cols.append(topic + '_average_favorites')
            cols.append(topic + '_sum_favorites')
            cols.append(topic + '_average_retweets')
            cols.append(topic + '_sum_retweets')

        candidate_category_info_df = pd.DataFrame(columns=cols)
        current_cand_id = -1
        current_row = {}
        for index, row in new_tweets_df.iterrows():
            if index % 500 == 0:
                print(index)
            if row['candidate_id'] != current_cand_id:
                for topic in topics:
                    if topic + '_count' not in current_row:
                        current_row[topic + '_count'] = 0
                        current_row[topic + '_average_favorites'] = 0
                        current_row[topic + '_sum_favorites'] = 0
                        current_row[topic + '_average_retweets'] = 0
                        current_row[topic + '_sum_retweets'] = 0

                if current_cand_id != -1:
                    candidate_category_info_df = candidate_category_info_df.append(current_row, ignore_index=True)
                current_row = {'candidate_id': row['candidate_id']}
                current_cand_id = row['candidate_id']

            category = row['category']
            current_row[category + '_count'] = row['count']
            current_row[category + '_average_favorites'] = row['tweet_favorites_mean']
            current_row[category + '_sum_favorites'] = row['tweet_favorites_sum']
            current_row[category + '_average_retweets'] = row['tweet_retweets_mean']
            current_row[category + '_sum_retweets'] = row['tweet_retweets_sum']

        engagement_df = CandidateGrouper.get_engagement_df(categorized_tweets_df)
        candidates_df = pd.read_csv(candidates_csv_filename)
        candidates_df = candidates_df[['candidate_id', 'party', 'gender']]

        candidate_category_info_df = candidate_category_info_df.merge(engagement_df, on='candidate_id')
        candidate_category_info_df = candidate_category_info_df.merge(candidates_df, on='candidate_id')

        # This part calculates masculine/feminine engagement
        feminine_topics = ['womens_rights', 'education', 'healthcare', 'familycare']
        masculine_topics = ['military', 'economics', 'foreign_affairs', 'policing']
        candidate_category_info_df['masculine_count'] = sum(candidate_category_info_df['{0}_count'.format(topic)] for topic in masculine_topics)
        candidate_category_info_df['feminine_count'] = sum(candidate_category_info_df['{0}_count'.format(topic)] for topic in feminine_topics)

        candidate_category_info_df['masculine_total_engagement'] = sum(candidate_category_info_df['{0}_sum_favorites'.format(topic)] for topic in masculine_topics) + sum(candidate_category_info_df['{0}_sum_retweets'.format(topic)] for topic in masculine_topics)
        candidate_category_info_df['feminine_total_engagement'] = sum(candidate_category_info_df['{0}_sum_favorites'.format(topic)] for topic in feminine_topics) + sum(candidate_category_info_df['{0}_sum_retweets'.format(topic)] for topic in feminine_topics)

        candidate_category_info_df['masculine_average_engagement'] = candidate_category_info_df['masculine_total_engagement'] / candidate_category_info_df['masculine_count']
        candidate_category_info_df['feminine_average_engagement'] = candidate_category_info_df['feminine_total_engagement'] / candidate_category_info_df['feminine_count']

        candidate_category_info_df.to_csv(output_filename)


year = 2020
CandidateGrouper.group(categorized_tweets_csv_filename='tweet_categorization\\output_csvs\\categorized_tweets_{0}.csv'.format(year),
                       candidates_csv_filename='ballotpedia_web_scraping\\output_csvs\\candidates_{0}.csv'.format(year),
                       output_filename='tweet_categorization\\output_csvs\\grouped_tweets_{0}.csv'.format(year))
