__author__ = 'Memray'
import os

directoryPath = 'E:\\acm_dl\\pdf\\ir\\'

# read the file and return text after pre-process
def readfile(path, removeReference=True):
    fp = open(path, 'r')
    fulltext = ""
    # print(fp.readlines())
    lines = fp.readlines()
    i = 0
    while i < len(lines):
        # remove references
        if removeReference & (len(lines[i]) < 15) & (
                    (lines[i].strip().lower().endswith('reference')) | (
                        lines[i].strip().lower().endswith('references'))):
            # print('#########FIND REFERENCE#########')
            break
        # remove copyright
        if lines[i].strip().lower().startswith('copyright is held by'):
            # print('FIND COPYRIGHT')
            i += 3
        # deal with the conjunction with hyphen
        if (i < len(lines)) & (i > 0) & (len(lines[i-1].strip()) > 0) & (lines[i-1].strip().endswith('-')):
            fulltext = fulltext[:-1] + lines[i].strip()
        elif i < len(lines):
            fulltext += ' ' + lines[i].strip()
        # print(lines[i].strip())
        # process with the hyphen
        i += 1
    fp.flush()
    fp.close()
    return fulltext


# read the file and return text after pre-process
def writefile(path, text):
    fp = open(path, 'w')
    fp.write(text)
    fp.flush()
    fp.close()

if __name__ == '__main__':
    pathList = filter(lambda x: (x.endswith('txt'))&(not x.endswith('_preprocess.txt')), os.listdir(directoryPath))
    for filepath in pathList:
        path = directoryPath + filepath
        print path
        text = readfile(directoryPath + filepath, True)
        writefile(directoryPath + filepath[:-4]+ '_preprocess.txt', text)
        print(text)
        # raw_input("press enter")
