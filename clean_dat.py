#!/bos/usr0/zhuyund/bin/python2.7
import argparse
from boilerpipe.extract import Extractor

import logging
import traceback
import string
import nltk
from os import listdir, makedirs
from os.path import isfile, join, exists


class WarcReader:
    """
    Read trec web files and give document raw text
    """

    def __init__(self, file_path):
        self.f = open(file_path)
        line = self.f.readline()

    def __iter__(self):
        return self

    def next(self):
        """
        :return: the next document
        """
        docno = ""
        line = self.f.readline()  
        if not line:
            raise StopIteration()

        tmp = 0
        while True:
            line = self.f.readline().strip()
            if 'WARC-TREC-ID' in line:
                docno = line.split(' ')[1].strip()
                continue
            if "Content-Length" in line:
                tmp += 1
            if tmp == 2:
                break
        lines = []
        while True:
            line = self.f.readline()
            if not line or "clueweb09-en" in line:
                break
            lines.append(line.strip())
        html_text = ' '.join(lines)
        return docno, html_text


class TrecReader:
    """
    Read warc files and give document raw text
    """

    def __init__(self, file_path):
        self.f = open(file_path)

    def __iter__(self):
        return self

    def next(self):
        """
        :return: the next document
        """
        line = self.f.readline()  # <DOC>
        if not line:
            raise StopIteration()

        line = self.f.readline()  # <DOCNO>
        docno = line.strip().split('>')[1].split('<')[0]

        while True:
            line = self.f.readline().strip()
            if line == "</DOCHDR>":
                break
        lines = []
        while True:
            line = self.f.readline().strip()
            if line == "</DOC>":
                break
            lines.append(line)
        html_text = ' '.join(lines)
        return docno, html_text

def text_clean(text):
    res = text
    res = filter(lambda x: x in string.printable, res)

    ltoken = nltk.word_tokenize(res)
    for i in range(len(ltoken)):
        #token = filter(lambda x: x.isalnum(), ltoken[i])
        token = ltoken[i]
        ltoken[i] = token.lower()
    res = ' '.join(ltoken)
    res = ' '.join(res.split())
    return res


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("raw_file_path")
    parser.add_argument("out_file_path")
    parser.add_argument("--start", "-s", type=int)
    parser.add_argument("--end", "-e", type=int)
    args = parser.parse_args()

    #f_names = [(int(f), f) for f in listdir(args.raw_dir_path)]
    f_names = [args.raw_file_path]
    f_names = sorted(f_names)
    fout = open(args.out_file_path, 'w')

    for f_name in f_names:
        #trec_reader = WarcReader(join(args.raw_dir_path, f_name))
        trec_reader = WarcReader(f_name)
        total_cnt = 0
        empty_cnt = 0
        err_cnt = 0

        for docno, html_text in trec_reader:
            total_cnt += 1
            if total_cnt < args.start:
                continue
            if total_cnt > args.end:
                break
            if not html_text:
                empty_cnt += 1
            try:
                extractor = Extractor(extractor='ArticleExtractor', html=html_text)
                text = extractor.getText()
                text = text.replace('\n', ' ').replace('\t', ' ')
                text = text.encode('ascii', 'ignore')
                text = text_clean(text)
                if text:
                    fout.write(docno + '\t' + text + '\n')
                else:
                    empty_cnt += 1
            except Exception as e:
                err_cnt += 1

    fout.close()
    print empty_cnt, err_cnt

if __name__ == '__main__':
    main()
