# -*- coding: utf-8 -*-
__author__ = 'Memray'

from scipy import stats
import numpy

def stat(name):
    print(name+'\t@1 mean:{0}\tvar:{1}'.format(numpy.mean(result_arrays[name+'@1']),numpy.std(result_arrays[name+'@1'])))
    print(name+'\t@3 mean:{0}\tvar:{1}'.format(numpy.mean(result_arrays[name+'@3']),numpy.std(result_arrays[name+'@3'])))
def sig(name1, name2):
    x=result_arrays[name1+'@1']
    y=result_arrays[name2+'@1']
    sig_test = stats.wilcoxon(x, y, zero_method='wilcox', correction=False)
    print(name1+' Vs. '+name2)
    print('\t@1 '+str(sig_test.pvalue))
    x=result_arrays[name1+'@3']
    y=result_arrays[name2+'@3']
    sig_test = stats.wilcoxon(x, y, zero_method='wilcox', correction=False)
    print('\t@3 '+str(sig_test.pvalue))

def do_significance_test(name1, name2, k=1):
    global result_arrays
    # Test for @1
    x=result_arrays[name1+'@'+str(k)]
    y=result_arrays[name2+'@'+str(k)]
    mean_x = numpy.mean(x)
    mean_y = numpy.mean(y)
    sig_test = stats.wilcoxon(x, y, zero_method='wilcox', correction=False)
    # print(numpy.mean(x),numpy.var(x),numpy.mean(y),numpy.var(y),if_significant(sig_test.pvalue))

    if(sig_test.pvalue<0.001):
        return('<0.001')
    # elif(p_value<0.05):
    #     print(0.05)
    else:
        return (str(sig_test.pvalue))


def Table1_significance_test():
    do_significance_test('Word_term-based','Word_phrase-replaced')
    # print('Word_term-based VS Word_phrase-replaced')
    # sig_test = stats.wilcoxon(x=result_arrays['Word_term-based@1'], y=result_arrays['Word_phrase-replaced@1'], zero_method='wilcox', correction=False)
    # if_significant(sig_test.pvalue)
    # sig_test = stats.wilcoxon(x=result_arrays['Word_term-based@3'], y=result_arrays['Word_phrase-replaced@3'], zero_method='wilcox', correction=False)
    # if_significant(sig_test.pvalue)

    do_significance_test('Word_term-based','Word_term-phrase-both')
    # print('Word_term-based VS Word_term-phrase-both')
    # sig_test = stats.wilcoxon(x=result_arrays['Word_term-based@1'], y=result_arrays['Word_term-phrase-both@1'], zero_method='wilcox', correction=False)
    # if_significant(sig_test.pvalue)
    # sig_test = stats.wilcoxon(x=result_arrays['Word_term-based@3'], y=result_arrays['Word_term-phrase-both@3'], zero_method='wilcox', correction=False)
    # if_significant(sig_test.pvalue)

if __name__ == '__main__':
    # RESULT_PATH = "/home/memray/Project/textbook_analyzer/data/result/pipeline/1000_rounds_result_file.txt"
    RESULT_PATH = "/home/memray/Desktop/algebra_result_file.txt"
    index_name_dict = {}
    result_arrays = {}

    term_only = 'Word_term-based'
    concept_only = 'pure_Keyword-stemmed'
    lda_only = 'pure_LDA_textbook_two_200'
    lda_only_book5 = 'pure_LDA_textbook_all_200'
    term_lda = 'LDA_textbook_two_200'
    term_concept = 'Keyword-stemmed'
    term_lda_book2_sigir_all = 'LDA_textbook_two+sigir_all_100'
    term_lda_book2_sigir_1971 = 'LDA_textbook_two+sigir_1971-2001_150'
    term_lda_book2_sigir_2002 = 'LDA_textbook_two+sigir_2002-2008_150'
    term_lda_book2_sigir_2009 = 'LDA_textbook_two+sigir_2009-2015_150'
    term_lda_book2_sigir_high = 'LDA_textbook_two+sigir_citation-high_200'
    term_lda_book2_sigir_medium = 'LDA_textbook_two+sigir_citation-medium_150'
    term_lda_book2_sigir_low = 'LDA_textbook_two+sigir_citation-low_150'

    term_lda_book5 = 'LDA_textbook_all_200'
    term_lda_book5_sigir_all = 'LDA_textbook_all+sigir_all_100'
    term_lda_book5_sigir_1971 = 'LDA_textbook_all+sigir_1971-2001_150'
    term_lda_book5_sigir_2002 = 'LDA_textbook_all+sigir_2002-2008_200'
    term_lda_book5_sigir_2009 = 'LDA_textbook_all+sigir_2009-2015_100'
    term_lda_book5_sigir_high = 'LDA_textbook_all+sigir_citation-high_150'
    term_lda_book5_sigir_medium = 'LDA_textbook_all+sigir_citation-medium_100'
    term_lda_book5_sigir_low = 'LDA_textbook_all+sigir_citation-low_200'

    global result_arrays
    file = open(RESULT_PATH, 'r')
    for line in file:
        # print(line)
        if(line.strip()==''):
            continue
        model_name = line[:line.index('\t')]
        values = [float(x) for x in line[line.index('\t')+1:].strip().split(',')]
        result_arrays[model_name] = values
    baseline_mean_1 = numpy.mean(result_arrays['Word_term-based@1'])
    baseline_mean_3 = numpy.mean(result_arrays['Word_term-based@3'])
    print('Baseline')
    print('\tmean:{0}\tvar:{1}'.format(numpy.mean(result_arrays['Word_term-based@1']),numpy.std(result_arrays['Word_term-based@1'])))
    print('\tmean:{0}\tvar:{1}'.format(numpy.mean(result_arrays['Word_term-based@3']),numpy.std(result_arrays['Word_term-based@3'])))
    print('\n----------------------------------------------\n')
    model_names = sorted(result_arrays.keys())
    for model_name in model_names:
        if model_name.startswith('Word_term-based'):
            continue
        if model_name.endswith('1'):
            model_name = model_name[:-2]
            print(model_name)
            print('\tmean:{0}\tvar:{1}'.format(numpy.mean(result_arrays[model_name+'@1']),numpy.std(result_arrays[model_name+'@1'])))
            print('\tVs. Baseline@1\t{0}\tsig:{1}\n'.format(numpy.mean(result_arrays[model_name+'@1'])-baseline_mean_1, do_significance_test(model_name, 'Word_term-based', 1)))

            print('\tmean:{0}\tvar:{1}'.format(numpy.mean(result_arrays[model_name+'@3']),numpy.std(result_arrays[model_name+'@3'])))
            print('\tVs. Baseline@3\t{0}\tsig:{1}\n----------------------------------------------\n'
                  .format(numpy.mean(result_arrays[model_name+'@3'])-baseline_mean_3, do_significance_test(model_name, 'Word_term-based', 3)))

            # print('{0}:mean:{1}\tvar:{2}'.format(model_name,numpy.mean(result_arrays[model_name]),numpy.var(result_arrays[model_name])))
            # print('{0}:mean:{1}\tvar:{2}'.format(model_name,numpy.mean(result_arrays['Word_term-based@3']),numpy.var(result_arrays['Word_term-based@3'])))
            # print('{0} VS {1}\tsig:{2}\n'.format(model_name, 'Word_term-based@1', do_significance_test(model_name, 'Word_term-based@3')))


    # Table1_significance_test()