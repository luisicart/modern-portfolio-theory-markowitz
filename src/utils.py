#%%
from datetime import datetime
from typing import List, Tuple

#%%
date_format = "%Y-%m-%d"
#%%
def get_valid_ticker(prompt) -> List[str]:

    tickers = []
    terminator = "done" 

    while True:
        ticker = input(prompt).strip()

        if ticker.lower() == terminator:
            break

        if ticker == "":
            print("Empty input is not allowed. Please try again.")
            continue

        if not ticker.isalnum():
            print("Invalid ticker. Use only letters and numbers (e.g., AAPL, PETR4).")
            continue

        tickers.append(ticker.upper())
    
    print("Tickers entered:", tickers)
    return tickers

#%%
def get_valid_date(prompt="Enter a date (YYYY-MM-DD): ") -> datetime.date:
    while True:
        date_str = input(prompt).strip()
        
        try:
            return datetime.strptime(date_str, date_format)
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")

#%%
def get_analysis_dates() -> Tuple[datetime.date, datetime.date]:

    start_date = get_valid_date("Enter the start date (YYYY-MM-DD): ")
    end_date = get_valid_date("Enter the end date (YYYY-MM-DD): ")

    while end_date < start_date:
        print("End date cannot be earlier than start date. Please enter again.")
        end_date = get_valid_date("Enter the end date (YYYY-MM-DD): ")

    print("Start date:", start_date.date())
    print("End date:", end_date.date())

    return start_date, end_date