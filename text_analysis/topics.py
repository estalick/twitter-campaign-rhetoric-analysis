import pandas as pd
import numpy as np


def get_topics(filepath='C:\\Users\\Eleanor\\Dropbox\\Honors Research\\Text Analysis\\category_terms.csv'):
    categories_df = pd.read_csv(filepath)
    topics = {}
    for column in categories_df.columns:
        topics[column] = [str(i) for i in list(categories_df[column]) if str(i) != 'nan']
    return topics
