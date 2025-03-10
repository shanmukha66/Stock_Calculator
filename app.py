import logging
import json
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import random
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
CORS(app)

# Global variable to store stock data
stocks_data = []

# Finnhub API key
FINNHUB_API_KEY = "cv7lss1r01qpecigi6ogcv7lss1r01qpecigi6p0"

def predict_target_price(current_price, history, pe_ratio, daily_change):
    """Generate a predicted target price when one is not available from the API."""
    try:
        # Method 1: Simple moving average-based prediction
        if history and len(history) > 5:
            # Calculate average price change over available history
            prices = [item['price'] for item in history]
            avg_price = sum(prices) / len(prices)
            
            # Calculate trend direction and strength
            if len(prices) > 10:
                recent_avg = sum(prices[-5:]) / 5
                older_avg = sum(prices[-10:-5]) / 5
                trend_factor = (recent_avg / older_avg) - 1
            else:
                trend_factor = daily_change / 100  # Use daily change as a proxy
            
            # Apply trend to current price with some dampening
            trend_prediction = current_price * (1 + (trend_factor * 3))  # Project trend forward
            
            # Method 2: PE ratio-based prediction
            pe_prediction = current_price
            if pe_ratio and pe_ratio > 0:
                # Adjust based on PE ratio (higher PE = higher growth expectations)
                if pe_ratio > 30:  # High PE ratio suggests growth
                    pe_prediction = current_price * 1.15
                elif pe_ratio > 20:
                    pe_prediction = current_price * 1.10
                elif pe_ratio > 15:
                    pe_prediction = current_price * 1.05
                else:
                    pe_prediction = current_price * 1.03
            
            # Method 3: Simple percentage increase based on market averages
            market_avg_prediction = current_price * 1.08  # Average market return ~8%
            
            # Weighted average of the three methods
            predicted_price = (trend_prediction * 0.5) + (pe_prediction * 0.3) + (market_avg_prediction * 0.2)
            
            # Add some randomness to make different stocks have different predictions
            randomness = 0.95 + (random.random() * 0.1)  # Random factor between 0.95 and 1.05
            predicted_price *= randomness
            
            # Round to two decimal places
            return round(predicted_price, 2)
        else:
            # Fallback if no history: use simple percentage increase
            growth_rate = 0.08  # Default 8% annual growth
            if daily_change > 0:
                growth_rate += (daily_change / 100) * 0.5  # Positive momentum
            else:
                growth_rate += (daily_change / 100) * 0.3  # Negative momentum but less impact
                
            return round(current_price * (1 + growth_rate), 2)
    except Exception as e:
        logging.error(f"Error in predict_target_price: {str(e)}")
        # Very simple fallback
        return round(current_price * 1.1, 2)  # Default 10% increase

def get_stock_data(ticker):
    """Fetch stock data from Finnhub API"""
    try:
        logging.info(f"Fetching data for {ticker} from Finnhub API")
        
        # Check if this is a cryptocurrency ticker
        is_crypto = False
        if "-" in ticker and ("USD" in ticker.upper() or "BTC" in ticker.upper()):
            is_crypto = True
            logging.info(f"Detected cryptocurrency ticker: {ticker}")
        
        # Get quote data
        if is_crypto:
            # For crypto, use a different endpoint
            crypto_symbol = ticker.split("-")[0].upper()
            quote_url = f"https://finnhub.io/api/v1/crypto/candle?symbol=BINANCE:{crypto_symbol}USDT&resolution=D&from={int(pd.Timestamp.now().timestamp()) - 24*60*60}&to={int(pd.Timestamp.now().timestamp())}&token={FINNHUB_API_KEY}"
            quote_response = requests.get(quote_url)
            crypto_data = quote_response.json()
            
            if crypto_data.get('s') == 'ok' and crypto_data.get('c'):
                # Use the latest close price
                current_price = crypto_data.get('c')[-1]
                previous_close = crypto_data.get('c')[0] if len(crypto_data.get('c')) > 1 else current_price
            else:
                # Fallback to regular quote endpoint
                quote_url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_API_KEY}"
                quote_response = requests.get(quote_url)
                quote_data = quote_response.json()
                current_price = quote_data.get('c', 0)
                previous_close = quote_data.get('pc', 0)
        else:
            # Regular stock quote
            quote_url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_API_KEY}"
            quote_response = requests.get(quote_url)
            quote_data = quote_response.json()
            
            if 'error' in quote_data:
                logging.error(f"Error fetching quote data for {ticker}: {quote_data['error']}")
                return None
                
            current_price = quote_data.get('c', 0)
            previous_close = quote_data.get('pc', 0)
        
        # Calculate daily change
        if previous_close > 0:
            daily_change = ((current_price - previous_close) / previous_close) * 100
        else:
            daily_change = 0
        
        # Get company profile (for stocks) or set defaults (for crypto)
        if is_crypto:
            company_name = f"{ticker.split('-')[0]} ({ticker})"
            sector = "Cryptocurrency"
            market_cap = 0  # We'll try to get this from CoinGecko API later
        else:
            profile_url = f"https://finnhub.io/api/v1/stock/profile2?symbol={ticker}&token={FINNHUB_API_KEY}"
            profile_response = requests.get(profile_url)
            profile_data = profile_response.json()
            
            if not profile_data or 'name' not in profile_data:
                logging.warning(f"Could not fetch company profile for {ticker}")
                company_name = ticker
                sector = "N/A"
            else:
                company_name = profile_data.get('name', ticker)
                sector = profile_data.get('finnhubIndustry', 'N/A')
            
            # Get market cap
            market_cap = profile_data.get('marketCapitalization', 0) * 1000000  # Convert from millions
        
        # Get basic financials for stocks
        if not is_crypto:
            metrics_url = f"https://finnhub.io/api/v1/stock/metric?symbol={ticker}&metric=all&token={FINNHUB_API_KEY}"
            metrics_response = requests.get(metrics_url)
            metrics_data = metrics_response.json()
            
            # Extract metrics
            metrics = metrics_data.get('metric', {})
            pe_ratio = metrics.get('peNormalizedAnnual', None)
            dividend_yield = metrics.get('dividendYieldIndicatedAnnual', None)
            fifty_two_week_high = metrics.get('52WeekHigh', None)
            fifty_two_week_low = metrics.get('52WeekLow', None)
            target_price = metrics.get('targetMedianPrice', None)
        else:
            # Default values for crypto
            pe_ratio = None
            dividend_yield = None
            fifty_two_week_high = None
            fifty_two_week_low = None
            target_price = None
            
            # Try to get some crypto data from CoinGecko API (no API key needed)
            try:
                crypto_id = ticker.split('-')[0].lower()
                coingecko_url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}"
                coingecko_response = requests.get(coingecko_url)
                coingecko_data = coingecko_response.json()
                
                if 'market_data' in coingecko_data:
                    market_data = coingecko_data['market_data']
                    current_price = market_data.get('current_price', {}).get('usd', current_price)
                    market_cap = market_data.get('market_cap', {}).get('usd', 0)
                    fifty_two_week_high = market_data.get('high_24h', {}).get('usd')
                    fifty_two_week_low = market_data.get('low_24h', {}).get('usd')
            except Exception as e:
                logging.warning(f"Error fetching CoinGecko data for {ticker}: {str(e)}")
        
        # Get historical data for chart
        history = []
        if is_crypto:
            # For crypto, use a different endpoint with a longer timeframe
            candles_url = f"https://finnhub.io/api/v1/crypto/candle?symbol=BINANCE:{crypto_symbol}USDT&resolution=D&from={int(pd.Timestamp.now().timestamp()) - 30*24*60*60}&to={int(pd.Timestamp.now().timestamp())}&token={FINNHUB_API_KEY}"
            candles_response = requests.get(candles_url)
            candles_data = candles_response.json()
        else:
            candles_url = f"https://finnhub.io/api/v1/stock/candle?symbol={ticker}&resolution=D&from={int(pd.Timestamp.now().timestamp()) - 30*24*60*60}&to={int(pd.Timestamp.now().timestamp())}&token={FINNHUB_API_KEY}"
            candles_response = requests.get(candles_url)
            candles_data = candles_response.json()
        
        if candles_data.get('s') == 'ok':
            timestamps = candles_data.get('t', [])
            close_prices = candles_data.get('c', [])
            
            for i in range(len(timestamps)):
                history.append({
                    'date': pd.Timestamp(timestamps[i], unit='s').strftime('%Y-%m-%d'),
                    'price': close_prices[i]
                })
        else:
            logging.warning(f"Could not fetch historical data for {ticker}")
        
        # If target price is not available, predict it
        if target_price is None or target_price == 0:
            target_price = predict_target_price(current_price, history, pe_ratio, daily_change)
            logging.info(f"Generated predicted target price for {ticker}: ${target_price}")
        
        # Generate recommendation
        if target_price is not None and current_price > 0:
            potential_change = ((target_price - current_price) / current_price) * 100
        else:
            potential_change = 0
            
        buy_recommendation = generate_recommendation(
            current_price, 
            target_price, 
            metrics.get('recommendationMean', 3) if not is_crypto else 3,  # Default to neutral for crypto
            daily_change,
            pe_ratio,
            fifty_two_week_high,
            fifty_two_week_low
        )
        
        # Format data for display
        formatted = {
            'current_price': format_currency(current_price),
            'daily_change': f"{daily_change:.2f}%",
            'market_cap': format_large_number(market_cap),
            'pe_ratio': f"{pe_ratio:.2f}" if pe_ratio else "N/A",
            'dividend_yield': f"{dividend_yield:.2f}%" if dividend_yield else "N/A",
            'fifty_two_week_high': format_currency(fifty_two_week_high) if fifty_two_week_high else "N/A",
            'fifty_two_week_low': format_currency(fifty_two_week_low) if fifty_two_week_low else "N/A",
            'target_price': format_currency(target_price) if target_price else "N/A",
            'potential_change': f"{potential_change:.2f}%" if target_price else "N/A"
        }
        
        # Construct the stock data object
        stock_data = {
            'ticker': ticker,
            'company_name': company_name,
            'sector': sector,
            'price': current_price,
            'daily_change': daily_change,
            'market_cap': market_cap,
            'pe_ratio': pe_ratio,
            'dividend_yield': dividend_yield,
            'fifty_two_week_high': fifty_two_week_high,
            'fifty_two_week_low': fifty_two_week_low,
            'target_price': target_price,
            'potential_change': potential_change,
            'buy_recommendation': buy_recommendation,
            'history': history,
            'formatted': formatted
        }
        
        return stock_data
        
    except Exception as e:
        logging.error(f"Error fetching data for {ticker}: {str(e)}")
        return None

def generate_recommendation(current_price, target_price, analyst_rec, daily_change, pe_ratio, high_52w, low_52w):
    """Generate a buy/sell recommendation based on multiple factors."""
    reasons = []
    
    # Initialize score (1-5 scale, where 1 is Strong Buy and 5 is Strong Sell)
    score = 3  # Default to Hold
    
    # Factor 1: Analyst recommendations (Finnhub uses 1-5 scale where 1=Strong Buy, 5=Strong Sell)
    if analyst_rec is not None:
        if analyst_rec < 2:  # Strong Buy to Buy
            score -= 0.8
            reasons.append(f"Analysts recommend buying (rating: {analyst_rec:.1f}/5)")
        elif analyst_rec < 2.5:  # Buy to Hold
            score -= 0.4
            reasons.append(f"Analysts are somewhat positive (rating: {analyst_rec:.1f}/5)")
        elif analyst_rec > 4:  # Strong Sell
            score += 0.8
            reasons.append(f"Analysts recommend selling (rating: {analyst_rec:.1f}/5)")
        elif analyst_rec > 3.5:  # Sell
            score += 0.4
            reasons.append(f"Analysts are somewhat negative (rating: {analyst_rec:.1f}/5)")
    
    # Factor 2: Target price vs current price
    if target_price is not None and current_price > 0:
        potential_upside = ((target_price - current_price) / current_price) * 100
        if potential_upside > 20:
            score -= 0.7
            reasons.append(f"High upside potential: {potential_upside:.1f}% to target price")
        elif potential_upside > 10:
            score -= 0.4
            reasons.append(f"Good upside potential: {potential_upside:.1f}% to target price")
        elif potential_upside < -15:
            score += 0.7
            reasons.append(f"Significant downside risk: {potential_upside:.1f}% to target price")
        elif potential_upside < -5:
            score += 0.4
            reasons.append(f"Some downside risk: {potential_upside:.1f}% to target price")
        else:
            reasons.append(f"Target price suggests {potential_upside:.1f}% change")
    
    # Factor 3: Price momentum (daily change)
    if daily_change > 5:
        score += 0.2  # Might be overbought
        reasons.append(f"Stock is up {daily_change:.1f}% today (potential momentum)")
    elif daily_change < -5:
        score -= 0.2  # Might be oversold
        reasons.append(f"Stock is down {daily_change:.1f}% today (potential value opportunity)")
    
    # Factor 4: 52-week range
    if high_52w is not None and low_52w is not None and current_price > 0:
        range_position = (current_price - low_52w) / (high_52w - low_52w) if (high_52w - low_52w) > 0 else 0.5
        if range_position < 0.2:
            score -= 0.5
            reasons.append(f"Stock is near its 52-week low (potential value)")
        elif range_position > 0.8:
            score += 0.5
            reasons.append(f"Stock is near its 52-week high (potential overvaluation)")
        else:
            reasons.append(f"Stock is trading at {range_position*100:.1f}% of its 52-week range")
    
    # Factor 5: P/E ratio
    if pe_ratio is not None and pe_ratio > 0:
        if pe_ratio > 50:
            score += 0.4
            reasons.append(f"High P/E ratio of {pe_ratio:.1f} (potentially overvalued)")
        elif pe_ratio < 15 and pe_ratio > 0:
            score -= 0.4
            reasons.append(f"Low P/E ratio of {pe_ratio:.1f} (potentially undervalued)")
        else:
            reasons.append(f"P/E ratio of {pe_ratio:.1f} is within normal range")
    
    # Determine final recommendation
    recommendation = "Hold"
    if score <= 1.8:
        recommendation = "Strong Buy"
    elif score <= 2.5:
        recommendation = "Buy"
    elif score >= 4.2:
        recommendation = "Strong Sell"
    elif score >= 3.5:
        recommendation = "Sell"
    
    # If we don't have enough reasons, add a generic one
    if not reasons:
        reasons.append("Based on overall market analysis")
    
    # Limit to top 3 most significant reasons
    reasons = reasons[:3]
    
    return {
        "recommendation": recommendation,
        "reasons": reasons
    }

def calculate_stock_profit(ticker, allotment, final_price, sell_commission, 
                         initial_price, buy_commission, capital_gain_tax_rate):
    """Calculate stock profit and related metrics."""
    # Calculate proceeds
    proceeds = allotment * final_price
    
    # Calculate total purchase price
    total_purchase_price = allotment * initial_price
    
    # Calculate capital gain before tax
    capital_gain = proceeds - total_purchase_price - buy_commission - sell_commission
    
    # Calculate tax on capital gain
    tax = (capital_gain * capital_gain_tax_rate / 100) if capital_gain > 0 else 0
    
    # Calculate total cost
    total_cost = total_purchase_price + buy_commission + sell_commission + tax
    
    # Calculate net profit
    net_profit = proceeds - total_cost
    
    # Calculate ROI
    roi = (net_profit / total_cost) * 100 if total_cost > 0 else 0
    
    # Calculate break even price
    break_even = (total_purchase_price + buy_commission + sell_commission) / allotment
    
    # Calculate days to break even (assuming 7% annual market return)
    annual_market_return = 0.07
    daily_market_return = annual_market_return / 365
    
    if net_profit < 0 and initial_price > 0:
        # Calculate how many days it would take to break even at 7% annual return
        days_to_recover = np.log(total_cost / total_purchase_price) / np.log(1 + daily_market_return)
        days_to_recover = round(days_to_recover)
    else:
        days_to_recover = 0

    return {
        'ticker': ticker,
        'allotment': allotment,
        'final_price': final_price,
        'initial_price': initial_price,
        'proceeds': proceeds,
        'total_cost': total_cost,
        'purchase_price': total_purchase_price,
        'buy_commission': buy_commission,
        'sell_commission': sell_commission,
        'capital_gain': capital_gain,
        'tax': tax,
        'net_profit': net_profit,
        'roi': roi,
        'break_even': break_even,
        'days_to_recover': days_to_recover
    }

def format_currency(amount):
    """Format amount as currency."""
    return f"${amount:,.2f}"

def format_large_number(num):
    """Format large numbers with K, M, B suffixes."""
    if num >= 1_000_000_000:
        return f"${num/1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"${num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"${num/1_000:.2f}K"
    else:
        return f"${num:.2f}"

@app.route('/')
def home():
    """Render the stock tracker page."""
    return render_template('index.html')

@app.route('/calculator')
def calculator():
    """Render the profit calculator page."""
    return render_template('calculator.html')

@app.route('/add_stock', methods=['GET'])
def add_stock():
    """Add a stock to the tracking list."""
    global stocks_data
    
    try:
        ticker = request.args.get('ticker', '').strip().upper()
        
        if not ticker:
            return jsonify({'error': 'No ticker symbol provided'}), 400
            
        # Check if we're already tracking 5 stocks
        if len(stocks_data) >= 5:
            return jsonify({'error': 'Maximum of 5 stocks can be tracked. Please remove some stocks first.'}), 400
            
        # Check if stock is already being tracked
        for stock in stocks_data:
            if stock['ticker'] == ticker:
                return jsonify({'error': f'{ticker} is already being tracked'}), 400
                
        # Get stock data
        stock_data = get_stock_data(ticker)
        
        if not stock_data:
            return jsonify({'error': f'Could not fetch data for {ticker}. Please verify the ticker symbol or check if the Finnhub API key is valid.'}), 400
            
        # Add to tracking list
        stocks_data.append(stock_data)
        
        # Return the stock data for immediate display
        return jsonify(stock_data)
        
    except Exception as e:
        logging.error(f"Error in add_stock: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_stocks')
def get_stocks():
    """Get all tracked stocks with updated data."""
    global stocks_data
    
    try:
        # If no stocks are being tracked, return empty list
        if not stocks_data:
            return jsonify({
                'stocks': [],
                'portfolio': {
                    'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            })
            
        # Update data for all tracked stocks
        updated_stocks = []
        for stock in stocks_data:
            ticker = stock['ticker']
            updated_data = get_stock_data(ticker)
            
            if updated_data:
                updated_stocks.append(updated_data)
            else:
                # If we couldn't update, keep the old data
                logging.warning(f"Could not update data for {ticker}, using cached data")
                updated_stocks.append(stock)
                
        # Replace the global list with updated data
        stocks_data = updated_stocks
        
        return jsonify({
            'stocks': stocks_data,
            'portfolio': {
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        })
        
    except Exception as e:
        logging.error(f"Error in get_stocks: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/calculate', methods=['POST'])
def calculate():
    """API endpoint to calculate stock profit."""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['ticker', 'allotment', 'final_price', 'sell_commission', 
                          'initial_price', 'buy_commission', 'capital_gain_tax_rate']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f"Missing required field: {field}"}), 400
        
        # Calculate profit
        result = calculate_stock_profit(
            data['ticker'],
            float(data['allotment']),
            float(data['final_price']),
            float(data['sell_commission']),
            float(data['initial_price']),
            float(data['buy_commission']),
            float(data['capital_gain_tax_rate'])
        )
        
        # Format values for display
        result['formatted'] = {
            'proceeds': format_currency(result['proceeds']),
            'total_cost': format_currency(result['total_cost']),
            'purchase_price': format_currency(result['purchase_price']),
            'buy_commission': format_currency(result['buy_commission']),
            'sell_commission': format_currency(result['sell_commission']),
            'tax': format_currency(result['tax']),
            'capital_gain': format_currency(result['capital_gain']),
            'net_profit': format_currency(result['net_profit']),
            'roi': f"{result['roi']:.2f}%",
            'break_even': format_currency(result['break_even']),
            'days_to_recover': f"{result['days_to_recover']} days" if result['days_to_recover'] > 0 else "N/A"
        }
        
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error in calculate: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/test')
def test_api():
    """Test endpoint to verify Finnhub API is working."""
    try:
        # Test with a well-known stock
        test_ticker = 'AAPL'
        stock_data = get_stock_data(test_ticker)
        
        if stock_data and stock_data['price'] > 0:
            return jsonify({
                'success': True,
                'message': f"API is working. {test_ticker} price: {format_currency(stock_data['price'])}",
                'data': {
                    'ticker': test_ticker,
                    'price': stock_data['price'],
                    'company_name': stock_data['company_name'],
                    'history_points': len(stock_data['history'])
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': f"API returned data but price is zero or missing for {test_ticker}",
                'data': stock_data
            }), 500
    except Exception as e:
        logging.error(f"API test failed: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"API test failed: {str(e)}",
            'error': str(e)
        }), 500

@app.route('/clear_stocks', methods=['POST'])
def clear_stocks():
    """Clear all tracked stocks."""
    global stocks_data
    
    try:
        logging.debug(f"Clearing {len(stocks_data)} stocks")
        stocks_data.clear()
        logging.info("All stocks cleared")
        return jsonify({
            'success': True,
            'message': 'All stocks cleared'
        })
    except Exception as e:
        logging.error(f"Error clearing stocks: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/debug_api')
def debug_api():
    """Debug endpoint to test the Finnhub API directly."""
    try:
        # Test with a well-known stock
        ticker = "AAPL"
        
        # Test quote endpoint
        quote_url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_API_KEY}"
        quote_response = requests.get(quote_url)
        quote_data = quote_response.json()
        
        # Test company profile endpoint
        profile_url = f"https://finnhub.io/api/v1/stock/profile2?symbol={ticker}&token={FINNHUB_API_KEY}"
        profile_response = requests.get(profile_url)
        profile_data = profile_response.json()
        
        # Test metrics endpoint
        metrics_url = f"https://finnhub.io/api/v1/stock/metric?symbol={ticker}&metric=all&token={FINNHUB_API_KEY}"
        metrics_response = requests.get(metrics_url)
        metrics_data = metrics_response.json()
        
        # Test candles endpoint
        candles_url = f"https://finnhub.io/api/v1/stock/candle?symbol={ticker}&resolution=D&from={int(pd.Timestamp.now().timestamp()) - 30*24*60*60}&to={int(pd.Timestamp.now().timestamp())}&token={FINNHUB_API_KEY}"
        candles_response = requests.get(candles_url)
        candles_data = candles_response.json()
        
        return jsonify({
            'status': 'success',
            'quote': quote_data,
            'profile': profile_data,
            'metrics': metrics_data,
            'candles': candles_data
        })
    except Exception as e:
        logging.error(f"Error in debug_api: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/test')
def test():
    """Simple test endpoint to verify the server is working."""
    return jsonify({
        'status': 'success',
        'message': 'Server is working correctly'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 