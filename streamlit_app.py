import pandas as pd

# from collections import namedtuple

import math
import folium
from streamlit_folium import st_folium

import altair as alt

from sklearn.feature_extraction.text import CountVectorizer
import matplotlib.pyplot as plt
from wordcloud import WordCloud

import streamlit as st


clinic_metadata = pd.read_csv('filtered_gp_clinics.csv', index_col='Unnamed: 0')
clinic_reviews = pd.read_csv('gp_reviews.csv', index_col='Unnamed: 0')

clinic_names = clinic_reviews.clinic.unique()
clinic_reviews['rating'] = clinic_reviews['rating'].astype(int)

with st.sidebar:
    option = st.selectbox(
        "What clinic are you interested in?",
        clinic_names
    )

clean_clinic_reviews = clinic_reviews[['clinic', 'date', 'rating', 'title', 'comment']]
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

lat = clinic_metadata[clinic_metadata['OrganisationName']==option].Latitude
log = clinic_metadata[clinic_metadata['OrganisationName']==option].Longitude

this_map = folium.Map(prefer_canvas=True, location=[lat, log], zoom_start=15)

fg = folium.FeatureGroup(name="GP Clinics")

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

#use df.apply(,axis=1) to "iterate" through every row in your dataframe
clinic_metadata.apply(plotDot, axis = 1)

st_map = st_folium(
    this_map,
    feature_group_to_add=fg,
    width=700,
    height=450
)

time_ratings = alt.Chart(clinic_reviews[clinic_reviews['clinic']==option]).mark_line().encode(
    x='yearmonth(date)',
    y='mean(rating)',
    tooltip=['mean(rating)']
).properties(
    width=800,
    height=300
)

st.altair_chart(time_ratings, use_container_width=True)

def word_cloud(reviews):
    word_vectorizer = CountVectorizer(ngram_range=(1,2), analyzer='word')
    sparse_matrix = word_vectorizer.fit_transform(reviews['comment_wo_stopwords'])
    frequencies = sum(sparse_matrix).toarray()[0]
    word_freq = pd.DataFrame(frequencies, index=word_vectorizer.get_feature_names_out(), columns=['frequency'])
    word_freq.sort_values(['frequency'], ascending=False).head(10)

    text = " ".join(cat.split()[1] for cat in reviews.comment_wo_stopwords)
    word_cloud = WordCloud(collocations = False, background_color = 'white', width=1000, height=500, scale=2).generate(text)

    fig, ax = plt.subplots(figsize = (20, 10))
    ax.imshow(word_cloud, interpolation='bilinear')
    plt.axis("off")
    return fig

st.write('General area')
glob_cloud = word_cloud(clinic_reviews)
st.pyplot(glob_cloud)

st.write('Local clinic')
local_cloud = word_cloud(clinic_reviews[clinic_reviews['clinic']==option])
st.pyplot(local_cloud)

st.table(clean_clinic_reviews[clean_clinic_reviews['clinic']==option].style.apply(highlight, axis=1))
