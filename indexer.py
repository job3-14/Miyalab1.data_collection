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
            json_list = self.read_json(self.open_file_list(input_path, self.args.category))
            word_dict = self.morphological_analysis(json_list)
            self.count_tf(self.make_word_count(word_dict))

            

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
            del json_raw_data['category'], json_raw_data['url']
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
    def count_tf(*word_count_dict):
        """
        tfを計算を行う
        入力した全てのもので計算を行う
        return {id:{word:tf}}
        """
        input_dict = {}
        for i in range(len(word_count_dict)): #全ての入力を結合
            input_dict |= word_count_dict[i]

        word_set = set() # ワードのキーを作成する
        for id in input_dict:
            for key in input_dict[id].keys():
                word_set.add(key)

        word_all_count = {} # ワードに対する全体の個数を計算する
        for serach_word in word_set:
            count = 0
            for id in input_dict: # idごとに抽出
                tmp = input_dict[id].get(serach_word,-1)
                if tmp != -1:
                    count += tmp
            word_all_count[serach_word] = count
        
        for id in input_dict:
            for key in input_dict[id]:
                input_dict[id][key] = input_dict[id][key] / word_all_count[key] # tfを計算する。文書内での出現回数 / 全ての文章での出現回数
        return input_dict




        


        


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
