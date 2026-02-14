import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.title("Theta Decay Estimation")

extrinsic_value = float(st.text_input("Extrinsic Value", value="10"))
dte = st.slider("Days to Expiry", min_value=1, max_value=365, value=30)

time_passed = st.slider("Time Passed", min_value=0, max_value=dte, value=0)

# Full time range (0 to expiry)
time_range = np.linspace(0, dte, 500)

# Square root decay model
theta_decay = np.sqrt((dte - time_range) / dte) * extrinsic_value

# Current value
current_value = np.sqrt((dte - time_passed) / dte) * extrinsic_value

# Estimate theta
theta = -extrinsic_value / (2 * dte * np.sqrt(1 - time_passed/dte))

# Build interactive plot
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=time_range,
    y=theta_decay,
    mode="lines",
    name="Extrinsic Value"
))

# Highlight current time point
fig.add_trace(go.Scatter(
    x=[time_passed],
    y=[current_value],
    mode="markers",
    marker=dict(size=10),
    name="Current Position"
))

fig.update_layout(
    xaxis_title="Days Passed",
    yaxis_title="Extrinsic Value",
    title="Interactive Theta Decay Curve",
)

st.plotly_chart(fig, use_container_width=True)

st.write(f"Current Extrinsic Value: {round(current_value, 2)}")
st.write(f"Estimated Theta (Rate of Decay): {round(theta, 2)}")
