import numpy as np
import streamlit as st
import datetime as dt
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff
from PIL import Image

st.set_page_config(layout="wide")

df_excel_stock = pd.read_csv('US STOCK TICKERS.csv')
df_excel_etf = pd.read_csv('US ETF TICKERS.csv')
df_excel_crypto = pd.read_csv('TOP 100 CRYPTO TICKERS csv.csv')
df_concat = pd.concat((df_excel_stock, df_excel_etf, df_excel_crypto), ignore_index=True)
df_concat.drop(columns=df_concat.iloc[:, 2:], inplace=True, axis=1)
# st.write(df_concat)
default_list1 = ["AAPL | Apple Inc. Common Stock", "DB | Deutsche Bank AG Common Stock",
                 "WMT | Walmart Inc. Common Stock", "TSLA | Tesla Inc. Common Stock"]
default_list2 = ["GLD | SPDR Gold Trust", "SPY | SPDR S&P 500"]
default_list3 = []
# "BTC-USD | Bitcoin"
NUM_TRADING_DAYS = 252
START_CAPITAL = 1000
DEFAULT_START_DATE = dt.date(2015, 1, 1)
compared_stock = "SPY"
sel = []
STOCK_LIST = []

col_header, col_name = st.columns((9, 1))
col_header.write("# Modern Portfolio Theory")
col_header.write("## :chart_with_upwards_trend: Portfolio optimisation using Monte Carlo Simulation ")
# col_name.caption("### ")
# col_name.write("###### By [John](https://www.linkedin.com/in/john-lee-b68a42145/)")
col_header.caption("")
col_header.write("###### By [John](https://www.linkedin.com/in/john-lee-b68a42145/)")
st.write("# ")
with st.container():
    col_text, col_image = st.columns((1.5, 1))
    with col_text:
        st.write("#### In this web application, we will:")
        st.caption("")
        st.write("###### 1. Select a basket of assets.")
        st.write("###### 2. Apply the Markowitz model, analyse various possible portfolios of the given assets.")
        st.write("###### 3. Perform Mean-Variance Analysis and estimate optimal asset ratios that yields:")
        st.caption("")
        st.write("######    • The highest reward at a given level of risk")
        st.write("######    • The least risk at a given level of return")
        st.caption("")
        st.write("See more detailed explanation on Modern Portfolio Theory [here]"
                 "(https://www.investopedia.com/managing-wealth/modern-portfolio-theory-why-its-still-hip/)")
    with col_image:
        image = Image.open('SAMPLE MCS.png')
        st.image(image, caption='Example of Monte Carlo Simulation')

st.warning("###### Disclaimer: All information displayed are for data visualisation purposes only."
           " Nothing contained in this web application should be taken as financial or investment advice!")

def get_dataset():
    # get data from yahoo finance and store it in a pandas dataframe
    stock_data = {}

    for stock in STOCK_LIST:
        stock_data[stock] = yf.Ticker(stock).history(stock, start=START_DATE, end=END_DATE)['Close']

    return pd.DataFrame(stock_data)


def set_new_date_for_available_data():
    # st.write(dataset)
    # get the series of dates where NaN value ends:
    # (series of dates when the stock has just been listed on exchange or equals to start_date variable)
    listing_date = dataset.apply(pd.Series.first_valid_index)

    # debug:
    # st.write(f"Initial listing date:\n{listing_date}")

    global START_DATE
    if listing_date.eq(START_DATE).all():
        pass

    else:
        # get the series containing info containing the latest listed ticker and its latest available date
        latest_listed_stock_date = listing_date.nlargest(1)
        # print(latest_listed_stock_date.index[0])

        # set the new starting date such that there are no NaN values in dataframe
        START_DATE = latest_listed_stock_date[0].date()

        st.warning(f"Yahoo Finance data not available for ticker \"{latest_listed_stock_date.index[0]}\" "
                   f"before {START_DATE},"f" new start date is set to {START_DATE}")

        return latest_listed_stock_date.index[0]


def plot_dataset(dataset_):
    st.write("# ")
    st.subheader("Graph of asset prices/USD against time")
    st.caption("Historical data retrieved from Yahoo Finance")
    st.line_chart(dataset_)
    st.write("***")


def get_normalised_daily_return(dataset_):
    # calculate the normalized daily returns:  r = log(Y(t+1) / Y(t))
    # need to measure all returns in comparable metrics
    log_daily_return_ = np.log(dataset_/dataset_.shift(1))

    # fill nan for distribution graph
    log_daily_return_filled = log_daily_return_.fillna(0)
    fig = ff.create_distplot([log_daily_return_filled[c] for c in log_daily_return_filled.columns],
                             log_daily_return_filled.columns)
    fig.update_layout(
        autosize=False,
        width=800,
        height=295, )
    fig['layout'].update(margin=dict(l=0, r=0, b=0, t=0))

    col_dist, col_text = st.columns(2)

    col_dist.subheader("Distribution graph of logged % daily return ")
    col_dist.caption("**Drag to zoom in!**")
    col_dist.plotly_chart(fig, use_container_width=True)

    col_text.subheader("Graph of logged % daily return against time")
    col_text.caption("**Drag/Scroll to zoom in!**")
    col_text.line_chart(log_daily_return_)

    st.write("##### Note:")
    st.write("+ In Modern Portfolio Theory, it is **assumed that asset returns are normally distributed variables**.")
    st.write("+ However, **actual returns do not follow normal distributions** as their distributions may be skewed"
             " or have heavy tails (high kurtosis) due to frequent price spikes.")

    st.write("***")

    return log_daily_return_[1:]


def annualised_mean_covariance(log_daily_return_):
    # calculating the annual mean and covariance
    mean_return_annual_ = log_daily_return_.mean() * NUM_TRADING_DAYS
    cov_matrix_annual_ = log_daily_return_.cov() * NUM_TRADING_DAYS
    return mean_return_annual_, cov_matrix_annual_


def display_mean_covariance_table():
    col1, col2 = st.columns((1.1, 3))
    with col1:
        st.subheader("Mean of annual returns: ")

        def pct_round(x):
            return ("%.1f" % (x * 100)) + "%"

        mean_return_annual_pct = mean_return_annual.apply(pct_round)
        mean_return_annual_pct.name = "Return"

        st.table(mean_return_annual_pct)

    with col2:

        st.subheader("Covariance matrix of annual returns:")
        st.table(cov_matrix_annual)

    st.write("##### Note:")
    st.write("+ Modern Portfolio Theory **assumes that correlation between assets are fixed over time**,"
             " however,  **in reality**,  they are **dynamic and always changing**.")
    st.write("+ Correlation between a pair of assets will change if a different date range is selected.")

    with st.expander("Why do we need a covariance matrix?"):
        st.write("+ A **covariance matrix  ∑** contains the relationship between all assets, "
                 "it is used to calculate the standard deviation of a portfolio"
                 " which is in turn used to quantify the portfolio's associated risk.")

        st.latex("\sigma_p ^ 2 = W \sum W^T")
        st.latex("portfolio\:standard\:deviation = " + "\sigma_p")
        st.latex("covariance\:matrix = " + "\sum")
        st.latex("weight\:array = " + "W")
        st.latex("transposed\:weight\:array = " + "W^T")
        st.write("")
        st.latex("W=\:" + "[w_1,w_2,w_3,\:...\:,w_i]\:" + ",\;\;where\:w_i\:is\:weight\;of\:the\;i^{th}\;asset")

    for k in mean_return_annual:
        st.write()
        if str(k) == "nan":
            st.error("Ticker may have been delisted.")
            st.stop()
        else:
            pass


def correlation_heatmap(log_daily_return_):
    st.subheader("")
    st.subheader("Correlation matrix of underlying assets")
    correlation_matrix = log_daily_return_.corr()

    fig, ax = plt.subplots()
    sns.heatmap(correlation_matrix, annot=True, cmap=sns.color_palette("Blues", 100), fmt='.2f')

    col_display, text_col = st.columns(2)

    text_col.write("##### Positive vs Negative Correlation:")
    text_col.write("Correlation describes the relationship that exists between two assets and their"
                   " respective price movements.")
    text_col.write("Price movements of a pair of assets can be positively correlated"
                   " when they move up or down in tandem.")
    text_col.write("+ Dark blue squares: A correlation value of 1 means"
                   " two assets have a perfect positive correlation.")
    text_col.write("+ White squares: If each asset seems to move completely independently of the other,"
                   " they could be considered uncorrelated and have a value of 0.")
    text_col.write("+ If one asset moves up while the other goes down, they would have a perfect negative correlation,"
                   " noted by a value of -1.")
    st.write("##### Note:")
    st.write("+ Having assets with **high positive correlation** in a portfolio is unfavourable as they"
             " **will not provide much diversification.**")
    st.write("+ The aim of diversification is to **eliminate fluctuations** in the long term,"
             " **reducing unsystematic risk.**")
    text_col.write("")

    col_display.pyplot(fig)

    st.write("***")


def generate_random_portfolios():
    # generate n sets of random variables, index in array corresponds to the nth random portfolio generated.
    portfolio_mean = []
    portfolio_sd = []
    portfolio_weights = []

    for _ in range(NUM_PORTFOLIOS):
        # generate random weights which sum = 1 for each portfolio:
        w = np.random.random(len(STOCK_LIST))
        w = w / np.sum(w)
        portfolio_weights.append(w)
        # portfolio mean:
        # summation of the product of (weights and mean annual return of individual asset)
        portfolio_mean.append(np.sum(w * mean_return_annual))
        # portfolio standard deviation:
        # square root of ( dot product of transposed weight matrix, (covariance matrix, weight matrix) )
        portfolio_sd.append(np.sqrt(np.dot(w.T, np.dot(cov_matrix_annual, w))))

    return np.array(portfolio_weights), np.array(portfolio_mean), np.array(portfolio_sd)


def calculate_portfolio_max_sharpe_min_risk(p_mean, p_stddev):
    # This is a function that retrieves the statistics array and weight array of the 2 optimal portfolios
    # Create a new dataframe with columns p_mean, p_stddev and p_sharpeRatio:
    df = pd.DataFrame({'p_means': p_mean, 'p_stdDevs': p_stddev})
    df['Sharpe_ratio'] = df['p_means'] / df['p_stdDevs']

    # debug print:
    # print(df)

    # Extracting the dataframe row containing index of portfolio with max sharpe ratio
    df_max_sharpe = df[df['Sharpe_ratio'] == df['Sharpe_ratio'].max()]
    # retrieve the index from single row df_max_sharpe to get corresponding row of the 2D weights array
    index = df_max_sharpe.index
    q = []
    for index in index:
        q.append(index)
    b = q[0]
    max_sharpe_weights = p_weights[int(b)]

    # Extracting the dataframe row containing index of portfolio with lowest risk (SD)
    df_min_risk = df[df['p_stdDevs'] == df['p_stdDevs'].min()]
    # retrieve the index from single row df_min_risk to get corresponding row of the 2D weights array
    index = df_min_risk.index
    c = []
    for index in index:
        c.append(index)
    d = c[0]
    min_risk_weights = p_weights[int(d)]

    return max_sharpe_weights, np.array(df_max_sharpe), min_risk_weights, np.array(df_min_risk)


def scatter_plot_optimal_portfolios(p_mean, p_sd):
    st.subheader('Monte Carlo Simulation')
    st.set_option('deprecation.showPyplotGlobalUse', False)
    # Function the does a scatter plot of the randomly generated portfolios, including the two optimal portfolios.
    # x-axis = portfolio SD and y-axis = portfolio mean
    plt.figure(figsize=(10, 6))
    plt.scatter(p_sd, p_mean, c=p_mean/p_sd, cmap='Spectral', marker='o', edgecolors='k')
    plt.style.use('seaborn')
    plt.grid(True)
    plt.xlabel("Expected Volatility (SD)")
    plt.ylabel("Expected Return (Mean)")
    plt.colorbar(label='Sharpe Ratio')
    plt.plot(max_sharpe_stats[0][1], max_sharpe_stats[0][0], marker="*", markersize=30, markeredgecolor="black",
             markerfacecolor="gold")
    plt.plot(min_risk_stats[0][1], min_risk_stats[0][0], marker="*", markersize=30, markeredgecolor="black",
             markerfacecolor="violet")

    col_plot, col_word = st.columns(2)

    with col_plot:
        plt.title(f"Scatter plot of {NUM_PORTFOLIOS} randomly generated portfolios with varying ratio of assets")
        st.pyplot()

    with col_word:
        st.write("##### Each dot in the scatter plot graph"
                 " represents a single portfolio with randomly generated asset weights.")

        st.caption("")
        st.write("###### Maximising our returns for a fixed level of risk (volatility):")
        st.write("+ Gold star: Estimate of **optimal portfolio with highest return for a given level of risk**"
                 " (Highest Sharpe Ratio)")
        st.caption("")

        st.write("###### Minimising risk given a fixed return:")
        st.write("+ Purple star: Estimate of **optimal portfolio with minimum risk**")
        st.caption("")

        st.write("The **upper boundary** of the scatter plot contains \"efficient portfolios\""
                 " which make up the **\"Efficient Frontier\"**, where investors can decide if they are willing"
                 " to take on additional risk for higher expected returns.")

    with st.expander("What is Sharpe Ratio?"):
        st.write("Sharpe ratio is the measure of risk-adjusted return of a portfolio. (Risk free rate assumed to be 0)")
        st.write("(Measure of excess portfolio return over the risk-free rate relative to its standard deviation)")
        st.latex(r"Sharpe\:Ratio = \frac{r_p-R_f}{\sigma_p}")
        st.latex("average\:rate\:of\:return=r_p")
        st.latex("risk\:free\:rate=R_f")
        st.latex("portfolio\:standard\:deviation=\sigma_p")

    st.write("##### Note:")
    st.write("+ This \"brute force\" method of solving an optimisation problem is"
             " not ideal, but it provides a good estimate of optimal portfolio ratios. ")

    st.write("***")


def plot_pie_charts(optimal_ratio_max_sharpe_, stock_list_, optimal_ratio_min_risk_):
    col_header1, col_header2 = st.columns(2)

    col_header1.subheader('Portfolio with Max Sharpe Ratio')
    col_header2.subheader('Portfolio with Minimum Risk')

    col_pie1, col_t1, col_pie2, col_t2 = st.columns((3, 1, 3, 1))

    # sort the ticker array and ratio array together in ascending order
    zipped_arrays = zip(optimal_ratio_max_sharpe_, stock_list_)
    sorted_pairs_ascending = sorted(zipped_arrays)

    # create reverse of array:
    sorted_pairs_ascending_reverse = sorted_pairs_ascending[::-1]

    # small ratio between large ratios
    sorted_pairs_between = []
    count = 0
    while count < np.floor(len(sorted_pairs_ascending)):
        sorted_pairs_between.append(sorted_pairs_ascending[count])
        sorted_pairs_between.append(sorted_pairs_ascending_reverse[count])
        count += 1

    # the above while loop creates a new array twice the elements of the input array,
    # need to return original length of the array
    sorted_pairs_between = sorted_pairs_between[:len(sorted_pairs_ascending)]

    # extract the sorted arrays from tuples
    tuples = zip(*sorted_pairs_between)
    optimal_ratio_max_sharpe_, stock_list_sorted1 = [list(t) for t in tuples]
    print(optimal_ratio_max_sharpe_)
    print(stock_list_)

    # pie chart of the portfolio with highest return for a given level of risk
    # col = ['#b7ffdf', '#3adaa2', '#6cd7dc', '#3d85c6', '#b0afe6', '#d8c8e9', '#ffdbe4', '#fcbbbb', '#faa17a',
    #        '#ffb3ba', '#ffdfba', '#ffffba', '#baffc9', '#ffb3ba']
    col = ["#fc9eff", "#d0a3ff", "#a8abff", "#8ae6ff", "#85ffb8", "#aaff75", "#d2ff61", "#edff61", "#ffe46b", "#ff998a",
           "#f822ff", "#8f26ff", "#2930ff", "#14ccff", "#10ff74", "#65ff06", "#b1f600", "#daf600", "#fdcf00", "#ff3314",
           "#fc9eff", "#d0a3ff", "#a8abff", "#8ae6ff", "#85ffb8", "#aaff75", "#d2ff61", "#edff61", "#ffe46b", "#ff998a",
           "#fc9eff", "#d0a3ff", "#a8abff", "#8ae6ff", "#85ffb8", "#aaff75", "#d2ff61", "#edff61", "#ffe46b", "#ff998a"]
    explode_array = []
    for index in range(len(STOCK_LIST)):
        explode_array.append(0.01)

    plt.figure(figsize=(5, 5), dpi=100)
    patches, texts, autotexts = plt.pie(optimal_ratio_max_sharpe_, labels=stock_list_sorted1, normalize=True,
                                        radius=0.6, explode=explode_array, autopct="%0.2f%%", pctdistance=0.8,
                                        wedgeprops={'linewidth': 0, 'edgecolor': 'black'}, colors=col)
    unused_variable = [text.set_color('black') for text in texts]
    unused_variable = [autotext.set_color('black') for autotext in autotexts]
    plt.axis("equal")
    col_pie1.pyplot()

    # display ratio table
    tuples1 = zip(*sorted_pairs_ascending_reverse)
    optimal_ratio_max_sharpe_display, stock_list_display = [list(f) for f in tuples1]
    optimal_ratio_max_sharpe_display = [("%.2f" % (item * 100)) + "%" for item in optimal_ratio_max_sharpe_display]
    display_max_sharpe_df = pd.DataFrame({'Asset': stock_list_display, "Weight": optimal_ratio_max_sharpe_display})
    display_max_sharpe_df.index = range(1, len(display_max_sharpe_df) + 1)
    col_t1.table(display_max_sharpe_df)

    # ---------- Second Pie Chart:--------------- ----------------------------------------------------------------------

    # sort the ticker array and ratio array together in ascending order
    zipped_arrays = zip(optimal_ratio_min_risk_, stock_list_)
    sorted_pairs_ascending = sorted(zipped_arrays)

    # create reverse of array:
    sorted_pairs_ascending_reverse = sorted_pairs_ascending[::-1]

    # small ratio between large ratios
    sorted_pairs_between = []
    count = 0
    while count < np.floor(len(sorted_pairs_ascending)):
        sorted_pairs_between.append(sorted_pairs_ascending[count])
        sorted_pairs_between.append(sorted_pairs_ascending_reverse[count])
        count += 1

    # the above while loop creates a new array twice the elements of the input array,
    # need to return original length of the array
    sorted_pairs_between = sorted_pairs_between[:len(sorted_pairs_ascending)]

    # extract the sorted arrays from tuples
    tuples = zip(*sorted_pairs_between)
    optimal_ratio_min_risk_, stock_list_sorted2 = [list(t) for t in tuples]
    print(optimal_ratio_min_risk_)
    print(stock_list_)

    # Find the colour array that corresponds to sorted_stick_list1
    col_corr_array = col[0:len(STOCK_LIST)]
    # st.write(col_corr_array)
    colour_dict = dict(zip(stock_list_sorted1, col_corr_array))
    # st.write(colour_dict)
    sorted_colour_array = []
    for stock in stock_list_sorted2:
        sorted_colour_array.append(colour_dict[stock])
    # st.write(sorted_colour_array)

    explode_array = []
    for index in range(len(STOCK_LIST)):
        explode_array.append(0.01)

    plt.figure(figsize=(5, 5), dpi=100)
    patches, texts, autotexts = plt.pie(optimal_ratio_min_risk_, labels=stock_list_sorted2, normalize=True,
                                        radius=0.6, explode=explode_array, autopct="%0.2f%%", pctdistance=0.8,
                                        wedgeprops={'linewidth': 0, 'edgecolor': 'black'}, colors=sorted_colour_array)

    unused_variable = [text.set_color('black') for text in texts]
    unused_variable = [autotext.set_color('black') for autotext in autotexts]
    plt.axis("equal")
    col_pie2.pyplot()

    # display ratio table
    tuples1 = zip(*sorted_pairs_ascending_reverse)
    optimal_ratio_min_risk_display, stock_list_display = [list(f) for f in tuples1]
    optimal_ratio_min_risk_display = [("%.2f" % (items * 100)) + "%" for items in optimal_ratio_min_risk_display]
    display_min_risk_df = pd.DataFrame({'Asset': stock_list_display, "Weight": optimal_ratio_min_risk_display})
    display_min_risk_df.index = range(1, len(display_min_risk_df) + 1)
    col_t2.table(display_min_risk_df)

    col5, col6, col7, col10, col11, col12 = st.columns((1.3, 1.1, 1, 1.3, 1.1, 1,))

    col5.metric("Annual Expected Return\n(Mean)", f"{round(max_sharpe_stats.reshape(-1)[0] * 100, 2)} %")
    col6.metric("Annual Volatility\n(Std Dev)", f"{round(max_sharpe_stats.reshape(-1)[1] * 100, 2)} %")
    col7.metric("Sharpe Ratio", round(max_sharpe_stats.reshape(-1)[2], 2))
    col10.metric("Annual Expected Return\n(Mean)", f"{round(min_risk_stats.reshape(-1)[0] * 100, 2)} %")
    col11.metric("Annual Volatility\n(Std Dev)", f"{round(min_risk_stats.reshape(-1)[1] * 100, 2)} %")
    col12.metric("Sharpe Ratio", round(min_risk_stats.reshape(-1)[2], 2))

    if NUM_PORTFOLIOS <= 100000:
        st.warning("Number of random portfolios may not enough to estimate optimal asset ratios accurately. For more "
                   "exact ratios, increase the slider and re-submit the form again.")
    st.write("***")


# COMPOUNDING RETURNS / EQUITY CURVE PLOTTING FUNCTIONS
# ----------------------------------------------------------------------------------------------------------------------

def download_data(start_date, end_date, stock_list):
    # get data from yahoo finance
    stock_data_ = {}

    for stock in stock_list:
        # closing prices
        ticker = yf.Ticker(stock)
        stock_data_[stock] = ticker.history(start=start_date, end=end_date)['Close']

    stock_dataframe  = pd.DataFrame(stock_data_)
    stock_dataframe = stock_dataframe.reindex(pd.date_range(start_date, end_date), fill_value=None)
    # back fill NaN values
    stock_dataframe = stock_dataframe.backfill()

    return stock_dataframe


def calculate_return(data):
    # get % change daily returns
    daily_return = data / data.shift(1)
    return daily_return[1:].to_numpy()


def weighted_capital(weights):
    # divide starting capital by portfolio weights
    weighted_starting_capital = []
    for w in weights:
        weighted_starting_capital.append(START_CAPITAL * w)
    return np.array(weighted_starting_capital)


def portfolio_df(wsc, dr, stock_data, stock_list):
    # create an array containing the price of assets owned, compounded over time:
    array = []

    g = 0
    while g < len(wsc):
        i = 0
        x = wsc[g]
        while i < len(dr):
            x = x * dr[i][g]
            array.append(x)
            i += 1
        g += 1

    array = np.array(array)

    # shape the array into 2D array
    array = array.reshape(len(wsc), len(dr))

    # make the array into a dataframe, transpose it such that the cols are prices of individual assets over time:
    df = pd.DataFrame(array).transpose()

    # insert weighted starting capital at first row of dataframe:
    df = pd.concat([pd.DataFrame(wsc).transpose(), df])

    # insert new column which is the sum of all prices horizontally in a single row (axis = 1):
    df["Portfolio Value"] = df.iloc[:, :].sum(axis=1)

    # taking the date index from stock_data, replace row index of new dataframe:
    df["Date"] = pd.DataFrame(stock_data.index)
    df.set_index("Date", inplace=True)
    print(df)

    # create dataframe with only the portfolio data:
    df = df.drop([i for i in range(len(stock_list))], axis=1)
    return df


def benchmark_portfolio(start_date, end_date):
    # get data from yahoo finance and store it in a pandas dataframe
    compared_data = yf.download(compared_stock, start_date, end_date)['Close']
    # fill the weekend / holiday dates that are skipped with NaN values
    compared_data = compared_data.reindex(pd.date_range(start_date, end_date), fill_value=None)
    # back fill NaN values
    compared_data = compared_data.backfill()


    # get % change of daily returns
    compared_data_return = compared_data / compared_data.shift(1)
    compared_data_return = compared_data_return[1:]

    print(compared_data_return)
    print(type(compared_data_return))

    capital = START_CAPITAL
    capital_array = [START_CAPITAL]
    for i in compared_data_return[:]:
        capital = capital * i
        capital_array.append(capital)

    print(pd.DataFrame(capital_array))
    capital_dataframe = pd.DataFrame(capital_array)

    #
    # # taking the date index from compared_data, replace row index of capital_dataframe:
    # capital_dataframe["Date"] = pd.DataFrame(compared_data.index)
    # capital_dataframe.set_index("Date", inplace=True)
    # print(capital_dataframe)
    #
    # capital_dataframe.columns = [compared_stock]
    # print(capital_dataframe)

    return capital_dataframe


def plot_equity_curve(start_date, end_date, stock_list, w_max_sharpe, w_min_risk):

    stock_data = download_data(start_date, end_date, stock_list)
    print(stock_data)

    daily_returns = calculate_return(stock_data)
    print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    print(daily_returns)
    daily_returns[np.isnan(daily_returns)] = 1
    print(daily_returns)

    weights = w_max_sharpe
    weighted_start_capital_max_sharpe = weighted_capital(weights)
    weights = w_min_risk
    weighted_start_capital_min_risk = weighted_capital(weights)
    print(weighted_start_capital_max_sharpe)
    print(weighted_start_capital_min_risk)

    weighted_start_capital = weighted_start_capital_max_sharpe
    portfolio_df_max_sharpe = portfolio_df(weighted_start_capital, daily_returns, stock_data, stock_list)
    print(portfolio_df_max_sharpe)

    weighted_start_capital = weighted_start_capital_min_risk
    portfolio_df_min_risk = portfolio_df(weighted_start_capital, daily_returns, stock_data, stock_list)
    print(portfolio_df_min_risk)

    portfolio_df_benchmark = benchmark_portfolio(start_date, end_date)

    # debug:
    # a,b,c,d,e = st.columns((1,1,1,1,1))
    # a.write(portfolio_df_benchmark.values.reshape(-1))
    # b.write(portfolio_df_max_sharpe.to_numpy().reshape(-1))
    # c.write(portfolio_df_min_risk.to_numpy().reshape(-1))
    # d.write(portfolio_df_min_risk.to_numpy().reshape(-1))
    # e.write(list(portfolio_df_max_sharpe.index.values.reshape(-1)))

    data = {'100% Snp 500 portfolio': portfolio_df_benchmark.iloc[:, :].values.reshape(-1),
            'Max Sharpe Ratio Portfolio': portfolio_df_max_sharpe.to_numpy().reshape(-1),
            'Min Risk Portfolio': portfolio_df_min_risk.to_numpy().reshape(-1)}

    df = pd.DataFrame(data, index=list(portfolio_df_max_sharpe.index.values.reshape(-1)))
    # st.write(df)

    pd.options.plotting.backend = "plotly"

    # normal graph
    fig = df.plot(template="seaborn", labels=dict(index="Date", value="Equity / USD", variable="Portfolios"))
    fig['data'][0]['line']['color'] = "#000000"
    fig['data'][1]['line']['color'] = "#A020F0"
    fig['data'][2]['line']['color'] = "#FFD700"
    fig.update_xaxes(showgrid=True, linecolor='black')
    fig.update_yaxes(showgrid=True, linecolor='black')
    fig.update_yaxes(tickprefix="$ ")
    fig.update_layout(
        autosize=False,
        width=1100,
        height=400)
    fig['layout'].update(margin=dict(l=0, r=0, b=0, t=0))
    st.subheader("Graph of equity curves (Lump sum starting capital = 1000 US$)")
    st.plotly_chart(fig)

    # logged graph
    fig = df.plot(template="seaborn", log_y=True,
                  labels=dict(index="Date", value="Equity / USD", variable="Portfolios"))
    fig['data'][0]['line']['color'] = "#000000"
    fig['data'][1]['line']['color'] = "#A020F0"
    fig['data'][2]['line']['color'] = "#FFD700"
    fig.update_xaxes(showgrid=True, linecolor='black')
    fig.update_yaxes(showgrid=True, linecolor='black')
    fig.update_yaxes(tickprefix="$ ")
    fig.update_layout(
        autosize=False,
        width=1100,
        height=400)
    fig['layout'].update(margin=dict(l=0, r=0, b=0, t=0))
    st.subheader("Graph of equity curves, logarithmic scale (Lump sum starting capital = 1000 US$)")
    st.plotly_chart(fig)


# ----------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # UI stuff, user input global variables:
    with st.form(key='form1'):
        sel = []
        st.subheader("1. Select Stocks / ETF(gold, bonds, stocks) / Cryptocurrencies:")
        stock_input = st.multiselect("Select Stocks (NYSE/NASDAQ/AMEX)", df_excel_stock["Ticker + Name"], key=1,
                                     default=default_list1)
        etf_input = st.multiselect("Select ETFs (NYSE/NASDAQ/AMEX)", df_excel_etf["Ticker + Name"], key=2,
                                   default=default_list2)
        crypto_input = st.multiselect("Select Cryptocurrencies (Top 100 only)", df_excel_crypto["Ticker + Name"], key=3,
                                      default=default_list3)

        def append_ticker(x):
            # maybe there is a better way to avoid error that happens when multiselect widget is left empty?
            try:
                for j in pd.DataFrame(x)[0]:
                    sel.append(j)
            except KeyError:
                pass

        append_ticker(stock_input)
        append_ticker(etf_input)
        append_ticker(crypto_input)

        st.write("###")
        st.subheader(f"2. Select date range of historical data (Default from {DEFAULT_START_DATE} - Today's date)")
        c1, c2 = st.columns(2)

        with c1:
            START_DATE = st.date_input("Start date", DEFAULT_START_DATE)
        with c2:
            END_DATE = st.date_input("End date", dt.date.today(), max_value=dt.date.today())

        st.write("###")
        st.subheader("3. Select number of randomly generated portfolios:")
        NUM_PORTFOLIOS = st.slider(" ", min_value=10000, max_value=500000, value=50000)

        st.write("+ 50000 for faster results, increase slider to improve estimate of optimal asset weights")

        submitted = st.form_submit_button(label='Enter')

    if submitted:
        ticker_index = []

        for i in sel:
            a = df_concat.loc[df_concat["Ticker + Name"] == str(i)]
            ticker_index.append(str(a.index[0]))
        for i in ticker_index:
            STOCK_LIST.append(df_concat.iloc[int(i), 0])

        if len(STOCK_LIST) <= 1:
            st.error("Please enter 2 or more assets!")
            st.stop()
        else:
            pass
        # debug:
        # st.write(STOCK_LIST)
    else:
        st.stop()

    dataset = get_dataset()

    newest_ticker = set_new_date_for_available_data()

    dataset_correct_date = get_dataset()

    dataset_final = dataset_correct_date.backfill()

    plot_dataset(dataset_final)

    log_daily_return = get_normalised_daily_return(dataset_final)

    # debug
    # st.write(dataset)

    mean_return_annual, cov_matrix_annual = annualised_mean_covariance(log_daily_return)

    display_mean_covariance_table()

    st.spinner(text='In progress...')

    correlation_heatmap(log_daily_return)

    p_weights, p_means, p_stdDevs = generate_random_portfolios()

    optimal_ratio_max_sharpe, max_sharpe_stats, optimal_ratio_min_risk, min_risk_stats\
        = calculate_portfolio_max_sharpe_min_risk(p_means, p_stdDevs)

    # debug
    # st.write("")
    # st.write(f"Asset ratio that yields highest sharpe ratio is {optimal_ratio_max_sharpe}")
    # st.write(f"Its expected return (mean), volatility (SD) and sharpe ratio are {max_sharpe_stats.reshape(-1)}")
    # st.write("")
    # st.write(f"Asset ratio that yields lowest risk is {optimal_ratio_min_risk}")
    # st.write(f"Its expected return (mean), volatility (SD) and sharpe ratio are {min_risk_stats.reshape(-1)}")
    # st.write("")

    scatter_plot_optimal_portfolios(p_means, p_stdDevs)

    plot_pie_charts(optimal_ratio_max_sharpe, STOCK_LIST, optimal_ratio_min_risk)

    plot_equity_curve(START_DATE, END_DATE, STOCK_LIST, optimal_ratio_max_sharpe, optimal_ratio_min_risk)