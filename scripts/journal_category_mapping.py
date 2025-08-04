# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 09:08:53 2025

@author: knappeel

Plotting the open alex cateogries
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
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
pio.renderers.default = "browser"

##############################################################################
###################Inputs and variables needed###############################

### Set working diretory -- python scripts are hosted in within a folder in this directory
### Going to be two folders in horizontal -- data and python
working_directory = "\\Users\\knappeel\\Documents\\library\\coding\\journals"
os.chdir(working_directory)

## Where to save
save_directory=(working_directory+'\\data\\journal_categories\\')
figsave_directory=(working_directory+'\\data\\journal_categories\\figures\\')


### Import the dataframe
oalexloc1 = "\\Users\\knappeel\\Documents\\library\\coding\\journals\\data\\journal_categories\\open_alex_topics_exportall.csv"

### function imporved with the help of claude
def create_domain_alluvial_plots(data_path):
    ## import the data
    cat = pd.read_csv(data_path, encoding='latin1')
    cat = cat.drop_duplicates(subset=['field_name','subfield_name'], keep='first')
    
    ## will plot one domain at a time -- what are the unique domains
    domains = cat['domain_name'].unique()
    
    ## unique to this dataframe, social sciences domain also has field social science
    ## this messes up the mapping so we will change it slightly here 
    cat['field_name'] = cat['field_name'].replace('Social Sciences', 'Social Science')
    
    ## create a figure for each domain
    figures = {}
    
    ## cycle through each domain
    for domain in domains:
        ## Filter data for current domain
        domain_data = cat[cat['domain_name'] == domain]
        
        ## group by source, target and value
        df1 = domain_data.groupby(['domain_name', 'field_name'])['topic_name'].count().reset_index()
        df1.columns = ['source', 'target', 'value']
        # want an intermediate node, so second dataframe
        df2 = domain_data.groupby(['field_name', 'subfield_name'])['topic_name'].count().reset_index()
        df2.columns = ['source', 'target', 'value']
        
        ## combine the dataframes
        links = pd.concat([df1, df2], axis=0)
        
        ## Create unique node list and mapping
        unique_source_target = list(set(links['source'].unique()) | set(links['target'].unique()))
        mapping_dict = {k: v for v, k in enumerate(unique_source_target)}
        
        ## map node names to indices -- this is for plotly to work properly
        links['source'] = links['source'].map(mapping_dict)
        links['target'] = links['target'].map(mapping_dict)
        
        ## generate colors for nodes so it looks nice nice
        n_colors = len(unique_source_target)
        colors = [
            f'rgb({int(r)}, {int(g)}, {int(b)})'
            for r, g, b in [
                (150 + 100 * np.sin(i * 2 * np.pi / n_colors),
                 150 + 100 * np.sin((i * 2 * np.pi / n_colors) + 2 * np.pi / 3),
                 150 + 100 * np.sin((i * 2 * np.pi / n_colors) + 4 * np.pi / 3))
                for i in range(n_colors)
            ]
        ]
        
        ## create individual figure
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=unique_source_target,
                color=colors,
                hovertemplate='%{label}<br>Total Flow: %{value}<extra></extra>',
            ),
            link=dict(
                source=links['source'],
                target=links['target'],
                value=links['value'],
                hovertemplate='%{source.label} → %{target.label}<br>Value: %{value}<extra></extra>',
                color=links['source'].map(lambda x: colors[x]).apply(lambda x: x.replace('rgb', 'rgba').replace(')', ',0.4)')),
        ))])
        
        # Update layout for individual figure
        fig.update_layout(
            title=dict(
                text=f"OpenAlex Subjects: {domain}",
                x=0.5,
                xanchor='center',
                font=dict(size=20)
            ),
            font=dict(size=12),
            height=1000,  
            paper_bgcolor='white',
            plot_bgcolor='white',
            hovermode='x',
        )
        
        figures[domain] = fig
    
    return figures

def display_all_plots(figures):
    """Helper function to display all plots in a notebook"""
    for domain, fig in figures.items():
        print(f"\n{domain}")
        fig.show()


## do the thing
figures = create_domain_alluvial_plots(oalexloc1)
display_all_plots(figures)








