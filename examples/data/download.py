import yfinance as yf

# ticker_list = ['VTI', 'TLT', 'IEI', 'GLD', 'GSG', 'SPY', 'AGG']
ticker_list = ['SPY', 'AGG'] #XLB', 'XLC', 'XLE', 'XLF', 'XLI', 'XLK', 'XLP', 'XLU', 'XLV', 'XLY']
start_date = "1990-01-01"
end_date = "2021-01-01"

for ticker in ticker_list:
    df = yf.download(ticker, start_date, end_date)
    df.to_csv(ticker+".csv", sep=',', header=True, index=True)

