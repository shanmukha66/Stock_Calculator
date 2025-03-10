# Stock Profit Calculator

A Python program that calculates stock profits, costs, and related metrics based on user inputs.

## Features

- Calculates proceeds from stock sales
- Computes total costs including:
  - Purchase price
  - Buy commission
  - Sell commission
  - Capital gains tax
- Determines net profit
- Calculates return on investment (ROI)
- Computes break-even price

## Requirements

- Python 3.x

## Usage

1. Run the program:
```bash
python stock_calculator.py
```

2. Enter the requested information when prompted:
   - Ticker Symbol
   - Allotment (number of shares)
   - Final Share Price (in dollars)
   - Sell Commission (in dollars)
   - Initial Share Price (in dollars)
   - Buy Commission (in dollars)
   - Capital Gain Tax Rate (in %)

3. The program will display a detailed profit report including:
   - Proceeds
   - Total Cost (with breakdown)
   - Net Profit
   - Return on Investment
   - Break-even Price

## Example Output
[!image]{/output.png}
```
Stock Profit Calculator
=====================

Ticker Symbol: ADBE
Allotment: 100
Final Share Price: 110
Sell Commission: 15
Initial Share Price: 25
Buy Commission: 10
Capital Gain Tax Rate (%): 15

PROFIT REPORT:
============

Proceeds
$11,000.00

Cost
$3,796.25

Cost details:
Total Purchase Price
100 × $25.00 = $2,500.00
Buy Commission = $10.00
Sell Commission = $15.00
Tax on Capital Gain = 15% of $8,475.00 = $1,271.25

Net Profit
$7,203.75

Return on Investment
189.76%

To break even, you should have a final share price of
$25.25 