import pandas as pd
import openpyxl as op

account = int(input('Plz choose Account Number:- 1: Mrsool    2: 1pass   3: Moddakir    '))
branch_traking = int(input('Enter 1 if you wanna to track data from branch: '))
add_ads = int(input('Enter 1 if you wanna to Add Ads in your Data: '))

#Function To set Target
def set_target(channel_data):
    if 'Conversions' in channel_data['Campaign Name'] or 'Orders' in channel_data['Campaign Name'] or 'Demand Gen' in channel_data['Campaign Name']  or 'Conversion' in channel_data['Campaign Name']:
        return 'Conversion'
    elif 'Installs' in channel_data['Campaign Name'] or 'Install' in channel_data['Campaign Name'] or 'app purchase' in channel_data['Campaign Name']:
        if account == 3:             #becouse Moddakir rename Acquisition by App Install
           return 'App Install'
        else: 
          return 'Acquisition'
    elif 'Awareness' in channel_data['Campaign Name'] or 'Video views' in channel_data['Campaign Name'] or 'Search' in channel_data['Campaign Name']:
        return 'Awareness'
    else:
        return 'NAN'


#if you wanna to get data from branch so take this data        
if branch_traking == 1:
   branch = pd.read_csv('branch.csv', skiprows=5)
   data_branch = branch[['date', 'ad partner', 'campaign', 'Unified installs', 'Unified purchases', 'Unified revenue']]
   data_branch['date'] = pd.to_datetime(data_branch['date']).dt.date                       #Formate Date   
   #Add datecampign coloumn, it's like primary kay                                               
   data_branch['datecampign'] = data_branch['date'].astype(str) + '' + data_branch['campaign']                             

   #function to take Install, Purchase, Revenue from branch and put it into platform data
   def set_data_branch(channel_data, branch_data):

    for index, row in channel_data.iterrows(): 
        matching_rows = data_branch[data_branch['datecampign'] == row['datecampign']] # Get the matching row from data_branch
        if not matching_rows.empty:                                      #skip unfound campigns 
            matching_row = matching_rows.iloc[0]
            channel_data.loc[index, 'Install Branch'] = matching_row['Unified installs']
            channel_data.loc[index, 'Purchase Branch'] = matching_row['Unified purchases']
            channel_data.loc[index, 'Revenue'] = matching_row['Unified revenue']
    return channel_data

#--------------------------Tiktok Data--------------------------
def tiktok_data(tiktokpath):
    tiktok = pd.read_csv(tiktokpath)
    tiktok_df = pd.DataFrame()
    tiktok = tiktok[tiktok['Cost'] > 0]                        # Remove rows where Cost <= 0
    # Remove Total Row (it means the last row)
    tiktok = tiktok.drop(tiktok.index[-1])
    tiktok['Date'] = pd.to_datetime(tiktok['Date']).dt.date

    # Filling Data
    tiktok_df['Date'] = tiktok['Date']
    tiktok_df['Campaign Name'] = tiktok['Campaign name']
    tiktok_df['Channel'] = 'Tiktok'
    tiktok_df['Spend'] = tiktok['Cost']
    tiktok_df['Install'] = tiktok['App Install'] + tiktok['App Install (SKAN)']
    tiktok_df['Purchase'] = tiktok['Total Purchase'] + tiktok['Total Purchase (SKAN)']
    tiktok_df['Reach'] = tiktok['Reach']
    tiktok_df['Impressions'] = tiktok['Impression']
    tiktok_df['Clicks'] = tiktok['Clicks (Destination)']
    tiktok_df['Objective'] = tiktok_df.apply(set_target, axis=1)
    tiktok_df['Video Views'] = tiktok['Video views']
    tiktok_df['Video Plays at 25%'] = tiktok['Video Views at 25%']
    tiktok_df['Video Plays at 50%'] = tiktok['Video Views at 50%']
    tiktok_df['Video Plays at 75%'] = tiktok['Video Views at 75%']
    tiktok_df['Video Completion'] = tiktok['Video Views at 100%']
    
    if branch_traking == 1:
       tiktok_df['datecampign'] = tiktok_df['Date'].astype(str) + '' + tiktok_df['Campaign Name']
       tiktok_df = set_data_branch(tiktok_df, data_branch)

    if add_ads == 1:
       tiktok_data['ad name'] = tiktok['Ad Name']   
   
    return tiktok_df

#--------------------------Twitter Data--------------------------
def twitter_data(twitterpath):

   twitter = pd.read_excel(twitterpath)
   twitter = twitter[twitter['Spend'] > 0]         #Remove Spent = 0
   twitter['Time period'] = pd.to_datetime(twitter['Time period']).dt.date     #Formate Date
   Twitter_df = pd.DataFrame()
   
   if(account == 2 or account == 3):
        twitter['Spend'] = twitter['Spend'] * 3.75                 #convert Currency into SAR
   if(account == 1):
        twitter['Spend'] = twitter['Spend'] / 3.75                 #convert Currency into $
           

   Twitter_df['Date'] = twitter['Time period']
   Twitter_df['Campaign Name'] = twitter['Campaign name']
   Twitter_df['Channel'] = 'Twitter'
   Twitter_df['Spend'] = twitter['Spend']
   Twitter_df['Reach'] = twitter['Total audience reach']
   Twitter_df['Impressions'] = twitter['Impressions']
   Twitter_df['Clicks'] = twitter['App clicks']
   Twitter_df['Install'] = twitter['Installs'] + twitter['SKAN installs']
   Twitter_df['Purchase'] = twitter['Purchases']
   Twitter_df['Revenue'] = ''
   Twitter_df['Objective'] = Twitter_df.apply(set_target, axis=1)

   Twitter_df['Video Views'] = twitter['Video views']
   Twitter_df['Video Plays at 25%'] = twitter['Video played 25%']
   Twitter_df['Video Plays at 50%'] = twitter['Video played 50%']
   Twitter_df['Video Plays at 75%'] = twitter['Video played 75%']
   Twitter_df['Video Completion'] = twitter['Video completions']

   if branch_traking == 1:
       Twitter_df['datecampign'] = Twitter_df['Date'].astype(str) + '' + Twitter_df['Campaign Name']
       Twitter_df = set_data_branch(Twitter_df, data_branch)

   if add_ads == 1:
       Twitter_df['ad name'] = twitter['Ad name']     

   return Twitter_df
   
#--------------------------Meta Data--------------------------
def meta_data(metapath):
   
   meta = pd.read_csv(metapath)
   #becouse spent cloumn in meta his name changed by currency
   if account == 1 :
      meta = meta.rename(columns={'Amount spent (USD)': 'spent'}) 
   else:
      meta = meta.rename(columns={'Amount spent (SAR)': 'spent'})  
      
   meta = meta[(meta['spent'] > 0)]                        
   meta['Reporting starts'] = pd.to_datetime(meta['Reporting starts']).dt.date
   meta_df = pd.DataFrame()


   meta_df['Date'] = meta['Reporting starts']
   meta_df['Campaign Name'] = meta['Campaign name']
   if(account == 3):
      meta_df['Channel'] = 'IG'                 #Moddakir name meta "IG"
   else:
      meta_df['Channel'] = 'Meta'  
   meta_df['Spend'] = meta['spent']
   meta_df['Install'] = meta['App installs']
   meta_df['Purchase'] = meta['Purchases']
   meta_df['Reach'] = meta['Reach']
   meta_df['Impressions'] = meta['Impressions']
   meta_df['Clicks'] = meta['Link clicks']
   meta_df['Objective'] = meta_df.apply(set_target, axis=1)
   meta_df['Video Views'] = meta['Video plays']
   meta_df['Video Plays at 25%'] = meta['Video plays at 25%']
   meta_df['Video Plays at 50%'] = meta['Video plays at 50%']
   meta_df['Video Plays at 75%'] = meta['Video plays at 75%']
   meta_df['Video Completion'] = meta['Video plays at 100%']

   if branch_traking == 1:
    meta_df['datecampign'] = meta_df['Date'].astype(str) + '' + meta_df['Campaign Name']
    meta_df = set_data_branch(meta_df, data_branch)

   if add_ads == 1:
       meta_df['ad name'] = meta['Ad name']      

   return meta_df

#--------------------------Google Data--------------------------
def google_data(googlepath):
   google = pd.read_csv(googlepath, skiprows=2)                #skip first 2 row in google data
   google = google[google['Cost'] > 0]                                   
   #Not Take Total Rows
   google = google[google['Campaign'].notnull()]
   google['Day'] = pd.to_datetime(google['Day']).dt.date

   if(account == 3):
        google['Cost'] = google['Cost'] * 3.75

   Google_df = pd.DataFrame()

   Google_df['Date'] = google['Day']
   Google_df['Campaign Name'] = google['Campaign']
   Google_df['Channel'] = 'Google'
   Google_df['Spend'] = google['Cost']
   Google_df['Install'] = google['Installs']
   Google_df['Reach'] = ""
   Google_df['Impressions'] = google['Impr.']
   Google_df['Clicks'] = google['Clicks']
   Google_df['Purchase'] = google['Purchase']
   Google_df['Objective'] = Google_df.apply(set_target, axis=1)
   Google_df['Video Views'] = google['Views']
   Google_df['Video Plays at 25%'] = google['Video played to 25%']
   Google_df['Video Plays at 50%'] = google['Video played to 50%']
   Google_df['Video Plays at 75%'] = google['Video played to 75%']
   Google_df['Video Completion'] = google['Video played to 100%']

   if branch_traking == 1:
    Google_df['datecampign'] = Google_df['Date'].astype(str) + '' + Google_df['Campaign Name']
    Google_df = set_data_branch(Google_df, data_branch)

   if add_ads == 1:
    Google_df['ad name'] = google['Ad name']   

   return Google_df

#--------------------------Snapchat Data--------------------------
def snap_data(snappath):

   snap = pd.read_csv(snappath)
   snap = snap[snap['Amount Spent'] > 0]                        
   snap['Start Time'] = pd.to_datetime(snap['Start Time']).dt.date
   Snap_df = pd.DataFrame()
   
   if(account == 2 or account == 3):
     snap['Amount Spent'] = snap['Amount Spent'] * 3.75

   Snap_df['Date'] = snap['Start Time']
   Snap_df['Campaign Name'] = snap['Campaign Name']
   if(account == 3):
      Snap_df['Channel'] = 'SC'
   else:
      Snap_df['Channel'] = 'Snapchat'
        
   Snap_df['Spend'] = snap['Amount Spent']
   Snap_df['Install'] = snap['App Installs'] + snap['Conversion Total Installs Sk AD Network Total']
   Snap_df['Purchase'] = snap['Purchases'] 
   Snap_df['Reach'] = snap['Paid Reach']
   Snap_df['Impressions'] = snap['Paid Impressions']
   Snap_df['Clicks'] = snap['Clicks']
   Snap_df['Objective'] = Snap_df.apply(set_target, axis=1)
   Snap_df['Video Views'] = ""
   Snap_df['Video Plays at 25%'] = snap['Video Plays at 25%']
   Snap_df['Video Plays at 50%'] = snap['Video Plays at 50%']
   Snap_df['Video Plays at 75%'] = snap['Video Plays at 75%']
   Snap_df['Video Completion'] = snap['Video Completions']

   if branch_traking == 1:
    Snap_df['datecampign'] = Snap_df['Date'].astype(str) + '' + Snap_df['Campaign Name']
    Snap_df = set_data_branch(Snap_df, data_branch)

   if add_ads == 1:
    Snap_df['ad name'] = snap['Ad name']  

   return Snap_df

#--------------------------Apple Data--------------------------
def apple_data(applepath):

   apple = pd.read_csv(applepath, skiprows=7)
   apple = apple[apple['Spend'] > 0]

   apple['Day'] = pd.to_datetime(apple['Day']).dt.date                     
   Apple_df = pd.DataFrame()
   
   if(account == 2 or account == 3):
       apple['Spend'] = apple['Spend'] * 3.75

   Apple_df['Date'] = apple['Day']
   Apple_df['Campaign Name'] = apple['Campaign Name']

   if(account == 3):
      Apple_df['Channel'] = 'Apple Search'
   else:   
      Apple_df['Channel'] = 'Apple'
   Apple_df['Spend'] = apple['Spend']
   Apple_df['Install'] = apple['Installs']
   Apple_df['Reach'] = 0
   Apple_df['Impressions'] = apple['Impressions']
   Apple_df['Clicks'] = apple['Taps']
   Apple_df['Purchase'] = ""
   Apple_df['Revenue'] = ""
   Apple_df['Objective'] = Apple_df.apply(set_target, axis=1)

   if branch_traking == 1:
    Apple_df['datecampign'] = Apple_df['Date'].astype(str) + '' + Apple_df['Campaign Name']
    Apple_df = set_data_branch(Apple_df, data_branch) 

   if add_ads == 1:
    Apple_df['ad name'] = apple['Ad Name'] 

   return Apple_df


#Call Data
tiktok = tiktok_data('tiktok.csv')
twitter = twitter_data('twitter.xlsx')
meta = meta_data('meta.csv')
google = google_data('google.csv')
snap = snap_data('snapchat.csv')
apple = apple_data('apple.csv')

final_data = pd.concat([tiktok,twitter,meta,google,snap,apple], ignore_index=True)

datapath = 'final_data.csv'
final_data.to_csv(datapath, index=False)