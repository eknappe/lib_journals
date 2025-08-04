# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 15:49:11 2025

@author: knappeel
Code to look at the 2024 collaborations across WSL and inter RI 
"""

##### Collaborations from WSL #####
## Import the necessary libraries 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy
import os
from ast import literal_eval

### Set working diretory -- python scripts are hosted in within a folder in this directory
### Going to be two folders in horizontal -- data and python
working_directory = "\\Users\\knappeel\\Documents\\library\\coding\\journals"
os.chdir(working_directory)

## where to save figures
save_directory=(working_directory+'\\data\\output\\')

## import the csv that contain all the publications
collab_loc=(working_directory+'\\data\\pub_lists\\wsl_collab_2024.csv')
wsl_loc=(working_directory+'\\data\\pub_lists\\wsl_2024.csv')
no_wsl_loc=(working_directory+'\\data\\pub_lists\\2024_no_wsl.csv')

## import as dataframes
fields = {"PID" : "object", "Publication Type": "category",
          "Full Text": "category", "Title": "category",
          "Journal Impact Factor": "str", "Publisher DOI" : "category",
          "Affiliation (authors)" : "object"}

## using the converters to upload the author affiliations from the same insitute
wsl_collab = pd.read_csv(collab_loc, dtype = fields, usecols=list(fields),
                         converters={"Affiliation (authors)": lambda x: x.split(";")},  encoding='latin1')
wsl = pd.read_csv(wsl_loc, dtype = fields, usecols=list(fields),
                         converters={"Affiliation (authors)": lambda x: x.split(";")},  encoding='latin1')
nowsl = pd.read_csv(no_wsl_loc, dtype = fields, usecols=list(fields),
                         converters={"Affiliation (authors)": lambda x: x.split(";")},  encoding='latin1')


### THIS SEGMENT of code (with the last bit) will provide a list with inter WSL collabs included ####
# ###Find the WSL collaborations-- eg the title is in the collab list
# ###This will also find all the WSL collaborations - we will remove the duplicates after
# ## this will also keep the non-wsl collaborations though
# wsl_pubs = pd.concat([wsl, wsl_collab], ignore_index = True)

# ### find where the title is the same and only keep those (should keep same pub, different RI)
# dup_titles = wsl_pubs[wsl_pubs.duplicated(subset=['Title'],keep = False)]

# ### drop the WSL repeats (using the PID)
# duplicated_titles = dup_titles.drop_duplicates(subset = ['PID'])

# ## expand out the author affiliations
# dt_explode = duplicated_titles.explode('Affiliation (authors)')

# ### remove the titles from expand that only appear once (eg no other affiliations)
# collaborations = dt_explode[dt_explode.duplicated(subset=['Title'],keep = False)]

# ## condense into only 1 entry per article
# collab_articles = collaborations.groupby(['Title'], as_index = False).agg({'PID':'first'})

################################################

## remove the collaborations that do not include WSL
wsl_dois = wsl['Publisher DOI']
wsl_dois = wsl_dois.dropna()
wsl_dois = wsl_dois.to_list()

## the dois in wsl that are also in the master list
wsl_collaborations = nowsl[nowsl['Publisher DOI'].isin(wsl_dois)]

## now add in the WSL collabs (do not include if running above segment)
collab_dois = wsl_collaborations['Publisher DOI']
collab_dois = collab_dois.to_list()

wsl_aff = wsl[wsl['Publisher DOI'].isin(collab_dois)]

### combine the wsl affil with the outside collab list
wsl_collab_external = pd.merge(wsl_aff, wsl_collaborations, on ='Publisher DOI')

## save the dataframe to a csv file 
# wsl_collaborations.to_csv(save_directory+'list_of_wsl_collab_2024.csv')
wsl_collab_external.to_csv(save_directory+'wls_external_collab_2024.csv')

#### WSL internal collaboration list #### 
### this is just the inter-wsl collaboration list 
wsl_explode = wsl.explode('Affiliation (authors)')
internal_collab = wsl_explode[wsl_explode.duplicated(subset=['Title'],keep = False)]
remove_inter_department = internal_collab.groupby('Title')['Affiliation (authors)'].apply(lambda x: list(np.unique(x)))

wtitles = internal_collab['Title']
wtitle = wtitles.drop_duplicates(keep = 'first')

internal_collab_articles = wsl[wsl['Title'].isin(wtitle)]

ib = internal_collab['Affiliation (authors)'].unique()

internal_collab.to_csv(save_directory+'wls_internal_collab_exploded2024.csv')

internal_collab_articles.to_csv(save_directory+'wls_internal_collab_2024.csv')


for ii in range(0,len(internal_collab_articles)):
    aa = internal_collab_articles['Affiliation (authors)']
    lina = aa.iloc[ii]
    uni = np.unique(lina)  
    

