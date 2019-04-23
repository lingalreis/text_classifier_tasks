# -*- coding: utf-8 -*-
# @Time        : 2019/3/13 18:14
# @Author      : tianyunzqs
# @Description : 在线预测

import os
import sys
import pickle
import json

import tensorflow as tf
import numpy as np
import jieba.posseg as pseg

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from text_cnn import TextCNN


def load_stopwords(path):
    stopwords = set([line.strip() for line in open(path, "r", encoding="utf-8").readlines() if line.strip()])
    return stopwords


stopwords = load_stopwords(r"../sample_data/stopwords.txt")
with open("./config_file", encoding="utf8") as f:
    config = json.load(f)


def load_model():
    with tf.Graph().as_default():
        session_conf = tf.ConfigProto(
            allow_soft_placement=config['allow_soft_placement'],
            log_device_placement=config['log_device_placement'])
        sess = tf.Session(config=session_conf)
        with open("./models/vocab33", 'rb') as f:
            vocab_processor = pickle.loads(f.read())
        with sess.as_default():
            cnn = TextCNN(
                sequence_length=config['sequence_length'],
                num_classes=config['num_classes'],
                vocab_size=len(vocab_processor.vocabulary_),
                embedding_size=config['embedding_dim'],
                filter_sizes=list(map(int, config['filter_sizes'].split(","))),
                num_filters=config['num_filters'],
                l2_reg_lambda=config['l2_reg_lambda'])

            saver = tf.train.Saver()  # defaults to saving all variables - in this case w and b
            # Initialize all variables
            sess.run(tf.global_variables_initializer())

            checkpoint_dir = os.path.abspath(os.path.join(os.path.curdir, "checkpoints"))
            ckpt = tf.train.get_checkpoint_state(checkpoint_dir)
            saver.restore(sess, ckpt.model_checkpoint_path)
    return vocab_processor, cnn, sess


vocab_processor, cnn, sess = load_model()


def evaluate_line(text):
    segwords = " ".join([w.word for w in pseg.cut(text) if w.word not in stopwords])
    data = np.array(list(vocab_processor.transform([segwords])))
    feed_dict = {
        cnn.input_x: data,
        cnn.input_y: np.array([[0] * config['num_classes']]),
        cnn.dropout_keep_prob: 1.0
    }
    predictions = sess.run(cnn.predictions, feed_dict)
    label = config['tags'][str(predictions[0])]
    return label


if __name__ == '__main__':
    text = "宏达股份钼铜项目或走他乡 募投恐推倒重来 开工仪式刚刚过去四天,宏达股份(600331)最重要的募投项目就走进了“死胡同”。宏达股份7月5日发布的公告引述当地政府的说法:“什邡今后不再建设这个项目(钼铜多金属资源深加工综合利用项目)”,这意味着钼铜项目已经无缘在什邡市建设。不过,作为四川省重点项目相关公司股票走势,宏达股份也许并不会放弃总投资逾百亿元的钼铜项目。一位什邡市官员透露:“下一步将取决于企业行为,可能会在其他地方重新选址建设。”“娘家”难容身“之所以当初钼铜项目选择在什邡市建设,一是由于宏达股份是本地企业,二是什邡是5·12特大地震的重灾区,希望通过投资拉动本地经济建设”,什邡市委宣传部的一位官员道出了当初引入钼铜多金属资源深加工综合利用项目的初衷。不过,尽管当地政府是为了“在一片废墟上建成灾后美好新家园”,但是由于群众反对,7月3日政府门户网站“什邡之窗”登载了《什邡今后不再建设宏达钼铜项目》的信息。什邡市政府表示:“经市委、市政府研究决定,坚决维护群众的合法权益,鉴于部分群众因担心宏达钼铜项目建成后,会影响环境,危及身体健康,反应十分强烈,决定停止该项目建设,什邡今后不再建设这个项目。”资料显示,钼铜多金属资源深加工综合利用项目主要包括建设钼4万t/a装置、阴极铜40万t/a装置、伴生稀贵金属回收装置、冶炼烟气制硫酸装置等,总投资额101.88亿元。什邡市委宣传部人士表示:“市政府态度已经十分明确,接下来就取决于企业行为了。钼铜项目属国家产业政策鼓励类项目,也是四川省\"十二五规划\"优势特色产业重点项目,可能在其他地方重新选址建设。”作为什邡市的本地企业,宏达股份募投项目遭到“娘家”反对,大大出乎了企业的预料。宏达股份高管4日下午召开了长时间的内部会议,内部人士会后表示,上市公司目前针对钼铜项目如何建设还没有形成具体的方案。董秘王延俊接受中国证券报记者采访时表示:“现在谈论钼铜项目的问题太敏感了,宏达股份的任何表态都会引起市场的波动。如果有新的进展,我们会及时进行披露。”募投恐推倒重来从2010年11月,宏达股份公告开展钼铜多金属资源深加工综合利用项目,到2012年6月末项目开工奠基,前后历经一年半,期间包含了融资、矿产资源储备、环评等众多努力。随着什邡市“不再建”的表态,宏达股份如果希望继续这一投资巨大的募投项目,必须重新选址,前期的项目备案、安全审查、节能审查等工作将会推倒重来。如今摆在宏达股份面前的将是一系列难题。首先,大量的矿产储备如何消化。按照《铜冶炼行业准入条件》,自有矿山原料比例需达到25%以上。为了满足钼铜多金属资源深加工的需要,宏达股份一直在扩张自己的矿产储备。此前,宏达股份矿石原料计划中,40万吨铜金属中50%来自于国内关联方自有矿山和战略关联方。公司7月3日的公告也显示,宏达股份、西藏自治区地质矿产勘查开发局第五地质大队、四川宏达(集团)有限公司、成都沃美东龙投资有限公司签订合作投资协议,拟共同投资设立西藏宏达多龙矿业有限公司,对西藏改则县多龙矿区进行地质勘查开发。如果重新选址,在宏达股份启动新的钼铜项目前,已经储备的大量矿产储备如何处理将是难题。其次,业绩将经受考验。2011年,宏达股份实现净利润5252.74万元,摆脱了2010年巨亏的泥潭,不过之所以业绩翻身主要是由于报告期内公司转让成都置成地产股权实现投资收益7.32亿元。如果钼铜项目短期内难以推进,就宏达股份目前的主营业务来看,铅锌价格震荡下跌,拖累了上市公司的采矿业务;冶炼加工费持续走低、环保成本日益提高等因素,导致公司金属冶炼业务毛利率进一步下滑9.55%,至8.57%。 (来源:中国证券报-中证网)"
    text = "Ivy Bridge平台 【ASUS(华硕) 华硕 M2412系列,索尼 YA2系列 Ivy Bridge平台 笔记本电脑】产品搜索"
    print(evaluate_line(text=text))