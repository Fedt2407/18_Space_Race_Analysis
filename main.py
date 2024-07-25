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
    trend_html = trend.to_html(full_html=False)
   
    # Plotting the number of missions per organization
    missions_per_org = data['Organisation'].value_counts()
    organisation = px.bar(missions_per_org, x=missions_per_org.index, y=missions_per_org.values, title='Number of Missions per Organization')
    organisation.update_layout(
        xaxis_title='Organization',
        yaxis_title='Number of Missions (Log Scale)',
        yaxis=dict(type='log')
    )
    organisation_html = organisation.to_html(full_html=False)


    return render_template('index.html', shape=shape, head=head, trend=trend_html, organisation=organisation_html)    


if __name__ == '__main__':
    app.run(debug=True)