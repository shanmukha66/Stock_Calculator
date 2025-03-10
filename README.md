# Stock Profit Calculator

A Python program that calculates stock profits, costs, and related metrics based on user inputs. The program now supports real-time stock price fetching and can analyze multiple stocks at once.

## Features

- Real-time stock price fetching using Yahoo Finance API
- Support for analyzing up to 5 stocks in one session
- Calculates proceeds from stock sales
- Computes total costs including:
  - Purchase price
  - Buy commission
  - Sell commission
  - Capital gains tax
- Determines net profit
- Calculates return on investment (ROI)
- Computes break-even price
- Provides summary table for all analyzed stocks
- Calculates portfolio-wide metrics

## Requirements

- Python 3.x
- yfinance>=0.2.36
- tabulate>=0.9.0

## Installation

1. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the program:
```bash
python stock_calculator.py
```

2. For each stock (up to 5 stocks), enter the requested information when prompted:
   - Ticker Symbol
   - Allotment (number of shares)
   - Final Share Price (automatically fetched, with option to enter manually)
   - Sell Commission (in dollars)
   - Initial Share Price (in dollars)
   - Buy Commission (in dollars)
   - Capital Gain Tax Rate (in %)

3. The program will display:
   - Individual profit report for each stock
   - Summary table comparing all stocks
   - Portfolio-wide totals and metrics

## Example Output

```
Stock Profit Calculator
=====================

Stock 1 of 5
--------------------
Ticker Symbol: ADBE
Current market price for ADBE: $110.25
Use this as final price? (y/n): y
...

PROFIT REPORT FOR ADBE:
=====================

[Individual stock report details...]

SUMMARY OF ALL STOCKS:
===================
+--------+------------+-----------+------------+--------+------------+
| Ticker | Proceeds   | Cost      | Net Profit | ROI    | Break Even |
+--------+------------+-----------+------------+--------+------------+
| ADBE   | $11,025.00 | $3,796.25 | $7,228.75  | 190.4% | $25.25     |
+--------+------------+-----------+------------+--------+------------+

PORTFOLIO TOTALS:
Total Proceeds: $11,025.00
Total Cost: $3,796.25
Total Net Profit: $7,228.75
Portfolio ROI: 190.4% 