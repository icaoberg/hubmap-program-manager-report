import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import plotly.express as px


def determine_type(dataset_type: str) -> str:
    if "[" in dataset_type and "]" in dataset_type:
        return "Derived"
    else:
        return "Primary"


@st.cache_data
def get_data() -> pd.DataFrame:
    """
    Fetch data from a predefined URL, extract the 'data' key,
    and return it as a DataFrame.

    Returns:
    pd.DataFrame: The data extracted from the 'data' key loaded into a DataFrame.
    """
    url = "https://ingest.api.hubmapconsortium.org/datasets/data-status"  # The URL to get the data from
    try:
        response = requests.get(url)  # Send a request to the URL to get the data
        response.raise_for_status()  # Check if the request was successful (no errors)
        json_data = response.json()  # Convert the response to JSON format

        # Ensure 'data' key exists in the JSON
        if "data" in json_data:  # Check if the JSON contains the key 'data'
            df = pd.DataFrame(
                json_data["data"]
            )  # Create a DataFrame using the data under 'data' key
            df["dataset_status"] = df["dataset_type"].apply(determine_type)
            print("Data successfully loaded.")  # Print a message indicating success
        else:
            raise KeyError(
                "'data' key not found in the JSON response"
            )  # Raise an error if 'data' key is missing

        return df  # Return the DataFrame with the data
    except (ValueError, KeyError) as e:  # Catch errors related to value or missing keys
        print(f"Error loading data: {e}")  # Print the error message
        return pd.DataFrame()  # Return an empty DataFrame if there is an error
    except requests.RequestException as e:  # Catch errors related to the request itself
        print(f"Request failed: {e}")  # Print the error message
        return pd.DataFrame()  # Return an empty DataFrame if the request fails


def get_list_of_unique_status(df):
    all_statuses = df["status_history"].apply(lambda x: [d["status"] for d in x])
    unique_statuses = list(
        set([status for sublist in all_statuses for status in sublist])
    )
    return unique_statuses.insert(0, "HuBMAP ID")


data = get_data()
df = data[data["dataset_status"] == "Primary"].copy()

#########################################################################################################################
# Add a sidebar
st.sidebar.title("")
logo_url = "https://hubmapconsortium.org/wp-content/uploads/2019/01/HuBMAP-Retina-Logo-Color-300x110.png"
st.sidebar.image(logo_url, use_column_width=True)

st.sidebar.title("Table of Contents")
st.sidebar.markdown(
    """
- [Introduction](#introduction)
- [Report](#report)
""",
    unsafe_allow_html=True,
)
#########################################################################################################################

#########################################################################################################################
df.rename(
    columns={"dataset_type": "Dataset Type", "group_name": "Group Name"}, inplace=True
)

# Aggregate the data by Group Name first, then Dataset Type
agg_df = df.groupby(["Group Name", "Dataset Type"]).size().unstack(fill_value=0)

# Calculate the total count for each Group Name and sort by it
agg_df["Total"] = agg_df.sum(axis=1)
agg_df = agg_df.sort_values(by="Total", ascending=False)
agg_df = agg_df.drop(columns="Total")  # Drop the 'Total' column after sorting

# Sort columns alphabetically (optional, depending on your needs)
agg_df = agg_df.sort_index(axis=1)

# Create the Streamlit app
st.header("Primary Datasets Report")

today = pd.Timestamp.today().strftime("%m-%d-%Y")
st.write(today)

st.subheader("Introduction")
st.text("The goal of the Human BioMolecular Atlas Program (HuBMAP) is to develop an open and global platform to map healthy cells in the human body.")

# Add the plot
st.subheader("Report")

# Rename columns
df.rename(columns={'dataset_type': 'Dataset Type', 'group_name':'Group Name'}, inplace=True)

# Aggregate the data by Dataset Type first, then Group Name
agg_df = df.groupby(['Dataset Type', 'Group Name']).size().unstack(fill_value=0)

# Sort columns alphabetically (optional)
agg_df = agg_df.sort_index(axis=1)

# Create a Plotly bar chart
fig = px.bar(
    agg_df.reset_index(),  # Reset index to use it in Plotly
    x='Dataset Type',  # x-axis is now Dataset Type
    y=agg_df.columns,  # The columns are now Group Names
    title=f'Published and unpublished primary datasets by dataset type vs data provider',
    labels={'value': 'Count', 'variable': 'Group Name'},
    barmode='stack',
    width=1600,  # Increase figure width
    height=1000   # Increase figure height
)

# Customize the x-axis tick labels
fig.update_xaxes(tickangle=45, title_text="Dataset Type")

# Display the Plotly figure in Streamlit
st.plotly_chart(fig)
#########################################################################################################################

#########################################################################################################################
import streamlit as st
import pandas as pd
import plotly.express as px

# Assuming df is your DataFrame
# df = pd.read_csv('your_file.csv')

# Rename columns
df.rename(
    columns={
        "dataset_type": "Dataset Type",
        "group_name": "Group Name",
        "status": "Status",
    },
    inplace=True,
)

# Aggregate the data by Dataset Type and Status
agg_df = df.groupby(["Dataset Type", "Status"]).size().unstack(fill_value=0)

# Calculate the total count for each Dataset Type and sort by it
agg_df["Total"] = agg_df.sum(axis=1)
agg_df = agg_df.sort_values(by="Total", ascending=False)
agg_df = agg_df.drop(columns="Total")  # Drop the 'Total' column after sorting

# Sort columns alphabetically (optional)
agg_df = agg_df.sort_index(axis=1)

# Create the Streamlit app
st.header("Published and Unpublished Primary Dataset Status Report")

# Add the plot
st.subheader("Datasets by Status")

# Create a Plotly bar chart
fig = px.bar(
    agg_df.reset_index(),  # Reset index to use it in Plotly
    x="Dataset Type",
    y=agg_df.columns,
    title=f"Published and unpublished primary dataset status",
    labels={"value": "Count", "variable": "Status"},
    barmode="stack",
    width=1200,  # Adjust figure width
    height=800,  # Adjust figure height
)

# Customize the x-axis tick labels
fig.update_xaxes(tickangle=45, title_text="Dataset Type")

# Display the Plotly figure in Streamlit
st.plotly_chart(fig)
#########################################################################################################################

#########################################################################################################################
df = data[data["dataset_status"] == "Primary"].copy()
df.rename(
    columns={
        "hubmap_id": "HuBMAP ID",
        "dataset_type": "Dataset Type",
        "group_name": "Group Name",
        "hubmap_id": "HuBMAP ID",
        "uuid": "UUID",
    },
    inplace=True,
)
df["Status Change"] = None

df.reset_index(drop=True)

#st.dataframe(df[["HuBMAP ID", "UUID", "Dataset Type", "Status Change"]])
#########################################################################################################################

#########################################################################################################################
# Add a copyright notice at the bottom
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: white;
        color: black;
        text-align: center;
    }
    </style>
    <div class="footer">
        <p>© 2024 Pittsburgh Supercomputing Center. All Rights Reserved.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
#########################################################################################################################