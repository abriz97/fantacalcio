import pandas as pd
import streamlit as st
from datetime import datetime

team_colors = {
    "Atalanta": "#1F4E79",  # Dark Blue
    "Bologna": "#A52A2A",  # Brown
    "Como": "#327AD9",  # Medium Violet Red
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
    "Parma" : "#edea42",  # Yellow
    "Roma": "#800000",  # Maroon
    "Salernitana": "#8B0000",  # Dark Red
    "Sampdoria": "#4169E1",  # Royal Blue
    "Sassuolo": "#228B22",  # Forest Green
    "Torino": "#8B4513",  # Saddle Brown
    "Udinese": "#808080",  # Gray
    "Verona": "#FFFF00",  # Yellow
    "Venezia": "#EDA042",  # Orange
    "Milan": "#FF0000"    # Red
}

# Function to color the value based on whether it's above or below minimal_value

value_colors = {
    "high": "orangered",
    "mid-high": "orange",
    "mid": "yellow",
    "mid-low": "aqua",
    "low": "blue",
}

def color_value(value, rank):
    
    color = "grey"
    if rank < minimal_value_idx/5:
        color = value_colors["high"]
    elif rank < minimal_value_idx*2/5:
        color = value_colors["mid-high"]
    elif rank < minimal_value_idx*3/5:
        color = value_colors["mid"]
    elif rank < minimal_value_idx*4/5:
        color = value_colors["mid-low"]
    elif rank < minimal_value_idx*5/5:
        color = value_colors["low"]
    
    return f'<span style="color: {color};">{value}</span>'


# Define constants
AUCTIONERS = [
    "None", "Andrea", "Claudio", "Enrico", "Filippo", 
    "Giulio", "Lollo Bichi", "Lollo Malga", "Luca", "Tino", "Valerio",
]
N_AUCTIONERS = len(AUCTIONERS) - 1
N_PLAYERS_PER_ROLE = {
    "P": 3,
    "D": 8,
    "C": 8,
    "A": 6,
}
VALUE_COLUMN = "Prezzo"
INCLUDE_VALUE_COLOR_LEGEND = False
INCLUDE_ORDER = False

# Load quotes dataset
@st.cache_data
def load_data(path="data/consolidated_data.csv"):
    # read with correct method
    if path.endswith(".csv"):
        quotes = pd.read_csv(path, header=0)
    if path.endswith(".xlsx"):
       quotes = pd.read_excel(path, header=1)
    if not VALUE_COLUMN in quotes.columns:
        raise ValueError(f"Column {VALUE_COLUMN} not found in quotes dataset")
    quotes = quotes.sort_values(['R', 'Nome']).reset_index(drop=True)
    return quotes

quotes = load_data()
# quotes[["Titolarita"]].astype(int)

# Initialize session state
if 'auction_results' not in st.session_state:
    st.session_state.auction_results = pd.DataFrame({
        'Ruolo': quotes["R"],
        'Nome': quotes['Nome'],
        'Squadra': quotes['Squadra'],
        'Value': quotes[VALUE_COLUMN].round(1),
        'Buyer': ['None'] * len(quotes),
        'Price': [0] * len(quotes),
        'Rank': [0] * len(quotes),
        'Top_X_R': [False] * len(quotes),
        'Titolarita': quotes["Titolarita"],
    })

# Navigation in the sidebar
page = st.sidebar.selectbox("Select Page", ["Auction", "Player Expenditure"])

# add a little figure in the sidebar, displaying the value colors.
if INCLUDE_VALUE_COLOR_LEGEND:
    st.sidebar.markdown("### Value Colors")
    for key, color in value_colors.items():
        st.sidebar.markdown(f"""
        <div style="background-color:{color}; padding:10px; border-radius:5px;">
            <span style="color:grey;">{key}</span>
        </div>
        """, unsafe_allow_html=True)

if page == "Auction":

    if 'edited_cells' not in st.session_state:
        st.session_state.edited_cells = {}

    # Callback function to update session state
    def update_cell(index, column):
        if column == "Buyer":
            st.session_state.auction_results.loc[index, column] = st.session_state[f'buyer_{index}']
        elif column == "Price":
            st.session_state.auction_results.loc[index, column] = st.session_state[f'price_{index}']

    # Streamlit app layout
    st.title("Auction List")

    # Custom CSS for better alignment
    st.markdown("""
    <style>
        .stSelectbox, .stNumberInput {
            margin-bottom: -1rem;
        }
        .row-data {
            margin-bottom: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

    # Role selection
    role = st.selectbox("Select the player's role:", options=list(N_PLAYERS_PER_ROLE.keys()))

    # Filter and process data
    filtered_quotes = quotes[quotes['R'] == role]
    auction_results_filtered = st.session_state.auction_results[
        st.session_state.auction_results['Nome'].isin(filtered_quotes['Nome'])
    ].copy()

    values = auction_results_filtered['Value'].sort_values(ascending=False)
    minimal_value_idx = N_PLAYERS_PER_ROLE[role] * N_AUCTIONERS
    if role == "P":
        minimal_value_idx //= 3
    minimal_value = values.iloc[minimal_value_idx]

    role_idx_min, role_idx_max = auction_results_filtered.index.min(), auction_results_filtered.index.max()

    # Rank players by their value and titularity
    auction_results_filtered = auction_results_filtered.sort_values(['Value', 'Titolarita'], ascending=[False, False])
    auction_results_filtered['Rank'] = range(len(auction_results_filtered))
    auction_results_filtered['Top_X_R'] = auction_results_filtered['Value'] >= minimal_value

    # # First player selection
    # first_player = st.selectbox("Select the first auctioned player:", options=filtered_quotes['Nome'])
    # first_player_idx = auction_results_filtered[auction_results_filtered['Nome'] == first_player].index[0]
    # new_order = list(range(first_player_idx, role_idx_max + 1)) + list(range(role_idx_min, first_player_idx))

    ## Color quotes based on rank
    auction_results_filtered['Color'] = auction_results_filtered.apply(lambda x: color_value(x['Value'], x['Rank']), axis=1)

    # Display editable table
    title = {
        "P": "Goalkeepers",
        "D": "Defenders",
        "C": "Midfielders",
        "A": "Forwards",
    }
    st.subheader(f"Auction Order for {title[role]}")

    # Add column names
    col_width = [1, 1, 0.5, 0.5,0.5, 1, 0.7]
    col1, col2, col3, col4, col5, col6, col7 = st.columns(col_width)
    col1.markdown("<b>Name</b>", unsafe_allow_html=True)
    col2.markdown("<b>Team</b>", unsafe_allow_html=True)
    if INCLUDE_ORDER:
        col_width = [1, 1, 0.5, 0.5, 1, 0.7]
        col3.markdown("<b>Order</b>", unsafe_allow_html=True)
    col4.markdown("<b>Value</b>", unsafe_allow_html=True)
    col5.markdown("<b>IT</b>", unsafe_allow_html=True)
    col6.markdown("<b>Buyer</b>", unsafe_allow_html=True)
    col7.markdown("<b>Price</b>", unsafe_allow_html=True)


    for idx in auction_results_filtered.index:

        col1, col2, col3, col4, col5, col6, col7 = st.columns(col_width)
        col1.markdown(f"<div class='row-data'>{auction_results_filtered.loc[idx, 'Nome']}</div>", unsafe_allow_html=True)

        # Apply background color from team colors
        team = auction_results_filtered.loc[idx, 'Squadra']
        # Default to white if team not found
        team_color = team_colors.get(team, "#FFFFFF")
        col2.markdown(
            f"<div class='row-data' style='background-color:{team_color}; color:white;'>{team}</div>",
            unsafe_allow_html=True)
    
        # Show the "Order" column
        if INCLUDE_ORDER:
            col3.markdown(f"<div class='row-data'>{auction_results_filtered.loc[idx, 'Rank']}</div>", unsafe_allow_html=True)
        col4.markdown(f"<div class='row-data'>{auction_results_filtered.loc[idx, 'Color']}</div>", unsafe_allow_html=True)
        col5.markdown(f"<div class='row-data'>{auction_results_filtered.loc[idx, 'Titolarita']}</div>", unsafe_allow_html=True)
        
        buyer = col6.selectbox(
            "Buyer",
            options=AUCTIONERS,
            key=f"buyer_{idx}",
            index=AUCTIONERS.index(st.session_state.auction_results.loc[idx, 'Buyer']),
            on_change=update_cell,
            args=(idx, 'Buyer'),
            label_visibility="collapsed"
        )
        
        price = col7.number_input(
            "Price",
            value=st.session_state.auction_results.loc[idx, 'Price'],
            key=f"price_{idx}",
            on_change=update_cell,
            args=(idx, 'Price'),
            label_visibility="collapsed"
        )


    # Button to save data
    if st.button("Save"):
        # Get the current date and time for the filename
        current_time = datetime.now().strftime("%y%b%d_%H%M")
        filename = f"results/auction_results_{current_time}.csv"
        
        # Select relevant columns
        save_df = auction_results_filtered[['Nome', 'Squadra', 'Ruolo', 'Buyer', 'Price']]
        
        # Save the DataFrame to a CSV file
        save_df.to_csv(filename, index=False)
        
        # Display a success message
        st.success(f"File saved as {filename}")

# Player Expenditure Page
elif page == "Player Expenditure":
    st.title("Player Expenditure")

    # Calculate the total expenditure and number of players bought for each buyer
    expenditure_df = st.session_state.auction_results.groupby('Buyer').agg(
        Total_Spent=('Price', 'sum'),
        Total_Value = ('Value', 'sum'),
        Players_Bought=('Nome', 'count'),
    ).reset_index()
    expenditure_df['Total_Value'] = expenditure_df['Total_Value'].astype(int)
    expenditure_df = expenditure_df[expenditure_df['Buyer'] != "None"]
    
    # Display the expenditure table
    st.table(expenditure_df)

    # Save expenditure table as CSV
    if st.button("Save Expenditure Report"):
        current_time = datetime.now().strftime("%y%m%d_%H%M")
        filename = f"results/expenditure_report_{current_time}.csv"
        expenditure_df.to_csv(filename, index=False)
        st.success(f"Expenditure report saved as {filename}")