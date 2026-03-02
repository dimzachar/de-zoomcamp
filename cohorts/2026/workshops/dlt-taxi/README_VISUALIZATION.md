# NYC Taxi Data Visualization with Marimo

Interactive visualization notebook for exploring NYC taxi pipeline data using Marimo and Ibis.

## Features

The notebook includes the following visualizations:

1. **Revenue by Payment Type** - Bar chart showing total revenue for each payment method
2. **Trip Distribution by Taxi Type** - Pie chart showing the proportion of trips by taxi type (green/yellow)
3. **Average Fare & Revenue Comparison** - Side-by-side bar charts comparing metrics across taxi types
4. **Daily Trip Volume Timeline** - Line chart showing trip patterns over time
5. **Top 10 Most Popular Routes** - Horizontal bar chart of the busiest pickup-dropoff combinations
6. **Fare Amount Distribution** - Histogram showing the distribution of fare amounts
7. **Summary Statistics** - Key metrics including total trips, average fare, and total revenue
8. **Sample Data Table** - Interactive table with raw trip data

## Setup

1. Install dependencies using uv:

```bash
uv sync
```

This will install all required packages including marimo, ibis, plotly, and pandas from the pyproject.toml.

## Running the Notebook

1. Make sure your DuckDB database file exists at `taxi_pipeline.duckdb`
2. Launch the marimo notebook with uv:

```bash
uv run marimo edit taxi_visualization.py
```

This will open the interactive notebook in your browser where you can explore the visualizations.

## Data Access with Ibis

The notebook uses Ibis to query the DuckDB database, which provides:
- Lazy evaluation for efficient queries
- SQL-like operations in Python
- Seamless integration with pandas and plotly

## Customization

You can modify the notebook to:
- Add filters for date ranges or specific taxi types
- Create additional visualizations
- Export data for further analysis
- Add interactive controls with marimo UI elements

## Reference

Based on the dlt documentation: https://dlthub.com/docs/general-usage/dataset-access/marimo
