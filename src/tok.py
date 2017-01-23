
# fname = '../data/dataset/SemEval2017-task4-test.subtask-A.english.txt'
# with open(fname, 'rt') as tst:
#     for line in tst:
#         items = line.split('\t')
#         txt = items[2]
#         tid = items[0]
#         with open('../data/dataset/tok/'+tid, 'wt') as out:
#             out.write(txt)
#


fname = '../data/dataset/SemEval2017-task4-test.subtask-A.english.txt'
with open(fname, 'rt') as tst:
    with open('../data/dataset/tst17', 'wt') as out:
        for line in tst:
            items = line.split('\t')
            tid = items[0]

            tokens = []
            with open('../data/dataset/toknlp/%s.nlp' % tid, 'rt') as nlp:
                for lnlp in nlp:
                    cols = lnlp.split('\t')
                    if len(cols)<2:
                        continue
                    tokens.append(cols[1])

            txt = ' '.join(tokens)
            outline = '%s\tpositive\t%s\n' % (tid, txt)
            # print outline
            out.write(outline)



