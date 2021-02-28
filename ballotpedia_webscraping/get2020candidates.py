import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import lxml  # need this for bs4
import time


states = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming']
states_pointer = 0

def get_candidates_profiles(url):
    '''
    Function to get "a-tags" for all candidates
    :param url:
    :return: a list of a-tags
    '''

    r = requests.get(url)
    html = r.content
    soup = BeautifulSoup(html, 'lxml')
    target = soup.find_all('h2', text='U.S. House')

    a_tags = []

    for h2 in target:
        for tag in h2.next_siblings:
            if tag.name == 'h2':
                break
            elif tag.name == 'ol':
                first_children = tag.findChildren()
                for li_tag in first_children:
                    second_children = li_tag.findChildren()
                    for a_tag in second_children:
                        a_tags.append(a_tag)

    return [(a_tag.text, a_tag['href']) for a_tag in a_tags]


def get_profile_info(profile_url):
    '''
    Get Twitter URL from profile URL
    :param profile_url: url to candidate profile
    :param campaign: retrieve campaign twitter if True, else retrieve official twitter
    :return: link to specified twitter
    '''

    profile_info = {}

    r = requests.get(profile_url)
    html = r.content
    soup = BeautifulSoup(html, 'lxml')

    target = soup.find('a', text='Campaign Twitter')
    profile_info['campaign_twitter'] = target['href'] if target is not None else None

    target = soup.find('a', text='Official Twitter')
    profile_info['official_twitter'] = target['href'] if target is not None else None

    target = soup.find('a', text='Personal Twitter')
    profile_info['personal_twitter'] = target['href'] if target is not None else None

    found_house = False
    target = soup.find('div', {"class": "infobox person"})
    if target is not None:
        children = target.find_all('p', recursive=True)
        for child in children:
            if 'U.S. House' in child.text:
                found_house = True
                break

    tenure = None
    if found_house:
        target = soup.find('div', {"class": "infobox person"})
        children = target.find_all('div', recursive=True)
        get_next = False
        for child in children:
            if get_next:
                tenure = child.text.strip()
                break
            elif 'Tenure' in child.text:
                get_next = True
    profile_info['tenure'] = tenure

    target = soup.find('div', {"class": "infobox person"})
    child = target.find('div', {"class": "widget-row value-only white"}, recursive=True)
    child = child.find('a', recursive=True)
    party = child.text
    profile_info['party'] = party

    gender = None
    cand_state = None
    target = soup.find('div', {"id": "mw-content-text"})
    children = target.find_all('p', recursive=False)
    for child in children:
        if child.text and '. She' in child.text:
            gender = 'Female'
        elif child.text and '. He' in child.text:
            gender = 'Male'

        if cand_state is None and child.text:
            for state in states:
                if state in child.text:
                    cand_state = state

    profile_info['gender'] = gender
    profile_info['state'] = cand_state
    profile_info['ballotpedia_url'] = profile_url

    return profile_info


def main():

    output_filename = 'Candidates2020_set_{0}.csv'.format(datetime.now().strftime("%H%M%S_%m%d%Y"))
    havent_written = True

    base_url = 'https://ballotpedia.org/List_of_congressional_candidates_in_the_2020_elections#'
    # base_url = 'https://ballotpedia.org/List_of_candidates_who_ran_in_U.S._Congress_elections,_2018#Candidates_by_state'

    names_and_profile_links = get_candidates_profiles(base_url)

    names = [i[0] for i in names_and_profile_links]
    profile_links = [i[1] for i in names_and_profile_links]

    df_list = []

    start_at = 0
    num_to_do = 1000000

    consec_exceptions_count = 0
    for i in range(start_at, start_at+num_to_do+1):
        print(i)
        if i >= len(names):
            break

        try:
            profile_info = get_profile_info(profile_links[i])
            if not names[i]:
                continue
            profile_info['name'] = names[i]
            df_list.append(profile_info)
            consec_exceptions_count = 0
        except Exception as e:
            consec_exceptions_count += 1
            print('exception', names[i], consec_exceptions_count)
            print(e)
            if consec_exceptions_count > 10:
                break

        if i % 20 == 0 or i == len(names) - 1 or i == start_at + num_to_do:
            df = pd.DataFrame(df_list)
            df.to_csv(output_filename, mode='a', sep=',', encoding='utf-8', index=False, header=havent_written)
            df_list = []
            havent_written = False
            print('wrote batch')

        time.sleep(0.2)


if __name__ == '__main__':
    main()
