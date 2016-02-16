# -*- coding: utf-8 -*-
__author__ = 'Memray'

from scipy import stats

def if_significant(p_value):
    if(p_value<0.01):
        print(0.01)
    elif(p_value<0.05):
        print(0.05)
    else:
        print('Not significant:'+str(p_value))


def Table1_significance_test():
    print('Word_term-based VS Word_phrase-replaced')
    sig_test = stats.wilcoxon(x=result_arrays['Word_term-based@1'], y=result_arrays['Word_phrase-replaced@1'], zero_method='wilcox', correction=False)
    if_significant(sig_test.pvalue)
    sig_test = stats.wilcoxon(x=result_arrays['Word_term-based@3'], y=result_arrays['Word_phrase-replaced@3'], zero_method='wilcox', correction=False)
    if_significant(sig_test.pvalue)

    print('Word_term-based VS Word_term-phrase-both')
    sig_test = stats.wilcoxon(x=result_arrays['Word_term-based@1'], y=result_arrays['Word_term-phrase-both@1'], zero_method='wilcox', correction=False)
    if_significant(sig_test.pvalue)
    sig_test = stats.wilcoxon(x=result_arrays['Word_term-based@3'], y=result_arrays['Word_term-phrase-both@3'], zero_method='wilcox', correction=False)
    if_significant(sig_test.pvalue)

if __name__ == '__main__':
    RESULT_PATH = "/home/memray/Project/textbook_analyzer/data/result/pipeline/1000_rounds_result_file.txt"
    index_name_dict = {}
    result_arrays = {}
    file = open(RESULT_PATH, 'r')
    for line in file:
        # deal with header
        if line.startswith('Round'):
            tokens = line.split(',')
            for i in range(len(tokens)):
                index_name_dict[i]=tokens[i]
                result_arrays[tokens[i]]=[]
        else:
            tokens = line.split(',')
            for i in range(len(tokens)):
                result_arrays[index_name_dict[i]].append(float(tokens[i]))

    Table1_significance_test()