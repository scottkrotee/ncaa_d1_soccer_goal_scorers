### Author: Scott Krotee - Sept 7, 2024 ###

import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.graph_objects as go
import os
from datetime import datetime

# Base URL and page identifiers for top NCAA goal scorers stats
base_url = 'https://www.ncaa.com/stats/soccer-men/d1/current/individual/5/'
pages = ['p1', 'p2', 'p3', 'p4', 'p5']  # Page identifiers for pagination

def scrape_ncaa_soccer_stats(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError if the response status code is 4XX/5XX

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the table containing the statistics
        stats_table = soup.find('table')
        if not stats_table:
            print("Statistics table not found.")
            return None, None

        # Extract headers
        headers = [header.text.strip() for header in stats_table.find_all('th')]

        # Extract rows
        rows = []
        for row in stats_table.find_all('tr')[1:]:  # skip the header row
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            rows.append(cols)
        
        return headers, rows

    except requests.HTTPError as e:
        print(f'HTTP Error occurred: {e.response.status_code}')
        return None, None
    except requests.RequestException as e:
        print(f'Request exception: {e}')
        return None, None
    except Exception as e:
        print(f'An error occurred: {e}')
        return None, None

# Initialize an empty list to collect all the data
all_rows = []
all_headers = None

# Loop through each page and scrape the data
for page in pages:
    url = base_url + page
    headers, rows = scrape_ncaa_soccer_stats(url)
    
    if headers and rows:
        all_headers = headers  # Save headers once
        all_rows.extend(rows)  # Collect rows from all pages

if all_headers and all_rows:
    # Create a DataFrame from the concatenated data
    df = pd.DataFrame(all_rows, columns=all_headers)

    # Get today's date in YYYY-MM-DD format
    today_date = datetime.today().strftime('%Y-%m-%d')

    # Determine the folder path dynamically for cross-platform compatibility
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Create the full file path with the date in the filename
    file_path = os.path.join(script_dir, f"ncaa_goal_scorers_stats_{today_date}.csv")

    # Save the DataFrame to the specified folder with the date in the filename
    df.to_csv(file_path, index=False)

    print(f"✅ Data saved successfully to: {file_path}")

    
    # Convert relevant columns to numeric for plotting
    df['Goals'] = pd.to_numeric(df['Goals'], errors='coerce')
    df['Per Game'] = pd.to_numeric(df['Per Game'], errors='coerce')
    df['Games'] = pd.to_numeric(df['Games'], errors='coerce')

    # Sort the DataFrame by Goals Per Game to identify top performers
    df = df.sort_values(by='Per Game', ascending=False)

    ### Dark Themed Table Display ###
    def display_table(df):
        fig = go.Figure(data=[go.Table(
            header=dict(values=list(df.columns),
                        fill_color='black',
                        font=dict(color='white', size=12),
                        align='left'),
            cells=dict(values=[df[col] for col in df.columns],
                       fill_color='darkslategray',
                       font=dict(color='white', size=11),
                       align='left'))
        ])

        fig.update_layout(
            title='Top NCAA Goal Scorers',
            title_x=0.5,
            paper_bgcolor='black',
            font=dict(color='white')
        )
        fig.show()

    ### Scatter Plot with Name Display Logic and Correct Hover Text ###
    def display_scatter(df):
        grouped = df.groupby(['Per Game', 'Games']).agg(
            Player_Names=('Name', lambda x: ', '.join(x)),
            Goals=('Goals', 'mean'),
            Team=('Team', lambda x: ', '.join(x)),
            Player_Count=('Name', 'count')
        ).reset_index()

        fig = go.Figure()

        # Identify top 3 players
        top_3 = df.head(3)
        top_3_names = top_3['Name'].tolist()

        ### Hover Text Creation ###
        def create_hover_text(row):
            # Retrieve all player data (names, goals, teams, etc.) for the given Per Game and Games
            player_data = df[(df['Per Game'] == row['Per Game']) & (df['Games'] == row['Games'])]
            hover_text = ""
            for _, player_row in player_data.iterrows():
                hover_text += (f"Name: {player_row['Name']}<br>"
                               f"Team: {player_row['Team']}<br>"
                               f"Goals: {player_row['Goals']}<br>"
                               f"Games: {player_row['Games']}<br>"
                               f"Goals Per Game: {player_row['Per Game']}<br><br>")
            return hover_text

        # Prepare hover text for grouped data
        hover_text = [create_hover_text(row) for i, row in grouped.iterrows()]

        # Color intensity based on Goals Per Game and larger markers for top players
        marker_size = [
            20 if any(name in top_3_names for name in row['Player_Names'].split(', ')) else 16
            for _, row in grouped.iterrows()
        ]

        # Stagger names, group them, and avoid showing top 3 names twice
        player_labels = [
            f"{row['Player_Count']} Players" if row['Player_Count'] > 2
            else ', '.join(
                name for name in df[(df['Per Game'] == row['Per Game']) & (df['Games'] == row['Games'])]['Name'].tolist()
                if name not in top_3_names)  # Exclude top 3 names from white labels
            for _, row in grouped.iterrows()
        ]

        # Scatter plot for grouped players
        fig.add_trace(go.Scatter(
            x=grouped['Per Game'], y=grouped['Games'], 
            mode='markers+text',  # Markers and text
            marker=dict(size=marker_size, color=grouped['Per Game'], colorscale='Viridis', opacity=0.8, line=dict(width=1, color='white')),
            text=player_labels,  # Show player names or "X Players"
            textposition='bottom center',  # Adjust label position to reduce overlap
            hovertext=hover_text,  # Use full hover text for all details
            hoverinfo='text',  # Show only the hover text
            textfont=dict(size=16)  # Increase text size
        ))

        # Highlight the top 3 players with yellow annotations
        for i, row in top_3.iterrows():
            fig.add_annotation(
                x=row['Per Game'], 
                y=row['Games'],
                text=row['Name'],  # Show player name for top 3
                showarrow=True,
                arrowhead=2,
                ax=-80 + (i * 80),  # Vary horizontal offset based on index to spread out labels
                ay=-100 + (i * 60),  # Vary vertical offset based on index to stagger labels
                font=dict(size=20, color="yellow"),  # Increase annotation text size
                arrowcolor="yellow"  # Match arrow color to the text color for clarity
            )

        # Add a label over the top 3 players in a modern, lower-opacity box
        fig.add_annotation(
            x=(top_3['Per Game'].mean()),  # Center horizontally above the top 3 players
            y=(top_3['Games'].max() + 2),  # Slightly above the top 3 players' y-axis position
            text="NCAA Most Dangerous Goal Scorers",
            showarrow=False,
            font=dict(size=20, color="red"),  # Customize font size and color
            bgcolor="rgba(50, 50, 50, 0.6)",  # Semi-transparent background
            bordercolor="white",
            borderwidth=2,
            borderpad=10
        )

        # Set plot background and styles with faint gridlines
        fig.update_layout(
            title='Goals Per Game vs. Games Played (Player Counts and Names)',
            xaxis_title='Goals Per Game',
            yaxis_title='Games Played',
            plot_bgcolor='black',
            paper_bgcolor='black',
            font=dict(color='white')
        )

        fig.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor='rgba(255,255,255,0.1)', zeroline=False, color='white')  # Faint x-axis gridlines
        fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='rgba(255,255,255,0.1)', zeroline=False, color='white')  # Faint y-axis gridlines

        fig.show()

    # Call both functions
    display_table(df)  # Display the table
    display_scatter(df)  # Display the scatter plot

else:
    print("No data to display.")
