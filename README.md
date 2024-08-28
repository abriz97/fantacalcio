# Fantacalcio

Welcome to the repository, here you can find the scripts necessary to make sure you won't lose any more at Fantacalcio.

The repository is structured as follows:

- Usage
- Folders
	- [R](#R)
	- [src](#src)

## Usage

Which packages are required to run the code? 
Provide installation script, possibly through `venv`. At the same time this is just a small project and there are very few dependencies so this is not crucial.

To get probability of your players playing, update the `lista_calciatori.yml` file with your players.


## Folders

### R

### src

The folder contains scripts to scrape data from online websites, or to analyse data.
For example, I wrote: 
- `scrape_colors.py` to obtain `data/seriea_colors.yaml`
- `scrape_data.py` to obtain `data/expectedgoals2223.csv`
- `dati_settimanali.R` is to be run prior to every game to offer an overview of your choices with their probability of playing, their opponents and ...

### data

- `giocatori_fantacalcio.csv` reports all the players in the fantacalcio (not updated after january session).

