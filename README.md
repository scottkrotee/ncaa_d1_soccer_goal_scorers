# README for NCAA Soccer Goal Scorers Web Scraper

## Overview
This project scrapes the top NCAA men's soccer goal scorers data from the NCAA website, processes it, and generates both a table and scatter plot visualizations using pandas and plotly. The main goal is to collect player statistics, save them into a CSV file, and provide an interactive visual display.

## Features:
- Scrapes multiple pages of player statistics from NCAA website.
- Saves data in a CSV file (ncaa_goal_scorers_stats.csv).
- Displays a dark-themed table using plotly to show top scorers.
- Creates a scatter plot with hover text to explore player performance based on goals per game and games played.

## Requirements
Before running this code, ensure you have the following Python packages installed:
```bash
pip install requests beautifulsoup4 pandas plotly
```
## Libraries Used:
- requests: For sending HTTP requests to fetch the HTML content from the web.
- BeautifulSoup: For parsing HTML and extracting the data from tables.
- pandas: For handling and manipulating the scraped data.
- plotly.graph_objects: For creating visualizations like tables and scatter plots.

## Usage
### Scraping NCAA Soccer Stats
The scraper iterates through the pages of the top NCAA men's soccer goal scorers stats. It extracts the relevant table data (player names, teams, goals, games played, etc.) and saves it into a CSV file.

## Steps:
1. Define the base URL for the NCAA stats page and list the page identifiers (p1, p2, etc.).
2. The scrape_ncaa_soccer_stats(url) function sends an HTTP GET request, parses the HTML, and extracts the table headers and rows.
3. The scraped data from all pages is compiled into a single Pandas DataFrame.
4. The DataFrame is saved as ncaa_goal_scorers_stats.csv.

## Visualizing Data
Two visualizations are generated from the scraped data:

1. Dark-Themed Table: Displays the sorted player statistics based on goals per game using plotly.Table.
    - To display, call the function display_table(df).
2. Scatter Plot: Shows a scatter plot of goals per game versus games played, with hover text for player details. Top 3 players are highlighted in yellow.
    - To display, call the function display_scatter(df).

# Running the Script
1. Scrape the NCAA website by running the following code:
```python
#Run the script to scrape and save the data
for page in pages:
    url = base_url + page
    headers, rows = scrape_ncaa_soccer_stats(url)
    
    if headers and rows:
        all_headers = headers  # Save headers once
        all_rows.extend(rows)  # Collect rows from all pages

if all_headers and all_rows:
    df = pd.DataFrame(all_rows, columns=all_headers)
    df.to_csv('ncaa_goal_scorers_stats.csv', index=False)  # Save to CSV

    # Data visualization
    display_table(df)
    display_scatter(df)
```
2. The script will save the data as ncaa_goal_scorers_stats.csv and open the visualizations in your default web browser.

## Error Handling
- If the scraper cannot find the statistics table or encounters an error during the request, the error is printed, and the script gracefully stops.
- HTTP and request exceptions are caught and displayed with their respective error codes.

## Customization
- Pages: You can extend or modify the number of pages to scrape by adding to the pages list.
- URL: Change the base_url if the NCAA website structure changes.
- Visualizations: Customize the display_table and display_scatter functions to tweak styles, fonts, colors, and layouts.

## Contribution
Feel free to fork this repository, suggest improvements, or submit pull requests.
