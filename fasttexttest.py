import fasttext
import csv
def gen_pairs_from_csv():
    with open('quora_duplicate_questions.tsv','rb') as tsvin, open('new.csv', 'wb') as csvout:
        tsvin = csv.reader(tsvin, delimiter='\t')
        csvout = csv.writer(csvout)

        for row in tsvin:
            # print(row)
            yield row[-3],row[-2],row[-1]
            # if count > 0:
            #     csvout.writerows([row[2:4] for _ in xrange(count)])
l = gen_pairs_from_csv()
t_file = './train_classify_data.txt'
v_file = './validate_classify_data.txt'
label_seperator = '__label__'
import os
neg = 0
pos = 0
if not os.path.exists(t_file):

    with open('./train_classify_data.txt', 'a') as train_data, open('./validate_classify_data.txt', 'a') as validate_data:


        line_seperator = '\n'
        count = 0
        for i,j,k in l:
            if k == str(1):
                neg += 1
            else:
                pos += 1
            count += 1
            if count%2 == 0:
                train_data.write('\n' + str(i) + " " + str(j) + label_seperator + k)
            else:
                validate_data.write('\n' + str(i) + " " + str(j) + label_seperator + k)

print(pos, neg)
import numpy
numpy.arange(0.1, 0.5, 0.01)
for rate in numpy.arange(0.91, 2, 0.05):
    rate = 0.9
    classifier = fasttext.supervised(t_file, "model/questionpair_fasttext.model", label_prefix=label_seperator, lr = rate)
    # classifier = fasttext.load_model('model/questionpair_fasttext.model.bin', label_prefix=label_seperator)
    result = classifier.test(v_file)
    print("rate: "+str(rate))
    print('precision: ' + str(result.precision))
    print('recall: ' + str(result.recall))
    break
test_text = "Astrology: I am a Capricorn Sun Cap moon and cap rising...what does that say about me? I'm a triple Capricorn (Sun, Moon and ascendant in Capricorn) What does this say about me?"
predicts = classifier.predict(test_text, 1)
print(len(test_text))
print(len(predicts))
print(test_text + " is type: " + str(predicts))
