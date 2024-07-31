import numpy as np
import pandas as pd
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import yfinance as yf
from datetime import datetime, timedelta

class LoadModel:
    def __init__(self, ticker, model_path, look_back=120):
        self.ticker = ticker
        self.look_back = look_back
        self.model_path = model_path
        self.model = None
        self.scaler = MinMaxScaler()


    def load_model(self):
        try:
            self.model = load_model(f"{self.model_path}")
            return True
        except Exception as e:
            print(f"An error occurred while loading the model: {e}")
            return False


    def predict(self, recent_data, num_prediction=30):
        try:
            # Assume recent_data is a DataFrame with a 'Close' column and a datetime index
            close_data = recent_data['Close'].values.reshape((-1, 1))
            close_data = self.scaler.fit_transform(close_data)

            prediction_list = close_data[-self.look_back:]

            for _ in range(num_prediction):
                x = prediction_list[-self.look_back:]
                x = x.reshape((1, self.look_back, 1))
                out = self.model.predict(x)[0][0]
                prediction_list = np.append(prediction_list, out)

            prediction_list = prediction_list[self.look_back:]
            forecast = self.scaler.inverse_transform(prediction_list.reshape(-1, 1)).reshape(-1)

            last_date = recent_data.index[-1]
            forecast_dates = pd.date_range(last_date, periods=num_prediction + 1).tolist()[1:]

            df_forecast = pd.DataFrame({'Date': forecast_dates, 'Close': forecast})
            df_forecast['Date'] = pd.to_datetime(df_forecast['Date'])

            return df_forecast

        except Exception as e:
            print(f"An error occurred during prediction: {e}")
            return
        


def get_market_metrics(ticker_names):
    tickers_dict = dict()

    for i in ticker_names:
        try:
            end_date = datetime.today()
            print(i)
            start_date = end_date - timedelta(days=120)  # 4 months before today

            # Fetch stock data using yfinance
            df = yf.download(i, start=start_date, end=end_date)
            stock_data = df.copy()

            # Calculate technical indicators using pandas-ta
            stock_data.ta.macd(append=True)
            stock_data.ta.rsi(append=True)


            financials = yf.Ticker(i).quarterly_financials
            balance_sheet = yf.Ticker(i).quarterly_balance_sheet
            eps_list = financials.loc['Diluted EPS'].tolist()

            balance_sheet = yf.Ticker(i).quarterly_balance_sheet
            book_value = balance_sheet.loc['Tangible Book Value'].tolist()

            balance_sheet = yf.Ticker(i).quarterly_balance_sheet
            # book_value = balance_sheet.loc['Tangible Book Value'].tolist()

            income_list = financials.loc['Net Income'].tolist()
            net_income = next((x for x in income_list if x is not None and pd.notna(x)), None)
            share_price = df.iloc[-1]['Close']
            market_price = df.iloc[-1]['Close']

            # Retrieve the relevant data
            book_value = balance_sheet.loc['Common Stock Equity'].tolist()
            book_value = next((x for x in book_value if x is not None and pd.notna(x)), None)
            num_shares = balance_sheet.loc['Ordinary Shares Number'].tolist()
            num_shares = next((x for x in num_shares if x is not None and pd.notna(x)), None)

            # Calculate Book Value per Share
            book_value_per_share = book_value / num_shares

            # Calculate P/B Ratio
            pb_ratio = market_price / book_value_per_share

            # Calculate EPS
            eps = net_income / num_shares

            # Calculate P/E Ratio
            pe_ratio = market_price / eps


            tickers_dict[i]['rsi'] = stock_data.iloc[-1]['RSI_14']
            tickers_dict[i]['MACD_12_26_9'] = stock_data.iloc[-1]['RSI_14']
            tickers_dict[i]['eps'] = next((x for x in eps_list if x is not None and pd.notna(x)), None)
            # tickers_dict[i]['book_value'] = next((x for x in book_value if x is not None and pd.notna(x)), None)
            tickers_dict[i]['pe_ratio'] = pe_ratio
            tickers_dict[i]['pb_ratio'] = pb_ratio

        except:
            # lst.append(i)s
            print(f"error occured for stock - {i}")


        
# Example usage:
'''
for i in tickers:
    loader = LoadModel(i)
    if loader.load_model(path):
        # Calculate the date range for the past 10 years
        end_date = datetime.now()
        start_date = end_date.replace(year=end_date.year - 10)
        # recent_data = pd.read_csv('/content/drive/MyDrive/data/ADANIGREEN.NS.csv', index_col=0, parse_dates=True)
        stock_data = yf.download(i, start=start_date, end=end_date)
        last_price = stock_data['Close'].iloc[-1]
        forecast_df = loader.predict(stock_data)
        latest_price = forecast_df['Close'].iloc[-1]

        tickers_growth[i] = ((latest_price - last_price) / last_price) * 100
'''