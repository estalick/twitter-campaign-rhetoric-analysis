import pandas as pd


def get_gendered_tweets_engagement(year):
    grouped_df = pd.read_csv('./tweet_categorization/output_csvs/grouped_tweets_{0}.csv'.format(year))
    feminine_topics = ['womens_rights', 'education', 'healthcare', 'familycare']
    masculine_topics = ['military', 'economics', 'foreign_affairs', 'policing']

    grouped_df['masculine_count'] = sum(grouped_df['{0}_count'.format(topic)] for topic in masculine_topics)
    grouped_df['feminine_count'] = sum(grouped_df['{0}_count'.format(topic)] for topic in feminine_topics)

    grouped_df['masculine_total_engagement'] = sum(grouped_df['{0}_sum_favorites'.format(topic)] for topic in masculine_topics) + sum(grouped_df['{0}_sum_retweets'.format(topic)] for topic in masculine_topics)
    grouped_df['feminine_total_engagement'] = sum(grouped_df['{0}_sum_favorites'.format(topic)] for topic in feminine_topics) + sum(grouped_df['{0}_sum_retweets'.format(topic)] for topic in feminine_topics)

    grouped_df['masculine_average_engagement'] = grouped_df['masculine_total_engagement'] / grouped_df['masculine_count']
    grouped_df['feminine_average_engagement'] = grouped_df['feminine_total_engagement'] / grouped_df['feminine_count']

    print(grouped_df[['candidate_id', 'masculine_average_engagement', 'feminine_average_engagement']])


if __name__ == '__main__':
    year = 2020
    get_gendered_tweets_engagement(year)
