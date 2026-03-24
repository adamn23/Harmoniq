import pandas as pd
import numpy as np
import datetime as dt

def process_csv(dataset_name: str) -> pd.DataFrame:
    """

    :param dataset_name:
    :return:
    """
    df_songs = pd.read_csv(dataset_name + '.csv')
    df_songs.dropna(inplace=True)
    df_songs['Length'] = 60*df_songs['Length'].str.split(':').str[0].astype(int)+df_songs['Length'].str.split(':').str[1].astype(int)
    df_songs['Release date'] = pd.to_datetime(df_songs['Release Date'], format='mixed')
    df_songs['Mode'] = df_songs['Key'].str.split(' ').str[1]
    df_songs.drop(columns=['Key'], inplace=True)
    df_songs['Loudness (db)'] = df_songs['Loudness (db)'].str.split('db').str[0].astype(float)
    df_songs['Explicit'] = df_songs['Explicit'].replace({'Yes': True, 'No': False})
    df_songs['Good for Party'] = df_songs['Good for Party'].astype(bool)
    df_songs['Good for Party'] = df_songs['Good for Party'].astype(bool)
    df_songs['Good for Work/Study'] = df_songs['Good for Work/Study'].astype(bool)
    df_songs['Good for Relaxation/Meditation'] = df_songs['Good for Relaxation/Meditation'].astype(bool)
    df_songs['Good for Exercise'] = df_songs['Good for Exercise'].astype(bool)
    df_songs['Good for Running'] = df_songs['Good for Running'].astype(bool)
    df_songs['Good for Yoga/Stretching'] = df_songs['Good for Yoga/Stretching'].astype(bool)
    df_songs['Good for Driving'] = df_songs['Good for Driving'].astype(bool)
    df_songs['Good for Social Gatherings'] = df_songs['Good for Social Gatherings'].astype(bool)
    df_songs['Good for Morning Routine'] = df_songs['Good for Morning Routine'].astype(bool)
    return df_songs

df = process_csv('spotify_dataset')
