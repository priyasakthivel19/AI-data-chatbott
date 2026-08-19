import pandas as pd
import numpy as np
from scipy import stats


def descriptive_stats(df):
    """Full statistics summary - Excel 'Data Analysis' madhiri"""
    numeric_df = df.select_dtypes(include='number')
    if numeric_df.empty:
        return None

    summary = pd.DataFrame({
        "Mean": numeric_df.mean(),
        "Median": numeric_df.median(),
        "Std Dev": numeric_df.std(),
        "Min": numeric_df.min(),
        "Max": numeric_df.max(),
        "Variance": numeric_df.var(),
        "Skewness": numeric_df.skew(),
        "Range": numeric_df.max() - numeric_df.min()
    })
    return summary.round(2)


def correlation_analysis(df):
    """Correlation matrix - relationships between columns"""
    numeric_df = df.select_dtypes(include='number')
    if numeric_df.shape[1] < 2:
        return None
    return numeric_df.corr().round(2)


def detect_outliers(df, column):
    """IQR method use panni outliers kandupidikka"""
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    outliers = df[(df[column] < lower) | (df[column] > upper)]
    return outliers, lower, upper


def linear_trend_forecast(df, x_col, y_col, future_periods=5):
    """Simple linear regression - future trend predict panna"""
    from sklearn.linear_model import LinearRegression

    data = df[[x_col, y_col]].dropna() if isinstance(x_col, str) else df[[y_col]].dropna()

    if data.shape[0] < 2:
        return None, None

    X = np.arange(len(data)).reshape(-1, 1)
    y = data[y_col].values

    model = LinearRegression()
    model.fit(X, y)

    future_X = np.arange(len(data), len(data) + future_periods).reshape(-1, 1)
    predictions = model.predict(future_X)

    return predictions, model.coef_[0]