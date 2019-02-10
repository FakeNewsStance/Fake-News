
class Main:
    
    def __init__(self):
        import numpy as np
        import pandas as pd
        from keras.preprocessing.text import Tokenizer
        from keras.utils import to_categorical       
        import keras
        
        self.MAX_SEQUENCE_LENGTH = 300
        self.MAX_NUM_WORDS = 60000
        self.EMBEDDING_DIM = 300
        self.VALIDATION_SPLIT = 0.2
        
        stances = pd.read_csv("train_stances.csv")
        bodies = pd.read_csv("train_bodies.csv")
        
        dataset = pd.merge(stances, bodies)
        
        dataset = dataset.drop(['BodyID'], axis=1)
        
        cols = dataset.columns.tolist()
        cols = cols[-1:] + cols[:-1]
        dataset = dataset[cols]
        
        y = dataset['Stance']
        y = np.array(y)
        
        from sklearn.preprocessing import LabelEncoder
        labelencoder_y = LabelEncoder()
        y = labelencoder_y.fit_transform(y)
        
        
        
        self.tokenizer = Tokenizer(nb_words=self.MAX_NUM_WORDS)
        self.tokenizer.fit_on_texts(dataset['Headline']+dataset['articleBody'])
        self.model = keras.models.load_model('model') 
        
    def test(self,tweet,articles):
        from keras.preprocessing.sequence import pad_sequences
        sequences1 = self.tokenizer.texts_to_sequences(tweet)
        test1 = pad_sequences(sequences1, maxlen=self.MAX_SEQUENCE_LENGTH) 
        for article in articles:
            sequences2 = self.tokenizer.texts_to_sequences(article)
            test2 = pad_sequences(sequences2, maxlen=self.MAX_SEQUENCE_LENGTH)
            y_pred = model.predict([test1, test2])
            y_pred[y_pred > 0.5] = 1
            y_pred[y_pred < 0.5] = 0
            print('\n\nY pred:',y_pred)
