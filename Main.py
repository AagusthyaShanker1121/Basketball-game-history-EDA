import streamlit as st
import pandas as pd
import numpy as np
import base64 
from PIL import Image   
import plotly.express as px
st.set_page_config(layout = "wide")

# Basic outline of the web page
# ------------------------------------------------
# front end :
# Title
# some content below title
# player stats display subheader
# displaying dyanamic data frame
# csv file downloading link
# button for showing intercorrelation matrix
# Side bar for taking user inputs
# user-inputs : year, teams, position of player

# --------------------------------------------------

# Backend : 

# web-scraping of NBA player statistics
# downloading csv functionality link

# ---------------------------------------------------



# Frontend:
# Title :

image = Image.open("C:\\Users\\AGASTYA SHANKER\\streamlit_apps\\nba-8176216_1280.jpg")
st.image(image, use_column_width=True)

st.title("NBA Player Stats Explorer")
st.markdown("""
This app performs simple webscraping of NBA player stats data!
* **Python libraries:** base64, pandas, streamlit, and PIL.
* **Data source:** [Basketball-reference.com](https://www.basketball-reference.com/).
""")
st.markdown("---")




def preprocess_data(player_df):
    player_df = player_df.drop(columns=["Rk"], axis="columns")
    player_df = player_df.drop(player_df[player_df['Age']=='Age'].index)

    # Gets a dataframe to get all the columns with missing values
    missing_val = player_df.isna().sum().reset_index()
    missing_val = missing_val.rename(columns={0 : "Missing_count", "index" : "feature"})
    missing_val = missing_val.loc[missing_val['Missing_count'] > 0].reset_index().drop(columns=['index'])
    # missing_val_records = player_df[missing_val['feature']]

    # st.dataframe(missing_val)

    # col1,col2 = st.columns(2)
    # # in each column display the histogram of each feature in missing_val
    # with col1 :
    #     for feature in missing_val['feature']:
    #         st.plotly_chart(px.histogram(player_df[feature]))

    # st.dataframe(missing_val_records)

    # I want to identify what columns are numeric and non-numeric
    # by looking at the data, there are only two columns that are non-numeric

    # Changing the datatype of numeric columns
    for column in player_df.columns:
        if column not in ['Player', 'Pos', 'Tm']:
            player_df[column] = player_df[column].astype('float64')

    # replace all nans with mean
    for column in missing_val['feature']:
        mean_val = player_df[column].mean(axis=0)
        player_df[column].replace(np.nan, mean_val, inplace=True)
    
    # with col2 :
    #     for feature in missing_val['feature']:
    #         st.plotly_chart(px.histogram(player_df[feature]))

    return player_df

# Web scrapping of the basketball data
@st.cache_resource
def load_data(selected_year):
    html_url = f"https://www.basketball-reference.com/leagues/NBA_{selected_year}_per_game.html"
    html = pd.read_html(html_url)
    player_df = html[0]
    player_df = preprocess_data(player_df)
    return player_df


# Taking user inputs
# sidebar consisting of year selected (drop-down menu), multi-select menu for choosing teams, and positions

st.sidebar.header("Filter by")
# st.sidebar.subheader("Year")


selected_year = st.sidebar.selectbox("Year", list(range(2023, 1990, -1)))
player_df = load_data(selected_year)
unique_teams = player_df['Tm'].unique()
unique_positions = player_df['Pos'].unique()


teams_list = st.sidebar.multiselect("Teams", unique_teams, unique_teams)
position_list = st.sidebar.multiselect("Positions", unique_positions, unique_positions)
st.sidebar.markdown('---')
st.sidebar.header('Glossary of Terms')
st.sidebar.markdown("""
* **Rn** -- Rank
* **Pos** -- Position
* **Tm** -- Team
* **G** -- Games
* **GS** -- Games started
* **MP** -- Minutes Played
* **FG** -- Field goals per game
* **FGA** -- Field goal attempts per game
* **FG%** -- Field goal %
* **3P** -- 3 point field goals per game
* **3PA** -- 3 point field goal attempts per game
* **3P%** -- 3 point field goal %
* **eFG%** -- effective field goal %
* **FT** -- Free throws per game
* **FTA** -- Free throws attempts per game
* **FT%** -- Free throws %
* **DRB** -- Defensive Rebounds Per Game
* **TRB** -- Total Rebounds Per Game
* **AST** -- Assists Per Game
* **STL** -- Steals Per Game
* **BLK** -- Blocks Per Game
* **TOV** -- Turnovers Per Game
* **PF** -- Personal Fouls Per Game
* **PTS** -- Points Per Game
""")



# Player data according to teams- header
st.subheader("Player Data Of Selected Teams")

filtered_player_df = player_df.loc[player_df['Tm'].map(lambda x: x in teams_list)]
filtered_player_df = filtered_player_df.loc[player_df['Pos'].map(lambda x: x in position_list)]

# Display dynamic data frame only if the check box is ticked
if st.checkbox("Show Player Data for the selected teams."):
    st.dataframe(filtered_player_df)

st.markdown("---")



#=======================================================================================================
# Data Visualization
#------------------------------------------------------------------------------------------------------

# [ Plot 1 ]---------------------------------> :
# Plotting graph of all teams and the total sum of points acheived for each position
team_and_pos_grouping = filtered_player_df.groupby(['Tm', 'Pos'])
points_sum = team_and_pos_grouping.PTS.sum()
points_sum = points_sum.reset_index()

total_points_by_team_and_pos_plot = px.bar(points_sum, 
                                            x='Tm', 
                                            y=['PTS', 'Pos'], 
                                            color='Pos', 
                                            barmode='stack').update_layout(xaxis_title = 'Team', 
                                                                            yaxis_title = 'Points Scored')

# st.dataframe(points_sum)

# [ Plot 2 ]------------------------------------>
# Plotting the total points scored individually by all teams in a single year.
team_grouping = filtered_player_df.groupby('Tm')
# team_points_sum = team_grouping.PTS.sum().reset_index()

# total_points_by_team_and_year_plot = px.bar(team_points_sum, 
#                                             x='Tm', 
#                                             y='PTS', 
#                                             title = 'Total points scored by each team').update_layout(xaxis_title = 'Team', 
#                                                                                                         yaxis_title = 'Points scored')

# st.plotly_chart(total_points_by_team_and_year_plot)
# st.dataframe(team_points_sum)

# Plotting min points scored in each position and by each team
min_points_scored = team_and_pos_grouping.apply(lambda df : df.loc[df.PTS.idxmin()])


min_points_scored_plot = px.bar(min_points_scored, 
                                x='Tm', 
                                y='PTS', 
                                barmode = 'group', 
                                color='Pos',
                                hover_data=['Player', 'Age', 'PTS']).update_layout(xaxis_title = 'Team', yaxis_title = 'Points')


# [ Plot 3 ]---------------------------------->
# Plotting max points scored in each position and by each team
max_points_scored = team_and_pos_grouping.apply(lambda df : df.loc[df.PTS.idxmax()])


max_points_scored_plot = px.bar(max_points_scored, 
                                x='Tm', 
                                y='PTS', 
                                barmode = 'group', 
                                color='Pos',
                                hover_data=['Player', 'Age', 'PTS']
                                ).update_layout(xaxis_title = 'Team', yaxis_title = 'Points')


# [Plot 4]-------------------------------------------->
# Plotting average points scored in each position and by each team
avg_points_scored = team_and_pos_grouping.PTS.agg('mean').reset_index()


avg_points_scored_plot = px.bar(avg_points_scored, 
                                x='Tm', 
                                y='PTS', 
                                barmode = 'group', 
                                color='Pos',
                                ).update_layout(xaxis_title = 'Team', yaxis_title = 'Points')



col1, col2 = st.columns(2, gap="large")
with col1:
    st.subheader('Points scored in each position by team')
    st.plotly_chart(total_points_by_team_and_pos_plot, use_container_width=True)

    st.markdown("---")
    st.subheader('Maximum points scored in each position in every team')
    st.plotly_chart(max_points_scored_plot, use_container_width=True)


with col2:
    st.subheader('Average points scored in each position in every team')
    st.plotly_chart(avg_points_scored_plot, use_container_width=True)

    st.markdown("---")
    st.subheader('Minimum points scored in each position in every team')
    st.plotly_chart(min_points_scored_plot, use_container_width=True)


# [Plot 5]------------------------------------------------>
# Plotting the maximum games played by a player in all teams
# after getting aggregate of all the teams
df = team_grouping.apply(lambda df : df.loc[df.G.idxmax()])

st.markdown('---')
st.subheader('Maximum Games played by a player in every team')
max_games = px.bar(df, 
                   x='Tm', 
                   y='G', 
                   color='Pos',
                   hover_data=['Player', 'Age', 'PTS']
                   ).update_layout(xaxis_title = 'Team', yaxis_title = 'Maximum Games played')
st.plotly_chart(max_games, use_container_width=True)


