import numpy as np

np.random.seed(1337)  # for reproducibility

from keras.models import save_model
from keras.models import Model  # 泛型模型
from keras.layers import Dense, Input
import matplotlib.pyplot as plt
import gensim
# X shape (60,000 28x28), y shape (10,000, )
# (x_train, _), (x_test, y_test) = mnist.load_data()
from wordembedding_vec_util import MySentences, add_all_words_vec_together
sent_list = MySentences('./text/raw')
def sent_vector_gen(sent_tags_list, wordembedding, embedding_dim):
    for sent_tags in sent_tags_list:
        sent_tags = [t.lower() for t in sent_tags]
        yield add_all_words_vec_together(sent_tags, wordembedding, embedding_dim)

loaded_embedding = gensim.models.Word2Vec.load("./text/word_embedding")
sent_vec_list = sent_vector_gen(sent_list,loaded_embedding,400)
sent_vec_list = [s for s in sent_vec_list]
sent_vec_list = np.array(sent_vec_list)
def generate_arrays_from_file(list):
    for vec in list:
        # create Numpy arrays of input data
        # and labels, from each line in the file
        yield (vec,vec)

# model.fit_generator(generate_arrays_from_file('/my_file.txt'),
#                     samples_per_epoch=10000, nb_epoch=10)
# 数据预处理
# x_train = sent_vec_list.astype('float32')  # minmax_normalized
# x_test = sent_vec_list.astype('float32')  # minmax_normalized
x_train = sent_vec_list
x_test = sent_vec_list
x_train = x_train.reshape((x_train.shape[0], -1))
x_test = x_test.reshape((x_test.shape[0], -1))

# print(x_train.shape)
# print(x_test.shape)

# 压缩特征维度至2维
encoding_dim = 2
input_vec_dim = 400
# this is our input placeholder
input_img = Input(shape=(input_vec_dim,))

# 编码层
encoded = Dense(128, activation='relu')(input_img)
encoded = Dense(64, activation='relu')(encoded)
encoded = Dense(10, activation='relu')(encoded)
encoder_output = Dense(encoding_dim)(encoded)

# 解码层
decoded = Dense(10, activation='relu')(encoder_output)
decoded = Dense(64, activation='relu')(decoded)
decoded = Dense(128, activation='relu')(decoded)
decoded = Dense(input_vec_dim, activation='tanh')(decoded)

# 构建自编码模型
autoencoder = Model(inputs=input_img, outputs=decoded)

# 构建编码模型
encoder = Model(inputs=input_img, outputs=encoder_output)

# compile autoencoder
autoencoder.compile(optimizer='adam', loss='mse')

# training
autoencoder.fit(x_train, x_train, epochs=20, batch_size=256, shuffle=True)
# autoencoder.fit_generator(generate_arrays_from_file(sent_vec_list),
#                     samples_per_epoch=10000, nb_epoch=10)
# plotting
encoded_imgs = encoder.predict(x_test)
encoder.save('./model/encoder')

plt.scatter(encoded_imgs[:, 0], encoded_imgs[:, 1], s=3)
# plt.colorbar()
plt.show()