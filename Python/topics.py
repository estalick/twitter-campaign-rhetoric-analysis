import pandas as pd


def get_topics(filepath='topics\\category_terms.csv'):
    categories_df = pd.read_csv(filepath)
    topics = {}
    for column in categories_df.columns:
        topics[column] = [str(i) for i in list(categories_df[column]) if str(i) != 'nan']
    return topics


def get_colors(color_type):
    if color_type == 'topics':
        colors = {
            'womens_rights': '#8D3EAF',
            'familycare': '#D77BFF',
            'education': '#D1A7E3',
            'healthcare': '#F8E7FF',
            'military': '#3BB7B5',
            'economics': '#70D9D7',
            'foreign_affairs': '#4CF7F4',
            'policing': '#BAFFFE',
            'covid': '#FF9A42',
        }
    elif color_type == 'topics_gendered':
        colors = {
            'masculine': '#3BB7B5',
            'feminine': '#8D3EAF',
        }
    elif color_type == 'gender':
        colors = {
            'male': '#595959',
            'female': '#A6A6A6',
        }
    elif color_type == 'party':
        colors = {
            'republican': '#FF0000',
            'democratic': '#0066FF',
        }
    elif color_type == 'gender_and_party':
        colors = {
            'republican_male': '#AA0000',
            'republican_female': '#FF4949',
            'democratic_male': '#0044AA',
            'democratic_female': '#448FFF',
        }
    else:
        colors = {}

    return colors
