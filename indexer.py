#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
転置インデックスで索引を作り、バイナリデータとして保存するプログラム
"""

__author__ = 'Ayumu Sakai'
__version__ = '1.0.0'
__date__ = '2023/10/25 (Created: 2023/10/25)'

import json
from operator import inv
import os
from re import S
import sys
import glob
import MeCab
import math
import pickle
import matplotlib.pyplot as plt
from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter



class Indexer:
    """
    転置インデックスを作成し、保存するクラス
    """
    def __init__(self, args):
        """
        初期化します
        """
        self.args = args

    def run(self):
        """
        インデックスの作成および保存を行う
        """
        try:
            input_path = self.join_path(self.args.input_path)     # inputパス
            self.output_path = self.join_path(self.args.output_path)   # outputパス
            json_list = self.read_json(input_path, self.args.category) # ファイル一覧を取得し、jsonファイルを読み込み辞書にして返す
            category_set = self.make_category_set(json_list)  # set(カテゴリー)を作成
            category_id = self.make_category_id(json_list)    # {id:カテゴリー}を作成
            word_dict = self.morphological_analysis(json_list) # 形態素解析行う {id:[[word_list],(word_set)]}
            word_count_dict = self.make_word_count(word_dict) # 文書内の回数リストを作成
            tf_dict = self.count_tf(json_list, word_count_dict) #tf値を計算する
            frequency = self.make_frequency(self.make_word_count(word_dict)) # 頻度を作成する
            self.make_plot(frequency) # プロットを作成する
            word_count_dict = self.make_word_count(word_dict)
            idf_dict = self.count_idf(json_list, word_count_dict) # idfを計算する
            self.count_tf_idf(tf_dict, idf_dict) # idfインデックスを作成
            self.make_tf(tf_dict)
            self.make_inverted_index(word_dict,category_id, category_set) # 転置インデックスを作成
        except KeyboardInterrupt:
            print('インデックスの作成を終了します')
    
    @staticmethod
    def join_path(*a_tuple):
        """
        ファイルをのディレクトリを返す。
        引数(*a_tuple)は複数の引数をタプルとして受け取る
        """
        return os.path.join(*a_tuple)
    
    @staticmethod
    def open_file_list(input_path, input_category):
        """
        引数に指定されたファイルないのファイル名の配列を返す。
        input_path:　入力ディレクトリ
        input_category: 転置インデックスを作成する対象カテゴリ
        """
        file_path = [] # フォルダ一覧
        for tmp_category in input_category:
            path = os.path.join(input_path,tmp_category,'*.json')
            files = glob.glob(path)
            for path in files:
                file_path.append(path)
        return file_path
    
    def read_json(self,input_path, input_category):
        """
        引数のパスの辞書からjsonを読み込む。
        jsonからtitleとbodyのみの辞書をリスト形式で返す。
        """
        path = self.open_file_list(input_path, input_category)
        json_list = []
        for tmp_path in path:
            with open(tmp_path) as f:
                json_raw_data = json.load(f)
            del  json_raw_data['url']
            json_list.append(json_raw_data)
        return json_list
    
    @staticmethod
    def make_category_set(json_list):
        """
        output内全てのカテゴリーのセットを作成し返す
        """
        category_set = set()
        for json_tmp in json_list:
            category_set.add(json_tmp['category'])
        return category_set
    
    @staticmethod
    def make_category_id(json_list):
        """
        json_listからカテゴリーとidの辞書リストを作成し返す
        return {id: category}
        """
        category_id = {}
        for json_tmp in json_list:
            category_id[json_tmp['id']] = json_tmp['category']
        return category_id
    
    @staticmethod
    def morphological_analysis(json_list):
        """
        入力の辞書リストから形態素解析を行い単語を返す。
        return {id:[[word_list],(word_set)]}  <2>
        """
        word_dict = {}
        for article in json_list:
            text = article['title'] + '\n' + article['body']
            tagger = MeCab.Tagger('')
            tagger.parse('')
            node = tagger.parseToNode(text)
            word_set = set()
            word_list = []
            while node:
                term = node.surface
                pos = node.feature.split(',')[0]
                if pos in '名詞':
                    word_set.add(term)
                    word_list.append(term)
                node = node.next
            word_dict[article['id']] = [word_list, word_set]
        return word_dict
    
    @staticmethod
    def make_word_count(word_dict):
        """
        ワードごとに回数リストを作成する。
        return {id:{word:回数}}<3>
        """
        word_count_dict = {}
        for article in word_dict:       # 全てのidで繰り返し
            word_count = {}
            for word in word_dict[article][1]:  # setのみを抽出
                word_count[word] = word_dict[article][0].count(word)
            word_count_dict[article] = word_count
        return word_count_dict

    @staticmethod
    def count_tf(json_list, word_count_dict, *category):
        """
        tfを計算を行う
        入力のカテゴリーのもので計算を行う
        引数 json_list, word_count_dict, *カテゴリー
        カテゴリーの引数がない場合は全てのカテゴリーで実行
        return {id:{word:tf}}
        参考：https://atmarkit.itmedia.co.jp/ait/articles/2112/23/news028.html
        """
        input_dict = {}
        if(len(category)==0):
            input_dict = word_count_dict
        else:
            for tmp_json in json_list: #全ての入力を結合
                if(tmp_json['category'] in category):
                    tmp_dict = {tmp_json['id']:word_count_dict.get(tmp_json['id'])}
                    input_dict |= tmp_dict
        all_count_dict = {} #文章内の単語数を計算
        for id in input_dict:
            count = 0
            for key in input_dict[id]:
                count += input_dict[id][key]
            all_count_dict[id] = count
        
        for id in input_dict:
            for key in input_dict[id]:
                input_dict[id][key] = input_dict[id][key] / all_count_dict[id] # tfを計算する。文書内での出現回数 / 文章ないの個数出現回数
        return input_dict
    
    @staticmethod
    def make_frequency_list(frequency):
        """
        tf値を頻度とその降順のx,yの配列で返す
        """
        cie_x = []
        for i in range(len(frequency)):
            frequency[i] = math.log(frequency[i])
            cie_x.append(math.log(i+1))
        frequency.sort(reverse=True)
        cie = [[cie_x],[frequency]]
        return cie
    
    def make_plot(self, frequency):
        """
        配列からグラフを作成する
        """
        cie = self.make_frequency_list(frequency)
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.scatter(cie[0], cie[1])
        ax.set_xlabel("rank(log)")
        ax.set_ylabel("frequency(log)")
        plt.show()

    @staticmethod
    def count_idf(json_list, word_count_dict, *category):
        """
        idfを計算する
        return {id:{word:idf}}
        """
        input_dict = {}
        if(len(category)==0):
            input_dict = word_count_dict
        else:
            for tmp_json in json_list: #全ての入力を結合
                if(tmp_json['category'] in category):
                    tmp_dict = {tmp_json['id']:word_count_dict.get(tmp_json['id'])}
                    input_dict |= tmp_dict
        
        count_id = len(input_dict) # 全文書数
        count_word = {} # 単語が出現する文書数
        word_set = set()
        # setを作る
        for tmp in input_dict:
            for key in input_dict.get(tmp):
                word_set.add(key)
        
        # setから0の辞書を作成
        for tmp in word_set:
            count_word[tmp] = 0
        
        # ワードが出現する文書数を数える
        for tmp_set in word_set: # キーワードに対して繰り返し
            for tmp in input_dict:
                for key in input_dict.get(tmp):
                    if(key==tmp_set):
                        count_word[tmp_set] += 1
                        break
        
        #idfを計算
        for key in count_word:
            count_word[key] = math.log(count_id / count_word[key])
        return count_word
    
    def count_tf_idf(self, tf_dict, idf_dict):
        """
        tfとidfからtf-idfを計算し、インデックスを作成し保存する
        index= {word:[{id:tf-idf}]}
        インデックスの形式 ファイル名:{word}.pkl -> {id:idf} <3>
        """
        index = {} #tfidfインデックス
        for id in tf_dict:
            for word in tf_dict[id]:
                tf_idf = tf_dict[id][word] * idf_dict[word]
                if word in index:
                    # 既にwordが存在する場合
                    index[word] |= {id:tf_idf}
                else:
                    # wordが存在しない場合(新規作成)
                    index[word] = {id:tf_idf}
        # 単語ごとに保存する
        path = self.join_path(self.output_path, 'idf')
        for word_index in index:
            self.perpetuation(index[word_index], path, word_index)

    
    def make_tf(self, tf_dict):
        """
        tfとidfからtf-idfを計算し、インデックスを作成し保存する
        index= {word:[{id:tf-idf}]}
        インデックスの形式 ファイル名:{word}.pkl -> {id:idf}
        """
        index = {} #tfidfインデックス
        for id in tf_dict:
            for word in tf_dict[id]:
                tf = tf_dict[id][word]
                if word in index:
                    # 既にwordが存在する場合
                    index[word] |= {id:tf}
                else:
                    # wordが存在しない場合(新規作成)
                    index[word] = {id:tf}
        # 単語ごとに保存する
        path = self.join_path(self.output_path, 'tf')
        for word_index in index:
            self.perpetuation(index[word_index], path, word_index)

    @staticmethod
    def make_frequency(word_count_dict):
        """
        プロット用の頻度を計算し返します。
        return frequency[頻度,,,] (降順)
        """
        frequency = [] #頻度
        word_count = {} #単語:回数
        all_count = 0 # 全体の回数

        # ワードごとの回数を集計する
        for tmp_id in word_count_dict:
            for tmp_word in word_count_dict[tmp_id]:
                tmp_count = word_count_dict[tmp_id][tmp_word]
                if tmp_word in word_count:
                    word_count[tmp_word] += tmp_count
                else:
                    word_count[tmp_word] = tmp_count
                all_count += tmp_count
        
        # 辞書から頻度を作成
        for tmp_id in word_count:
            frequency.append(word_count[tmp_id] / all_count)
        return frequency
        
    
    
    def make_inverted_index(self, word_dict, category_id, category_set):
        """
        転置インデックスを作成し、保存する
        {word:[id]}
        """
        # 空の辞書を作成
        inverted_index = {} #転置インデックス {category:{word:[id]}}
        for tmp in category_set:
            inverted_index[tmp] = {}

        for tmp_id in word_dict:   # idごとに繰り返し
            tmp_category = category_id[tmp_id]
            for tmp_word in word_dict[tmp_id][1]:  # 各idごとのワードを取り出す
                if tmp_word in inverted_index[tmp_category]:
                    # 既にwordが存在する場合
                    inverted_index[tmp_category][tmp_word].append(tmp_id)
                else:
                    # wordが存在しない場合(新規作成)
                    inverted_index[tmp_category][tmp_word] = [tmp_id]
        # カテゴリーごとに保存する
        for tmp_category in inverted_index:
            path = self.join_path(self.output_path, 'inverted_index', tmp_category)
            self.perpetuation(inverted_index[tmp_category], path, 'inverted_index')


    @staticmethod
    def make_directories(path):
        """
        出力するディレクトリを作成する
        """
        os.makedirs(path, exist_ok=True)
    
    def perpetuation(self, keep_var, output_path, filename):
        """
        引数から入力された変数をバイナリデータとして保存する
        """
        self.make_directories(output_path)
        output_path = self.join_path(output_path, filename+'.pkl')
        with open(output_path,'wb') as f:
            pickle.dump(keep_var, f)

def get_args():
    """
    コマンドライン引数を応答します
    """
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "--category", nargs='*', required=True,
        help="転置インデックスを作成するカテゴリーを指定する。２種類以上のカテゴリーを入力した場合には組み合わせたインデックスを作成する。",
    )
    parser.add_argument(
        "-o", "--output_path", type=str, required=False, default='index',
        help="出力ディレクトリ名を指定します",
    )
    parser.add_argument(
        "-i", "--input_path", type=str, required=False, default='output',
        help="入力ディレクトリ名を指定します",
    )
    return parser.parse_args()


def main():
    """
    メイン（main）プログラムです
    常に0を応答します
    """
    args = get_args()
    app = Indexer(args)
    app.run()
    return 0


if __name__ == '__main__':
    sys.exit(main())
