#!/usr/bin/env python3

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
    # At break even: allotment * x - (allotment * initial_price + buy_commission + sell_commission) = 0
    # where x is the break even price
    break_even = (total_purchase_price + buy_commission + sell_commission) / allotment
    
    return {
        'proceeds': proceeds,
        'total_cost': total_cost,
        'purchase_price': total_purchase_price,
        'buy_commission': buy_commission,
        'sell_commission': sell_commission,
        'tax': tax,
        'net_profit': net_profit,
        'roi': roi,
        'break_even': break_even
    }

def format_currency(amount):
    """Format amount as currency."""
    return f"${amount:,.2f}"

def main():
    print("\nStock Profit Calculator")
    print("=====================\n")
    
    # Get user inputs
    ticker = input("Ticker Symbol: ").strip().upper()
    allotment = int(input("Allotment: "))
    final_price = float(input("Final Share Price: "))
    sell_commission = float(input("Sell Commission: "))
    initial_price = float(input("Initial Share Price: "))
    buy_commission = float(input("Buy Commission: "))
    capital_gain_tax_rate = float(input("Capital Gain Tax Rate (%): "))
    
    # Calculate results
    results = calculate_stock_profit(
        ticker, allotment, final_price, sell_commission,
        initial_price, buy_commission, capital_gain_tax_rate
    )
    
    # Display results
    print("\nPROFIT REPORT:")
    print("============\n")
    
    print("Proceeds")
    print(format_currency(results['proceeds']))
    print()
    
    print("Cost")
    print(format_currency(results['total_cost']))
    print()
    
    print("Cost details:")
    print(f"Total Purchase Price")
    print(f"{allotment} × {format_currency(initial_price)} = {format_currency(results['purchase_price'])}")
    print(f"Buy Commission = {format_currency(results['buy_commission'])}")
    print(f"Sell Commission = {format_currency(results['sell_commission'])}")
    print(f"Tax on Capital Gain = {capital_gain_tax_rate}% of {format_currency(results['proceeds'] - results['purchase_price'] - results['buy_commission'] - results['sell_commission'])} = {format_currency(results['tax'])}")
    print()
    
    print("Net Profit")
    print(format_currency(results['net_profit']))
    print()
    
    print("Return on Investment")
    print(f"{results['roi']:.2f}%")
    print()
    
    print("To break even, you should have a final share price of")
    print(format_currency(results['break_even']))

if __name__ == "__main__":
    main() 