import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas 
import re

# DONE:
# - find how to change page

# Exploratory helpers
def print_ls(ls):
    for element in ls:
        print(element)

def print_attribute(ls, attribute="innerHTML" ):
    for element in ls:
        inner=element.get_attribute(attribute)
        print(inner)

def test_xpath(path):
    ls=driver.find_elements("xpath", path)
    print_ls(ls)
    return(ls)

# Main helpers
def find_buttons():
    return(driver.find_elements("xpath","//li[@data-page]/a"))

def click_button_by_text(buttons, text):
    for b in buttons:
        if b.text == text:
            b.click()
            return(find_buttons())
    print("no button with such text")

    
options = Options()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome( service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://encycolorpedia.com/teams/football/serie-a")
driver.maximize_window()

# to heach team corresponds aan h2? 
# then Team colors:  are contained in ul

# get colors
def get_colors_singlepage():

    team_names = test_xpath("//article/h2")
    team_names = [ h for h in team_names if h.text != 'Top Serie A Football (Soccer) Team Hex Colors' ]
    team_names_ls = [ h.text for h in team_names ]

    colors=driver.find_elements("xpath","//article[descendant::h2]/ul/li[2]")
    colors_ls = [c.text.lstrip("Team colors:\u2002") for c in colors]
    out=dict(zip(team_names_ls, colors_ls))
    return(out)

# get buttons
buttons=driver.find_elements("xpath", "//p//a[text()=2]")

colors1=get_colors_singlepage()
buttons[0].click()
colors2=get_colors_singlepage()
colors1.update(colors2)

import yaml
with open('../data/seriea_colors.yaml', 'w') as yaml_file:
    yaml.dump(colors1, yaml_file, default_flow_style=False)
