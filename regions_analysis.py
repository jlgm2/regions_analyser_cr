import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Streamlit Sidebar for Filters
st.sidebar.title("Filters")

# Multi-select box for region selection
regions = st.sidebar.multiselect(
    "Select Regions to Compare:",
    options=['U.S.', 'Europe (Germany)', 'Asia (Japan)'],
    default=['U.S.', 'Europe (Germany)', 'Asia (Japan)']  # Default: All regions selected
)

# Dropdown for selecting Alkali Sorbent
alkali_sorbent = st.sidebar.selectbox(
    "Select Alkali Sorbent:",
    options=[
        'Lime produced using clean fuels and electricity',
        'Lime as tailing by-products from mining operations (generic)',
        'Lime, regenerated using thermal calcination',
        'Lime, regenerated using electrical calcination',
        'NaOH - commercial',
        'NaOH - renewable',
        'KOH - commercial',
        'KOH - renewable',
        'MgO - Commercial',
        'MgO - Renewable'
    ]  # Replace with actual sorbent names from your data
)

# Dropdown for Building Savings
building_savings = st.sidebar.selectbox(
    "Select Building Savings:",
    options=['Not considered', 'Considered']
)

# Map building savings to numeric filter
if building_savings == "Not considered":
    building_savings_data = 0
else:
    building_savings_data = 1

# Mapping regions to file paths
region_to_file = {
    'U.S.': 'scenarios_results_data_US.csv',
    'Europe (Germany)': 'scenarios_results_data_EU.csv',
    'Asia (Japan)': 'scenarios_results_data_Asia.csv'
}

# Load and combine data for the selected regions
dataframes = []
for region in regions:
    file_path = region_to_file[region]
    df = pd.read_csv(file_path)
    df['Region'] = region  # Add a column to distinguish regions
    dataframes.append(df)

# Combine all selected regions into one dataframe
if dataframes:
    data = pd.concat(dataframes, ignore_index=True)
else:
    st.error("Please select at least one region.")
    st.stop()

# Rename columns for consistency
data = data.rename(columns=lambda x: x.strip())

# Define columns for environmental impact indicators
impact_columns = [
    "Climate change (total), kg CO2 eq", "Acidification, mol H+ eq",
    "Climate change (biogenic), kg CO2 eq", "Climate change (fossil), kg CO2 eq",
    "human toxicity: non-carcinogenic , inorganics, CTUh",
    "ionising radiation: human health , kg Bq U235eq", "land use, (dimensionless)",
    "material resources: metals/minerals, kg Sb-eq", "ozone depletion, kg CFC11-eq",
    "particulate matter formation, disease incidence",
    "photochemical oxidant formation: human health, kg NMVOC-eq",
    "water use , m3 world eq depriv"
]

# Dropdown for Environmental Impact Indicator
impact_indicator = st.sidebar.selectbox(
    "Select Environmental Impact Indicator:",
    options=impact_columns
)

# Filter dataset based on user selections
filtered_data = data[
    (data['Alkali sorbent'] == alkali_sorbent) &
    (data['Building savings'] == building_savings_data)
]

# Generate the Plotly Chart for Comparison
fig = px.scatter(
    data_frame=filtered_data,
    x=impact_indicator,
    y="Cost, USD2023",
    color="Region",  # Compare by region
    hover_name="Label",
    labels={"x": impact_indicator, "y": "Cost (USD2023)"},
    title=f"{impact_indicator} vs Cost ({alkali_sorbent}, Building Savings: {building_savings})",
)

# Enhance chart aesthetics
fig.update_traces(
    marker=dict(size=12, opacity=0.8)  # Bigger data points
)

# Add horizontal line at Y = 10000 (Red dashed line)
fig.add_trace(
    go.Scatter(
        x=[min(filtered_data[impact_indicator]), max(filtered_data[impact_indicator])],
        y=[10000, 10000],
        mode='lines',
        line=dict(color="red", width=2, dash="dash"),
        name="100 USD per tonne of CO2",
        showlegend=True  # This will show the line in the legend
    )
)

# Add vertical line at X = 0 (Blue dashed line)
fig.add_trace(
    go.Scatter(
        x=[0, 0],
        y=[min(filtered_data["Cost, USD2023"]), max(filtered_data["Cost, USD2023"])],
        mode='lines',
        line=dict(color="blue", width=2, dash="dash"),
        name="Carbon Neutrality",
        showlegend=True  # This will show the line in the legend
    )
)

# Update layout with visible gridlines
fig.update_layout(
    plot_bgcolor="white",
    xaxis=dict(
        gridcolor="lightgrey",  # Grey gridlines for X axis
        zerolinecolor="grey",
        title_font=dict(size=14, family="Arial", color="black"),
        showgrid=True,  # Ensure grid lines are visible on x-axis
        gridwidth=1  # Set gridline width
    ),
    yaxis=dict(
        gridcolor="lightgrey",  # Grey gridlines for Y axis
        zerolinecolor="grey",
        title_font=dict(size=14, family="Arial", color="black"),
        showgrid=True,  # Ensure grid lines are visible on y-axis
        gridwidth=1  # Set gridline width
    ),
    legend_title="Region",
    title_font=dict(size=18, family="Arial"),
    font=dict(size=12, family="Arial"),
    height=800,  # Adjust height for a more reasonable size
    width=800,   # Adjust width to match the height and make it more square
    legend=dict(
        orientation="h",  # Horizontal legend
        yanchor="top",
        y=-0.1,  # Move the legend further down
        xanchor="center",
        x=0.5
    )
)

# Streamlit main page content
st.title("Regional Comparison Dashboard")
st.plotly_chart(fig)
