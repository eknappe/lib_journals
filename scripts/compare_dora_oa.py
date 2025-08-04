# -*- coding: utf-8 -*-
"""
Spyder Editor

E.K. 14 Jan 2025
Script to compare dora journals to the library contracts
"""

## Import the necessary libraries 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy
import os
import math

### Set working diretory -- python scripts are hosted in within a folder in this directory
### Going to be two folders in horizontal -- data and python
working_directory = "\\Users\\knappeel\\Documents\\library\\coding\\journals"
os.chdir(working_directory)

### under data I have a seperate folder for the publication lists that contains the necessary cssv
publist_dir = (working_directory+'\\data\\pub_lists\\')


## Where to save figures
save_directory=(working_directory+'\\data\\output\\')
# if save folder does not exist, create it
if not os.path.exists(save_directory):
    os.makedirs(save_directory)

##Import the csv that contain all the publications
eawag_loc=(publist_dir+'eawag_pub_jan2025.csv')
empa_loc=(publist_dir+'empa_pub_jan2025.csv')
wsl_loc=(publist_dir+'wsl_pub_jan2025.csv')
psi_loc=(publist_dir+'psi_pub_jan2025.csv')
## dora journals masterlist from Andre:
dora_journ_url= "http://lib-dora-prod1.emp-eaw.ch:8080/solr/collection1/select?q=PID%3Ajournals%5C%3A*&sort=PID+asc&rows=7000&fl=PID%2C+mods_titleInfo_title_ms%2C+mods_titleInfo_title_ms%2C+mods_identifier_issn_ms%2C+mods_identifier_e-issn_ms%2C+mods_originInfo_publisher_ms++&wt=csv&indent=true"

#import the lib4ri oa list from dimitiris
lib_loc=(working_directory+'\\data\\pub_lists\\library_oa_jan2025.csv')

#import lothars list of journals
lothar_loc= (working_directory+'\\data\\pub_lists\\lothar_journal_compare.csv')

#import as dataframes -- tell the import what datatypes of each column should be
fields = {"PID" : "object", "Publication Type": "category",
          "Full Text": "category", "Title": "object",
          "Journal Title (Book Title)": "category", 
         "ISSN": "object","ISBN": "str"}

lotharfield = {"ISSN": "object","EISSN": "str", "jtitle": "category",
               "Publisher": "category"}

dorafield = {"PID" : "object", "mods_titleInfo_title_ms": "category",
          "mods_identifier_issn_ms": "object", "mods_identifier_e-issn_ms": "object",
          "mods_originInfo_publisher_ms": "category"}

##import the dataframes
dora_eawag = pd.read_csv(eawag_loc, dtype = fields, usecols=list(fields) + ["Publication Year"], parse_dates = ["Publication Year"])
dora_empa = pd.read_csv(empa_loc, dtype = fields, usecols=list(fields) + ["Publication Year"], parse_dates = ["Publication Year"])
dora_wsl = pd.read_csv(wsl_loc, dtype = fields, usecols=list(fields) + ["Publication Year"], parse_dates = ["Publication Year"])
dora_psi = pd.read_csv(psi_loc, dtype = fields, usecols=list(fields) + ["Publication Year"], parse_dates = ["Publication Year"])
lothar = pd.read_csv(lothar_loc, dtype = lotharfield, usecols=list(lotharfield),  encoding='latin1')


##import the journal list from the url 
masterjournal = pd.read_csv(dora_journ_url)
##the columns have strange names so lets change them
masterjournal = masterjournal.rename(columns={"mods_titleInfo_title_ms" : "jtitle",
                                              "mods_identifier_issn_ms" : "ISSN",
                                              "mods_identifier_e-issn_ms": "EISSN",
                                              "mods_originInfo_publisher_ms": "Publisher"})

#library import (OA agreements)
lfields = {"Publisher" : "category",  "Title" : "category", 
           "ISSN": "str", "EISSN" : "str", "Link" :"category", 
           "License": "category", "Agreement type": "category"}
library = pd.read_csv(lib_loc, encoding='utf-8', dtype = lfields, usecols=list(lfields))


#combine into one dora dataframe
dora_all = pd.concat([dora_eawag,dora_empa,dora_wsl,dora_psi])

#Drop the entries that do not have a Journal/BookTitle
dfil = dora_all.dropna(subset = ['Journal Title (Book Title)'])

#Approx 12% of entries do not have a journal title
#Drop other types of non-journal enteries that we are un interested in
books='Book Chapter'
dfil = dfil.loc[dfil['Publication Type'] != books]
magis='Magazine Issue'
dfil = dfil.loc[dfil['Publication Type'] != magis]
#lothar wants newspapers and magazines
## news='Newspaper or Magazine Article'
## dfil = dfil.loc[dfil['Publication Type'] != news]
ppapers='Proceedings Paper'
dfil = dfil.loc[dfil['Publication Type'] != ppapers]
conf='Conference Item'
doraj = dfil.loc[dfil['Publication Type'] != conf]

#To check that all the other pub types have been removed
# doraj['Publication Type'].value_counts()
doraj['Journal Title (Book Title)'].value_counts().count()

#What journals exist in DORA
journ_types = doraj.groupby('Journal Title (Book Title)').count()

#How many articles are published in each journal? 
journals = pd.DataFrame({"title":journ_types.index, "num": journ_types.PID})
journals = journals.sort_values("num")

#How many journals only have a few articles published in them?
#Num = number of articles, count is how many journals only have that number of pub articles
jj = journals["num"].value_counts()
jj = jj.to_frame()
jj = jj.reset_index()
jj = jj.sort_values("num")
jj = jj.rename(columns = {'count':'jcount'}) #count is a function, changing name
#just the low level titles
j20 = jj.head(20)

# #Plot quickly the low level journals - less then 20 article published per journal
# plt.plot(j20.num, j20.jcount, '-o')
# plt.xlabel('Number of articles published in a journal')
# plt.ylabel('Number of journals')
# plt.title('DORA journals with low number of articles published')
# plt.savefig(save_directory+"dora_journ_vs_art.pdf", format='pdf',orientation='landscape')
# plt.show()

### Comparision of DORA and library contracts ####
#Rename the journal title in each dataframe to be consistent
journals = journals.rename(columns = {"title" : "jtitle"})
library = library.rename(columns = {"Title" : "jtitle"})

#what journals are ris publishing in that we also have agreements with (based on title only)
libraryjournals = pd.merge(journals,library, on ='jtitle', how='inner')

## how about only multiple published journals
journalmore = journals.loc[journals['num'] > 1]
j3 = journals.loc[journals['num'] > 2] #more then 2
j4 = journals.loc[journals['num'] > 3] #more then 2
j5 = journals.loc[journals['num'] > 4] #more then 2
jmorelib = pd.merge(journalmore,library, on ='jtitle', how='inner')
lib3 = pd.merge(j3,library, on ='jtitle', how='inner')
lib4 = pd.merge(j4,library, on ='jtitle', how='inner')
lib5 = pd.merge(j5,library, on ='jtitle', how='inner')

#Which journals are researchers publishing in that we don't have OA agreements with 
dora_no_agreements = journalmore[~journalmore.jtitle.isin(library.jtitle)]
dora_no_agreements_high_pub = dora_no_agreements.loc[dora_no_agreements['num'] > 50]

#which journals do we have that we are not publishing in 
agreements_no_dora = library[~library.jtitle.isin(journalmore.jtitle)]

# #######################################################
######### ISSN comparision #####################
#sort dora by the issn numbers
doraj = doraj.rename(columns={"Journal Title (Book Title)" : "jtitle"})
isdora = doraj.groupby(['ISSN'], as_index = False).agg({'PID':'first', 'Publication Type': 'first', 
                                                        'Full Text': 'first', 'jtitle': 'first'})
##compare dora and the library issns
issncompare = pd.merge(isdora,library, on='ISSN', how = 'inner')

##Getting a better picture of the dora journals 
journdora = doraj.groupby(['jtitle'], as_index = False).agg({'PID':'first', 'Publication Type': 'first', 
                                                        'Full Text': 'first', 'ISSN': 'first'})
titlesame_issndiff = journdora[journdora.duplicated(subset = ['ISSN'], keep =False)]
titlesame_issndiff = titlesame_issndiff.dropna(subset = ['ISSN'])

##which journals is dora do not have an issn associated
doraissnmask = pd.isna(journdora['ISSN'])
journdora['issnmask'] = doraissnmask
doranoissn = journdora[journdora['issnmask'] == True]

##how many of these journals w/o issn have more then 2 publications
noissndora_moreone = pd.merge(doranoissn,journalmore, on ='jtitle', how='inner')

## which journals do we have the issn but it is not in DORA?
addissntodora = pd.merge(doranoissn,library, on ='jtitle', how='inner')

## which journals have the same issn but different journal titles? 
jtitle_not_match = issncompare.query('jtitle_x != jtitle_y')

#### Save the dataframes we want
# jtitle_not_match.to_csv(save_directory+'journal_titles_not_matching.csv')
# addissntodora.to_csv(save_directory+'issn_not_in_DORA.csv')
# dora_no_agreements_high_pub.to_csv(save_directory+'high_pubrate_no_OA_agreement.csv')


##are there duplicated titles? eg duplicated entries
# duplicated_titles = dora_all[dora_all.duplicated(subset=['Title'],keep = False)]
#yes, but because majority of them are cross listed. eg on psi and empa
## approx 5,000 of these 

# #######################################################
# #######################################################


######### ISSN comparision #####################
###### do this comparision with lothar's list###
##First need to get rid of the nans in the issn column -- otherwise I think it behaves poorly


##compare dora and the library titles
title_combine= pd.merge(masterjournal,library, on='jtitle', how='inner')

## where do the titles match but the ISSNs do not match
title_match_issn_not = title_combine.query('ISSN_x != ISSN_y')
##where do the title match but the EISSN do not match
title_match_eissn_not = title_combine.query('EISSN_x != EISSN_y')
##where do the publishers not match
title_match_publisher_not = title_combine.query('Publisher_x != Publisher_y')




## remove the nan in issn so the combining doesn't go wacky
## those journals still matter so making a new dataframe
moi = masterjournal.dropna(subset = ['ISSN'])
lli = library.dropna(subset = ['ISSN'])

## where do issn match but titles/eissn/publisher do not match
issn_combine = pd.merge(moi,lli, on ='ISSN', how='inner')

issn_match_title_not = issn_combine.query('jtitle_x != jtitle_y')
issn_match_eissn_not = issn_combine.query('EISSN_x != EISSN_y')
issn_match_publisher_not = issn_combine.query('Publisher_x != Publisher_y')

### when doing this, we don't want duplicates of journals, in the sense, the publisher
### has already been found in a previous iteration
issn_match_publisher_not = issn_match_publisher_not[~issn_match_publisher_not.PID.isin(title_match_publisher_not.PID)]
issn_match_eissn_not = issn_match_eissn_not[~issn_match_eissn_not.PID.isin(title_match_eissn_not.PID)]
##since I already edited ISSN match title not, will update the previous for ease of my life



## remove nan eissn so the combining doesnt go wacky
moe = masterjournal.dropna(subset = ['EISSN'])
lle = library.dropna(subset = ['EISSN'])

## where do the eissn match but titles/issn/publisher do not match
eissn_combine = pd.merge(moe,lle, on ='EISSN', how='inner')

eissn_match_title_not = eissn_combine.query('jtitle_x != jtitle_y')
eissn_match_issn_not = eissn_combine.query('ISSN_x != ISSN_y')
eissn_match_publisher_not = eissn_combine.query('Publisher_x != Publisher_y')

### when doing this, we don't want duplicates of journals, in the sense, the publisher
### has already been found in a previous iteration
eissn_match_publisher_not = eissn_match_publisher_not[~eissn_match_publisher_not.PID.isin(issn_match_publisher_not.PID)]
eissn_match_publisher_not = eissn_match_publisher_not[~eissn_match_publisher_not.PID.isin(title_match_publisher_not.PID)]

eissn_match_issn_not = eissn_match_issn_not[~eissn_match_issn_not.PID.isin(title_match_issn_not.PID)]
eissn_match_title_not = eissn_match_title_not[~eissn_match_title_not.PID.isin(issn_match_title_not.PID)]


### try to sort the eissn issn kerfluffle
issn_matching = pd.DataFrame()
title_but_no_matchy = pd.DataFrame()
not_in_oa = pd.DataFrame()
check_issn = pd.DataFrame()
wiley_being_a_bitch = pd.DataFrame()

for ii in range(0,len(masterjournal)):
    this_issn = masterjournal.loc[ii].ISSN
    this_eissn = masterjournal.loc[ii].EISSN
    this_title = masterjournal.loc[ii].jtitle
    
    if (library['ISSN'].eq(this_issn)).any() == True:

        b = masterjournal.iloc[ii:ii+1]
        d = library.loc[library['ISSN'] == this_issn]
        if len(d)>1:
            wiley_being_a_bitch= pd.concat([wiley_being_a_bitch,d], ignore_index = True)
        else: 
            d = d.set_index(pd.Index(b.index))
            aaa = pd.merge(b, d, left_index=True, right_index=True)
            issn_matching = pd.concat([issn_matching,aaa], ignore_index = True)
        

    elif (library['EISSN'].eq(this_eissn)).any() == True:

        b = masterjournal.iloc[ii:ii+1]
        d = library.loc[library['EISSN'] == this_eissn]
        if len(d)>1:
            wiley_being_a_bitch= pd.concat([wiley_being_a_bitch,d], ignore_index = True)
        else: 
            d = d.set_index(pd.Index(b.index))
            aaa = pd.merge(b, d, left_index=True, right_index=True)
            issn_matching = pd.concat([issn_matching,aaa], ignore_index = True)
        
    elif (library['EISSN'].eq(this_issn)).any() == True and pd.isnull(this_eissn) == True:

        b = masterjournal.iloc[ii:ii+1]
        d = library.loc[library['EISSN'] == this_issn]
        if len(d)>1:
            wiley_being_a_bitch= pd.concat([wiley_being_a_bitch,d], ignore_index = True)
        else: 
            d = d.set_index(pd.Index(b.index))
            aaa = pd.merge(b, d, left_index=True, right_index=True)
            issn_matching = pd.concat([issn_matching,aaa], ignore_index = True)
        
    elif (library['ISSN'].eq(this_eissn)).any() == True and pd.isnull(this_issn) == True:

        b = masterjournal.iloc[ii:ii+1]
        d = library.loc[library['ISSN'] == this_eissn]
        if len(d)>1:
            wiley_being_a_bitch= pd.concat([wiley_being_a_bitch,d], ignore_index = True)
        else: 
            d = d.set_index(pd.Index(b.index))
            aaa = pd.merge(b, d, left_index=True, right_index=True)
            issn_matching = pd.concat([issn_matching,aaa], ignore_index = True)
        
        
    elif (library['EISSN'].eq(this_issn)).any() == True:
        b = masterjournal.iloc[ii:ii+1]
        d = library.loc[library['EISSN'] == this_issn]
        if len(d)>1:
            wiley_being_a_bitch= pd.concat([wiley_being_a_bitch,d], ignore_index = True)
        else: 
            d = d.set_index(pd.Index(b.index))
            aaa = pd.merge(b, d, left_index=True, right_index=True)
            check_issn = pd.concat([check_issn,aaa], ignore_index = True)

        
    elif (library['ISSN'].eq(this_eissn)).any() == True:
        b = masterjournal.iloc[ii:ii+1]
        d = library.loc[library['ISSN'] == this_eissn]
        if len(d)>1:
            wiley_being_a_bitch= pd.concat([wiley_being_a_bitch,d], ignore_index = True)
        else: 
            d = d.set_index(pd.Index(b.index))
            aaa = pd.merge(b, d, left_index=True, right_index=True)
            check_issn = pd.concat([check_issn,aaa], ignore_index = True)        
        
    elif (library['jtitle'].eq(this_title)).any() == True:
        b = masterjournal.iloc[ii:ii+1]
        d = library.loc[library['jtitle'] == this_title]
        if len(d)>1:
            wiley_being_a_bitch= pd.concat([wiley_being_a_bitch,d], ignore_index = True)
        else: 
            d = d.set_index(pd.Index(b.index))
            aaa = pd.merge(b, d, left_index=True, right_index=True)
            title_but_no_matchy = pd.concat([title_but_no_matchy,aaa], ignore_index = True)              
        
    else:
        b = masterjournal.iloc[ii:ii+1]        
        not_in_oa = pd.concat([not_in_oa,b], ignore_index = True)              


## saving to dataframes

# eissn_match_title_not.to_csv(save_directory+'eissn_match_title_not.csv')
# eissn_match_issn_not.to_csv(save_directory+'eissn_match_issn_not.csv')
# eissn_match_publisher_not.to_csv(save_directory+'eissn_match_publisher_not.csv')

# issn_match_title_not.to_csv(save_directory+'issn_match_title_not.csv')
# issn_match_eissn_not.to_csv(save_directory+'issn_match_eissn_not.csv')
# issn_match_publisher_not.to_csv(save_directory+'issn_match_publisher_not.csv')

# title_match_issn_not.to_csv(save_directory+'title_match_issn_not.csv')
# title_match_eissn_not.to_csv(save_directory+'title_match_eissn_not.csv')
# title_match_publisher_not.to_csv(save_directory+'title_match_publisher_not.csv')


################################################################
###### THIS IS FOR GETTING SUBJECTS FROM OPEN ALEX ###############
# all_journals = pd.concat([library,masterjournal], sort = False)

# all_journals = all_journals.drop_duplicates(subset = ['jtitle'])
# all_journals = all_journals[~all_journals['ISSN'].duplicated() | all_journals['ISSN'].isna()]
# all_journals = all_journals[~all_journals['EISSN'].duplicated() | all_journals['EISSN'].isna()]
# all_journals.to_csv(save_directory+'all_our_journals_start.csv')


##### the code graveyard -- aka the code that we don't really need anymore but possibly might
##### want at some point to we are leaving it here

###### LOTHAR's LIST -- which we have replaced witht he master list from Andre'sUrl
# ######### ISSN comparision #####################
# ###### do this comparision with lothar's list###
# ##First need to get rid of the nans in the issn column -- otherwise I think it behaves poorly
# loi = lothar.dropna(subset = ['ISSN'])
# dori = journdora.dropna(subset = ['ISSN'])

# ##compare dora and the library issns
# lothar_title_compare = pd.merge(library,lothar, on='jtitle', how='inner')

# no_lothar_issn = lothar_title_compare.loc[lothar_title_compare[['ISSN_y']].isnull().any(axis=1)]
# no_lothar_eissn = lothar_title_compare.loc[lothar_title_compare[['ISSN_y']].isnull().any(axis=1)]


# ## which dora journals exist in dora list but not lothar list
# ab = pd.merge(loi,dori, on ='ISSN', how='inner')

# isn_no_match_lothar_dora = ab.query('jtitle_x != jtitle_y')



# ## Which journals are in the lothars list but not in dora
# not_titles_in_dora = lothar[~lothar.jtitle.isin(journdora.jtitle)]
# not_issn_in_dora = journdora[~journdora.ISSN.isin(lothar.ISSN)]

# ## which journals don't exist in the dora export 
# ##combine the two datasets 
# combo = pd.concat([lothar,journdora])

# droptitles = combo.drop_duplicates(subset = ['jtitle'], keep =False)

# drop_dup_issn = droptitles[(~droptitles.duplicated(subset='ISSN')) | droptitles['ISSN'].isnull()]

# ### saving the dataframes 
# # drop_dup_issn.to_csv(save_directory+'lothar_no_entry_in_dora.csv')
# # dora_all.to_csv(save_directory+'dora_jan2025.csv')
# # isn_no_match_lothar_dora.to_csv(save_directory+'lothar_dora_title_mismatch.csv')


# not_titles = journdora[~journdora.jtitle.isin(lothar.jtitle)]
# not_titles_in_lothar = not_titles[(~not_titles.duplicated(subset='ISSN')) | not_titles['ISSN'].isnull()]


# ##compare lothar's list and the library issns
# ba = pd.merge(loi,library, on='ISSN', how = 'inner')
# ba = ba.astype({'jtitle_y': object})
# ba = ba.astype({'Publisher_y': object})
# #ISSN match but titles do not
# lothar_oa_issn_compare = ba.query('jtitle_x != jtitle_y')

# ##ISSN match but the eisn does not
# lothar_oa_eissn_compare = ba.query('EISSN_x != EISSN_y')

# ##ISSN match but the publishers don't
# lothar_oa_publisher_compare = ba.query('Publisher_x != Publisher_y')


# # lothar_oa_issn_compare.to_csv(save_directory+'lothar_oa_issn_compare.csv')
# # lothar_oa_eissn_compare.to_csv(save_directory+'lothar_oa_eissn_compare.csv')
# # lothar_oa_publisher_compare.to_csv(save_directory+'lothar_oa_publisher_compare.csv')


# ##what about if we make the comparision on the eissn
# lnoeissn = library.dropna(subset = ['EISSN'])
# ad = pd.merge(loi,lnoeissn, on='EISSN', how = 'inner')
# ad = ad.astype({'jtitle_y': object})
# ad = ad.astype({'Publisher_y': object})

# lothar_oa_publisher_E_compare = ad.query('Publisher_x != Publisher_y')

# # lothar_oa_publisher_E_compare.to_csv(save_directory+'lothar_oa_publisher_E_compare.csv')

