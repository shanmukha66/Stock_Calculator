#!/usr/bin/env python3
import yfinance as yf
from tabulate import tabulate
import time
from datetime import datetime
import os

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_current_stock_price(ticker):
    """
    Get real-time stock price using Yahoo Finance API.
    
    Args:
        ticker (str): Stock symbol
    
    Returns:
        tuple: (price, currency)
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return (info['regularMarketPrice'], info.get('currency', 'USD'))
    except Exception as e:
        print(f"Error fetching price for {ticker}: {e}")
        return None, None

def calculate_stock_profit(ticker, allotment, final_price, sell_commission, 
                         initial_price, buy_commission, capital_gain_tax_rate):
    """
    Calculate stock profit and related metrics.
    
    Args:
        ticker (str): Stock symbol
        allotment (int): Number of shares
        final_price (float): Final share price in dollars
        sell_commission (float): Sell commission in dollars
        initial_price (float): Initial share price in dollars
        buy_commission (float): Buy commission in dollars
        capital_gain_tax_rate (float): Capital gain tax rate in percentage
    
    Returns:
        dict: Dictionary containing all calculated values
    """
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
    roi = (net_profit / total_cost) * 100
    
    # Calculate break even price
    break_even = (total_purchase_price + buy_commission + sell_commission) / allotment
    
    return {
        'ticker': ticker,
        'proceeds': proceeds,
        'total_cost': total_cost,
        'purchase_price': total_purchase_price,
        'buy_commission': buy_commission,
        'sell_commission': sell_commission,
        'tax': tax,
        'net_profit': net_profit,
        'roi': roi,
        'break_even': break_even,
        'final_price': final_price,
        'initial_price': initial_price,
        'allotment': allotment
    }

def format_currency(amount, currency='USD'):
    """Format amount as currency."""
    symbols = {'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥'}
    symbol = symbols.get(currency, '$')
    return f"{symbol}{amount:,.2f}"

def print_live_summary(stocks_data, update_time):
    """Print real-time summary of all stocks."""
    clear_screen()
    print("\nLIVE STOCK PROFIT CALCULATOR")
    print("=========================")
    print(f"Last Update: {update_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    table_data = []
    headers = ["Ticker", "Current Price", "Shares", "Initial Price", "Net Profit", "ROI"]
    
    total_profit = 0
    total_investment = 0
    
    for stock in stocks_data:
        current_price, currency = get_current_stock_price(stock['ticker'])
        if current_price:
            results = calculate_stock_profit(
                stock['ticker'], 
                stock['allotment'],
                current_price,
                stock['sell_commission'],
                stock['initial_price'],
                stock['buy_commission'],
                stock['capital_gain_tax_rate']
            )
            
            table_data.append([
                stock['ticker'],
                format_currency(current_price, currency),
                stock['allotment'],
                format_currency(stock['initial_price'], currency),
                format_currency(results['net_profit'], currency),
                f"{results['roi']:.2f}%"
            ])
            
            total_profit += results['net_profit']
            total_investment += results['total_cost']
    
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    if total_investment > 0:
        portfolio_roi = (total_profit / total_investment) * 100
        print(f"\nPORTFOLIO SUMMARY:")
        print(f"Total Investment: {format_currency(total_investment)}")
        print(f"Total Profit: {format_currency(total_profit)}")
        print(f"Portfolio ROI: {portfolio_roi:.2f}%")
    
    print("\nPress Ctrl+C to exit")

def main():
    print("\nStock Profit Calculator (Live Updates)")
    print("================================\n")
    
    stocks_data = []
    num_stocks = 5
    
    for i in range(num_stocks):
        print(f"\nStock {i+1} of {num_stocks}")
        print("-" * 20)
        
        stock_info = {}
        stock_info['ticker'] = input("Ticker Symbol: ").strip().upper()
        
        while True:
            try:
                stock_info['allotment'] = int(input("Number of shares: "))
                break
            except ValueError:
                print("Please enter a whole number for shares.")
        
        current_price, currency = get_current_stock_price(stock_info['ticker'])
        if current_price:
            print(f"Current market price: {format_currency(current_price, currency)}")
        
        stock_info['initial_price'] = float(input("Initial Share Price: "))
        stock_info['sell_commission'] = float(input("Sell Commission: "))
        stock_info['buy_commission'] = float(input("Buy Commission: "))
        stock_info['capital_gain_tax_rate'] = float(input("Capital Gain Tax Rate (%): "))
        
        stocks_data.append(stock_info)
        
        if i < num_stocks - 1:
            continue_input = input("\nPress Enter to add another stock (or 'q' to start monitoring): ")
            if continue_input.lower().strip() == 'q':
                break
    
    print("\nStarting live monitoring of stocks...")
    print("Press Ctrl+C to exit")
    time.sleep(2)
    
    try:
        while True:
            print_live_summary(stocks_data, datetime.now())
            time.sleep(5)  # Update every 5 seconds
    except KeyboardInterrupt:
        print("\nExiting live stock monitoring...")

if __name__ == "__main__":
    main() 