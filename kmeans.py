import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.utils import shuffle

class KMeansMethod:
    def __init__(self):
        self.kmeans = KMeans(n_clusters=6)
        songsDb = pd.read_csv('datasets/newSongDb.csv')
        self.metadata = pd.read_csv('datasets/metadataDB.csv')
        self.metadata.set_index('ID')
        songsDb = shuffle(shuffle(songsDb))
        self.X = songsDb.loc[[i for i in range(0, 100000)]]
        self.fitted = self.fit()
        
    def fit(self):
        self.kmeans.fit(self.X) 
        self.X['label'] = self.kmeans.labels_
        return (self.X, self.kmeans)    
        
    def predict(self, Y):
        y_pred = self.fitted[1].predict(Y)
        mode = pd.Series(y_pred).mode()
        predicted = self.fitted[0][self.fitted[0]['label'] == mode.loc[0]]
        predicted['ID'] = self.metadata.filter(['ID'])
        return predicted

    def recommend(self, Y):
        dat = []
        for i in Y['Key']:
            dat.append(i)
        return self.metadata.loc[dat]['Uri'].mode()

    def list_to_dataFrame(self, list_to_transform):
        df = pd.DataFrame(list_to_transform, columns=[
            'danceability', 'energy', 'loudness', 'mode', 'speechiness',
            'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo'
        ])
        print(df)
        return df

if __name__=="__main__":
    kmeansInstance = KMeansMethod()
    input_user = pd.read_csv('datasets/input.csv')
    prediction = kmeansInstance.predict(input_user)
    recommendation = kmeansInstance.recommend(input_user)
    print("Recomendation: ")
    print(recommendation[:5])