import glob
import operator

basepath = '../data/output/w2v_sem_ama/'
best_model_path_list = glob.glob(basepath+'*')

dic={}
tid_list=[]
records={}
for f in best_model_path_list:
    if f.endswith('ensemble.txt'):
        continue
    with open(f, 'rt') as handle:
        for idx, line in enumerate(handle):
            items = line.split('\t')
            tid = items[0]
            sent = items[1].replace('\n','')

            if records.has_key(idx):
                records[idx]['sent'][sent]+=1
            else:
                records[idx]={'tid':tid, 'sent':{'positive':0,'neutral':0,'negative':0,}}
                records[idx]['sent'][sent] += 1
                tid_list.append(tid)

with open(basepath+'ensemble.txt', 'wt') as out:
    for idx, tid in enumerate(tid_list):
        out.write('%s\t%s\n' % (tid, max(records[idx]['sent'].iteritems(), key=operator.itemgetter(1))[0]))




