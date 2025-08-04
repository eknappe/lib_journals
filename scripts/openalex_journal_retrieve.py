# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 08:21:05 2025

@author: knappeel

Code to scrape open alex for the journal categories
OpenAlex has 200,000 journals -- We have approx 15,000 journals
 
Going to limit to only journals that have a certain number of articles published 
then see if that gets us majority of our journals

To find the correct api call, go onto open alex, create your search you want 
then in the upper right hand corner there is a setting wheel -- the drop down 
offers you the API call -- super handy

Will be using the "topic share" - since the domain, field, subfield seems to be a better rep
for the journals then the normal "topic". In this we will pull the first two entries, but there
can be up to 25

"""


## Import the necessary libraries 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy
import os
import requests
import csv
import json

##############################################################################
###################Inputs and variables needed###############################

### Set working diretory -- python scripts are hosted in within a folder in this directory
### Going to be two folders in horizontal -- data and python
working_directory = "\\Users\\knappeel\\Documents\\library\\coding\\journals"
os.chdir(working_directory)

## Where to save
save_directory=(working_directory+'\\data\\journal_categories\\')
# if save folder does not exist, create it
if not os.path.exists(save_directory):
    os.makedirs(save_directory)
 
## pull in the list of all our journals 
library_location ="\\Users\\knappeel\\Documents\\library\\coding\\journals\\data\\output\\all_our_journals_start.csv"
fields = {"Publisher" : "category",  "jtitle" : "category", 
           "ISSN": "str", "EISSN" : "str"}

library_journals = pd.read_csv(library_location, dtype = fields, usecols=list(fields))


##just pulling the DORA journals
## dora journals masterlist from Andre:
dora_journ_url= "http://lib-dora-prod1.emp-eaw.ch:8080/solr/collection1/select?q=PID%3Ajournals%5C%3A*&sort=PID+asc&rows=7000&fl=PID%2C+mods_titleInfo_title_ms%2C+mods_titleInfo_title_ms%2C+mods_identifier_issn_ms%2C+mods_identifier_e-issn_ms%2C+mods_originInfo_publisher_ms++&wt=csv&indent=true"

##import the journal list from the url 
dorajournal = pd.read_csv(dora_journ_url)
##the columns have strange names so lets change them
dorajournal = dorajournal.rename(columns={"mods_titleInfo_title_ms" : "jtitle",
                                              "mods_identifier_issn_ms" : "ISSN",
                                              "mods_identifier_e-issn_ms": "EISSN",
                                              "mods_originInfo_publisher_ms": "Publisher"})
    

## since a query can be time consuming -- dump the full export to a json for later tinkerin
save_the_imported_json=(save_directory+'export_of_openalex100-299.json')
other_json=(save_directory+'export_of_openalex300-.json')
combine_json=(save_directory+'export_of_openalex_combo.json')

#### set the openalex api parameters
mailto="ellen.knappe@lib4ri.ch" #email address to ensure 'polite'/faster queries

## url for the openalex journals
url="https://api.openalex.org/sources"

### set the parameters
### setting to journals that have 300+ articles in them -- based on a quick search
### of random journals this seems like an ok number to start
### this reduces the catalog from 200k to 70k

params = {
    "mailto":mailto,
    "filter":"works_count:100-299",
    "per-page":100,
    "select":"issn_l,issn,display_name,abbreviated_title,topics,topic_share",}

### testing to ensure params are correct and url is correct
# response = requests.get(url, params = params)

# ## testing to see if it worked 
# if response.status_code == 200:
#     print("Success!")

##############################################################################
#############################Code portion#####################################

""" Start the code -- first define the necessary functions """

# ################################################################
# ##### only need to run when you need a new api pull ##########
# ##### time consuming, only run when need, else import from comp ####

# ## function from the openalex workbook:https://github.com/ourresearch/openalex-api-tutorials/blob/main/notebooks/getting-started/api-webinar-apr2024/tutorial01.ipynb
# # This code just defines the function. We'll need to call the function later on to get it to actually get it to run.
# def api_query_page_results(url, params):
#     # Initialize cursor
#     cursor = "*"

#     # Loop through pages
#     all_results = []
#     while cursor:
#         params["cursor"] = cursor
#         response = requests.get(url, params=params)
#         if response.status_code != 200:
#             print("Oh no! Something went wrong!")
#             response.raise_for_status()
#         this_page_results = response.json()['results']
#         for result in this_page_results:
#             all_results.append(result)

#         # Update cursor
#         cursor = response.json()['meta']['next_cursor']
#     return all_results

# ##another function to flatten a json out from: https://towardsdatascience.com/flattening-json-objects-in-python-f5343c794b10
def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out

# """is this the most efficient way to do this, unlikely... but this is tricky because of how nested it is"""



# ## first make the api call using the above function
# journal_list = api_query_page_results(url,params)

# ## Save the full api pull so don't have to run it everytime ####
# ## save the whole batch for later tinkering, only need to do this once
# with open(save_the_imported_json, "w") as f:
#     json.dump(journal_list, f)

###### if already pulled from open alex -- import the jsons
with open(save_the_imported_json) as file:
    smalljson= json.load(file)


with open(other_json) as file:
    largejson= json.load(file)

## Which one to use first
# journal_list = largejson
journal_list = smalljson

## make a blank dictionary to fill
all_references = {}
notopics = {}

# ## how many journals
# ## can check this number against the openalex search to make sure you are getting the results you want
number_of_journal = len(journal_list) 
## this is a ton of journals -- so we will loop through the library journals

# ##### Using TOPICS-SHARE ###
# for ii in range(0,number_of_journal):
#     ## the api output is a list of dictionaries (with lists and dictionaries in them) - it is very nested
#     journal_json = journal_list[ii]
#     journal_data = flatten_json(journal_json)
#     key = journal_data['display_name']
#     issn_l = journal_data['issn_l']
    
#     ## see if the journal title is in there, then continue
#     if (library_journals['jtitle'].eq(key)).any() == True:
#         ## not all journals have topics, apparently, so we only want those
#         if len(journal_json['topic_share']) > 0:
            
#             ## assemble!, will use a dictionary to be computationally faster
#             entry = {'abbreviated_title':journal_data['abbreviated_title'],
#                       'ISSN':journal_data['issn_l'], 'other_ISSN':journal_json['issn'],'domain1':journal_data['topic_share_0_domain_display_name'],
#                       'field1':journal_data['topic_share_0_field_display_name'], 'subfield1':journal_data['topic_share_0_subfield_display_name'],
#                       'domain2':journal_data['topic_share_1_domain_display_name'], 'field2':journal_data['topic_share_1_field_display_name'],
#                       'subfield2':journal_data['topic_share_1_subfield_display_name'], 'domain3':journal_data['topic_share_2_domain_display_name'],
#                       'field3':journal_data['topic_share_2_field_display_name'], 'subfield3':journal_data['topic_share_2_subfield_display_name']}
            
#             key = journal_data['display_name'] #not all have issn, so using the title
#             all_references[key] = entry
#         else: #track when they don't have topics
#             notopics[key] = journal_data['issn_l']

#     ##journal titles do not match but the ISSN is somewhere
#     elif (library_journals['EISSN'].eq(issn_l)).any() == True:
#         ## not all journals have topics, apparently, so we only want those
#         if len(journal_json['topic_share']) > 0:
            
#             ## assemble!, will use a dictionary to be computationally faster
#             entry = {'abbreviated_title':journal_data['abbreviated_title'],
#                       'ISSN':journal_data['issn_l'], 'other_ISSN':journal_json['issn'],'domain1':journal_data['topic_share_0_domain_display_name'],
#                       'field1':journal_data['topic_share_0_field_display_name'], 'subfield1':journal_data['topic_share_0_subfield_display_name'],
#                       'domain2':journal_data['topic_share_1_domain_display_name'], 'field2':journal_data['topic_share_1_field_display_name'],
#                       'subfield2':journal_data['topic_share_1_subfield_display_name'], 'domain3':journal_data['topic_share_2_domain_display_name'],
#                       'field3':journal_data['topic_share_2_field_display_name'], 'subfield3':journal_data['topic_share_2_subfield_display_name']}
            
#             key = journal_data['display_name'] #not all have issn, so using the title
#             all_references[key] = entry        
#         else: #track when they don't have topics
#             notopics[key] = journal_data['issn_l']

#     elif (library_journals['ISSN'].eq(issn_l)).any() == True:
#         ## not all journals have topics, apparently, so we only want those
#         if len(journal_json['topic_share']) > 0:
#             ## assemble!, will use a dictionary to be computationally faster
#             entry = {'abbreviated_title':journal_data['abbreviated_title'],
#                       'ISSN':journal_data['issn_l'], 'other_ISSN':journal_json['issn'],'domain1':journal_data['topic_share_0_domain_display_name'],
#                       'field1':journal_data['topic_share_0_field_display_name'], 'subfield1':journal_data['topic_share_0_subfield_display_name'],
#                       'domain2':journal_data['topic_share_1_domain_display_name'], 'field2':journal_data['topic_share_1_field_display_name'],
#                       'subfield2':journal_data['topic_share_1_subfield_display_name'], 'domain3':journal_data['topic_share_2_domain_display_name'],
#                       'field3':journal_data['topic_share_2_field_display_name'], 'subfield3':journal_data['topic_share_2_subfield_display_name']}
            
#             key = journal_data['display_name'] #not all have issn, so using the title
#             all_references[key] = entry   
#         else: #track when they don't have topics
#             notopics[key] = journal_data['issn_l']


used_journals = pd.DataFrame() #keep track of the library journals which have topics 

##### Using TOPICS ###
for ii in range(0,number_of_journal):
    ## the api output is a list of dictionaries (with lists and dictionaries in them) - it is very nested
    journal_json = journal_list[ii]
    journal_data = flatten_json(journal_json)
    key = journal_data['display_name']
    issn_l = journal_data['issn_l']
    
    ## see if the journal title is in there, then continue
    if (library_journals['jtitle'].eq(key)).any() == True:
        ## not all journals have topics, apparently, so we only want those
        if len(journal_json['topic_share']) > 0:
            
            ## assemble!, will use a dictionary to be computationally faster
            entry = {'abbreviated_title':journal_data['abbreviated_title'],
                      'ISSN':journal_data['issn_l'], 'other_ISSN':journal_json['issn'],'domain1':journal_data['topics_0_domain_display_name'],
                      'field1':journal_data['topics_0_field_display_name'], 'subfield1':journal_data['topics_0_subfield_display_name'],
                      'domain2':journal_data['topics_1_domain_display_name'], 'field2':journal_data['topics_1_field_display_name'],
                      'subfield2':journal_data['topics_1_subfield_display_name'], 'domain3':journal_data['topics_2_domain_display_name'],
                      'field3':journal_data['topics_2_field_display_name'], 'subfield3':journal_data['topics_2_subfield_display_name']}
            
            key = journal_data['display_name'] #not all have issn, so using the title
            all_references[key] = entry
            #keep track of the journals found
            mask = library_journals['jtitle'].eq(key)
            libj = library_journals[mask]
            used_journals = pd.concat([used_journals, libj])
        else: #track when they don't have topics
            notopics[key] = journal_data['issn_l']

    ##journal titles do not match but the ISSN is somewhere
    elif (library_journals['EISSN'].eq(issn_l)).any() == True:
        ## not all journals have topics, apparently, so we only want those
        if len(journal_json['topic_share']) > 0:
            
            ## assemble!, will use a dictionary to be computationally faster
            entry = {'abbreviated_title':journal_data['abbreviated_title'],
                      'ISSN':journal_data['issn_l'], 'other_ISSN':journal_json['issn'],'domain1':journal_data['topics_0_domain_display_name'],
                      'field1':journal_data['topics_0_field_display_name'], 'subfield1':journal_data['topics_0_subfield_display_name'],
                      'domain2':journal_data['topics_1_domain_display_name'], 'field2':journal_data['topics_1_field_display_name'],
                      'subfield2':journal_data['topics_1_subfield_display_name'], 'domain3':journal_data['topics_2_domain_display_name'],
                      'field3':journal_data['topics_2_field_display_name'], 'subfield3':journal_data['topics_2_subfield_display_name']}
            
            key = journal_data['display_name'] #not all have issn, so using the title
            all_references[key] = entry   
            #keep track of the journals found
            mask = library_journals['EISSN'].eq(issn_l)
            libj = library_journals[mask]
            used_journals = pd.concat([used_journals, libj])
        else: #track when they don't have topics
            notopics[key] = journal_data['issn_l']

    elif (library_journals['ISSN'].eq(issn_l)).any() == True:
        ## not all journals have topics, apparently, so we only want those
        if len(journal_json['topic_share']) > 0:
            ## assemble!, will use a dictionary to be computationally faster
            entry = {'abbreviated_title':journal_data['abbreviated_title'],
                      'ISSN':journal_data['issn_l'], 'other_ISSN':journal_json['issn'],'domain1':journal_data['topics_0_domain_display_name'],
                      'field1':journal_data['topics_0_field_display_name'], 'subfield1':journal_data['topics_0_subfield_display_name'],
                      'domain2':journal_data['topics_1_domain_display_name'], 'field2':journal_data['topics_1_field_display_name'],
                      'subfield2':journal_data['topics_1_subfield_display_name'], 'domain3':journal_data['topics_2_domain_display_name'],
                      'field3':journal_data['topics_2_field_display_name'], 'subfield3':journal_data['topics_2_subfield_display_name']}
            
            key = journal_data['display_name'] #not all have issn, so using the title
            all_references[key] = entry   
            #keep track of the journals found
            mask = library_journals['ISSN'].eq(issn_l)
            libj = library_journals[mask]
            used_journals = pd.concat([used_journals, libj])
        else: #track when they don't have topics
            notopics[key] = journal_data['issn_l']






# no_topic_small = pd.DataFrame.from_dict(notopics, orient='index')



### Which library journals do we not have topics for:
library_no_topic = pd.concat([library_journals,used_journals], sort = False)
library_no_topic = library_no_topic.drop_duplicates(subset = ['jtitle'], keep =False)
library_no_topic.to_csv(save_directory+'library_without_topics_assigned.csv')


# ab = pd.merge(library_no_topic,journals, on ='jtitle', how='inner')


### save as json just in case
filelocation = (save_directory+"library_alex_topics300under.json")
with open(filelocation, "w") as outfile:
    json.dump(all_references,outfile)

## convert to a dataframe, because its my prefered format
test_dataframe = pd.DataFrame.from_dict(all_references, orient='index')

test_dataframe['jtitle'] = test_dataframe.index
test_dataframe.to_csv(save_directory+'open_alextopics300under.csv')
#############################################################
#############################################################


#############################################################
#####################DORA ONLY##############################

used_journals = pd.DataFrame() #keep track of the library journals which have topics 

##### Using TOPICS ###
for ii in range(0,number_of_journal):
    ## the api output is a list of dictionaries (with lists and dictionaries in them) - it is very nested
    journal_json = journal_list[ii]
    journal_data = flatten_json(journal_json)
    key = journal_data['display_name']
    issn_l = journal_data['issn_l']
    
    ## see if the journal title is in there, then continue
    if (dorajournal['jtitle'].eq(key)).any() == True:
        ## not all journals have topics, apparently, so we only want those
        if len(journal_json['topic_share']) > 0:
            
            ## assemble!, will use a dictionary to be computationally faster
            entry = {'abbreviated_title':journal_data['abbreviated_title'],
                      'ISSN':journal_data['issn_l'], 'other_ISSN':journal_json['issn'],'domain1':journal_data['topics_0_domain_display_name'],
                      'field1':journal_data['topics_0_field_display_name'], 'subfield1':journal_data['topics_0_subfield_display_name'],
                      'domain2':journal_data['topics_1_domain_display_name'], 'field2':journal_data['topics_1_field_display_name'],
                      'subfield2':journal_data['topics_1_subfield_display_name'], 'domain3':journal_data['topics_2_domain_display_name'],
                      'field3':journal_data['topics_2_field_display_name'], 'subfield3':journal_data['topics_2_subfield_display_name']}
            
            key = journal_data['display_name'] #not all have issn, so using the title
            all_references[key] = entry
            #keep track of the journals found
            mask = dorajournal['jtitle'].eq(key)
            libj = dorajournal[mask]
            used_journals = pd.concat([used_journals, libj])
        else: #track when they don't have topics
            notopics[key] = journal_data['issn_l']

    ##journal titles do not match but the ISSN is somewhere
    elif (dorajournal['EISSN'].eq(issn_l)).any() == True:
        ## not all journals have topics, apparently, so we only want those
        if len(journal_json['topic_share']) > 0:
            
            ## assemble!, will use a dictionary to be computationally faster
            entry = {'abbreviated_title':journal_data['abbreviated_title'],
                      'ISSN':journal_data['issn_l'], 'other_ISSN':journal_json['issn'],'domain1':journal_data['topics_0_domain_display_name'],
                      'field1':journal_data['topics_0_field_display_name'], 'subfield1':journal_data['topics_0_subfield_display_name'],
                      'domain2':journal_data['topics_1_domain_display_name'], 'field2':journal_data['topics_1_field_display_name'],
                      'subfield2':journal_data['topics_1_subfield_display_name'], 'domain3':journal_data['topics_2_domain_display_name'],
                      'field3':journal_data['topics_2_field_display_name'], 'subfield3':journal_data['topics_2_subfield_display_name']}
            
            key = journal_data['display_name'] #not all have issn, so using the title
            all_references[key] = entry   
            #keep track of the journals found
            mask = dorajournal['EISSN'].eq(issn_l)
            libj = dorajournal[mask]
            used_journals = pd.concat([used_journals, libj])
        else: #track when they don't have topics
            notopics[key] = journal_data['issn_l']

    elif (dorajournal['ISSN'].eq(issn_l)).any() == True:
        ## not all journals have topics, apparently, so we only want those
        if len(journal_json['topic_share']) > 0:
            ## assemble!, will use a dictionary to be computationally faster
            entry = {'abbreviated_title':journal_data['abbreviated_title'],
                      'ISSN':journal_data['issn_l'], 'other_ISSN':journal_json['issn'],'domain1':journal_data['topics_0_domain_display_name'],
                      'field1':journal_data['topics_0_field_display_name'], 'subfield1':journal_data['topics_0_subfield_display_name'],
                      'domain2':journal_data['topics_1_domain_display_name'], 'field2':journal_data['topics_1_field_display_name'],
                      'subfield2':journal_data['topics_1_subfield_display_name'], 'domain3':journal_data['topics_2_domain_display_name'],
                      'field3':journal_data['topics_2_field_display_name'], 'subfield3':journal_data['topics_2_subfield_display_name']}
            
            key = journal_data['display_name'] #not all have issn, so using the title
            all_references[key] = entry   
            #keep track of the journals found
            mask = dorajournal['ISSN'].eq(issn_l)
            libj = dorajournal[mask]
            used_journals = pd.concat([used_journals, libj])
        else: #track when they don't have topics
            notopics[key] = journal_data['issn_l']



test_dataframe = pd.DataFrame.from_dict(all_references, orient='index')

test_dataframe['jtitle'] = test_dataframe.index
test_dataframe.to_csv(save_directory+'DORA_open_alextopics300under.csv')














