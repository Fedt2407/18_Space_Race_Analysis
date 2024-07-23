from flask import Flask, render_template
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_APP_KEY')

@app.route('/')
def hello_world():
    data = pd.read_csv('./static/mission_launches.csv', index_col=0)
    shape = data.shape
    return render_template('index.html', shape=shape)    


if __name__ == '__main__':
    app.run(debug=True)