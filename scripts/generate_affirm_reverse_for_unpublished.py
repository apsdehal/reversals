import pickle
from zipfile import ZipFile
import sys
import os
from glob import glob
import re
import multiprocessing
from joblib import Parallel, delayed


dir = sys.argv[1]
dic = pickle.load(open("affirm_reverse.pkl", 'rb'))

file_path = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(file_path, os.pardir)
os.chdir(dir)

zipfiles = glob('*zip')
zipfiles = sorted(zipfiles)


affirm_list = ["affirmed", "affirm", "affirming", "affirms", "dismissed"]
reverse_list = ["reversed", "reverse", "reversing", "reverses", "reversal"]


def set_affirm_reverse(zfname):

    count = 0
    total = 0
    year = zfname[:-4]
    if int(year) < 1924:
        return {}
    # print(year)
    affirm_reverse_dict = {}
    zfile = ZipFile(zfname)
    members = zfile.namelist()
    pickle_file = "%s_95.pkl" % year
    pickle_file = os.path.join(file_path, "pickles", pickle_file)

    with open(pickle_file, "rb") as f:
        match_dic = pickle.load(f)
    total = 0
    count = 0

    for fname in members:

        if not fname.endswith('-maj.txt'):
            continue

        total += 1
        caseid = fname.split('/')[-1][:-8]

        case = dic.loc[dic['caseid'] == caseid]
        status = ""

        if case.empty and caseid in match_dic:

            data = zfile.read(fname).decode()
            data = re.sub(r'![\W\s_]+', "", data)
            data = data.lower().split(" ")
            for i in affirm_list:
                if i in data:
                    status = "Affirmed"
                    break

            if status != "Affirmed":
                for i in reverse_list:
                    if i in data:
                        # if status == "Affirmed":
                        #     status = ""
                        # else:
                        status = "Reversed"
                        break

            if len(status) == 0:
                print(caseid)
                continue
            else:
                count += 1
                # print(caseid, status)
                affirm_reverse_dict[caseid] = (year, match_dic[caseid], status)

    return(count, total)
    # return affirm_reverse_dict


if __name__ == '__main__':
    num_cores = multiprocessing.cpu_count()
    r = Parallel(n_jobs=num_cores)(delayed(set_affirm_reverse)(f) for f in zipfiles)
    total_matches = 0
    total_cases = 0

    for tups in r:

        total_matches += tups[0]
        total_cases += tups[1]

    print(total_matches, total_cases)
    # affirm_reverse_dict = {}
    # for d in r:
    #     affirm_reverse_dict.update(d)
    # pickle.dump(affirm_reverse_dict, open("unpublished_affirm_reverse.pkl", "wb"))
