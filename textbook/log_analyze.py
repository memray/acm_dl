
if __name__ == '__main__':
    LOG_PATH = "/home/memray/Desktop/algebra_log_file.txt"

    line_experiment = []
    # models_of_interest = 'Blending *Word_term-based* and *Keyword-only*'
    # model_of_interest = 'LDA_textbook_two_200'
    models_of_interest = ['Word_term-based', 'LDA_algebra_five_100','LDA_algebra_five_150','LDA_algebra_five_200',# 0-3
                          'LDA_algebra_two_100','LDA_algebra_two_150','LDA_algebra_two_200', # 4-6
                          'pure_LDA_algebra_five_100','pure_LDA_algebra_five_150','pure_LDA_algebra_five_200', # 7-9
                          'pure_LDA_algebra_two_100','pure_LDA_algebra_two_150','pure_LDA_algebra_two_200'] # 10-12
    length = 10
    k_of_interest = 1
    model_of_interest = models_of_interest[1]

    # k = 1
    ndcg = {}
    for i in range(10):
        ndcg[i]=0

    log = open(LOG_PATH,'r')
    for line in log:
        # reach the delimiter, do process
        #[Testing:Keyword-only]
        if line.strip()=='':
            model_name = line_experiment[-1][line_experiment[-1].index(':')+1: line_experiment[-1].index(']')]
            # print(model_name)
            if((model_name.startswith(model_of_interest))):
                if(len(line_experiment) < 10):
                    length = 1
                k = int(line_experiment[-1][9])
                if (k==k_of_interest):
                    print(model_name)
                    for i in range(length):
                        print(line_experiment[i].strip())
                        value = float(line_experiment[i].strip()[line_experiment[i].strip().rindex(':')+1:])
                        ndcg[i]+=value
                # if k==1:
                #     k = 3
                # else:
                #     k = 1
            line_experiment = []

        else:
            line_experiment.append(line)

    for i in range(length):
        print(ndcg[i]/100.0)