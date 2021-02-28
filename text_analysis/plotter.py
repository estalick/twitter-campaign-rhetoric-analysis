import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import topics as t


def main():
    topics = t.get_topics()
    include_uncategorized = False

    candidates_df = pd.read_csv('candidates_counts2.csv')
    candidates_df = candidates_df[candidates_df.total_tweets > 0]
    cols_to_keep = ['gender', 'total_tweets'] + [topic + '_count' for topic in topics]
    candidates_df = candidates_df[cols_to_keep]
    candidates_df = candidates_df.groupby(['gender']).sum().reset_index()

    labels = ['Men', 'Women', 'Non-Binary']

    catagory_counts = {topic + '_count': list(candidates_df[topic + '_count']) for topic in topics}
    print(catagory_counts)
    if include_uncategorized:
        total_counts = list(candidates_df['total_tweets'])
    else:
        total_counts = [0 for i in range(len(labels))]
        for i in range(len(labels)):
            for topic_count_key in catagory_counts:
                total_counts[i] += catagory_counts[topic_count_key][i]

    print(total_counts)

    fig, ax = plt.subplots()

    belows = [0 for i in range(len(labels))]
    for topic in topics:
        axis_counts = catagory_counts[topic + '_count']
        ratioes = [(1.0 * axis_counts[i]) / (1.0 * total_counts[i]) for i in range(len(labels))]
        print(ratioes)
        ax.bar(labels, ratioes, width=0.35, label=topic, bottom=belows)
        belows = [belows[i] + ratioes[i] for i in range(len(labels))]

    if include_uncategorized:
        non_categorized_ratios = [0 for i in range(len(labels))]
        for i in range(len(labels)):
            for category in catagory_counts:
                non_categorized_ratios[i] += catagory_counts[category][i]
        for i in range(len(labels)):
            non_categorized_ratios[i] = (1.0 * (total_counts[i] - non_categorized_ratios[i])) / (1.0 * total_counts[i])

        ax.bar(labels, non_categorized_ratios, width=0.35, label='non_categorized', bottom=belows)
        print(non_categorized_ratios)

    ax.set_ylabel('Percent of Tweets')
    ax.set_title('Percent of Tweets by Category and Gender')
    ax.legend()

    plt.show()


if __name__ == '__main__':
    main()
