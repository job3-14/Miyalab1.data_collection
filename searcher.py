#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
サーチャー
バイナリデータとして保存した索引を読み込み検索をする。
"""

__author__ = 'Ayumu Sakai'
__version__ = '1.0.0'
__date__ = '2023/10/31'

from operator import inv
import os
from re import S
import sys
import pickle
import matplotlib.pyplot as plt
from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter




class Searcher:
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
            inverted_index_path = self.make_path(input_path, self.args.category)     # 転置インデックスのパス
            self.inverted_index = self.make_inverted_index(inverted_index_path)
            id_list = self.serach(self.args.search_word)
            self.rank_tf_idf(self.args.search_word, id_list, input_path)

        except KeyboardInterrupt:
            print('インデックスの作成を終了します')
    
    @staticmethod
    def join_path(*a_tuple):
        """
        ファイルをのディレクトリを返す。
        引数(*a_tuple)は複数の引数をタプルとして受け取る
        """
        return os.path.join(*a_tuple)
    
    def make_path(self, input_path, input_category):
        """
        引数に指定されたカテゴリーの転置インデックスのパスを配列で返す
        """
        inverted_index_path = []
        for tmp in input_category:
            inverted_index_path.append(self.join_path(input_path, 'inverted_index', tmp,'inverted_index.pkl'))
        return inverted_index_path
    
    def make_inverted_index(self,inverted_index_path):
        """
        バイナリファイルを読み込み転置インデックスを結合し返す
        """
        # 転置インデックスを読み込み配列に入れる
        inverted_index_list = []
        for tmp_index_path in inverted_index_path:
            inverted_index_list.append(self.load_pkl(tmp_index_path))

        # 転置インデックスを結合する
        inverted_index = {}
        for tmp_index in inverted_index_list:
            for word in tmp_index:
                # キーが存在した場合
                if word in inverted_index:
                    inverted_index[word] += tmp_index[word]
                # キーが存在しなかった場合
                else:
                    inverted_index[word] = tmp_index[word]
        return inverted_index
        
    

    def load_pkl(self, input_path):
        """
        バイナリファイルを読み込み辞書を返す。
        """
        with open(input_path, mode='rb') as f:
            dict = pickle.load(f)
        return dict
    
    def serach(self, word):
        """
        転置インデックスからワードを検索し文書id一覧を返す。
        見つからなければ-1を返す
        """
        if word in self.inverted_index:
            print(len(self.inverted_index[word]),end='')
            print('個の文書が見つかりました :',end='')
            print(self.inverted_index[word])
            print('')
            return self.inverted_index[word]
        else:
            print('文書が見つかりませんでした。')
            sys.exit()
    

    def rank_tf_idf(self, word, id_list, input_path):
        """
        単語からから文書のtf-idfのランキングを作成し出力する
        word = 検索ワード
        id_list = 該当する文書idのリスト
        input_path = 入力パス
        """
        # ワードのif-idfを読み込む
        idf_path = self.join_path(input_path, 'idf', word+'.pkl')  # idfのパス
        load_tfidf_list = self.load_pkl(idf_path)

        # 該当するtf-idfのみを抽出
        tfidf_list = {} # 該当する文書のifidfの辞書
        for tmp_id in load_tfidf_list:
            if tmp_id in id_list:
                tfidf_list[tmp_id] = load_tfidf_list[tmp_id]

        # tf-idfでランキングを作成する(ランク高い順でidの辞書を作成
        score_sorted = sorted(tfidf_list.items(), reverse=True, key=lambda x:x[1])
        print('マッチした文章をtd-idfでランキングします')
        i = 0
        for tmp_tuple in score_sorted:
            i += 1
            print('{: ^5}'.format(i), end=' ')
            print('{: ^15}'.format(tmp_tuple[0]), end=' ')
            print(tmp_tuple[1])
            

def get_args():
    """
    コマンドライン引数を応答します
    """
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "-i", "--input_path", type=str, required=False, default='index',
        help="入力フォルダを指定します",
    )
    parser.add_argument(
        "-w", "--search_word", type=str, required=True,
        help="検索するワードを指定します",
    )
    parser.add_argument(
        "-c", "--category", type=str, required=True, nargs="*",
        help="カテゴリーを指定します",
    )
    return parser.parse_args()


def main():
    """
    メイン（main）プログラムです
    常に0を応答します
    """
    args = get_args()
    app = Searcher(args)
    app.run()
    return 0


if __name__ == '__main__':
    sys.exit(main())
