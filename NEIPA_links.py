# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 12:49:25 2019

@author: night
"""

import requests
import dill
from bs4 import BeautifulSoup
from datetime import datetime
import re

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