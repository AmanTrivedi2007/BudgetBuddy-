import streamlit as st
import pandas as pd
import numpy as np


import streamlit as st

# Define your pages


page1 = st.Page("income_monitoring.py", title="Income", icon="💰")
page2 = st.Page("expense.py",title="Expense",icon="🫰")
page3 = st.Page("Saving_goal.py", title="Saving Goal", icon="🎯")
page4 = st.Page("Description.py", title="About Us", icon="💰")

# Create navigation in sidebar
pg = st.navigation([page1,page2,page3,page4], position="sidebar")
pg.run()

