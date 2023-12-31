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
import copy
import math
from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter
from indexer import FileHandler




class Searcher:
    """
    転置インデックスを作成し、保存するクラス
    """
    def __init__(self, args):
        """
        初期化します
        """
        self.args = args
        self.fileHandler = FileHandler2()
        self.rank = Rank()
        self.makeindex = MakeIndex()


    def run(self):
        """
        インデックスの作成および保存を行う
        """
        try:
            input_path = self.fileHandler.join_path(self.args.input_path)     # inputパス
            serach_word = self.args.search_word
            mode = self.args.mode
            inverted_index_path = self.fileHandler.make_path(input_path, self.args.category)     # 転置インデックスのパス
            inverted_index = self.makeindex.make_inverted_index(inverted_index_path)
            self.serach_class = Serach(inverted_index)
            # 検索モード:single
            if mode == 'single':
                id_list = self.serach_class.serach(serach_word[0])
                self.rank.rank_sort_data(serach_word[0], id_list, input_path, 'tf-idf')
                self.rank.rank_sort_data(serach_word[0], id_list, input_path, 'tf')
            # AND検索
            elif mode == 'and':
                self.serach_class.serach_and(serach_word)
            # OR検索
            elif mode == 'or':
                self.serach_class.serach_or(serach_word)
        except KeyboardInterrupt:
            print('インデックスの作成を終了します')



        


class Serach:
    """
    検索を行うクラス
    """
    def __init__(self, inverted_index):
        self.printMessage = PrintMessage()
        self.inverted_index = inverted_index

    def serach(self, word):
        """
        転置インデックスからワードを検索し文書id一覧を返す。
        見つからなければプログラムを終了する
        """
        if word in self.inverted_index:
            self.printMessage.print_result(self.inverted_index[word])
            return self.inverted_index[word]
        else:
            self.printMessage.not_fund()

    
    def serach_and(self, word):
        """
        転置インデックスからワードをAND検索し文書id一覧を返す。
        見つからなければプログラムを終了する
        """
        # 38 速報
        result = set()
        index1 = self.inverted_index[word[0]]
        index2 = self.inverted_index[word[1]]
        for tmp_id1 in index1:
            copy_index = copy.deepcopy(index2)
            while True:
                index_len = len(copy_index)
                center_index = int(index_len / 2)
                if copy_index[center_index] == tmp_id1:
                    result.add(tmp_id1)
                    break
                elif len(copy_index) == 1:
                    break
                elif copy_index[center_index] < tmp_id1:
                    del copy_index[center_index:]
                elif copy_index[center_index] > tmp_id1:
                    del copy_index[:center_index]
        if len(result) >= 1:
            self.printMessage.print_result(result)
            return result
        else:
            self.printMessage.not_fund()

    def serach_or(self, word):
        """
        転置インデックスからワードをOR検索し文書id一覧を返す。
        見つからなければプログラムを終了する
        """
        result = set()
        if word[0] in self.inverted_index:
            result = set(self.inverted_index[word[0]])
        if word[1] in self.inverted_index:
            index = self.inverted_index[word[1]]
            for tmp in index:result.add(tmp)
        if len(result) >= 1:
            self.printMessage.print_result(result)
            return result
        else:
            self.printMessage.not_fund()

class Rank:
    """
    ランキングを行うクラス
    """
    def __init__(self):
        self.fileHandler = FileHandler()

    def rank_sort_data(self, word, id_list, input_path, type):
        """
        単語からから文書の引数typeのランキングを作成し出力する
        word = 検索ワード
        id_list = 該当する文書idのリスト
        input_path = 入力パス
        type = ランキング種別(ファイル名)
        """
        # ワードのif-idfを読み込む
        idf_path = self.fileHandler.join_path(input_path, type, word+'.pkl')  # idfのパス
        load_tfidf_list = self.fileHandler.open_pkl(idf_path)

        # 該当するtf-idfのみを抽出
        tfidf_list = {} # 該当する文書のifidfの辞書
        for tmp_id in load_tfidf_list:
            if tmp_id in id_list:
                tfidf_list[tmp_id] = load_tfidf_list[tmp_id]

        self.printRank(tfidf_list, f'マッチした文章を{type}でランキングします')

    @staticmethod
    def printRank(dict, detail='ランキング表示します'):
        """
        入力の値からランキング表示します
        input: {文書id:値}, 表示するテキスト
        """
        score_sorted = sorted(dict.items(), reverse=True, key=lambda x:x[1]) # ランク高い順でidの辞書を作成
        print(detail)
        i = 0
        for tmp_tuple in score_sorted:
            i += 1
            print('{: ^5}'.format(i), end=' ')
            print('{: ^15}'.format(tmp_tuple[0]), end=' ')
            print(tmp_tuple[1])
        print('')



class FileHandler2(FileHandler):
    """
    ファイル操作を行うクラスです
    """
    def __init__(self):
        pass

    def make_path(self, input_path, input_category):
        """
        引数に指定されたカテゴリーの転置インデックスのパスを配列で返す
        """
        inverted_index_path = []
        for tmp in input_category:
            inverted_index_path.append(self.join_path(input_path, 'inverted_index', tmp,'inverted_index.pkl'))
        return inverted_index_path




class PrintMessage:
    """
    結果などを表示するためのクラス
    """
    @staticmethod
    def not_fund():
        """
        文書が見つからないことを表示し、プログラムを終了します
        """
        print('文書が見つかりませんでした。')
        sys.exit()
    
    @staticmethod
    def print_result(result):
        """
        入力されたセットから結果を表示します。
        """
        print(len(result),end='')
        print('個の文書が見つかりました :',end='')
        print(result)




class MakeIndex():
    """
    転置インデックスを作成するクラス
    """
    def __init__(self):
        self.fileHandler = FileHandler()

    def make_inverted_index(self,inverted_index_path):
        """
        バイナリファイルを読み込み転置インデックスを結合し返す
        setに変える
        """
        # 転置インデックスを読み込み配列に入れる
        inverted_index_list = []
        for tmp_index_path in inverted_index_path:
            inverted_index_list.append(self.fileHandler.open_pkl(tmp_index_path))

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
        "-w", "--search_word", type=str, required=True, nargs="*",
        help="検索するワードを指定します",
    )
    parser.add_argument(
        "-c", "--category", type=str, required=True, nargs="*",
        help="カテゴリーを指定します",
    )
    parser.add_argument(
        "-m", "--mode", type=str, required=False, default='single',
        help="検索モードを指定します。single=1つのワードの検索 and=2ワードに対してand検索 or=2ワードに対してand検索",
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
