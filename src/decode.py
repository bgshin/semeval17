#! /usr/bin/env python
'''
 Copyright 2016, Emory University

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
'''
import tensorflow as tf
import numpy as np
import os
import time
import datetime
import gc
import argparse
import sys
from utils import cnn_data_helpers
from utils.butils import Timer
from cnn_models.w2v_cnn import W2V_CNN, W2V_CNN_A2V
from cnn_models.w2v_lex_cnn import W2V_LEX_CNN, W2V_LEX_CNN_CONCAT_A2V
import utils.word2vecReaderUtils as utils

from utils.cnn_data_helpers import load_w2v_withpath
from utils.cnn_data_helpers import load_lexicon_unigram, load_w2v

# Parameters
# ==================================================

# Model Hyperparameters
tf.flags.DEFINE_string("filter_sizes", "2,3,4,5", "Comma-separated filter sizes (default: '3,4,5')")
tf.flags.DEFINE_float("dropout_keep_prob", 0.8, "Dropout keep probability (default: 0.5)")
# Training parameters
tf.flags.DEFINE_integer("batch_size", 64, "Batch Size (default: 64)")
tf.flags.DEFINE_integer("evaluate_every", 100, "Evaluate model on dev set after this many steps (default: 100)")
# Misc Parameters
tf.flags.DEFINE_boolean("allow_soft_placement", True, "Allow device soft device placement")
tf.flags.DEFINE_boolean("log_device_placement", False, "Log placement of ops on devices")

FLAGS = tf.flags.FLAGS
FLAGS._parse_flags()
# print("\nParameters:")
# for attr, value in sorted(FLAGS.__flags.items()):
#     print("{}={}".format(attr.upper(), value))
# print("")

# run_test(args.m, args.v, args.l, args.i)
def run_test(model_name, model_path, w2v_path, lex_path_list, input_path, output_fn):
    max_len = 60
    w2vnumfilters = 64
    lexnumfilters = 9
    l2_reg_lambda = 2.0
    l1_reg_lambda = 0.0


    w2vdim = 0
    lexdim = 0

    with utils.smart_open(w2v_path) as fin:
        header = utils.to_unicode(fin.readline())
        w2vdim = int(header.split(' ')[1].strip())

    with Timer("w2v"):
        w2vmodel = load_w2v_withpath(w2v_path)

    with Timer("lex"):
        norm_model, raw_model = load_lexicon_unigram(lex_path_list)

    for model_idx in range(len(norm_model)):
        lexdim += len(norm_model[model_idx].values()[0])

    unigram_lexicon_model = norm_model

    x_sample, x_lex_sample, ids = cnn_data_helpers.load_test_data(input_path, w2vmodel, unigram_lexicon_model, max_len)

    del(w2vmodel)
    gc.collect()


    with tf.Graph().as_default():
        session_conf = tf.ConfigProto(
          allow_soft_placement=FLAGS.allow_soft_placement,
          log_device_placement=FLAGS.log_device_placement)
        sess = tf.Session(config=session_conf)
        with sess.as_default():
            if model_name == 'W2V':
                cnn = W2V_CNN(
                    sequence_length=max_len,
                    num_classes=3,
                    embedding_size=w2vdim,
                    filter_sizes=list(map(int, FLAGS.filter_sizes.split(","))),
                    num_filters=w2vnumfilters,
                    l2_reg_lambda=l2_reg_lambda,
                    l1_reg_lambda=l1_reg_lambda)

            elif model_name == 'W2VLEX':
                cnn = W2V_LEX_CNN(
                    sequence_length=max_len,
                    num_classes=3,
                    embedding_size=w2vdim,
                    embedding_size_lex=lexdim,
                    num_filters_lex=lexnumfilters,
                    filter_sizes=list(map(int, FLAGS.filter_sizes.split(","))),
                    num_filters=w2vnumfilters,
                    l2_reg_lambda=l2_reg_lambda,
                    l1_reg_lambda=l1_reg_lambda)

            elif model_name == 'W2VATT':
                cnn = W2V_CNN_A2V(
                    sequence_length=max_len,
                    num_classes=3,
                    embedding_size=w2vdim,
                    filter_sizes=list(map(int, FLAGS.filter_sizes.split(","))),
                    num_filters=w2vnumfilters,
                    attention_depth_w2v=50,
                    l2_reg_lambda=l2_reg_lambda,
                    l1_reg_lambda=l1_reg_lambda)

            elif model_name == 'W2VLEXATT':
                cnn = W2V_LEX_CNN_CONCAT_A2V(
                    sequence_length=max_len,
                    num_classes=3,
                    embedding_size=w2vdim,
                    filter_sizes=list(map(int, FLAGS.filter_sizes.split(","))),
                    num_filters=w2vnumfilters,
                    embedding_size_lex=lexdim,
                    attention_depth_w2v=50,
                    attention_depth_lex=20,
                    l2_reg_lambda=l2_reg_lambda,
                    l1_reg_lambda=l1_reg_lambda)

            else:
                cnn = W2V_LEX_CNN(
                    sequence_length=max_len,
                    num_classes=3,
                    embedding_size=w2vdim,
                    embedding_size_lex=lexdim,
                    num_filters_lex=lexnumfilters,
                    filter_sizes=list(map(int, FLAGS.filter_sizes.split(","))),
                    num_filters=w2vnumfilters,
                    l2_reg_lambda=l2_reg_lambda,
                    l1_reg_lambda=l1_reg_lambda)

            saver = tf.train.Saver(tf.global_variables())
            saver.restore(sess, model_path)

            def get_prediction(x_batch, x_batch_lex=None):
                if x_batch_lex is None:
                    feed_dict = {
                        cnn.input_x: x_batch,
                        cnn.input_y: np.array([[1,0,0]]),
                        cnn.dropout_keep_prob: 1.0
                    }
                else:
                    feed_dict = {
                        cnn.input_x: x_batch,
                        cnn.input_y: np.array([[1,0,0]]),
                        cnn.input_x_lexicon: x_batch_lex,
                        cnn.dropout_keep_prob: 1.0
                    }

                predictions = sess.run([cnn.predictions], feed_dict)
                print 'len(predictions)', len(predictions)
                return predictions[0]

            if model_name == 'W2V' or model_name == 'W2VATT':
                predictions = get_prediction(x_sample)
            else:
                predictions = get_prediction(x_sample, x_lex_sample)

            labels={0:'negative', 1:'neutral', 2:'positive'}
            # print '%s\n'*len(x_sample) % tuple(labels[l] for l in predictions)
            with open(output_fn, 'wt') as out:
                for idx in range(len(x_sample)):
                    out.write( '%s\t%s\n' % (ids[idx], labels[predictions[idx]]) )


def get_lex_file_list(lexfile_path):
    lex_file_list = []
    with open(lexfile_path, 'rt') as handle:
        for line in handle.readlines():
            path = line.strip()

            if os.path.isfile(path):
                lex_file_list.append(path)
            else:
                print 'wrong file name(s) in the lex_config.txt\n%s' % path
                return None

    return lex_file_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # python decode.py -m model_file -l lex_config.txt -i input_data
    parser.add_argument('-mp', default='../data/bestmodel/', type=str)
    parser.add_argument('-v', default='../data/w2v/w2v-400.bin', type=str)  # w2v-400.bin
    parser.add_argument('-l', default='../data/lex_config.txt', type=str)
    parser.add_argument('-i', default='../data/dataset/tst', type=str)
    parser.add_argument('-m', default='W2V', choices=['W2V', 'W2VATT', 'W2VLEX', 'W2VLEXATT'],
                        type=str)  # model_file
    parser.add_argument('-c', default='0', type=str)  # cuda
    parser.add_argument('-a', default='0', type=int)  # attempt

    args = parser.parse_args()
    program = os.path.basename(sys.argv[0])

    # print 'model: %s\n' % (args.model)

    if args.l == 'none':
        lex_list = []
    else:
        lex_list = get_lex_file_list(args.l)

    # if not os.path.isfile(args.mp):
    #     print 'wrong model path name\n%s' % args.mp
    #     exit()

    if not os.path.isfile(args.v):
        print 'wrong file name for the w2v binary\n%s' % args.v
        exit()

    if not os.path.isfile(args.i):
        print 'wrong input file name\n%s' % args.i
        exit()

    if lex_list == None:
        exit()

    for l in lex_list:
        print l

    os.environ["CUDA_VISIBLE_DEVICES"] = args.c

    model_file_name = args.mp + '%s.%s.%d.model' % (
        args.m, args.v.split('/')[-1].replace('.bin', ''), args.a)

    output_fn = '../data/output/%s.%s.%d.txt' % (
        args.m, args.v.split('/')[-1].replace('.bin', ''), args.a)

    print model_file_name

    with Timer("decode..."):
        run_test(args.m, model_file_name, args.v, lex_list, args.i, output_fn)

    # python decode.py -m ./mymodel2 -v ../data/emory_w2v/w2v-50.bin  -l lex_config2.txt -i ../data/tweets/sample
