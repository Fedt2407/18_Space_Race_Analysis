from flask import Flask, render_template
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_APP_KEY')

@app.route('/')
def hello_world():
    data = pd.read_csv('./static/mission_launches.csv', index_col=0)

    # Data structure and head
    shape = data.shape
    head = data.head().iloc[:, 1:].to_html(classes='dataframe', index=False)

    # Plotting the number of missions per year
    # Extract the year from the Date column
    data['Date'] = pd.to_datetime(data['Date'], errors='coerce', infer_datetime_format=True)
    data['Year'] = data['Date'].dt.year
    # Counts the number of missions per year
    missions_per_year = data['Year'].value_counts().sort_index()
    # Create a bar plot
    trend = px.line(missions_per_year, x=missions_per_year.index, y=missions_per_year.values)
    trend.update_layout(xaxis_title='Year', yaxis_title='Number of Missions')
    trend.update_yaxes(range=[0, 120])
    trend.update_traces(line=dict(width=3))
    trend_html = trend.to_html(full_html=False)
   
    # Plotting the number of missions per organization
    missions_per_org = data['Organisation'].value_counts()
    organisation = px.bar(missions_per_org, x=missions_per_org.index, y=missions_per_org.values)
    organisation.update_layout(
        xaxis_title='Organization',
        yaxis_title='Number of Missions (Log Scale)',
        yaxis=dict(type='log')
    )
    organisation_html = organisation.to_html(full_html=False)

    # Plotting the number of succesful mission vs unsuccessful missions
    status = data['Mission_Status'].value_counts()
    status = status.reindex(['Success', 'Failure', 'Partial Failure', 'Prelaunch Failure'])
    status = px.pie(status, values=status.values, names=status.index, hole=0.8)
    status.update_traces(textposition='outside', textinfo='percent+label')
    status_html = status.to_html(full_html=False)

    # Plotting price per year
    data['Date'] = pd.to_datetime(data['Date'], errors='coerce', infer_datetime_format=True)
    data['Year'] = data['Date'].dt.year
    # Remove rows with missing Price
    data = data.dropna(subset=['Price'])
    # Convert the Price column to float
    data['Price'] = data['Price'].str.replace(',', '').astype(float)
    price_per_year = data.groupby('Year')['Price'].sum()
    price_per_year_rolling = price_per_year.rolling(window=5).mean()  # Calculate 5-year rolling average
    price_plot = px.bar(price_per_year, x=price_per_year.index, y=price_per_year.values,
                        labels={'x': 'Year', 'y': 'Total Spending'})
    price_plot.add_scatter(x=price_per_year.index, y=price_per_year_rolling.values, 
                           mode='lines', name='5-Year Rolling Average', line=dict(width=3))  # Add rolling average line with line width of 3
    price_plot.update_layout(xaxis_title='Year', yaxis_title='Total Spending in USD milions')
    price_plot.update_layout(legend=dict(x=0, y=1))  # Move legend to top left
    price_plot_html = price_plot.to_html(full_html=False)

    # Plotting the budget per organisation
    budget_per_org = data.groupby('Organisation')['Price'].sum()
    budget_per_org = budget_per_org.sort_values(ascending=False)
    budget_per_org = px.bar(budget_per_org, x=budget_per_org.index, y=budget_per_org.values)
    budget_per_org.update_layout(xaxis_title='Organization', yaxis_title='Total Spending in USD milions (Log Scale)', yaxis=dict(type='log'))
    budget_per_org.update_layout(legend=dict(x=0, y=1))
    budget_per_org_html = budget_per_org.to_html(full_html=False)

    # Plotting rocket status in a donut chart
    rocket_status = data['Rocket_Status'].value_counts()
    rocket_status = px.pie(rocket_status, values=rocket_status.values, names=rocket_status.index, hole=0.8)
    rocket_status.update_traces(textposition='outside', textinfo='percent+label')
    rocket_status_html = rocket_status.to_html(full_html=False)


    return render_template('index.html', 
                           shape=shape, 
                           head=head, 
                           trend=trend_html, 
                           organisation=organisation_html, 
                           status=status_html,
                           price_per_year=price_plot_html,
                           budget_per_org=budget_per_org_html,
                           rocket_status=rocket_status_html
                           )    


if __name__ == '__main__':
    app.run(debug=True)