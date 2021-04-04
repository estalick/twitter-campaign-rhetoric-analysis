from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import topics as t

topics = t.get_topics()
topic_colors = t.get_colors('topics')
topic_gendered_colors = t.get_colors('topics_gendered')


def replace_party(party):
    if party == 'Republican Party':
        return 'Republican'
    elif party == 'Democratic Party':
        return 'Democratic'
    else:
        return party


def date_to_month_and_year(date_string):
    date_string = standardize_date_string(date_string)
    month, day, year = date_string.split('/')
    month_and_year = month + '/' + year
    return month_and_year


def standardize_date_string(date_string):
    ret = ''
    split_string = date_string.split('/')
    for i in range(len(split_string) - 1):
        ret += split_string[i] if len(split_string[i]) == 2 else '0' + split_string[i]
        ret += '/'
    ret += split_string[len(split_string) - 1]
    return ret


def date_key(date):
    date = standardize_date_string(date)
    date = datetime.strptime(date, '%m/%d/%Y') if date.count('/') == 2 else datetime.strptime(date, '%m/%Y')
    return date


def generate_eng_df(csv_filename, plot_mode, x_granularity='day', plot_type='eng', include_covid=True):
    global topics

    female_topics = ['womens_rights', 'education', 'healthcare', 'familycare']
    male_topics = ['military', 'economics', 'foreign_affairs', 'policing']

    topics_all = [topic for topic in topics if include_covid or topic != 'covid']

    categorized_tweets_df = pd.read_csv(csv_filename)
    cols_to_kep = ['candidate_gender', 'tweet_timestamp', 'party', 'tweet_favorites', 'tweet_retweets'] + topics_all
    categorized_tweets_df = categorized_tweets_df[cols_to_kep]

    categorized_tweets_df['party'] = categorized_tweets_df['party'].apply(replace_party)
    categorized_tweets_df = categorized_tweets_df[categorized_tweets_df['party'].isin(['Republican', 'Democratic'])]

    categorized_tweets_df = categorized_tweets_df[categorized_tweets_df['candidate_gender'].isin(['Male', 'Female'])]

    # remove time, keep date
    categorized_tweets_df['tweet_timestamp'] = categorized_tweets_df['tweet_timestamp'].apply(lambda x: x.split()[0])

    if x_granularity == 'month':
        categorized_tweets_df['tweet_timestamp'] = categorized_tweets_df['tweet_timestamp'].apply(
            date_to_month_and_year)

    groups = ['candidate_gender', 'party', 'tweet_timestamp']
    if plot_mode == 'gender':
        groups.remove('party')
    elif plot_mode == 'party':
        groups.remove('candidate_gender')

    topic_summed_dfs = []
    for topic in topics_all:
        df = categorized_tweets_df[categorized_tweets_df[topic] == 1].groupby(by=groups).sum().reset_index()
        df = df[groups + ['tweet_favorites', 'tweet_retweets', topic]]
        df.columns = groups + [topic + '_favorites_sum', topic + '_retweets_sum', topic + '_count']
        topic_summed_dfs.append(df)

    summed_tweets_df = topic_summed_dfs[0]
    for df in topic_summed_dfs[1:]:
        summed_tweets_df = summed_tweets_df.merge(df, on=groups, how='outer')

    for topic in topics_all:
        summed_tweets_df[topic + '_total_engagements'] = summed_tweets_df[topic + '_favorites_sum'] + summed_tweets_df[topic + '_retweets_sum']
    cols_to_kep = groups + [topic + '_total_engagements' for topic in topics_all] + [topic + '_count' for topic in topics_all]
    summed_tweets_df = summed_tweets_df[cols_to_kep]

    count_tweets_df = categorized_tweets_df[groups + [topics_all[0]]]
    count_tweets_df = count_tweets_df.groupby(by=groups).count().reset_index()
    count_tweets_df.columns = groups + ['total_tweets']
    summed_tweets_df = summed_tweets_df.merge(count_tweets_df, on=groups)

    engagement_df = categorized_tweets_df[groups + ['tweet_favorites', 'tweet_retweets']]
    engagement_df = engagement_df.groupby(by=groups).sum().reset_index()
    engagement_df['total_engagements'] = engagement_df['tweet_favorites'] + engagement_df['tweet_retweets']
    engagement_df = engagement_df[groups + ['total_engagements']]
    summed_tweets_df = summed_tweets_df.merge(engagement_df, on=groups)

    summed_tweets_df['daily_avg_engagement'] = summed_tweets_df['total_engagements'] / summed_tweets_df['total_tweets']
    for topic in topics_all:
        summed_tweets_df[topic + '_avg_engagement'] = summed_tweets_df[topic + '_total_engagements'] / summed_tweets_df[topic + '_count']
        summed_tweets_df[topic + '_engagement_score'] = summed_tweets_df[topic + '_avg_engagement'] / summed_tweets_df['daily_avg_engagement']

    summed_tweets_df = summed_tweets_df[groups + ['daily_avg_engagement'] + [topic + '_engagement_score' for topic in topics_all]]

    summed_tweets_df = summed_tweets_df[groups + [topic + '_engagement_score' for topic in topics_all]]
    summed_tweets_df.columns = groups + [topic for topic in topics_all]

    unique_dates = list(summed_tweets_df['tweet_timestamp'].unique())
    unique_dates.sort(key=date_key)
    summed_tweets_df['tweet_timestamp'] = pd.Categorical(summed_tweets_df['tweet_timestamp'], unique_dates)

    summed_tweets_df = summed_tweets_df.sort_values(by=groups)

    summed_tweets_df['masculine_topics'] = summed_tweets_df[[topic for topic in male_topics]].sum(axis=1)
    summed_tweets_df['feminine_topics'] = summed_tweets_df[[topic for topic in female_topics]].sum(axis=1)

    return summed_tweets_df, unique_dates


def generate_count_df(csv_filename, plot_mode, x_granularity='day', plot_type='eng', include_covid=True):
    global topics

    female_topics = ['womens_rights', 'education', 'healthcare', 'familycare']
    male_topics = ['military', 'economics', 'foreign_affairs', 'policing']

    topics_all = [topic for topic in topics if include_covid or topic != 'covid']

    categorized_tweets_df = pd.read_csv(csv_filename)
    cols_to_kep = ['candidate_gender', 'tweet_timestamp', 'party', 'tweet_favorites', 'tweet_retweets'] + topics_all
    categorized_tweets_df = categorized_tweets_df[cols_to_kep]

    categorized_tweets_df['party'] = categorized_tweets_df['party'].apply(replace_party)
    categorized_tweets_df = categorized_tweets_df[categorized_tweets_df['party'].isin(['Republican', 'Democratic'])]

    categorized_tweets_df = categorized_tweets_df[categorized_tweets_df['candidate_gender'].isin(['Male', 'Female'])]

    # remove time, keep date
    categorized_tweets_df['tweet_timestamp'] = categorized_tweets_df['tweet_timestamp'].apply(lambda x: x.split()[0])

    if x_granularity == 'month':
        categorized_tweets_df['tweet_timestamp'] = categorized_tweets_df['tweet_timestamp'].apply(
            date_to_month_and_year)

    groups = ['candidate_gender', 'party', 'tweet_timestamp']
    if plot_mode == 'gender':
        groups.remove('party')
    elif plot_mode == 'party':
        groups.remove('candidate_gender')

    summed_tweets_df = categorized_tweets_df.groupby(by=groups).sum().reset_index()
    count_tweets_df = categorized_tweets_df[['candidate_gender', 'party', 'tweet_timestamp', topics_all[0]]]
    count_tweets_df = count_tweets_df.groupby(by=groups).count().reset_index()

    grouped_tweets_df = pd.merge(summed_tweets_df, count_tweets_df, on=groups)

    grouped_tweets_df.columns = [*grouped_tweets_df.columns[:-1], 'total_tweets_on_day']
    grouped_tweets_df.columns = [i if not i.endswith('_x') else i[:i.index('_x')] for i in grouped_tweets_df.columns]

    unique_dates = list(grouped_tweets_df['tweet_timestamp'].unique())
    unique_dates.sort(key=date_key)
    grouped_tweets_df['tweet_timestamp'] = pd.Categorical(grouped_tweets_df['tweet_timestamp'], unique_dates)
    grouped_tweets_df = grouped_tweets_df.sort_values(by=['tweet_timestamp', 'party'])

    grouped_tweets_df['masculine_topics'] = grouped_tweets_df[[topic for topic in male_topics]].sum(axis=1)
    grouped_tweets_df['feminine_topics'] = grouped_tweets_df[[topic for topic in female_topics]].sum(axis=1)

    return grouped_tweets_df, unique_dates


def plot_tweets(df, unique_dates, plot_mode, group_topics=False, x_granularity='day', plot_type='cat', include_covid=True, plot_year='2020', save_images=False):
    global topics
    global topic_colors
    global topic_gendered_colors

    topics_all = [topic for topic in topics if include_covid or topic != 'covid']

    female_topics = ['womens_rights', 'education', 'healthcare', 'familycare']
    male_topics = ['military', 'economics', 'foreign_affairs', 'policing']

    if plot_mode == 'gender':
        sub_charts = [('Male', None), ('Female', None)]
    elif plot_mode == 'party':
        sub_charts = [(None, 'Republican'), (None, 'Democratic')]
    else:
        sub_charts = [('Male', 'Republican'), ('Female', 'Republican'),
                      ('Male', 'Democratic'), ('Female', 'Democratic')]

    for i, sub_chart in enumerate(sub_charts):
        gender, party = sub_chart
        num_subplots = len(topics_all) if not group_topics else (3 if include_covid else 2)
        subplots = plt.subplots(num_subplots)
        subplots[0].set_size_inches(12, 10)
        gender_noun = 'Women' if gender == 'Female' else 'Men'
        party_noun = 'Republicans' if party == 'Republican' else 'Democrats'

        # need to change title based on granularity
        if plot_type == 'cat':
            if not group_topics:
                if plot_mode == 'gender':
                    title = 'Number of Tweets over Time by Category for {0}'.format(gender_noun)
                    chart_df = df[df['candidate_gender'].str.match(gender)]
                elif plot_mode == 'party':
                    title = 'Number of Tweets over Time by Category for {0}'.format(party_noun)
                    chart_df = df[df['party'].str.match(party)]
                else:
                    title = 'Number of Tweets over Time by Category for {0} {1}'.format(party, gender_noun)
                    chart_df = df[(df['candidate_gender'].str.match(gender)) & (df['party'].str.match(party))]
            else:
                if plot_mode == 'gender':
                    title = 'Number of Tweets over Time by Gendered Topic for {0}'.format(gender_noun)
                    chart_df = df[df['candidate_gender'].str.match(gender)]
                elif plot_mode == 'party':
                    title = 'Number of Tweets over Time by Gendered Topic for {0}'.format(party_noun)
                    chart_df = df[df['party'].str.match(party)]
                else:
                    title = 'Number of Tweets over Time by Gendered Topic for {0} {1}'.format(party, gender_noun)
                    chart_df = df[(df['candidate_gender'].str.match(gender)) & (df['party'].str.match(party))]
        else:
            if not group_topics:
                if plot_mode == 'gender':
                    title = 'Fraction of Average Engagement over Time by Category for {0}'.format(gender_noun)
                    chart_df = df[df['candidate_gender'].str.match(gender)]
                elif plot_mode == 'party':
                    title = 'Fraction of Average Engagement over Time by Category for {0}'.format(party_noun)
                    chart_df = df[df['party'].str.match(party)]
                else:
                    title = 'Fraction of Average Engagement over Time by Category for {0} {1}'.format(party, gender_noun)
                    chart_df = df[(df['candidate_gender'].str.match(gender)) & (df['party'].str.match(party))]
            else:
                if plot_mode == 'gender':
                    title = 'Fraction of Average Engagement over Time by Gendered Topic for {0}'.format(gender_noun)
                    chart_df = df[df['candidate_gender'].str.match(gender)]
                elif plot_mode == 'party':
                    title = 'Fraction of Average Engagement over Time by Gendered Topic for {0}'.format(party_noun)
                    chart_df = df[df['party'].str.match(party)]
                else:
                    title = 'Fraction of Average Engagement over Time by Gendered Topic for {0} {1}'.format(party, gender_noun)
                    chart_df = df[(df['candidate_gender'].str.match(gender)) & (df['party'].str.match(party))]
        title += ' ({0})'.format(plot_year)

        subplots[0].suptitle(title, fontsize=16)

        if not group_topics:
            plot_topics = topics_all
        elif include_covid:
            plot_topics = ['masculine_topics', 'feminine_topics', 'covid']
        else:
            plot_topics = ['masculine_topics', 'feminine_topics']

        for j, topic in enumerate(plot_topics):
            values = list(chart_df[topic])

            if topic in male_topics or topic == 'masculine_topics':
                line_color = topic_gendered_colors['masculine']
            elif topic in female_topics or topic == 'feminine_topics':
                line_color = topic_gendered_colors['feminine']
            else:
                line_color = topic_colors['covid']

            subplots[1][j].plot(unique_dates, values, color=line_color)

            twelfth = (len(subplots[1][j].get_xticks()) - 1) / 12.0
            xticks = [i * twelfth for i in range(13)]

            text_string = ' '.join(topic.split('_')).title() if topic != 'womens_rights' else "Women's Rights"

            subplots[1][j].annotate(text=text_string,
                                    xy=(0.02, 0.95),
                                    verticalalignment='top',
                                    xycoords=subplots[1][j].transAxes,
                                    bbox=dict(facecolor='white', edgecolor='none', pad=0))

            if j != len(plot_topics) - 1:
                pass
                subplots[1][j].tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
            else:
                if plot_year == '2020':
                    labels = ["Nov '19", "Dec '19", "Jan '20", "Feb '20", "Mar '20", "Apr '20", "May '20",
                         "Jun '20", "Jul '20", "Aug '20", "Sep '20", "Oct '20", "Nov '20"]
                else:
                    labels = ["Nov '17", "Dec '17", "Jan '18", "Feb '18", "Mar '18", "Apr '18", "May '18",
                              "Jun '18", "Jul '18", "Aug '18", "Sep '18", "Oct '18", "Nov '18"]
                subplots[1][j].set_xticks(xticks)
                subplots[1][j].set_xticklabels(labels)

            for x in xticks:
                subplots[1][j].axvline(x=x, linestyle="dashed", color='#A6A6A6')

        x_axis_label = x_granularity.title()
        subplots[0].text(0.5, 0, x_axis_label, va='bottom', ha='center', bbox=dict(boxstyle='square,pad=2', fc='none', ec='none'))

        y_axis_label = 'Number of Tweets' if plot_type == 'cat' else 'Fraction of Average Engagement'
        subplots[0].text(0, 0.5, y_axis_label, va='center', rotation='vertical', bbox=dict(boxstyle='square,pad=2', fc='none', ec='none'))

        subplots[0].tight_layout(pad=2)

        if save_images:
            image_name = 'plotting\\output_images\\'
            image_name += 'tweets_over_time\\' if plot_type == 'cat' else 'engagement_over_time\\'
            image_name += '_'.join(title.lower().split())
            image_name += '_by_' + x_granularity
            if not include_covid:
                image_name += '_no_covid'
            print(image_name)
            subplots[0].savefig(image_name)
            plt.close(subplots[0])

    if not save_images:
        plt.show()


def main():

    plot_type = 'cat'
    year = '2020'
    csv = 'tweet_categorization\\output_csvs\\categorized_tweets_{0}.csv'.format(year)
    x_granularity = 'day'
    mode = 'all'
    include_covid = True
    group_topics = False

    df_func = generate_count_df if plot_type == 'cat' else generate_eng_df
    df, unique_dates = df_func(csv, x_granularity=x_granularity, plot_mode=mode,
                                           include_covid=include_covid)
    plot_tweets(df, unique_dates, plot_mode=mode, group_topics=group_topics,
                x_granularity=x_granularity, plot_type=plot_type, include_covid=include_covid,
                            plot_year=year, save_images=False)

    # for group_topics in [True, False]:
    #     for include_covid in [True, False]:
    #         for mode in ['all', 'gender', 'party']:
    #             df_func = generate_count_df if plot_type == 'cat' else generate_eng_df
    #             df, unique_dates = df_func(csv, x_granularity=x_granularity, plot_mode=mode,
    #                                        include_covid=include_covid)
    #             plot_tweets(df, unique_dates, plot_mode=mode, group_topics=group_topics,
    #                         x_granularity=x_granularity, plot_type=plot_type, include_covid=include_covid,
    #                         plot_year=year, save_images=True)


if __name__ == '__main__':
    main()
