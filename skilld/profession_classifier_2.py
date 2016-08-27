import pandas as pd
from text_unidecode import unidecode

df = pd.read_csv('Profession Matcher - out.csv')

df1 = pd.DataFrame(columns = ['job description', 'skilld profile'])

for i, row in df.iterrows():
    description = unidecode(str(row['description'])).lower()
    if 'sales' in description:
        profile = 'Sales Representive'
    elif 'cafe' in description:
        profile = 'Cafe Allrounder'
    elif 'customer' in description and 'service' in description:
        profile = 'Customer Service Attendant'
    elif 'cashier' in description:
        profile = 'Cashier'
    elif 'chef' in description:
        profile = 'Executive Chef'
    elif 'barista' in description:
        profile = 'Barista'
    elif 'waiter' in description:
        profile = 'Waiter'
    elif 'waitress' in description:
        profile = 'Waitress'
    elif 'bartender' in description:
        profile = 'Bartender'
    elif 'cook' in description:
        profile = 'Cook'
    elif 'game' in description:
        profile = 'Gaming Room Attendant'
    elif 'tour' in description and 'guide' in description:
        profile = 'Tour Guide'
    elif 'butcher' in description or 'meat' in description:
        profile = 'Butcher'
    elif 'laundry' in description:
        profile = 'Laundry Manager'
    elif 'car' in description and 'park' in description:
        profile = 'Cark Park Attendant'
    else:
        profile = 'NA'

    df1.loc[i] = [description, profile]

df1.to_csv('Job profiles.csv')
    
