import utils 

def main():
    tickers = utils.get_valid_ticker()
    start_date, end_date = utils.get_analysis_dates()

    print("Tickers:", tickers)
    print("Start date:", start_date.date())
    print("End date:", end_date.date())

if __name__ == "__main__":
    main()