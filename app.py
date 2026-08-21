import streamlit as st
import pandas as pd
from utils.data_loader import load_data, get_data_summary, clean_data
from utils.query_engine import ask_question
from utils.visualizer import auto_chart, correlation_heatmap, forecast_chart, dashboard_view
from utils.stats_engine import descriptive_stats, correlation_analysis, detect_outliers, linear_trend_forecast
from utils.firebase_config import init_firebase, save_chat_history
from utils.firebase_auth import init_firebase_auth, sign_up, sign_in

st.set_page_config(page_title="AI Data Analytics Chatbot", layout="wide")

# ---- LOGIN / SIGNUP SECTION STARTS HERE ----
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("🔐 AI Data Analytics Chatbot")

    auth = init_firebase_auth()

    login_tab, signup_tab = st.tabs(["Login", "Sign Up"])

    # ---- LOGIN TAB ----
    with login_tab:
        st.subheader("Login with your email")
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", key="login_btn"):
            if login_email and login_password:
                success, result = sign_in(auth, login_email, login_password)
                if success:
                    st.session_state['logged_in'] = True
                    st.session_state['user_email'] = login_email
                    # localId is Firebase's unique ID for this user - used to keep each user's data separate
                    st.session_state['user_id'] = result['localId']
                    st.rerun()
                else:
                    st.error(result)
            else:
                st.warning("Please enter both email and password.")

    # ---- SIGN UP TAB ----
    with signup_tab:
        st.subheader("Create a new account")
        signup_email = st.text_input("Email", key="signup_email")
        signup_password = st.text_input("Password (min 6 characters)", type="password", key="signup_password")
        signup_password_confirm = st.text_input("Confirm Password", type="password", key="signup_password_confirm")

        if st.button("Sign Up", key="signup_btn"):
            if not signup_email or not signup_password:
                st.warning("Please fill in all fields.")
            elif signup_password != signup_password_confirm:
                st.error("Passwords do not match.")
            else:
                success, result = sign_up(auth, signup_email, signup_password)
                if success:
                    st.success("Account created successfully! Please go to the Login tab to sign in.")
                else:
                    st.error(result)

    st.stop()
# ---- LOGIN / SIGNUP SECTION ENDS HERE ----

db = init_firebase()

# ---- LOGOUT BUTTON (sidebar top) ----
with st.sidebar:
    st.write(f"👤 Logged in as: **{st.session_state['user_email']}**")
    if st.button("Logout"):
        st.session_state['logged_in'] = False
        st.session_state.pop('user_id', None)
        st.session_state.pop('user_email', None)
        st.rerun()

st.title("📊 AI Data Analytics Chatbot")
st.markdown("Upload a CSV or Excel file - **Statistics, Dashboard, Forecasting, and Chat**, all in one place!")

with st.sidebar:
    st.header("📁 Upload Data")
    uploaded_file = st.file_uploader("CSV or Excel file", type=["csv", "xlsx", "xls"])

if uploaded_file:
    df = load_data(uploaded_file)

    if df is not None:
        df = clean_data(df)
        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        categorical_cols = df.select_dtypes(include='object').columns.tolist()

        # -------- SIDEBAR FILTERS --------
        with st.sidebar:
            st.header("🎛️ Filters")
            filter_col = st.selectbox("Filter by column (optional)", ["None"] + categorical_cols)
            if filter_col != "None":
                unique_vals = df[filter_col].unique().tolist()
                selected_vals = st.multiselect("Select values", unique_vals, default=unique_vals)
                df = df[df[filter_col].isin(selected_vals)]

        # -------- TABS (Dashboard Style) --------
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            ["👀 Data", "📊 Dashboard", "📈 Statistics", "🔮 Forecast", "💬 Chat"]
        )

        # TAB 1 - DATA PREVIEW
        with tab1:
            st.subheader("Data Preview")
            st.dataframe(df.head(20), use_container_width=True)

            summary = get_data_summary(df)
            col1, col2, col3 = st.columns(3)
            col1.metric("Rows", summary["rows"])
            col2.metric("Columns", summary["columns"])
            col3.metric("Missing Values", sum(summary["missing_values"].values()))

        # TAB 2 - DASHBOARD (PowerBI/Tableau Style)
        with tab2:
            st.subheader("📊 Auto Dashboard")
            figs = dashboard_view(df, numeric_cols, categorical_cols)
            if figs:
                cols = st.columns(2)
                for i, fig in enumerate(figs):
                    with cols[i % 2]:
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Not enough numeric/categorical columns to build a dashboard.")

            st.divider()
            st.subheader("🛠️ Custom Chart Builder")
            c1, c2, c3, c4 = st.columns(4)
            chart_type = c1.selectbox("Chart Type", ["bar", "line", "pie", "scatter", "histogram", "box"])
            col_x = c2.selectbox("X Axis", df.columns)
            col_y = c3.selectbox("Y Axis", df.columns) if chart_type != "histogram" else None
            color_by = c4.selectbox("Color By (optional)", ["None"] + df.columns.tolist())
            color_by = None if color_by == "None" else color_by

            if st.button("Generate Chart"):
                fig = auto_chart(df, chart_type, col_x, col_y, color_by)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

            with st.expander("🔥 Correlation Heatmap"):
                heatmap_fig = correlation_heatmap(df)
                if heatmap_fig:
                    st.plotly_chart(heatmap_fig, use_container_width=True)
                else:
                    st.info("At least 2 numeric columns are needed.")

        # TAB 3 - STATISTICS (Excel Data Analysis Style)
        with tab3:
            st.subheader("📈 Descriptive Statistics")
            stats_df = descriptive_stats(df)
            if stats_df is not None:
                st.dataframe(stats_df, use_container_width=True)
            else:
                st.info("No numeric columns available for statistics.")

            st.divider()
            st.subheader("🔗 Correlation Matrix")
            corr_df = correlation_analysis(df)
            if corr_df is not None:
                st.dataframe(corr_df, use_container_width=True)
            else:
                st.info("At least 2 numeric columns are needed.")

            st.divider()
            st.subheader("⚠️ Outlier Detection")
            if numeric_cols:
                outlier_col = st.selectbox("Select a column", numeric_cols)
                outliers, lower, upper = detect_outliers(df, outlier_col)
                st.write(f"**Normal Range:** {lower:.2f} to {upper:.2f}")
                st.write(f"**Outliers Found:** {len(outliers)}")
                if len(outliers) > 0:
                    st.dataframe(outliers, use_container_width=True)
            else:
                st.info("No numeric column available for outlier detection.")

        # TAB 4 - FORECASTING
        with tab4:
            st.subheader("🔮 Trend Forecasting")
            if numeric_cols:
                fc_col = st.selectbox("Column to predict", numeric_cols)
                periods = st.slider("Future periods", 1, 20, 5)

                if st.button("Generate Forecast"):
                    predictions, slope = linear_trend_forecast(df, None, fc_col, periods)
                    if predictions is not None:
                        trend = "📈 Increasing" if slope > 0 else "📉 Decreasing"
                        st.write(f"**Trend Direction:** {trend} (slope: {slope:.2f})")
                        fig = forecast_chart(df, None, fc_col, predictions, periods)
                        st.plotly_chart(fig, use_container_width=True)
                        st.write("**Predicted Values:**", [round(p, 2) for p in predictions])
                    else:
                        st.warning("Not enough data to generate a forecast.")
            else:
                st.info("A numeric column is needed for forecasting.")

        # TAB 5 - CHAT
        with tab5:
            st.subheader("💬 Ask Your Data")

            # User-specific message key - each logged-in user gets their own separate chat history
            msg_key = f"messages_{st.session_state['user_id']}"
            if msg_key not in st.session_state:
                st.session_state[msg_key] = []

            for msg in st.session_state[msg_key]:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

            user_question = st.chat_input("Example: Which category has highest sales?")

            if user_question:
                st.session_state[msg_key].append({"role": "user", "content": user_question})
                with st.chat_message("user"):
                    st.write(user_question)

                with st.chat_message("assistant"):
                    with st.spinner("Analyzing..."):
                        answer = ask_question(df, user_question)
                        st.write(answer)
                        st.session_state[msg_key].append({"role": "assistant", "content": answer})
                        save_chat_history(db, st.session_state['user_id'], user_question, answer)
else:
    st.info("👈 Upload a file from the sidebar to get started")