from collections import namedtuple
import altair as alt
import math
import pandas as pd
import streamlit as st


clinic_metadata = pd.read_csv('filtered_gp_clinics.csv', index_col='Unnamed: 0')
clinic_reviews = pd.read_csv('gp_reviews.csv', index_col='Unnamed: 0')
clinic_metadata.rename(columns={"Latitude": "latitude", "Longitude": "longitude"}, inplace=True)
# clinic_names = clinic_metadata.OrganisationName.unique()
clinic_names = clinic_reviews.clinic.unique()
clinic_reviews['rating'] = clinic_reviews['rating'].astype(int)

option = st.selectbox(
    "What clinic are you interested in?",
    clinic_names
)

clinic_reviews = clinic_reviews[['clinic', 'date', 'rating', 'title', 'comment']]
select_clinic = clinic_reviews[clinic_reviews['clinic']==option]
no_ratings = select_clinic['rating'].count()
avg_rating = select_clinic['rating'].mean().round(1)
delta_rating = select_clinic['rating'].iat[0] - select_clinic['rating'].iat[-1]

def highlight(s):
    if s.rating > 3:
        return ['background-color: green'] * len(s)
    elif s.rating < 3:
        return ['background-color: red'] * len(s)
    else:
        return ['background-color: white'] * len(s)

col1, col2 = st.columns(2)
col1.metric(label="Number of Ratings", value=no_ratings)
col2.metric(label="Average Rating", value=avg_rating, delta=delta_rating.item())

st.map(data=clinic_metadata[clinic_metadata['OrganisationName']==option], zoom=None, use_container_width=True)

st.table(clinic_reviews[clinic_reviews['clinic']==option].style.apply(highlight, axis=1))
