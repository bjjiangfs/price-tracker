# BTC Price Tracker
## Features:
- Checkbox to select or multi-select the currency to show
- Graphs with btc in different currencies as selected in the past 24h
- A table of standard deviation of each currency and the ranking
![Screenshot](demo.png)

# How to install and run locally

1. Download the repo
```
git clone https://github.com/bjjiangfs/price-tracker.git
```

2. Install bokeh
```
pip install bokeh
```

3. Cd into the repo and run the webserver
```
cd price-tracker; bokeh serve --show app.py
```

A tab should pop up in your browser, if not manually go to http://localhost:5006/app


