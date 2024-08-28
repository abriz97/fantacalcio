#/bin/python3

import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup


def scrape_from_pianetafanta(time=5):
    url = "https://www.pianetafanta.it/giocatori-statistiche-archivio.asp"

    driver = webdriver.Chrome()
    driver.get(url)

    # Accept the cookies
    buttons = driver.find_elements(By.TAG_NAME, "button")
    button = [button for button in buttons if button.text == "Acconsento"][0]
    button.click()

    # select the season and search
    season = Select(driver.find_element(By.CSS_SELECTOR, ".bordino .form-control-p"))
    season.select_by_index(1)
    driver.find_element(By.CSS_SELECTOR, "#Cerca").click()

    # wait for the page to load
    driver.implicitly_wait(time)

    # Look for a table and if it exists, extract data into a pandas dataframe
    table = driver.find_element(By.TAG_NAME, "table")
    df = pd.read_html(table.get_attribute('outerHTML'))[0]

    # quit the driver and return output
    driver.quit()
    return df

scraped_data = scrape_from_pianetafanta(1)
data = scraped_data.copy()

# get column names
new_names = ["", "Giocatore-Squadra", "Ruolo", "Presenze", "Titolare", 
             "", "", "Quotazione", "", "", "", "", "", "Voti", 
             "Goal", "Assist", "Autogoal", "Goal Subiti", "Ammonizioni", "Espulsioni", 
             "Rig_segnati", "Rig_subiti", "Rig_sbagliati", "Rig_parati"
             ]
data.columns = new_names

# remove all columns that have empty name = ""
data = data.drop("", axis=1)

# Keep only Ruolo in "D", "C", "A", "P"
data = data[data["Ruolo"].isin(["D", "C", "A", "P"])]

# # how many "Giocatore-Squadra" have a "." in the name?
# data["Giocatore-Squadra"].str.contains("\.").value_counts()
# data[ (data["Giocatore-Squadra"].str.contains("\.")  == False) ]

# Last three letters of the "Giocatore-Squadra" are the team
data["Giocatore"] = data["Giocatore-Squadra"].str[:-4]
# data["Giocatore"] = data["Giocatore"].str.replace(".", "")
data["Squadra"] = data["Giocatore-Squadra"].str[-3:]
data = data.drop("Giocatore-Squadra", axis=1)

# move "Giocatore" and "Squadra" to the front
if "Giocatore" == data.columns[0]:
    cols = data.columns.tolist()
    cols = cols[-2:] + cols[:-2]
    data = data[cols]

# Check no weird teams
data.value_counts("Squadra")

data



