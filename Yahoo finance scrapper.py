
# coding: utf-8

# In[1]:


# import the relevant libraries

import requests 
import csv
import re
from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
import numpy as np
import datetime as dt

# enter the path of the csv file to store the list of tickers for which you need
# market cap, dividend yield and % off from 52 week high details
security_list = pd.read_csv('C:\\Users\\shauvik\\Desktop\\Google Drive Backup\\Dividend\\Input\\Ex-div Security List.csv')

######################## Fetch market cap from Yahoo Finance ########################

# setup the base url4
ticker_url2 = "https://finance.yahoo.com/quote/"

# create an empty list to capture and aggregate the details for each ticker
marketcap_details = []

# loop through the csv file 
for row2 in security_list.itertuples(index=True):
    a2 = (getattr(row2,"Ticker"))
    
    # construct the final url for each ticker
    market_cap_url = ticker_url2 + str(a2)
    
    # read the content of each url using Beautiful Soup
    details = requests.get(market_cap_url,allow_redirects=False)
    details_status = details.status_code
    c2 = details.content
    
    soup2 = BeautifulSoup(c2,"html.parser")
    
    # check for a valid Yahoo Finance url for each ticker
    if details_status == 200:
        
        # inspect the Yahoo Finance page to figure out the exact html tag structure
        page_validity_check1 = soup2.find('td', class_='Ta(end) Fw(600) Lh(14px)')
        
        if page_validity_check1 == 'None':
            print(a2, " does not have market cap details.")              
            
        # only capture details from valid urls   
        else:
            market_cap = soup2.find_all('td', class_='Ta(end) Fw(600) Lh(14px)')[8].text
            
            # create an empty dictionary to create a easy reference of market cap figure for each ticker
            market_cap_list = {}
            
            # use try and except framework to check for errors
            try:   
                for mktcap in market_cap:
                    if mktcap == 'N/A':
                        continue
                
                    market_cap_list['Ticker'] = str(a2)
                    market_cap_list['Market Cap Details'] = market_cap
                    
            except IndexError:
                print(a2, " does not have market cap details.")
            
            # update the empty master list with the dictionary data
            marketcap_details.append(market_cap_list)
        
    else:
        print(a2, " is not a valid url.")

# convert the master list to a pandas dataframe        
df_marketcap = pd.DataFrame(marketcap_details)

# Determine the units of market cap figure        
df_marketcap['Market Cap Unit'] = df_marketcap['Market Cap Details'].str.get(-1) 

# Only extract the numbers from the string
df_marketcap['Market Cap'] = df_marketcap['Market Cap Details'].str.extract('(\d+\.\d*)') 

# Convert string to numeric (i.e. float data type) and convert all market cap figures to Millions
df_marketcap['Market Cap'] = df_marketcap['Market Cap'].astype(float).fillna(0.0)                   
df_marketcap['Market Cap (Mn)'] = df_marketcap.apply(lambda row: (row['Market Cap']/1000 
                                               if row['Market Cap Unit']=='M'
                                               else row['Market Cap']),axis=1)                                

df_marketcap = df_marketcap[['Ticker','Market Cap (Mn)']]

######################## Fetch the latest dividend yield of tickers from Yahoo Fiannce ########################

# setup a base url
url_temp = "https://finance.yahoo.com/quote/"

yld = []

# lopp through the list of tickers from the df_marketcap dataframe created previously
for row in df_marketcap.itertuples(index=True):
    a1 = (getattr(row,"Ticker"))
    
    # construct the actual url for each ticker
    url = url_temp + str(a1)
    
    # read the content of each url using Beautiful Soup 
    details = requests.get(url)
    s = details.status_code
    c2 = details.content
    
    soup2 = BeautifulSoup(c2,"html.parser")
    
    # check for valid Yahoo Finance pages
    if s == 200:

        check = soup2.find_all("td", class_='Ta(end) Fw(600) Lh(14px)')
        
        if check == 'None':
            print(a1, " does not have yield details.")  
            
        else:
            a2 = soup2.find_all("td", class_='Ta(end) Fw(600) Lh(14px)')[13].text
            
            yld_list = {}
            
            try:   
                for i in a2:
                    if i == 'N/A':
                        continue
                
                    yld_list['Ticker'] = str(a1)
                    yld_list['Yield Details'] = a2
                    
            except IndexError:
                print(a1, " does not have yield details.")
            
            yld.append(yld_list)
        
    else:
        print(a1, " is not a valid url.")

# convert the list to a pandas dataframe
df_yld = pd.DataFrame(yld)   

# use pandas dataframe string methods to split and extarct text between parenthesis
# also make sure to exclude % sign from yield to retain numerical format for easy calculations
df_yld['Yield'] = df_yld['Yield Details'].str.split('(').str[1].str.split('%').str[0]
df_yld = df_yld[['Ticker','Yield']]

# merge the 2 dataframes across a common index, i.e. ticker
df_merge1 = df_marketcap.set_index('Ticker').join(df_yld.set_index('Ticker'))

######################## Fetch the 52 week high of tickers from Yahoo Finance ########################

# again setup a base url
ticker_url3 = "https://finance.yahoo.com/quote/"

other_details = []

# loop through the tickers from the first dataframe
# rest of the procedure follows a similar pattern like above
for row3 in df_marketcap.itertuples(index=True):
    a3 = (getattr(row3,"Ticker"))
    other_details_url = ticker_url3 + str(a3)
    other_det = requests.get(other_details_url)
    other_details_status = other_det.status_code
    c3 = other_det.content
    
    soup3 = BeautifulSoup(c3,"html.parser")
        
    if other_details_status == 200:
        page_validity_check2 = soup3.find_all("td", class_='Ta(end) Fw(600) Lh(14px)')
        
        if page_validity_check2 == []:
            print(a3, " does not have 52 week details.")
    
        else:
            other1 = soup3.find_all("td", class_='Ta(end) Fw(600) Lh(14px)')[5]
    
            other_list = {}
        
            try:   
                other_list['Ticker'] = str(a3)
                other_list['52 week range'] = other1.text
                
            except IndexError:
                print(a3, " does not have 52 week details.")
            
            other_details.append(other_list)
        
    else:
        print(a3, " does not have 52 week details.")
                
df_other_details = pd.DataFrame(other_details)

# extarct the 2nd part of the string appearing after '-'
df_other_details['52 Week High'] = df_other_details['52 week range'].str.split('-').str[1] 

# convert the column to a numeric format
df_other_details['52 Week High'] = df_other_details['52 Week High'].astype(float)
df_other_details = df_other_details[['Ticker','52 Week High']]

df_merge2 = df_other_details.set_index('Ticker').join(df_merge1)

######################## Fetch the latest closing price data from Yahoo Finance ########################

# setup a base url
# rest of the procedure is similar as above
ticker_url4 = "https://finance.yahoo.com/quote/"

closing_price_hist = []
for row4 in df_marketcap.itertuples(index=True):
    a4 = (getattr(row4,"Ticker"))
    closing_price_url = ticker_url4 + str(a4) + '/history'
    close = requests.get(closing_price_url)
    close_status = close.status_code
    c4 = close.content
    
    soup4 = BeautifulSoup(c4,"html.parser")

    if close_status == 200:
        page_validity_check3 = soup4.find_all('td', class_='Py(10px) Pstart(10px)')
               
        if page_validity_check3 == 'None':
            print(a4, " does not have closing price details.")
            
        else:
            closing_price = soup4.find_all('td', class_='Py(10px) Pstart(10px)')[4]
            closing_date = soup4.find_all('td', class_='Py(10px) Ta(start) Pend(10px)')[0]
    
            closing_price_list = {}
        
            try:   
                closing_price_list['Ticker'] = str(a4)
                closing_price_list['Closing Price'] = closing_price.text
                closing_price_list['Closing Date'] = closing_date.text
               
            except IndexError:
                print(a4, " does not have closing price details.")
            
            closing_price_hist.append(closing_price_list)
        
    else:
        print(a4, " does not have closing price details.")
        
df_closing_price = pd.DataFrame(closing_price_hist)

# convert the column to a numeric format
df_closing_price['Closing Price'] = df_closing_price['Closing Price'].astype(float)
df_closing_price = df_closing_price[['Ticker','Closing Price','Closing Date']]

######################## Merge everythinng ########################

df_merge_all = df_closing_price.set_index('Ticker').join(df_merge2)

# calculate the % off from 52 week high and store it in a new dataframe column 'Off from 52-week High'
df_merge_all['Off from 52-week High'] = df_merge_all.apply(lambda row: (((row['Closing Price']-row['52 Week High'])/row['52 Week High'])*100), axis=1)

df_merge_all = df_merge_all[['Market Cap (Mn)','Yield','Off from 52-week High']]

df_merge_all.to_csv("C:\\Users\\shauvik\\Desktop\\Google Drive Backup\\Dividend\\Ex-div output.csv")

