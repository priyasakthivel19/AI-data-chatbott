import pandas as pd
import streamlit as st

def load_data(uploaded_file):
    """CSV or Excel file ah load pannum"""
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        return df
    except Exception as e:
        st.error(f"File load panna error: {e}")
        return None

def get_data_summary(df):
    """Dataset basic info kudukkum"""
    summary = {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "column_names": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "missing_values": df.isnull().sum().to_dict(),
        "numeric_columns": df.select_dtypes(include='number').columns.tolist(),
        "categorical_columns": df.select_dtypes(include='object').columns.tolist()
    }
    return summary

def clean_data(df):
    """Basic cleaning - duplicates remove, etc."""
    df = df.drop_duplicates()
    return df