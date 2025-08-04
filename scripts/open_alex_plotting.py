# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 15:35:38 2025

@author: knappeel

Plotting the different categories of subjects for our journals 
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
import seaborn as sns

##############################################################################
###################Inputs and variables needed###############################

### Set working diretory -- python scripts are hosted in within a folder in this directory
### Going to be two folders in horizontal -- data and python
working_directory = "\\Users\\knappeel\\Documents\\library\\coding\\journals"
os.chdir(working_directory)

## Where to save
save_directory=(working_directory+'\\data\\journal_categories\\')
figsave_directory=(working_directory+'\\data\\journal_categories\\figures\\')
# if save folder does not exist, create it
if not os.path.exists(save_directory):
    os.makedirs(save_directory)
 
## pull in the list of all our journals 
library_location ="\\Users\\knappeel\\Documents\\library\\coding\\journals\\data\\output\\all_our_journals_start.csv"
fields = {"Publisher" : "category",  "jtitle" : "category", 
           "ISSN": "str", "EISSN" : "str"}

library_journals = pd.read_csv(library_location, dtype = fields, usecols=list(fields))
 
### Import the two openalex dataframes 
oalexloc1 = "\\Users\\knappeel\\Documents\\library\\coding\\journals\\data\\journal_categories\\DORA_open_alextopics300.csv"
oalexloc2 = "\\Users\\knappeel\\Documents\\library\\coding\\journals\\data\\journal_categories\\DORA_open_alextopics300under.csv"

fields = {"jtitle" : "category",  "abbreviated_title" : "str", 
           "ISSN": "str", "other_ISSN" : "str", "domain1": "category",
           "field1": "category","subfield1": "category","domain2": "category",
           "field2": "category","subfield2": "category","domain3": "category",
           "field3": "category","subfield3": "category"}

oa1 = pd.read_csv(oalexloc1, dtype = fields, usecols=list(fields))
oa2 = pd.read_csv(oalexloc2, dtype = fields, usecols=list(fields))

##combine into one openalex dataframe
open_alex = pd.concat([oa1,oa2], ignore_index = True)

# ## exporting the open_alex dataframe, so don't need to run retrieve again### 
# open_alex.to_csv(save_directory+'open_alex_topic_ALL.csv')
##############################################################################
#############################Code portion#####################################

### for all three different domain/field will change this below accordingly, 
### everything else will run properly from there
open_alex.index=pd.MultiIndex.from_arrays(open_alex[['domain1','field1']].values.T, names=['d1','f1'])


##### This has the total above the graphs #### 
##########################################################

# Group by domain and field, then count the number of journals in each field
grouped_data = open_alex.groupby(['d1', 'f1']).size().reset_index(name='count')

# Extract unique domains and their fields for plotting
domains = grouped_data['d1'].unique()
fields_per_domain = {domain: grouped_data[grouped_data['d1'] == domain] for domain in domains}

# Calculate the total number of journals and the percentage for each domain
domain_totals = grouped_data.groupby('d1')['count'].sum()
total_journals = domain_totals.sum()
domain_percentages = (domain_totals / total_journals * 100).round(1)

# Create the bar plot and include total counts and percentages
fig, ax = plt.subplots(figsize=(14, 7))
bar_width = 0.4
domain_offsets = []
current_offset = 0

for domain, fields in fields_per_domain.items():
    positions = np.arange(len(fields)) + current_offset
    domain_offsets.append((domain, positions))
    ax.bar(positions, fields['count'], bar_width, label=domain)
    
    # Add the total number and percentage for each domain above the grouped bars
    total_pos = (positions[0] + positions[-1]) / 2  # Center position for the total label
    ax.text(total_pos, fields['count'].max() + 5,  # Position above the tallest bar
            f"{domain} = {domain_totals[domain]}, {domain_percentages[domain]}%",
            ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    current_offset += len(fields) + 1  # Add spacing between domains

# Set x-ticks and labels
x_ticks = [pos for _, positions in domain_offsets for pos in positions]
x_labels = [field for _, fields in fields_per_domain.items() for field in fields['f1']]
ax.set_xticks(x_ticks)
ax.set_xticklabels(x_labels, rotation=90)

# Add labels, legend, and title
ax.set_ylabel('Number of Journals')
ax.set_title('Hierarchical Bar Plot: Journals by Domain and Field\n(with Totals and Percentages)')
ax.legend(title='Domain', bbox_to_anchor=(1.05, 1), loc='upper left')

# Display the plot
plt.tight_layout()

## save figure
plt.savefig(figsave_directory+'DORAjournal_subject_1.pdf')
plt.show()
s

#### to plot the subfields #### 

open_alex.index=pd.MultiIndex.from_arrays(open_alex[['domain1','field1']].values.T, names=['d1','f1'])


# Filter the data for the "Physical Sciences" domain
physical_sciences_data = open_alex[open_alex['domain1'] == 'Social Sciences']

# Group by subfields within Physical Sciences and count the number of journals
subfield_counts = physical_sciences_data.groupby('subfield1').size().sort_values(ascending=False)

# Create a horizontal bar plot for better readability of long subfield names
plt.figure(figsize=(10, 12))
plt.barh(subfield_counts.index, subfield_counts.values, color='red')

# Add labels and title
plt.xlabel('Number of Journals')
plt.title('Bar Plot: Journals in Social Sciences Subfields')

# Display the plot
plt.tight_layout()

plt.savefig(figsave_directory+'DORAjournal_subfield_socialsciences1.pdf')
plt.show()



# all_journals = pd.concat([library_journals,open_alex], sort = False)

# all_journals = all_journals.drop_duplicates(subset = ['jtitle'], keep = False)
# all_journals = all_journals[~all_journals['ISSN'].duplicated(keep=False) | all_journals['ISSN'].isna()]
# all_journals = all_journals[~all_journals['EISSN'].duplicated(keep=False) | all_journals['EISSN'].isna()]















##########################################################
############### CODE GRAVEYARD #######################
##########################################################





##### This does not have the total above the graphs #### 
##########################################################
# # Group by domain and field, then count the number of journals in each field
# grouped_data = open_alex.groupby(['d1', 'f1']).size().reset_index(name='count')

# # Extract unique domains and their fields for plotting
# domains = grouped_data['d1'].unique()
# fields_per_domain = {domain: grouped_data[grouped_data['d1'] == domain] for domain in domains}

# # Initialize the plot
# fig, ax = plt.subplots(figsize=(14, 7))
# bar_width = 0.4  # Width of each bar
# domain_offsets = []
# current_offset = 0

# # Create bars for each domain and its fields
# for domain, fields in fields_per_domain.items():
#     positions = np.arange(len(fields)) + current_offset
#     domain_offsets.append((domain, positions))
#     ax.bar(positions, fields['count'], bar_width, label=domain)
#     current_offset += len(fields) + 1  # Add spacing between domains

# # Set x-ticks and labels
# x_ticks = [pos for _, positions in domain_offsets for pos in positions]
# x_labels = [field for _, fields in fields_per_domain.items() for field in fields['f1']]
# ax.set_xticks(x_ticks)
# ax.set_xticklabels(x_labels, rotation=90)

# # Add labels, legend, and title
# ax.set_ylabel('Number of Journals')
# ax.set_title('Hierarchical Bar Plot: Journals by Domain and Field')
# ax.legend(title='Domain', bbox_to_anchor=(1.05, 1), loc='upper left')

# # Display the plot
# plt.tight_layout()
# plt.show()

# plt.savefig(save_directory+'journal_subject_3.pdf')




























