import marimo

__generated_with = "0.19.11"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import dlt
    import ibis
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import pandas as pd

    return dlt, go, ibis, make_subplots, mo, pd, px


@app.cell
def _(mo):
    mo.md("""
    # NYC Taxi Data Visualization

    Interactive dashboard for exploring NYC taxi trip data from the pipeline.
    """)
    return


@app.cell
def _(dlt):
    # Attach to the dlt pipeline
    pipeline = dlt.attach("taxi_pipeline")
    dataset = pipeline.dataset()

    # Get ibis connection for rich data exploration (read-only to avoid locking)
    con = dataset.ibis(read_only=True)

    # List available tables
    tables = con.list_tables()
    return con, dataset, pipeline, tables


@app.cell
def _(con, mo, tables):
    mo.md(f"**Available tables:** {', '.join(tables)}")

    # Load taxi data
    trips = con.table("taxi_data")

    # Show schema
    mo.md(f"**Columns:** {', '.join(trips.columns)}")
    return (trips,)


@app.cell
def _(mo, trips):
    # Show data overview
    total_trips = trips.count().execute()

    mo.md(f"""
    ## Data Overview

    Total trips in dataset: **{total_trips:,}**
    """)
    return


@app.cell
def _(ibis, mo, px, trips):
    # Revenue by payment type
    payment_revenue = (
        trips
        .group_by("payment_type")
        .aggregate(
            total_revenue=trips.fare_amt.sum(),
            trip_count=trips.count()
        )
        .order_by(ibis.desc("total_revenue"))
        .execute()
    )

    fig_payment = px.bar(
        payment_revenue,
        x="payment_type",
        y="total_revenue",
        title="Revenue by Payment Type",
        labels={"payment_type": "Payment Type", "total_revenue": "Total Revenue ($)"},
        color="total_revenue",
        color_continuous_scale="Blues"
    )

    mo.ui.plotly(fig_payment)
    return


@app.cell
def _(mo, px, trips):
    # Trips by vendor
    vendor_stats = (
        trips
        .group_by("vendor_name")
        .aggregate(
            trips_count=trips.count(),
            avg_fare=trips.fare_amt.mean(),
            total_revenue=trips.fare_amt.sum()
        )
        .execute()
    )

    fig_vendor = px.pie(
        vendor_stats,
        values="trips_count",
        names="vendor_name",
        title="Trip Distribution by Vendor",
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    mo.ui.plotly(fig_vendor)
    return (vendor_stats,)


@app.cell
def _(go, make_subplots, mo, vendor_stats):
    # Average fare comparison
    fig_fare = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Average Fare by Vendor", "Total Revenue by Vendor"),
        specs=[[{"type": "bar"}, {"type": "bar"}]]
    )

    fig_fare.add_trace(
        go.Bar(
            x=vendor_stats["vendor_name"],
            y=vendor_stats["avg_fare"],
            name="Avg Fare",
            marker_color="lightblue"
        ),
        row=1, col=1
    )

    fig_fare.add_trace(
        go.Bar(
            x=vendor_stats["vendor_name"],
            y=vendor_stats["total_revenue"],
            name="Total Revenue",
            marker_color="lightgreen"
        ),
        row=1, col=2
    )

    fig_fare.update_xaxes(title_text="Vendor", row=1, col=1)
    fig_fare.update_xaxes(title_text="Vendor", row=1, col=2)
    fig_fare.update_yaxes(title_text="Fare ($)", row=1, col=1)
    fig_fare.update_yaxes(title_text="Revenue ($)", row=1, col=2)

    mo.ui.plotly(fig_fare)
    return


@app.cell
def _(mo, px, trips):
    # Time series analysis - trips over time
    trips_with_date = trips.mutate(
        pickup_date=trips.trip_pickup_date_time.cast("date")
    )

    daily_trips = (
        trips_with_date
        .group_by("pickup_date")
        .aggregate(
            daily_trips=trips_with_date.count(),
            daily_revenue=trips_with_date.fare_amt.sum()
        )
        .order_by("pickup_date")
        .execute()
    )

    fig_timeline = px.line(
        daily_trips,
        x="pickup_date",
        y="daily_trips",
        title="Daily Trip Volume Over Time",
        labels={"pickup_date": "Date", "daily_trips": "Number of Trips"}
    )
    fig_timeline.update_traces(line_color="steelblue", line_width=2)

    mo.ui.plotly(fig_timeline)
    return


@app.cell
def _(ibis, mo, px, trips):
    # Top routes by coordinates
    top_routes = (
        trips
        .group_by(["start_lat", "start_lon", "end_lat", "end_lon"])
        .aggregate(
            trip_count=trips.count(),
            avg_fare=trips.fare_amt.mean()
        )
        .order_by(ibis.desc("trip_count"))
        .limit(10)
        .execute()
    )

    top_routes["route"] = (
        "(" + top_routes["start_lat"].round(3).astype(str) + ", " + 
        top_routes["start_lon"].round(3).astype(str) + ") → (" +
        top_routes["end_lat"].round(3).astype(str) + ", " + 
        top_routes["end_lon"].round(3).astype(str) + ")"
    )

    fig_routes = px.bar(
        top_routes,
        x="trip_count",
        y="route",
        orientation="h",
        title="Top 10 Most Popular Routes",
        labels={"trip_count": "Number of Trips", "route": "Route (Start → End)"},
        color="avg_fare",
        color_continuous_scale="Viridis"
    )

    mo.ui.plotly(fig_routes)
    return


@app.cell
def _(mo, px, trips):
    # Fare amount distribution
    fare_sample = trips.select("fare_amt").limit(10000).execute()

    fig_fare_dist = px.histogram(
        fare_sample,
        x="fare_amt",
        nbins=50,
        title="Fare Amount Distribution",
        labels={"fare_amt": "Fare Amount ($)"},
        color_discrete_sequence=["coral"]
    )
    fig_fare_dist.update_layout(showlegend=False)

    mo.ui.plotly(fig_fare_dist)
    return


@app.cell
def _(mo, px, trips):
    # Trip distance vs fare
    distance_fare = trips.select(["trip_distance", "fare_amt"]).limit(1000).execute()

    fig_scatter = px.scatter(
        distance_fare,
        x="trip_distance",
        y="fare_amt",
        title="Trip Distance vs Fare Amount",
        labels={"trip_distance": "Distance (miles)", "fare_amt": "Fare ($)"},
        opacity=0.5,
        color_discrete_sequence=["steelblue"]
    )

    mo.ui.plotly(fig_scatter)
    return


@app.cell
def _(mo, trips):
    # Summary statistics
    stats = trips.aggregate(
        total_trips=trips.count(),
        avg_fare=trips.fare_amt.mean(),
        max_fare=trips.fare_amt.max(),
        min_fare=trips.fare_amt.min(),
        total_revenue=trips.fare_amt.sum(),
        avg_distance=trips.trip_distance.mean(),
        avg_passengers=trips.passenger_count.mean()
    ).execute()

    mo.md(f"""
    ## Summary Statistics

    - **Total Trips:** {stats['total_trips'].iloc[0]:,}
    - **Average Fare:** ${stats['avg_fare'].iloc[0]:.2f}
    - **Maximum Fare:** ${stats['max_fare'].iloc[0]:.2f}
    - **Minimum Fare:** ${stats['min_fare'].iloc[0]:.2f}
    - **Total Revenue:** ${stats['total_revenue'].iloc[0]:,.2f}
    - **Average Distance:** {stats['avg_distance'].iloc[0]:.2f} miles
    - **Average Passengers:** {stats['avg_passengers'].iloc[0]:.2f}
    """)
    return


@app.cell
def _(mo, trips):
    # Sample data table
    sample_data = trips.limit(100).execute()

    mo.md("## Sample Data")
    return (sample_data,)


@app.cell
def _(mo, sample_data):
    mo.ui.table(sample_data)
    return


@app.cell
def _(mo, trips):
    # Date range for trip_pickup_date_time
    _trips_with_date_stats = trips.mutate(
        pickup_date=trips.trip_pickup_date_time.cast("date")
    )

    date_stats = _trips_with_date_stats.aggregate(
        start_date=_trips_with_date_stats.pickup_date.min(),
        end_date=_trips_with_date_stats.pickup_date.max(),
    ).execute()

    start_date = date_stats["start_date"].iloc[0]
    end_date = date_stats["end_date"].iloc[0]

    mo.md(
        f"""
    ## SQL Answers

    ### Question 1: Date range

    - **Start date:** {start_date}
    - **End date:** {end_date}
    """
    )
    return


@app.cell
def _(mo, trips):
    # Credit card proportion
    _credit_stats = trips.aggregate(
        credit_trips=(trips.payment_type == "Credit").sum(),
        total_trips=trips.count(),
    ).execute()

    _credit_trips = _credit_stats["credit_trips"].iloc[0]
    _total_trips_credit = _credit_stats["total_trips"].iloc[0]

    _credit_percentage = (
        100.0 * _credit_trips / _total_trips_credit if _total_trips_credit else 0.0
    )

    mo.md(
        f"""
    ### Question 2: Credit card proportion

    - **Credit card trips:** {_credit_trips:,}
    - **Total trips:** {_total_trips_credit:,}
    - **Credit percentage:** {_credit_percentage:.2f}%
    """
    )
    return


@app.cell
def _(mo, trips):
    # Total tips
    tip_stats = trips.aggregate(total_tips=trips.tip_amt.sum()).execute()
    total_tips = tip_stats["total_tips"].iloc[0]

    mo.md(
        f"""
    ### Question 3: Total tips

    - **Total tips:** ${total_tips:.2f}
    """
    )
    return


if __name__ == "__main__":
    app.run()
