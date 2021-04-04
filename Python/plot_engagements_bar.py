import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import topics as t


class StackedEngagementPlotter:
    def __init__(self, grouped_tweets_csv_filename, plot_year):
        self.grouped_tweets_csv_filename = grouped_tweets_csv_filename
        self.year = plot_year

        self.topics = t.get_topics()
        self.female_topics = ['womens_rights', 'education', 'healthcare', 'familycare']
        self.male_topics = ['military', 'economics', 'foreign_affairs', 'policing']

        self.party_and_gender_colors = t.get_colors('gender_and_party')
        self.gender_colors = t.get_colors('gender')
        self.party_colors = t.get_colors('party')


    @staticmethod
    def replace_party(party):
        if party == 'Republican Party':
            return 'Republican'
        elif party == 'Democratic Party':
            return 'Democratic'
        else:
            return party

    @staticmethod
    def auto_label(rects, ax):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = str(round(rect.get_height(), 2))
            if len(height) == 3:
                height += '0'

            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, float(height)),
                        xytext=(0, 12),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='top',
                        fontsize=8,)
                        # color = rect.get_facecolor()

    def get_plot_data(self, plot_mode):
        candidates_df = pd.read_csv(self.grouped_tweets_csv_filename)
        candidates_df = candidates_df[candidates_df.total_tweets > 0]

        cols_to_keep = ['candidate_id', 'gender', 'party', 'total_tweets', 'total_candidate_favorites',
                        'total_candidate_retweets',
                        'mean_candidate_favorites', 'mean_candidate_retweets']
        cols_to_keep += [topic + '_average_favorites' for topic in self.topics]
        cols_to_keep += [topic + '_average_retweets' for topic in self.topics]
        cols_to_keep += [topic + '_sum_favorites' for topic in self.topics]
        cols_to_keep += [topic + '_sum_retweets' for topic in self.topics]
        cols_to_keep += [topic + '_count' for topic in self.topics]
        candidates_df = candidates_df[cols_to_keep]

        candidates_df['party'] = candidates_df['party'].apply(self.replace_party)

        candidates_df = candidates_df[candidates_df['party'].isin(['Republican', 'Democratic'])]

        candidates_df['candidate_total_eng'] = candidates_df['total_candidate_favorites'] + \
                                               candidates_df['total_candidate_retweets']

        candidates_df['candidate_avg_eng'] = candidates_df['candidate_total_eng'] / candidates_df['total_tweets']

        for topic in self.topics:
            candidates_df[topic + '_total_eng'] = candidates_df[topic + '_sum_favorites'] + \
                                                  candidates_df[topic + '_sum_retweets']
            candidates_df[topic + '_engagement_score'] = (candidates_df[topic + '_total_eng'] / \
                                                          candidates_df[topic + '_count']) / \
                                                         candidates_df['candidate_avg_eng']  # divide

        # candidates_df.to_csv('checkeng.csv')
        # exit()

        cols_to_keep = ['gender', 'party', 'total_tweets', 'total_candidate_favorites', 'total_candidate_retweets',
                        'mean_candidate_favorites', 'mean_candidate_retweets', 'candidate_total_eng']
        cols_to_keep += [topic + '_engagement_score' for topic in self.topics]
        cols_to_keep += [topic + '_total_eng' for topic in self.topics]
        candidates_df = candidates_df[cols_to_keep]

        # group
        if plot_mode == 'gender':
            candidates_df = candidates_df.groupby(['gender']).mean().reset_index()
        elif plot_mode == 'party':
            candidates_df = candidates_df.groupby(['party']).mean().reset_index()
        else:
            candidates_df = candidates_df.groupby(['gender', 'party']).mean().reset_index()

        candidates_df_dict_list = candidates_df.to_dict(orient='records')
        return candidates_df_dict_list

    def plot(self, plot_mode='all', plot_year='2020'):

        candidates_df_dict_list = self.get_plot_data(plot_mode)

        fig, (ax_female_cats, ax_male_cats) = plt.subplots(2)

        width = 0.1

        max_val = 0

        # male
        r_male_values = []
        r_female_values = []
        d_male_values = []
        d_female_values = []
        m_values = []
        f_values = []
        d_values = []
        r_values = []

        for d in candidates_df_dict_list:
            for key in d:
                if '_engagement_score' not in key:
                    continue
                if key[:key.index('_engagement_score')] in self.male_topics:
                    if plot_mode == 'gender':
                        if d['gender'] == 'Male':
                            m_values.append(d[key])
                        elif d['gender'] == 'Female':
                            f_values.append(d[key])
                    elif plot_mode == 'party':
                        if d['party'] == 'Democratic':
                            d_values.append(d[key])
                        elif d['party'] == 'Republican':
                            r_values.append(d[key])
                    else:
                        if d['gender'] == 'Male' and d['party'] == 'Republican':
                            r_male_values.append(d[key])
                        elif d['gender'] == 'Female' and d['party'] == 'Republican':
                            r_female_values.append(d[key])
                        elif d['gender'] == 'Male' and d['party'] == 'Democratic':
                            d_male_values.append(d[key])
                        elif d['gender'] == 'Female' and d['party'] == 'Democratic':
                            d_female_values.append(d[key])

        x = np.arange(len(self.male_topics)) / 2

        if plot_mode == 'gender':
            max_val = max([max_val, max(m_values), max(f_values)])
            rects_m = ax_male_cats.bar(x - width / 2, m_values, width, label='Men', color=self.gender_colors['female'])
            rects_f = ax_male_cats.bar(x + width / 2, f_values, width, label='Women', color=self.gender_colors['male'])
            self.auto_label(rects_m, ax_male_cats)
            self.auto_label(rects_f, ax_male_cats)

        elif plot_mode == 'party':
            max_val = max([max_val, max(d_values), max(r_values)])
            max_val = max([max_val, max(d_values), max(r_values)])
            rects_d = ax_male_cats.bar(x - width / 2, d_values, width, label='Democrats', color=self.party_colors['democratic'])
            rects_r = ax_male_cats.bar(x + width / 2, r_values, width, label='Republicans', color=self.party_colors['republican'])
            self.auto_label(rects_d, ax_male_cats)
            self.auto_label(rects_r, ax_male_cats)

        else:
            max_val = max([max_val, max(r_male_values), max(r_female_values), max(d_male_values), max(d_female_values)])
            rects_mr = ax_male_cats.bar(x - width - width / 2, r_male_values, width, label='Republican Men', color=self.party_and_gender_colors['republican_male'])
            rects_fr = ax_male_cats.bar(x - width / 2, r_female_values, width, label='Republican Women', color=self.party_and_gender_colors['republican_female'])
            rects_md = ax_male_cats.bar(x + width / 2, d_male_values, width, label='Democratic Men', color=self.party_and_gender_colors['democratic_male'])
            rects_fd = ax_male_cats.bar(x + width + width / 2, d_female_values, width, label='Democratic Women', color=self.party_and_gender_colors['democratic_female'])
            self.auto_label(rects_mr, ax_male_cats)
            self.auto_label(rects_fr, ax_male_cats)
            self.auto_label(rects_md, ax_male_cats)
            self.auto_label(rects_fd, ax_male_cats)

        ax_male_cats.set_xticks(x)
        x_lables = [' '.join(topic.split('_')).title() for topic in self.male_topics]
        ax_male_cats.set_xticklabels(x_lables)

        # female
        r_male_values = []
        r_female_values = []
        d_male_values = []
        d_female_values = []
        m_values = []
        f_values = []
        d_values = []
        r_values = []

        for d in candidates_df_dict_list:
            for key in d:
                if '_engagement_score' not in key:
                    continue
                if key[:key.index('_engagement_score')] in self.female_topics:
                    if plot_mode == 'gender':
                        if d['gender'] == 'Male':
                            m_values.append(d[key])
                        elif d['gender'] == 'Female':
                            f_values.append(d[key])
                    elif plot_mode == 'party':
                        if d['party'] == 'Democratic':
                            d_values.append(d[key])
                        elif d['party'] == 'Republican':
                            r_values.append(d[key])
                    else:
                        if d['gender'] == 'Male' and d['party'] == 'Republican':
                            r_male_values.append(d[key])
                        elif d['gender'] == 'Female' and d['party'] == 'Republican':
                            r_female_values.append(d[key])
                        elif d['gender'] == 'Male' and d['party'] == 'Democratic':
                            d_male_values.append(d[key])
                        elif d['gender'] == 'Female' and d['party'] == 'Democratic':
                            d_female_values.append(d[key])

        x = np.arange(len(self.female_topics)) / 2

        if plot_mode == 'gender':
            max_val = max([max_val, max(f_values), max(m_values)])
            rects_m = ax_female_cats.bar(x - width / 2, m_values, width, label='Men', color=self.gender_colors['female'])
            rects_f = ax_female_cats.bar(x + width / 2, f_values, width, label='Women', color=self.gender_colors['male'])
            self.auto_label(rects_m, ax_female_cats)
            self.auto_label(rects_f, ax_female_cats)

        elif plot_mode == 'party':
            max_val = max([max_val, max(d_values), max(r_values)])
            rects_d = ax_female_cats.bar(x - width / 2, d_values, width, label='Democrats', color=self.party_colors['democratic'])
            rects_r = ax_female_cats.bar(x + width / 2, r_values, width, label='Republicans', color=self.party_colors['republican'])
            self.auto_label(rects_d, ax_female_cats)
            self.auto_label(rects_r, ax_female_cats)

        else:
            max_val = max([max_val, max(r_male_values), max(r_female_values), max(d_male_values), max(d_female_values)])
            rects_mr = ax_female_cats.bar(x - width - width / 2, r_male_values, width, label='Republican Men', color=self.party_and_gender_colors['republican_male'])
            rects_fr = ax_female_cats.bar(x - width / 2, r_female_values, width, label='Republican Women', color=self.party_and_gender_colors['republican_female'])
            rects_md = ax_female_cats.bar(x + width / 2, d_male_values, width, label='Democratic Men', color=self.party_and_gender_colors['democratic_male'])
            rects_fd = ax_female_cats.bar(x + width + width / 2, d_female_values, width, label='Democratic Women', color=self.party_and_gender_colors['democratic_female'])

            self.auto_label(rects_mr, ax_female_cats)
            self.auto_label(rects_fr, ax_female_cats)
            self.auto_label(rects_md, ax_female_cats)
            self.auto_label(rects_fd, ax_female_cats)

        ax_female_cats.set_xticks(x)
        x_lables = [' '.join(topic.split('_')).title() if topic != 'womens_rights' else "Women's Rights" for topic in
                    self.female_topics]
        ax_female_cats.set_xticklabels(x_lables)

        ax_female_cats.legend(bbox_to_anchor=(1.04, 1), loc='upper left', fontsize='small')

        if plot_mode == 'gender':
            title = 'Fraction of Average Tweet Engagement by Category across Genders'
        elif plot_mode == 'party':
            title = 'Fraction of Average Tweet Engagement by Category across Parties'
        else:
            title = 'Fraction of Average Tweet Engagement by Category across Genders and Parties'
        title += ' ({0})'.format(self.year)

        ax_female_cats.text(s=title, x=0.5, y=1.2, size=12, ha='center',
                            transform=ax_female_cats.transAxes, fontweight='medium')

        ax_male_cats.set_ylabel('Fraction of Avg. Engagement')
        ax_female_cats.set_ylabel('Fraction of Avg. Engagement')

        ax_female_cats.set_title("Feminine Categories", size=10)
        ax_male_cats.set_title("Masculine Categories", size=10)

        ax_female_cats.set_ylim([0, max_val * 1.2])
        ax_male_cats.set_ylim([0, max_val * 1.2])

        fig.tight_layout()

        fig.set_size_inches(10, 6)

        # plt.savefig('C:\\Users\\zachg\\Downloads\\generated_plots\\' + title)

        plt.show()


if __name__ == '__main__':
    year = '2018'
    x = StackedEngagementPlotter('tweet_categorization\\output_csvs\\grouped_tweets_{0}.csv'.format(year), plot_year=year)
    x.plot(plot_mode='party')
