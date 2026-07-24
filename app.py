import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
import os

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="ChurnSense AI",
    page_icon="🤖",
    layout="wide"
)

# ---------------------------------------------------
# CSS
# ---------------------------------------------------

st.markdown("""
<style>

.main{
    background:#F5F7FA;
}

h1{
    color:#1565C0;
}

.stButton>button{
    background:#1565C0;
    color:white;
    border-radius:8px;
    height:50px;
    width:220px;
    font-size:18px;
}

.stDownloadButton>button{
    background:#2E7D32;
    color:white;
    border-radius:8px;
}

div[data-testid="metric-container"]{
    background:white;
    padding:20px;
    border-radius:12px;
    box-shadow:0px 0px 10px rgba(0,0,0,.15);
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

st.sidebar.title("🤖 ChurnSense AI")

st.sidebar.markdown("---")

st.sidebar.subheader("Project")

st.sidebar.info("""
Customer Churn Prediction
using Machine Learning
""")

st.sidebar.markdown("### Technology")

st.sidebar.write("""
✔ Python

✔ Streamlit

✔ Pandas

✔ Scikit-Learn

✔ Random Forest

✔ Plotly
""")

st.sidebar.markdown("---")

st.sidebar.success("Model Loaded Successfully")

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------

st.title("📊 Customer Churn Prediction Dashboard")

st.write("""
Upload a telecom customer dataset and predict
which customers are likely to leave the company.
""")

st.markdown("---")

# ---------------------------------------------------
# LOAD MODEL
# ---------------------------------------------------

model = joblib.load("model/churn_model.pkl")

feature_columns = joblib.load(
    "model/feature_columns.pkl"
)

# ---------------------------------------------------
# FILE UPLOAD
# ---------------------------------------------------

uploaded_file = st.file_uploader(
    "📂 Upload Excel or CSV File",
    type=["xlsx","csv"]
)

if uploaded_file is not None:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("Uploaded Dataset")

    st.dataframe(
        df,
        use_container_width=True
    )

    st.markdown("---")

    col1,col2 = st.columns(2)

    col1.metric(
        "Rows",
        len(df)
    )

    col2.metric(
        "Columns",
        len(df.columns)
    )

    st.markdown("---")

    if st.button("🚀 Predict Churn"):

        data = df.copy()

        id_columns=[
            "customerID",
            "CustomerID",
            "Customer_Id",
            "CustID",
            "Cust_ID",
            "ID"
        ]

        for col in id_columns:
            if col in data.columns:
                data.drop(
                    columns=[col],
                    inplace=True
                )

        if "Churn" in data.columns:
            data.drop(
                columns=["Churn"],
                inplace=True
            )

        for col in data.select_dtypes(
            include=["object"]
        ).columns:

            data[col]=(
                data[col]
                .astype("category")
                .cat.codes
            )

        for col in feature_columns:

            if col not in data.columns:
                data[col]=0

        data=data[feature_columns]

        predictions=model.predict(data)

        df["Prediction"]=[
            "Yes" if i==1 else "No"
            for i in predictions
        ]
        st.success("✅ Prediction Completed Successfully!")

        # ==========================================
        # DASHBOARD METRICS
        # ==========================================

        total = len(df)
        churn = (df["Prediction"] == "Yes").sum()
        safe = (df["Prediction"] == "No").sum()

        st.markdown("## 📈 Dashboard")

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "👥 Total Customers",
            total
        )

        c2.metric(
            "⚠️ Likely to Churn",
            churn
        )

        c3.metric(
            "✅ Safe Customers",
            safe
        )

        st.markdown("---")

        # ==========================================
        # PREDICTION SUMMARY
        # ==========================================

        summary = (
            df["Prediction"]
            .value_counts()
            .reset_index()
        )

        summary.columns = [
            "Prediction",
            "Count"
        ]

        left, right = st.columns(2)

        with left:

            st.subheader("📊 Bar Chart")

            fig = px.bar(
                summary,
                x="Prediction",
                y="Count",
                color="Prediction",
                text="Count",
                title="Customer Churn Prediction"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with right:

            st.subheader("🥧 Pie Chart")

            fig2 = px.pie(
                summary,
                names="Prediction",
                values="Count",
                hole=0.45,
                title="Prediction Distribution"
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

        st.markdown("---")

        # ==========================================
        # MONTHLY CHARGES CHART
        # ==========================================

        if "MonthlyCharges" in df.columns:

            st.subheader("💰 Monthly Charges")

            fig3 = px.histogram(
                df,
                x="MonthlyCharges",
                color="Prediction",
                nbins=20,
                title="Monthly Charges Distribution"
            )

            st.plotly_chart(
                fig3,
                use_container_width=True
            )

        # ==========================================
        # CONTRACT DISTRIBUTION
        # ==========================================

        if "Contract" in df.columns:

            st.subheader("📄 Contract Types")

            contract = (
                df["Contract"]
                .value_counts()
                .reset_index()
            )

            contract.columns = [
                "Contract",
                "Customers"
            ]

            fig4 = px.bar(
                contract,
                x="Contract",
                y="Customers",
                color="Contract",
                text="Customers"
            )

            st.plotly_chart(
                fig4,
                use_container_width=True
            )

        st.markdown("---")

        # ==========================================
        # SUMMARY TABLE
        # ==========================================

        st.subheader("📋 Prediction Summary")

        st.table(summary)

        st.markdown("---")
                # ==========================================
        # PREDICTION RESULTS
        # ==========================================

        st.subheader("📑 Prediction Results")

        # Add prediction confidence if supported
        try:
            probabilities = model.predict_proba(data)

            confidence = [
                round(max(prob) * 100, 2)
                for prob in probabilities
            ]

            df["Confidence (%)"] = confidence

        except:
            pass

        st.dataframe(
            df,
            use_container_width=True,
            height=500
        )

        st.markdown("---")

        # ==========================================
        # CUSTOMER INSIGHTS
        # ==========================================

        st.subheader("📌 Insights")

        churn_percentage = round((churn / total) * 100, 2)

        safe_percentage = round((safe / total) * 100, 2)

        insight1, insight2 = st.columns(2)

        with insight1:

            st.info(
                f"""
                **Likely to Churn**

                {churn} Customers

                ({churn_percentage}%)
                """
            )

        with insight2:

            st.success(
                f"""
                **Safe Customers**

                {safe} Customers

                ({safe_percentage}%)
                """
            )

        st.markdown("---")

        # ==========================================
        # DOWNLOAD RESULTS
        # ==========================================

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Download Prediction Report",
            data=csv,
            file_name="prediction_results.csv",
            mime="text/csv"
        )

        st.balloons()

# ==========================================
# FOOTER
# ==========================================

st.markdown("---")

st.markdown(
    """
    <center>

    ### 🤖 ChurnSense AI

    Customer Churn Prediction using Machine Learning

    **Algorithm:** Random Forest Classifier

    **Frontend:** Streamlit

    **Backend:** Python

    **Developed By:** Ayushi and Sakshi

    © 2026 All Rights Reserved

    </center>
    """,
    unsafe_allow_html=True
)