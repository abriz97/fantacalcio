"""
Created on Mon 2 Sep 

Adapted from giovanni.davoli's
(much more readable now)
"""

import requests
import lxml.html as lh
import pandas as pd

url='https://www.fantacalcio-online.com/it/asta-fantacalcio-stima-prezzi'
page = requests.get(url)
doc = lh.fromstring(page.content)
tr_elements = doc.xpath('//tr')

def parse_row(row):
    if len(row) != 11:
        return None
    
    ruolo = row[1].text_content()
    ruolo = "".join([c for c in ruolo if c.isupper()])

    squadra = row[2].text_content()
    nome = row[3].text_content()

    k       = row[4].text_content()
    k350_8  = row[5].text_content()
    k350_10 = row[6].text_content()
    k500_8  = row[7].text_content()
    k500_10 = row[8].text_content()

    # return a pandas dataframe row
    return pd.DataFrame({
        "Ruolo": [ruolo],
        "Squadra": [squadra],
        "Nome": [nome],
        "K": [k],
        "K350_8": [k350_8],
        "K350_10": [k350_10],
        "K500_8": [k500_8],
        "K500_10": [k500_10]
    })

parsed = list(map(parse_row, tr_elements))
data = pd.concat(parsed, ignore_index=True)
data.columns = data.loc[0]
data.drop(0, inplace=True)
data.to_csv('data/price_fanta.csv')