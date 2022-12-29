import pandas as pd

import math
import folium
from streamlit_folium import st_folium

import altair as alt

import matplotlib.pyplot as plt
import matplotlib
from wordcloud import WordCloud

import streamlit as st



# Plots coordinates on a map
def plotDot(point):
    '''input: series that contains a numeric named latitude and a numeric named longitude
    this function creates a CircleMarker and adds it to your feature group'''
    fg.add_child(
        folium.CircleMarker(
            location=[point.Latitude, point.Longitude],
            radius=2,
            weight=5,
            tooltip=point.OrganisationName
        )
    )

# Colours Dataframes based on rating
def highlight(s):
    if s.rating > 3:
        return ['background-color: green'] * len(s)
    elif s.rating < 3:
        return ['background-color: red'] * len(s)
    else:
        return ['background-color: white'] * len(s)

# WordCloud generator
@st.cache(hash_funcs={matplotlib.figure.Figure: hash})
def word_cloud(reviews, clinic_name=None):
    if clinic_name != None:
        reviews = reviews[reviews['clinic']==clinic_name]

    text = " ".join(cat.split()[1] for cat in reviews.comment_wo_stopwords)
    word_cloud = WordCloud(collocations = False, background_color = 'white', width=1000, height=500, scale=2).generate(text)

    fig, ax = plt.subplots(figsize = (20, 10))
    ax.imshow(word_cloud, interpolation='bilinear')
    plt.axis("off")
    return fig

clinic_metadata = pd.read_csv('filtered_gp_clinics.csv', index_col='Unnamed: 0')
clinic_reviews = pd.read_csv('gp_reviews.csv', index_col='Unnamed: 0')

clinic_names = sorted(clinic_reviews.clinic.unique())
clinic_reviews['rating'] = clinic_reviews['rating'].astype(int)

with st.sidebar:
    option = st.selectbox(
        "What clinic are you interested in?",
        clinic_names
    )

select_clinic = clinic_reviews[clinic_reviews['clinic']==option]
no_ratings = select_clinic['rating'].count()
avg_rating = select_clinic['rating'].mean().round(1)
delta_rating = select_clinic['rating'].iat[0] - select_clinic['rating'].iat[-1]

lat = clinic_metadata[clinic_metadata['OrganisationName']==option].Latitude
log = clinic_metadata[clinic_metadata['OrganisationName']==option].Longitude

# Create Streamlit Page
st.title("NHS Primary Care Patient Reviews")
st.markdown("This mini-app allows patients to see how their local GP clinic has been reviewed. It is based on patient reviews scraped from [NHS Services](https://www.nhs.uk/services/gp-surgery/the-ridgeway-surgery/E84068/ratings-and-reviews)")

col1, col2 = st.columns(2)
col1.metric(label="Number of Ratings", value=no_ratings)
col2.metric(label="Average Rating", value=avg_rating, delta=delta_rating.item())

this_map = folium.Map(prefer_canvas=True, location=[lat, log], zoom_start=15)
fg = folium.FeatureGroup(name="GP Clinics")
clinic_metadata.apply(plotDot, axis = 1)
st_map = st_folium(
    this_map,
    feature_group_to_add=fg,
    width=700,
    height=450
)

st.write("Average Monthly Patient Rating")
time_ratings = alt.Chart(select_clinic).mark_line().encode(
    x='yearmonth(date)',
    y='mean(rating)',
    tooltip=['mean(rating)']
).properties(
    width=800,
    height=300
)
st.altair_chart(time_ratings, use_container_width=True)

general_word_tabs, specific_words_tab = st.tabs(["General", "Specific"])

with general_word_tabs:
    st.subheader('Common words reported for Harrow')
    glob_cloud = word_cloud(clinic_reviews)
    st.pyplot(glob_cloud)

with specific_words_tab:
    st.subheader('Common words reported for ' + option)
    local_cloud = word_cloud(clinic_reviews, option)
    st.pyplot(local_cloud)

with st.expander("See all reviews"):
    st.table(select_clinic[['clinic', 'date', 'rating', 'title', 'comment']].style.apply(highlight, axis=1))
