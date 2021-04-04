

## <div align="center">Gendered Rhetoric: Femininity, Masculinity, and the Influence of Candidate Gender on Discussions of Gendered Topics on Twitter</div>
### <div align="center">Written by Eleanor Stalick, Advised by Dr. Dawn Teele</div>

### Abstract
Social and legal history in the U.S. have associated women with homemaking and men with breadwinning. Consequently, Americans equate femininity and masculinity with the competencies required of homemakers and breadwinners, respectively. Femininity implies competency on women’s rights, education, healthcare, and familycare, whereas masculinity implies competency on the military, economics, foreign policy, and policing. Americans further view politics, especially Republican politics, as masculine. These stereotypes imply differences in the rhetorical strategies of male and female political candidates. Using a novel dataset of 698,609 tweets posted across 2,092 major-party House congressional campaigns in the years prior to the 2018 and 2020 elections, I find that a candidate’s gender determines the gendered topics they discuss, a candidate’s gender does not determine the engagement they receive on tweets discussing gendered topics, and the COVID-19 pandemic and the 2020 Black Lives Matter protests changed the relationship between candidate party and gendered topic discussion.

### Python File Descriptions
* candidates_getter_2018/2020.py scrapes information on each US House candidate from Ballotpedia.
* plot_categories_stacked_bar.py plots a stacked bar graph of the frequency of twitter posts within each category.
* plot_engagements_bar.py plots a bar graph of the engagement scores for each category of tweet across candidate types.
* plot_over_time.py plots both tweet frequencies and engagement scores over time across candidate types.
* topics.py provides a dictionary of category terms.
* tweet_categorizer.py assigned a binar indicatory for each category to each tweet.
* tweet_grouper.py generates statistics for each candidate.
* twitter_api_wrapper.py collects tweet data from relevant candidates.

### R File Descriptions
* PennSeniorThesis2018/2020.RMD create regressions describing trends in tweet data.
