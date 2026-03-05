import streamlit as st
import pandas as pd 
import datetime
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go 


import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(BASE_DIR, "tp_pt_en.csv"))

df["Year"] = df["fy_ef"].str.extract(r'(\d{4})').astype(int)

df["FY_Label"] = df["Year"].astype(str) + "-" + (df["Year"] + 1).astype(str).str[-2:]

result = df.groupby("FY_Label", as_index=False)["expenditures"].sum()
st.set_page_config(layout="wide")

def fmt_money(x):
    try:
        return f"${x:,.0f}"
    except:
        return x

st.markdown('<style>div.block-container{padding-top:1rem}</style>', unsafe_allow_html=True)

col1, col2 = st.columns([0.1,0.8])
 
html_title = """
<style>
.title-test { font-weight: 800; padding: 6px; border-radius: 8px; }
.subtle { opacity: 0.85; font-size: 0.95rem; }
</style>
<center>
  <h1 class="title-test">Public Accounts of Canada – Transfer Payments Dashboard</h1>
  <div class="subtle">Expenditures vs Authorities (Budget) — summarized views</div>
</center>
"""
with col2:
    st.markdown(html_title, unsafe_allow_html=True)
col3, col4, col5 = st.columns ([0.1,0.45,0.45])
top_n = st.slider("Organizations shown (Top N by expenditures)", 5, 50, 15, 5)
with col3:
    account_date = str(datetime.datetime.now().strftime("%d %B %Y"))
    st.write(f"Last updated by:  \n {account_date}")

with col4:
    org_sum = df.groupby("org_name", as_index=False)["expenditures"].sum()
    org_sum = org_sum.sort_values("expenditures", ascending=False).head(top_n)

    fig = px.bar(
        org_sum,
        x="org_name",
        y="expenditures",
        labels={"expenditures": "Total Expenses ($)", "org_name": "Organization"},
        title=f"Total Expenditure (Top {top_n})",
        hover_data={"expenditures": ":,.0f"},
        template="plotly_dark",
        height=520
    )
    fig.update_layout(margin=dict(l=10, r=10, t=60, b=160))
    fig.update_xaxes(tickangle=-60, automargin=True)
    fig.update_yaxes(tickformat=",.0f")
    st.plotly_chart(fig, use_container_width=True)

df["Year"] = df["fy_ef"].str.extract(r'(\d{4})').astype(int)

result = df.groupby("Year", as_index=False)["expenditures"].sum()

result = result.sort_values("Year")


with col5:
    fig1 = px.line(
        result,
        x="Year",
        y="expenditures",
        title="Total Expenditures Over Time",
        template="plotly_dark",
        markers=True
    )
    fig1.update_yaxes(tickformat=",.0f")
    fig1.update_layout(template="plotly_dark")
    st.plotly_chart(fig1, use_container_width=True)

_, view2, dwn2 = st.columns([0.5,0.25,0.25])
with view2:
    expander = st.expander ("Expenditures")
    data = result
    expander.write(data)

with dwn2:
    st.download_button(
        "Get Data",
        data = result.to_csv().encode("utf-8"),
        file_name="Canada_Public_aCCOUNTS_2011_12.csv",
        mime="text/csv"
        )
    
st.divider()


result = df.groupby(by="org_name")[["expenditures","authorities"]].sum().reset_index()
result = result.sort_values("expenditures", ascending=False).head(top_n)

fig3 = go.Figure()
fig3.add_trace(go.Bar(x = result["org_name"], y = result["expenditures"], name = "Total Expenses"))
fig3.add_trace(go.Scatter(
    x=result["org_name"],
    y=result["authorities"],
    mode="lines",
    name="Total Budget",
    yaxis="y2"
))
fig3.update_layout(
    title= "Total Expenses and Budget by Organization",
    xaxis = dict(title="org_name"),
    yaxis = dict(title="Total Expenses", showgrid=True),
    yaxis2 = dict(title="Total Budget", overlaying = "y", side = "right"),
    template = "plotly_dark",
    legend = dict(x=1, y=2)
)

_, col6= st.columns([0.1,0.5])
with col6:
    st.plotly_chart(fig3,use_container_width=True)

_, view3, dwn3= st.columns([0.5,0.45,0.45])
with view3:
    epander = st.expander("View Total Expenses and Budget by Organization")
    view_df = result.copy()
    view_df["expenditures"] = view_df["expenditures"].map(fmt_money)
    view_df["authorities"] = view_df["authorities"].map(fmt_money)
    epander.write(view_df)