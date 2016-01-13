__author__ = 'Memray'
import traceback
import sys


class FieldOfStudy:
    """
     Reading the field-of-study index and return in a dictionary
    """
    fields_path = ""
    field_dict = {}  # key is the name of domain, value is the corresponding id

    def __init__(self):
        global base_dir
        self.fields_path = base_dir + "FieldsOfStudy.txt"
        file = open(self.fields_path, 'r')
        for line in file.readlines():
            strs = line.strip().split('\t')
            self.field_dict[strs[1]] = strs[0]

    def load_cs_domains(self, cs_path):
        file = open(cs_path, 'r')
        cs_domains = set()
        # load all the domain names in CS
        for line in file.readlines():
            domain_name = line.strip().lower()
            cs_domains.add(domain_name)
        print('Total domains in CCS:{0}'.format(len(cs_domains)))
        result_items = {}
        for item in self.field_dict.iteritems():
            if str(item[0]).lower() in cs_domains:
                result_items[str(item[1])] = str(item[0])

        print('Found in Microsoft:{0}'.format(len(result_items)))
        # print('\n'.join(result_items))
        # print(result_items)
        return result_items


class MicrosoftAcademicKeywords:
    """
     Provide some functions facilitating processing the keywords of Microsoft Academic Search
    """
    def __init__(self):
        global base_dir
        self.microsoft_keywords_path = base_dir + "PaperKeywords.txt"
        self.cs_keywords_duplicated_path = base_dir + 'cs_keywords_duplicated.txt'
        self.cs_keywords_remove_duplicate_path =  base_dir + "cs_keywords.txt"

    def find_keywords_by_domains(self, domains):
        keywords_file = open(self.microsoft_keywords_path, 'r')
        count = 0
        cs_keywords_count = 0

        keywords_filter = set()

        global base_dir
        try:
            output_file = open(self.cs_keywords_remove_duplicate_path, 'w')
            line = keywords_file.readline()
            while (line is not None) & (line!=''):
                count += 1
                if count % 100000 == 0:
                    print('{0:3.2}%, {1}/{2}'.format(float(count)/176760816.00*100.00,count, 176760816))
                    print(len(keywords_filter))
                strs = line.strip().split('\t')
                # print(strs)
                # if domains.has_key(strs[2]):
                if True:
                    cs_keywords_count += 1
                    # print(strs[1].strip().lower())
                    keywords_filter.add(strs[1].strip().lower())
                line = keywords_file.readline()

            print('Found {0} related keywords'.format(len(keywords_filter)))
            for word in keywords_filter:
                output_file.write(word.strip()+'\n')
        except Exception, err:
            print(traceback.format_exc())
            print(sys.exc_info()[0])
        finally:
            keywords_file.close()
            output_file.close()
        print(count)


    def remove_duplicates(self):
        """
        deplicated as I find that seemlingly the number of nonredundant keywords is small
        so no need of two-stage process
        """
        file = open(self.cs_keywords_duplicated_path,'r')
        keywords = set()
        line = file.readline()
        count = 0
        while (line is not None) & (line!=''):
            if count % 10000 == 0:
                print(count)
            if line.strip()!='':
                count += 1
                keywords.add(line.strip())
            line = file.readline()
        file.close()

        print('Before removing duplicates:{0}\nAfter:{1}'.format(count, len(keywords)))
        file = open(self.cs_keywords_remove_duplicate_path,'w')
        for word in keywords:
            file.write(word.strip()+'\n')
        file.close()





base_dir = 'E:\\acm_dl\keyword\\'
if __name__ == '__main__':
    field_dict = FieldOfStudy()
    cs_domains = field_dict.load_cs_domains(base_dir + "acm_cs_domain.txt")
    MicrosoftAcademicKeywords().find_keywords_by_domains(cs_domains)
