from __future__ import print_function
import numpy as np
import pandas as pd
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
from keras.layers import Dense, Input,  LSTM
from keras.layers import Embedding
from keras.models import Model
import keras

MAX_SEQUENCE_LENGTH = 300
MAX_NUM_WORDS = 60000
EMBEDDING_DIM = 300
VALIDATION_SPLIT = 0.2

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

labels = to_categorical(np.asarray(y))

tokenizer = Tokenizer(nb_words=MAX_NUM_WORDS)
tokenizer.fit_on_texts(dataset['Headline']+dataset['articleBody'])

sequences1 = tokenizer.texts_to_sequences(dataset['Headline'])
sequences2 = tokenizer.texts_to_sequences(dataset['articleBody'])

word_index = tokenizer.word_index
print('Found %s unique tokens.' % len(word_index))

data1 = pad_sequences(sequences1, maxlen=MAX_SEQUENCE_LENGTH)
data2 = pad_sequences(sequences2, maxlen=MAX_SEQUENCE_LENGTH)


embeddings_index = {}
filename = 'glove.6B.300d.txt'
f = open(filename, encoding = 'utf')
for line in f:
    values = line.split()
    word = values[0]
    coefs = np.asarray(values[1:], dtype='float32')
    embeddings_index[word] = coefs
f.close()


embedding_matrix = np.zeros((len(word_index) + 1, EMBEDDING_DIM))
for word, i in word_index.items():
    embedding_vector = embeddings_index.get(word)
    if embedding_vector is not None:
        # words not found in embedding index will be all-zeros.
        embedding_matrix[i] = embedding_vector


embedding_layer = Embedding(len(word_index) + 1,
                            EMBEDDING_DIM,
                            weights=[embedding_matrix],
                            input_length=MAX_SEQUENCE_LENGTH,
                            trainable=False)

left_input = Input(shape=(MAX_SEQUENCE_LENGTH,), dtype='int32')
right_input = Input(shape=(MAX_SEQUENCE_LENGTH,), dtype='int32')

encoded_left = embedding_layer(left_input)
encoded_right = embedding_layer(right_input)

shared_lstm = LSTM(150)
left_output = shared_lstm(encoded_left)
right_output = shared_lstm(encoded_right)

merged_out = keras.layers.concatenate([left_output, right_output], axis = -1)

predictions = Dense(4, activation= 'softmax')(merged_out)
model = Model([left_input, right_input], outputs = predictions)
model.compile(loss='categorical_crossentropy',
              optimizer='rmsprop',
              metrics=['acc'])

# split the data into a training set and a validation set
from sklearn.cross_validation import train_test_split
data1_train, data1_test, data2_train, data2_test, y_train,y_test = train_test_split(data1, data2, labels,test_size = 1/5, random_state = 0)

# happy learning!
model.fit([data1_train, data2_train], y_train,epochs=5)

model.save('model')
model = keras.models.load_model('model') 

y_pred = model.predict([data1_test, data2_test])
y_pred[y_pred > 0.5] = 1
y_pred[y_pred < 0.5] = 0

#model.save('model.h5')


from sklearn.metrics import confusion_matrix
cm = confusion_matrix(y_test.argmax(axis=1), y_pred.argmax(axis=1))


    
    