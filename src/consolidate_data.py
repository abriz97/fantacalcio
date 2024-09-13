"""
Friday 6 Sep 2025
Andrea Brizzi

AIM: 
Consolidate downloaded and scraped data into a single csv to analyze/use for auction.
The ouput is a single csv file with:
    - player name - players info: team, role
    - player stats: past goals, assists, FVM, number of played games
    - player predictions: expected FVM, meausre of "titolarita'`
    - player value / price: how much should I spend for this player? 
This implies:
    - fixing player names
    - ...

# Ideas 
# Fixing names can be complicated: I want to keep the same order as the official Fantacalcio
# however, merging can be hard. Instead, let us use an Id column which is Nome-Squadra?
# but where nome only includes family name (and no initials)
"""
 
team_colors = {
    "Atalanta": "#1F4E79",  # Dark Blue
    "Bologna": "#A52A2A",  # Brown
    "Cagliari": "#C71585",  # Medium Violet Red
    "Empoli": "#006BB6",  # Royal Blue
    "Fiorentina": "#6A0DAD",  # Purple
    "Genoa": "#D91E18",  # Red
    "Inter": "#0033CC",  # Blue
    "Juventus": "#000000",  # Black
    "Lazio": "#87CEEB",  # Sky Blue
    "Lecce": "#FFD700",  # Gold
    "Monza": "#FF4500",  # Orange Red
    "Napoli": "#00FFFF",  # Cyan
    "Roma": "#800000",  # Maroon
    "Salernitana": "#8B0000",  # Dark Red
    "Sampdoria": "#4169E1",  # Royal Blue
    "Sassuolo": "#228B22",  # Forest Green
    "Torino": "#8B4513",  # Saddle Brown
    "Udinese": "#808080",  # Gray
    "Verona": "#FFFF00",  # Yellow
    "Milan": "#FF0000"  # Red
}


import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
pio.renderers.default = "browser"
from pathlib import Path
# Model fitting
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline




# Define paths
ProjectRoot = Path.cwd()
data_dir = ProjectRoot / 'data'
output_dir = ProjectRoot / 'data'

# Check if directories exist
if not data_dir.exists():
    raise Error("Data directory not found: check paths")
if not output_dir.exists():
    output_dir.mkdir()

# load data
path_quotes = data_dir / 'Quotazioni_Fantacalcio_Stagione_2024_25.xlsx'
path_stats  = data_dir / 'Statistiche_Fantacalcio_Stagione_2023_24.xlsx'
path_eval   = data_dir / 'price_fanta.csv'
path_titolarita = data_dir / 'Quotazioni_FantacalcioOnline.xlsx'
# path for output
path_output = data_dir / 'consolidated_data.csv'
path_profeta = data_dir / 'valutazioni_profeta.csv'

quotes = pd.read_excel(path_quotes, header=1)
stats  = pd.read_excel(path_stats,  header=1)
profeta = pd.read_csv(path_profeta, header=0)
quotes = pd.merge(quotes, profeta, on=["Nome", "R"], how="left")
quotes["Prezzo"][ quotes["Prezzo"].isnull() ]  = 0.5

def add_id_column(df):
    out = df["Nome"].str.replace(r" [A-z\.]*\.$", "", regex=True)
    out = out.str.replace("'", "")
    out = out.str.title()
    out = out.str.replace(r"^.* ([A-z]*)$", r"\1", regex=True)
    # fix for milinkovic-savic -like
    out = out.str.replace(r"-[A-z]*$", r"", regex=True)
    out += "-" + df["Squadra"]
    out = out.str.replace("Junior-Bologna", "Iling-Bologna")
    return out


quotes["Id"] = add_id_column(quotes)
stats["Id"] = add_id_column(stats)
# quotes["Id"].str.contains("Di-").sum()
if quotes["Id"].str.contains("Di-").sum() > 0:
    raise Error("Di- in Id")

def fix_players(dt):
    dt["Nome"] = dt["Nome"].str.replace("MALINOVSKIY", "MALINOVSKYI", regex=True)
    dt = dt[~((dt["Nome"] == "BIANCO Alessandro") & (dt["Squadra"] == "Fiorentina"))]
    dt = dt[~((dt["Nome"] == "BONIFAZI Kevin") & (dt["Squadra"] == "Bologna"))]
    dt = dt[~((dt["Nome"] == "CASALE Nicolò") & (dt["Squadra"] == "Lazio"))]
    dt = dt[~((dt["Nome"] == "GAETANO Gianluca" ) & ( dt["Squadra"] == "Cagliari"))]
    dt = dt[~((dt["Nome"] ==             "HASA Luis" ) & ( dt["Squadra"] == "Lecce"   ))]
    dt = dt[~((dt["Nome"] ==       "PELLEGRI Pietro" ) & ( dt["Squadra"] == "Torino"  ))]
    dt = dt[~((dt["Nome"] ==          "SAZONOV Saba" ) & ( dt["Squadra"] == "Empoli"  ))]
    dt = dt[~((dt["Nome"] == "WALUKIEWICZ Sebastian" ) & ( dt["Squadra"] == "Empoli"  ))]
    return dt

def fix_names(dt):
    # Keep only uppercase letters in "Nome"
    eval["Nome2"] = eval["Nome"].str.replace(r"([A-Z\s]*) (.*)$", r"\2", regex=True)
    eval["Nome"] = eval["Nome"].str.replace(r"([A-Z\s]*) .*$", r"\1", regex=True).str.title()

    # dt["Nome"] = dt["Nome"].str.replace("[a-z]", "").str.replace(" [A-Z]$", "").str.title()
    # # dt = dt[(dt.Posizione != "POR") | (dt.Nome != "Martinez")]
    # dt["Nome"] = dt["Nome"].str.replace(" ..$", "")
    # dt["Nome"] = dt["Nome"].str.replace(" [A-Z]$", "")
    # dt["Nome"] = dt["Nome"].str.replace(" -$", "")
    # return(dt)
    return(dt)

# Fix players/Nome appearing in multiple teams/Squadra
titolarita = pd.read_excel(path_titolarita, header=1)
titolarita.drop(["Ruolo trequartista", "Ruolo standard", "Posizione", "ETA'", "RAT", "POT", "Kapitals"], axis = 1, inplace=True)
eval   = pd.read_csv(path_eval).drop('Unnamed: 0', axis=1)
eval = pd.merge(eval, titolarita, on = ["Nome", "Squadra"], how="outer")

eval = eval[ (eval.Squadra != "Estero") & (eval.Squadra != "Serie Minori") ]
eval = fix_players(eval)
# Set Nome = Family Name
eval.groupby("Nome").count().sort_values("Squadra", ascending=False)
fix_names(eval)
eval["Id"] = add_id_column(eval)
if eval["Id"].str.contains("Di-").sum() > 0:
    raise Error("Di- in Id")

# need to compare the "official" fantacalcio names (quotes)
# against unofficial, scraped valuations (eval)
def compare_names(quotes, eval, diff = True):

    # Merge quotes and eval
    on_cols = "Id"
    dim_shared = pd.merge(quotes, eval, on=on_cols,  how='inner').shape
    data = pd.merge(quotes, eval, on=on_cols,  how='outer')
    dim_all = data.shape
    print(f"Shared: {dim_shared[0]}/{dim_all[0]}")

    if diff:
        data = data[ (data["R"].isnull()) | (data["Kap."].isnull()) ]
        data=data.sort_values("Id")

    return data

tmp = compare_names(quotes, eval)
tmp.head(50)

# def team_diffs(df, team = "Napoli"):
#     return df[ (df["Squadra_x"] == team) | (df["Squadra_y"] == team) ].sort_values("Id")

# team_diffs(tmp)
# team_diffs(tmp, team = "Torino")


# Only keep the official ones
out = compare_names(quotes, eval, diff = False)
out = out[ ~(out["R"].isna()) ]
out.drop(["Nome_y", "Squadra_y", "RM", "RT"], axis=1, inplace=True)
out.rename(columns={"Nome_x":"Nome", "Squadra_x":"Squadra"}, inplace=True)

out.loc[(out.Id == "Martinez-Inter") & (out.R == "P"), "Id"] = "Martinez2-Inter"
out = out[~((out["Id"] == "Martinez2-Inter")  & (out["Kap."] > 10))]
out = out[~((out["Id"] == "Martinez-Inter")  & (out["Kap."] < 10))]

out.rename(columns={"IS %":"Titolarita"}, inplace=True)

# Now fill in missing values
# For Kap. set NAs to 1
# For 500K (10), use a quadratic model for imputation
out["Kap."] = out["Kap."].fillna(1)

# Impute missing values in "500K (10)" column using a quadratic model
model_data = out[ ~out["500K (10)"].isna() ]
X = model_data["Kap."].values.reshape(-1, 1)
y = model_data["500K (10)"].values
model = make_pipeline(PolynomialFeatures(2), LinearRegression())
model.fit(X, y)

# Generate a range of "Kap." values for smooth line
x_range = np.linspace(out["Kap."].min(), out["Kap."].max(), 500).reshape(-1, 1)
y_range = model.predict(x_range)

# Visualize the model fit
fig = go.Figure()
fig.add_trace(go.Scatter(x=model_data["Kap."], y=model_data["500K (10)"], mode='markers', name='Observed'))
fig.add_trace(go.Scatter(x=x_range.flatten(), y=y_range, mode='lines', name='Quadratic Fit', line=dict(color='red')))
fig.update_layout(title='Quadratic Model Fit for "500K (10)"', xaxis_title='Kap.', yaxis_title='500K (10)')
fig.show()

# Predict missing values and update the dataframe
out.loc[out["500K (10)"].isna(), "500K (10)"] = model.predict(out.loc[out["500K (10)"].isna(), "Kap."].values.reshape(-1, 1))

# save output
out.to_csv(path_output)

def plot_valuations(df, ruolo="all"):
    dplot = df.copy()
    if not ruolo in ["all", "P", "D", "C", "A"]:
        raise ValueError("ruolo must be 'all', 'P', 'D', 'C' or 'A'")
    if ruolo != "all":
        dplot = dplot[dplot["R"] == ruolo]

    fig = px.scatter(dplot, x="Prezzo", y="500K (10)",
                    hover_name="Nome",
                    hover_data={
                        "Titolarita": True, "Bonus": True, "R": False, "Kap.": False
                    },
                    color="Squadra", color_discrete_map=team_colors,
                    facet_col="R", facet_col_wrap=2
                    )
    fig.show()

plot_valuations(out, ruolo = "A")
