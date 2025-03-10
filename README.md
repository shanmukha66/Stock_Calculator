# Stock Profit Calculator & Tracker

A comprehensive web application for tracking stocks and cryptocurrencies in real-time and calculating potential profits from investments. This application provides detailed financial analysis, buy/sell recommendations, historical price charts, and intelligent price predictions.

## Features

### Stock & Crypto Tracker
- **Real-time Asset Tracking**: Monitor up to 5 stocks or cryptocurrencies with live price updates every 6.67 seconds (9 times per minute)
- **Comprehensive Financial Information**: View current price, daily change, market cap, P/E ratio, dividend yield, and 52-week range
- **AI-Powered Price Predictions**: Get intelligent target price predictions when analyst targets aren't available
- **Buy/Sell Recommendations**: Receive investment recommendations based on multiple financial factors
- **Historical Price Charts**: Visualize 30-day price history for each tracked asset
- **Cryptocurrency Support**: Track major cryptocurrencies with specialized data handling

### Profit Calculator
- **Detailed Profit Analysis**: Calculate proceeds, costs, net profit, and ROI
- **Tax Impact Assessment**: See how capital gains tax affects your investment returns
- **Break-Even Analysis**: Determine the price at which your investment breaks even
- **Recovery Time Estimation**: For losing investments, see how long it might take to recover at market average returns
- **Investment Insights**: Get personalized insights about your investment's performance
- **Historical Price Charts**: View 30-day price history for the selected asset

## Price Prediction Algorithm

When analyst target prices aren't available from the Finnhub API, our application uses a sophisticated multi-factor prediction algorithm:

1. **Trend Analysis**: Analyzes recent price movements to identify momentum
2. **PE Ratio Assessment**: Considers PE ratio to adjust growth expectations
3. **Market Average Returns**: Incorporates typical market returns as a baseline
4. **Weighted Combination**: Combines these factors with appropriate weighting

This ensures you always have a target price to help guide investment decisions, even for assets with limited analyst coverage or cryptocurrencies.

## Technologies Used
- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Data Visualization**: Chart.js
- **Stock Data**: Finnhub API
- **Cryptocurrency Data**: Finnhub API with CoinGecko API fallback

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-directory>
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Get a Finnhub API key:
   - Go to https://finnhub.io/
   - Sign up for a free account
   - You'll receive an API key on your dashboard

4. Update the API key in the app.py file:
   - Open app.py
   - Find the line `FINNHUB_API_KEY = "YOUR_API_KEY"`
   - Replace "YOUR_API_KEY" with your actual Finnhub API key

5. Run the application:
```bash
python app.py
```

6. Open your browser and navigate to:
```
http://127.0.0.1:5001/
```

## Usage

### Stock & Crypto Tracker
1. Enter a valid ticker symbol (e.g., AAPL, MSFT, GOOGL) or cryptocurrency (e.g., BTC-USD, ETH-USD) in the form
2. Click "Add Stock" to start tracking
3. View real-time updates, price predictions, and recommendations
4. Click "Clear All" to remove all tracked assets

### Profit Calculator
1. Enter the asset details:
   - Ticker Symbol
   - Allotment (number of shares/units)
   - Final Share Price (selling price)
   - Sell Commission
   - Initial Share Price (purchase price)
   - Buy Commission
   - Capital Gain Tax Rate
2. Click "Calculate" to see the profit report
3. Review the insights and recommendations

## Example Calculation

The application includes a pre-configured example for Adobe (ADBE) stock:
- Ticker: ADBE
- Allotment: 100 shares
- Final Share Price: $110
- Sell Commission: $15
- Initial Share Price: $25
- Buy Commission: $10
- Capital Gain Tax Rate: 15%

Click "Fill Example Values" to use these values.

## API Rate Limits

The Finnhub API has the following rate limits for free accounts:
- 60 API calls per minute
- 25,000 API calls per month

Our application is configured to make 9 updates per minute to stay well within these limits.

## How It Works

### Price Predictions
The application generates price predictions based on:
- Historical price trends
- PE ratio analysis
- Market average returns
- Sector performance benchmarks

### Stock Recommendations
The application generates buy/sell recommendations based on:
- Analyst recommendations
- Target price vs. current price
- Price momentum
- 52-week price range
- P/E ratio

### Profit Calculation
The profit calculation includes:
- Proceeds = Allotment × Final Share Price
- Capital Gain = Proceeds - (Allotment × Initial Share Price) - Buy Commission - Sell Commission
- Tax = Capital Gain × Capital Gain Tax Rate (if positive)
- Total Cost = (Allotment × Initial Share Price) + Buy Commission + Sell Commission + Tax
- Net Profit = Proceeds - Total Cost
- ROI = (Net Profit / Total Cost) × 100
- Break Even Price = (Total Purchase Price + Buy Commission + Sell Commission) / Allotment

##Output Images
![alt text]{1.png}
![alt text]{2.png}

## Acknowledgements
- [Finnhub](https://finnhub.io/) for providing stock data
- [CoinGecko](https://www.coingecko.com/) for supplementary cryptocurrency data
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Bootstrap](https://getbootstrap.com/) for the UI components
- [Chart.js](https://www.chartjs.org/) for data visualization 
