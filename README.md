# Fantacalcio

Welcome to the repository, here you can find the scripts necessary to make sure you won't lose any more at Fantacalcio.
The repository is structured as follows:
... 


## Preparation for the auction

Let us restart. 

There are two main tasks, and associated data:

1. Who can we buy? 	-> database
2. Who to buy ? 	-> past and predicted future performances

The resources used here can both be downloaded from [fantacalcio.it](https://www.fantacalcio.it/quotazioni-fantacalcio)

1. `data/Quotazioni_Fantacalcio_Stagione_2024_2025.xlsx`.
2. `data/Statistiche_Fantacalcio_Stagione_2024_2025.xslx`.

It is of course harder to predict future performances, and to value players.
We will try to use a tool already developed (even though I have not had the chance to test it).
For this task, we will scrape the data from [fantacalcio-online](https://www.fantacalcio-online.com/it/asta-fantacalcio-stima-prezzi), with outputs in:

3. `data/Valutazioni_FantacalcioOnline_Stagione_2024_2025.csv`

Code for this can be found at `src/scrape_value_player.py`, which was inspired from `giovanni.davoli`.


## The auction

The main tool of the auction is a streamlit app coded up in `src/auction.py`.
Run this with:

```{zsh run-app}
streamlit run src/auction.py
```

Explain what it is.

## Week to week updates
