import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from datetime import timedelta

# Load Data
df = pd.read_json("workitems.json")
df["iterationStartDate"] = pd.to_datetime(df["iterationStartDate"])
df["workStartDate"] = pd.to_datetime(df["workStartDate"])
df["finishDate"] = pd.to_datetime(df["finishDate"])

# Header
st.title("Eli Newguy Performance Review")
st.write("Judging by story points, I went from worst to first in 4 months!")

# Sidebar configuration
days = st.sidebar.slider("Days of history to use", 15, 150, 140)
show_details = st.sidebar.checkbox("Show more details")

#Filter data to what we're looking for
all_owners = df.owner.unique().tolist()
chosen_owners = st.multiselect("Developers to display", all_owners, ['Eli','Heather'])
show_all_owners = st.checkbox("Show all developers (overrides selection)")

if show_all_owners:
    chosen_owners = all_owners

df = df[df.owner.isin(chosen_owners)]

end_date = df["iterationStartDate"].max()
start_date = end_date - timedelta(days)

df = df[df.iterationStartDate.between(start_date, end_date)]

# Wrangle data to get cumulative points over time
date_range = pd.date_range(start_date, end_date)
points_over_time = pd.pivot_table(df, values="points", index=["finishDate"], columns=["owner"], aggfunc=np.sum, fill_value=0)
points_over_time = points_over_time.reindex(date_range, fill_value=0)
points_over_time = points_over_time.cumsum()
points_over_time = points_over_time.T.reset_index()
points_over_time = pd.melt(points_over_time, id_vars=["owner"], var_name="date", value_name="points")

# Now graph it
st.altair_chart(alt.Chart(points_over_time).mark_line().encode(
    x = 'date',
    y = 'points',
    color = 'owner'
))

st.markdown("**Give this kid a raise!**")

if show_details:
    st.subheader("Additional Details")
    st.write("To make this report, I started with this dataset from JIRA:")
    df
    st.write("And twiddled bits until it looked more like this, before graphing it:")
    points_over_time
