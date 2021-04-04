# takes a CSV of candidates that has been processed by both the categorizer and grouping scripts and outputs a plot
# which displays "Percent of Tweets by Category and Gender"

import matplotlib.pyplot as plt
import pandas as pd
import topics as t


class StackedCategoryPlotter:
    def __init__(self, grouped_tweets_csv_filename):
        self.grouped_tweets_csv_filename = grouped_tweets_csv_filename
        self.topics = t.get_topics()
        self.topic_colors = t.get_colors('topics')

        self.last_ys = None

    @staticmethod
    def replace_party(party):
        if party == 'Republican Party':
            return 'Republican'
        elif party == 'Democratic Party':
            return 'Democratic'
        else:
            return party

    def auto_label(self, rects, ax, belows):
        if self.last_ys is None:
            self.last_ys = [0] * len(rects)

        for i, rect in enumerate(rects):  # one rec for each column
            height = str(round(rect.get_height(), 3))
            if len(height) == 4:
                height += '0'

            y_pos = (float(height) + 2 * belows[i]) / 2

            y = max(y_pos, self.last_ys[i] + 0.02)
            self.last_ys[i] = y

            x_offset = 34
            if i + 1 > len(rects) / 2:
                x_offset *= -1
            if len(rects) == 2:
                x_offset *= 2

            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, y),
                        xytext=(x_offset, 0),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='top',
                        fontsize=8)
                        # color=rect.get_facecolor())
                        # bbox={'facecolor': 'black', 'boxstyle': 'square,pad=-0.05'})

    def get_plot_data(self, plot_mode, only_major_parties, include_uncategorized, include_covid):
        candidates_df = pd.read_csv(self.grouped_tweets_csv_filename)
        candidates_df = candidates_df[candidates_df['total_tweets'] > 0]
        cols_to_keep = ['gender', 'party', 'total_tweets'] + [topic + '_count' for topic in self.topics if (topic != 'covid' or include_covid)]
        candidates_df = candidates_df[cols_to_keep]
        candidates_df['party'] = candidates_df['party'].apply(self.replace_party)

        if only_major_parties:
            candidates_df = candidates_df[candidates_df['party'].isin(['Republican', 'Democratic'])]

        if plot_mode == 'gender':
            candidates_df = candidates_df.groupby(['gender']).sum().reset_index()
            labels = ['Women', 'Men']
        elif plot_mode == 'party':
            candidates_df = candidates_df.groupby(['party']).sum().reset_index()
            labels = ['Democrats', 'Republicans']
        else:  # plot_mode == 'all'
            candidates_df = candidates_df.groupby(['gender', 'party']).sum().reset_index()
            labels = ['Democratic\nWomen', 'Republican\nWomen', 'Democratic\nMen', 'Republican\nMen']

        category_counts = {topic + '_count': list(candidates_df[topic + '_count']) for topic in self.topics if (topic != 'covid' or include_covid)}
        if include_uncategorized:
            total_counts = list(candidates_df['total_tweets'])
        else:
            total_counts = [0 for i in range(len(labels))]
            for i in range(len(labels)):
                for topic_count_key in category_counts:
                    total_counts[i] += category_counts[topic_count_key][i]

        return labels, category_counts, total_counts

    def plot(self, plot_mode='all', year='2020', only_major_parties=True, include_uncategorized=True, include_covid=False):
        labels, category_counts, total_counts = self.get_plot_data(plot_mode, only_major_parties, include_uncategorized, include_covid)

        fig, ax = plt.subplots()
        fig.set_size_inches(8, 6)

        belows = [0 for i in range(len(labels))]
        for topic in [topic for topic in self.topics if (topic != 'covid' or include_covid)][::-1]:
            axis_counts = category_counts[topic + '_count']
            ratios = [(1.0 * axis_counts[i]) / (1.0 * total_counts[i]) for i in range(len(labels))]
            section_label = ' '.join(topic.split('_')).title() if topic != 'womens_rights' else "Women's Rights"
            topic_rects = ax.bar(labels, ratios, width=0.35, label=section_label, bottom=belows, color=self.topic_colors[topic])

            if not include_uncategorized:
                self.auto_label(topic_rects, ax, belows)

            belows = [belows[i] + ratios[i] for i in range(len(labels))]

        if include_uncategorized:
            non_categorized_ratios = [0 for i in range(len(labels))]
            for i in range(len(labels)):
                for category in category_counts:
                    non_categorized_ratios[i] += category_counts[category][i]
            for i in range(len(labels)):
                non_categorized_ratios[i] = (1.0 * (total_counts[i] - non_categorized_ratios[i])) / (
                            1.0 * total_counts[i])

            ax.bar(labels, non_categorized_ratios, width=0.35, label='non_categorized', bottom=belows)

        if plot_mode == 'gender':
            title = 'Fraction of Tweets by Category across Genders'
        elif plot_mode == 'party':
            title = 'Fraction of Tweets by Category across Parties'
        else:
            title = 'Fraction of Tweets by Category across Genders and Parties'
        title += ' ({0})'.format(year)

        ax.set_ylabel('Fraction of Tweets')
        ax.set_title(title)
        legend_handles, legend_labels = ax.get_legend_handles_labels()
        ax.legend(legend_handles[::-1], legend_labels[::-1], loc='upper left', bbox_to_anchor=(1.04, 1))
        # https://stackoverflow.com/questions/4700614/how-to-put-the-legend-out-of-the-plot
        fig.tight_layout()

        # plt.savefig('C:\\Users\\zachg\\Downloads\\generated_plots\\' + title)
        plt.show()


if __name__ == '__main__':
    year = '2018'
    plotter = StackedCategoryPlotter('tweet_categorization\\output_csvs\\grouped_tweets_{0}.csv'.format(year))
    plotter.plot(plot_mode='all', include_covid=False, year=year, include_uncategorized=False)


