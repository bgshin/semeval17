from utils.cnn_data_helpers import load_data_and_labels, pad_sentences
import numpy as np
import tensorflow as tf



from cnn_models.w2v_lex_cnn import W2V_LEX_CNN, W2V_LEX_CNN_CONCAT_A2V
from cnn_models.w2v_cnn import W2V_CNN_A2V



model_path = '../data/bestmodel/model-5600'
with tf.Graph().as_default():
    cnn = W2V_CNN_A2V(
        sequence_length=60,
        num_classes=3,
        embedding_size=400,
        filter_sizes=list(map(int, '2,3,4,5'.split(","))),
        num_filters=64,
        attention_depth_w2v=50,
        l2_reg_lambda=0.2,
        l1_reg_lambda=0.0)

    # cnn = W2V_LEX_CNN_CONCAT_A2V(
    #     sequence_length=60,
    #     num_classes=3,
    #     embedding_size=400,
    #     filter_sizes=list(map(int, '2,3,4,5'.split(","))),
    #     num_filters=64,
    #     embedding_size_lex=15,
    #     attention_depth_w2v=50,
    #     attention_depth_lex=20,
    #     l2_reg_lambda=0.2,
    #     l1_reg_lambda=0.0)


    session_conf = tf.ConfigProto(
        allow_soft_placement=True,
        log_device_placement=False)
    sess = tf.Session(config=session_conf)
    with sess.as_default():
        # saver = tf.train.Saver(tf.global_variables())
        # saver.restore(sess, model_path)
        sess.run(tf.global_variables_initializer())

        feed_dict = {
            cnn.input_x: np.random.random((64, 60, 400)),
            cnn.input_y: np.random.random((64, 3)),
            # cnn.input_x_lexicon: np.random.random((64, 60, 15)),
            cnn.dropout_keep_prob: 1.0
        }

        predictions = sess.run([cnn.predictions], feed_dict)

        print len(predictions[0])
        print predictions[0]

        labels = {0: 'negative', 1: 'objective', 2: 'positive'}
        print '%s\n' * 3 % tuple(labels[l] for l in [0,1,2])


"""
dataset = '../data/dataset/dev'

sentences, labels = load_data_and_labels(dataset)
sentences_padded = pad_sentences(sentences, 60)

w2v_dim = 50
w2vmodel={}


def get_index_of_voca(model, word):
    try:
        return model[word]
    except:
        return np.array([np.float32(0.0)]*w2v_dim)


input_x = np.array([np.array([get_index_of_voca(w2vmodel,word) for word in sentence]) for sentence in sentences_padded])


print input_x.shape
"""



