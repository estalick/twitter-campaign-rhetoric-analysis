import pandas as pd


class GeneralStats:
    @staticmethod
    def replace_party(party):
        if party == 'Republican Party':
            return 'Republican'
        elif party == 'Democratic Party':
            return 'Democratic'
        else:
            return party

    @staticmethod
    def get_general_stats(year):
        year = str(year)

        candidates_csv_filename = 'ballotpedia_web_scraping\\output_csvs\\candidates_{0}.csv'.format(year)
        candidates_df = pd.read_csv(candidates_csv_filename)
        candidates_df['party'] = candidates_df['party'].apply(GeneralStats.replace_party)
        candidates_df = candidates_df[candidates_df['party'].isin(['Republican', 'Democratic'])]

        # tweets_csv_filename = 'tweet_collection\\output_csvs\\tweets_{0}.csv'.format(year)
        # tweets_df = pd.read_csv(tweets_csv_filename)

        num_total_candidates = len(candidates_df['candidate_id'].unique())
        print(num_total_candidates)

        temp_df = candidates_df[candidates_df['official_twitter'].notna() | candidates_df['personal_twitter'].notna()
                                | candidates_df['campaign_twitter'].notna()]
        num_twitter_candidates = len(temp_df['candidate_id'].unique())
        print(num_twitter_candidates)

        temp_df = candidates_df[candidates_df['gender'] == 'Male']
        num_male_candidates = len(temp_df['candidate_id'].unique())
        print(num_male_candidates)

        temp_df = candidates_df[candidates_df['gender'] == 'Female']
        num_female_candidates = len(temp_df['candidate_id'].unique())
        print(num_female_candidates)


if __name__ == '__main__':
    GeneralStats.get_general_stats(2020)