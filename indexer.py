#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
転置インデックスで索引を作り、バイナリデータとして保存するプログラム
"""

__author__ = 'Ayumu Sakai'
__version__ = '1.0.0'
__date__ = '2023/10/25 (Created: 2023/10/25)'

import json
import os
import sys
import glob
import MeCab
import math
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
            input_path = self.join_path(self.args.input_path)
            output_path = self.join_path(self.args.output_path)
            json_list = self.read_json(self.open_file_list(input_path, self.args.category)) # ファイル一覧を取得し、jsonを開き辞書にして返す
            word_dict = self.morphological_analysis(json_list)
            tf_dict = self.count_tf(json_list, self.make_word_count(word_dict), 'society', 'government', 'sports')
            self.make_plot(self.make_tf(tf_dict))


            

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
    def open_file_list(input_path, category):
        """
        引数に指定されたファイルないのファイル名の配列を返す。
        input_path:　入力ディレクトリ
        category: 転置インデックスを作成する対象カテゴリ
        """
        file_path = [] # フォルダ一覧
        for list in category:
            path = os.path.join(input_path, list)
            for j in glob.iglob(f'{path}/*.json'):
                file_path.append(j)
        return file_path
    
    @staticmethod
    def read_json(path):
        """
        引数のパスの辞書からjsonを読み込む。
        jsonからtitleとbodyのみの辞書をリスト形式で返す。
        """
        json_list = []
        for tmp_path in path:
            with open(tmp_path) as f:
                json_raw_data = json.load(f)
            del  json_raw_data['url']
            json_list.append(json_raw_data)
        return json_list
    
    @staticmethod
    def morphological_analysis(json_list):
        """
        入力の辞書リストから形態素解析を行い単語を返す。
        return {id:[[word_list],(word_set)]}
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
        return {id:{word:回数}}
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
        引数 
        return {id:{word:tf}}
        参考：https://atmarkit.itmedia.co.jp/ait/articles/2112/23/news028.html
        """
        input_dict = {}
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
    def make_tf(tf_dict):
        """
        tf値を頻度とその降順のx,yの配列で返す
        """
        frequency = [] # 頻度
        for id in tf_dict:
            for key in tf_dict[id]:
                frequency.append(math.log(tf_dict[id][key]))
        frequency.sort(reverse=True)
        cie_x = []
        for i in range(len(frequency)):
            cie_x.append(math.log(i+1))
        cie = [[cie_x],[frequency]]
        return cie
    
    @staticmethod
    def make_plot(cie):
        """
        配列からグラフを作成する
        """
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.scatter(cie[0], cie[1])
        plt.show()




        


        


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
