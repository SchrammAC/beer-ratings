# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 17:30:11 2019

@author: night
"""

import requests
import dill
from bs4 import BeautifulSoup
from datetime import datetime
import re
import pandas as pd
import string


def load_pkl(filename):
    with open(filename,'rb') as fobj:
        df = dill.load(fobj)
    return df


beer_links = load_pkl('data/NEIPA_beer_links.pkl')
beer_links = beer_links[64:]

user_reviews_list = []
user_ratings_list = []
brewery_list = []
location_list = []
availability_list = []
user_id_list = []
score_list = []
look_score_list = []
smell_score_list = []
taste_score_list = []
feel_score_list = []
overall_score_list = []
comment_time_list = []
comment_body_list = []

for partial_link in beer_links:
    base_link = 'https://www.beeradvocate.com' + partial_link + '?view=beer&sort=&start='

    page = requests.get(base_link+'0')
    soup = BeautifulSoup(page.text, 'html.parser')
    
    #Get name
    headings = [st for st in soup.find('div', class_='titleBar').strings]
    name = str(headings[1])
    brewery = str(headings[2])
    
    #Get score
    beerscore = soup.find_all('span', class_='ba-score Tooltip')
    ba_score = int(beerscore[0].select('b')[0].text)
    
    #user score
    beerscore = soup.find_all('span', class_='ba-ravg Tooltip')
    user_score = float(beerscore[0].text)
    
    #user score deviation
    beerscore = soup.find_all('span', class_='ba-pdev muted Tooltip')
    user_deviation = beerscore[0].text
    
    #Other beer stats and info
    pagetext = soup.find_all('dd', class_='beerstats')
    user_reviews = int(pagetext[4].text.replace(',',''))
    user_ratings = int(pagetext[5].text.replace(',',''))
    location = pagetext[7].text
    availability = pagetext[8].text
    
    pg = 0
    print(name)
    while pg*25 < int(user_reviews):
        print('Page: '+str(pg))
        page = requests.get(base_link+str(pg*25))
        soup = BeautifulSoup(page.text, 'html.parser')
        comments = soup.find_all('div', class_='user-comment')
        
        for comment in comments:
            user_regex = re.compile(r'div ba-user=\"(\d+)\"')
            user_id = re.findall(user_regex, str(comment))[0]
            score = comment.find_all('span', class_='BAscore_norm')[0].text
            
            try:
                look_score = re.findall(re.compile(r"look: ([\d\.]+)"), comment.text)[0]
                smell_score = re.findall(re.compile(r"smell: ([\d\.]+)"), comment.text)[0]
                taste_score = re.findall(re.compile(r"taste: ([\d\.]+)"), comment.text)[0]
                feel_score = re.findall(re.compile(r"feel: ([\d\.]+)"), comment.text)[0]
                overall_score = re.findall(re.compile(r"overall: ([\d\.]+)"), comment.text)[0]
                comment_body = re.findall(re.compile(r"overall: [\d\.]+(.+?)\d+ characters"), comment.text.replace('\n',' '))[0]

            except IndexError:
                look_score = 'NaN'
                smell_score = 'NaN'
                taste_score = 'NaN'
                feel_score = 'NaN'
                overall_score = 'NaN'
                comment_body = re.findall(re.compile(r"%(.+?)\d+ characters"), comment.text.replace('\n',' '))[0]                
             
            comment_time = comment.find_all('a')[2].text
            
            user_reviews_list.append(user_reviews)
            user_ratings_list.append(user_ratings)
            brewery_list.append(brewery)
            location_list.append(location)
            availability_list.append(availability)
            user_id_list.append(user_id)
            score_list.append(score)
            look_score_list.append(look_score)
            smell_score_list.append(smell_score)
            taste_score_list.append(taste_score)
            feel_score_list.append(feel_score)
            overall_score_list.append(overall_score)
            comment_time_list.append(comment_time)
            comment_body_list.append(comment_body)
        
        
        pg += 1
    
    exclude = set(string.punctuation)
    filename = ''.join(ch for ch in name if ch not in exclude)
    
    beer_dict = {}
    beer_dict['user_reviews'] = user_reviews_list
    beer_dict['user_ratings'] = user_ratings_list
    beer_dict['brewery'] = brewery_list
    beer_dict['location'] = location_list
    beer_dict['availability'] = availability_list
    beer_dict['user_id'] = user_id_list
    beer_dict['score'] = score_list
    beer_dict['look_score'] = look_score_list
    beer_dict['smell_score'] = smell_score_list
    beer_dict['taste_score'] = taste_score_list
    beer_dict['feel_score'] = feel_score_list
    beer_dict['overall_score'] = overall_score_list
    beer_dict['comment_time'] = comment_time_list
    beer_dict['comment_body'] = comment_body_list
    beer_dict['name'] = [name for i in range(len(comment_body_list))]
    beer_df = pd.DataFrame(beer_dict)
    with open('data/'+filename+'.pkl','wb') as fobj:
        dill.dump(beer_df,fobj)
    
    
def get_page_tags(links):
    link_list = []
    for i in range(len(links)):
        link_list.extend(get_link(links[i]))
    return link_list

def get_link(el):
    atag = el.select('a')
    if len(atag):
        url = atag[0]['href']
    else:
        url = ''
    return(re.findall(r'/beer/profile/\d*/\d*/',url))

pagelink_prefix = 'https://www.beeradvocate.com/beer/styles/189/?sort=revsD&start='

beer_link_list = []
num = 0

for i in range(0,179):
    page_link = pagelink_prefix + str(i*50)

    page = requests.get(page_link)
    
    soup = BeautifulSoup(page.text, 'html.parser')
    
    links = soup.find_all('td', class_='hr_bottom_light')
    
    beer_link_list.extend(get_page_tags(links))