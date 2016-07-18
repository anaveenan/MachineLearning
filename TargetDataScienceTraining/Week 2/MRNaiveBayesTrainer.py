
"""An implementation of a multinomial Naive Bayes learner as an MRJob.
   This is meant as an example of why mapper_final is useful.
   
   This learning algorithm implementation can be further optimised. HOW?
   
   Use a cool pattern to do this!

"""
from mrjob.job import MRJob

class MRNaiveBayesTrainer(MRJob):

    def __init__(self, *args, **kwargs):
        super(MRNaiveBayesTrainer, self).__init__(*args, **kwargs)
        self.modelStats = {}
        self.classTotalFreq = [0, 0]
        self.vocab=0

    def jobconf(self):
        
        orig_jobconf = super(MRNaiveBayesTrainer, self).jobconf()        
        custom_jobconf = {
            'mapred.output.key.comparator.class': 'org.apache.hadoop.mapred.lib.KeyFieldBasedComparator',
            'mapred.text.key.comparator.options': '-k1rn',
            'mapred.reduce.tasks': '1',
        }
        combined_jobconf = orig_jobconf
        combined_jobconf.update(custom_jobconf)
        self.jobconf = combined_jobconf
        return combined_jobconf

    def mapper(self, _, line):
        
        docID, docClass,text = line.split("\t",2)   
        words = text.split()
        vocab = {}
        if docID != "D5":
            if docClass == "1":
                yield("PriorProbs", "0,1")
                yield("*classTotalFreq", ("0, " + str(len(words))))
                for word in words:
                    vocab[word] = 1
                    yield(word, "0,1")
            else:
                yield("PriorProbs", "1,0")
                yield("*classTotalFreq", (str(len(words)) + ", 0"))
                for word in words:
                    vocab[word] = 1
                    yield(word, "1,0")
        for k in vocab.keys():
            yield "*!"+k, "1,0"

    def reducer(self, word, values):    
        #aggregate counts for Pr(Word|Class)
        #yield("number of values for "+word, str(values))
        w0Total=0
        w1Total=0
        c0Total=0
        c1Total=1
        for value in values:
            w0, w1 =  value.split(",")
            w0Total += float(w0)
            w1Total += float(w1)  
        if word == "*classTotalFreq":
            self.modelStats[word] = [w0Total, w1Total]
        elif word.startswith("*!"):
            self.vocab += 1
        elif word == "TomsPriors":
            yield("TomsPriors", ','.join(str(j) for j in [w0Total,w1Total,w0Total/(w0Total+w1Total),w1Total/(w0Total+w1Total)]))
        else:
            yield(word, ','.join(str(j) for j in [w0Total,w1Total,(w0Total+1)/(self.modelStats["*classTotalFreq"][0] + self.vocab),(w1Total+1)/(self.modelStats["*classTotalFreq"][1] + self.vocab)]))
        #yield("JIMI "+word, [w0Total, w1Total])"""
        
if __name__ == '__main__':
    MRNaiveBayesTrainer.run()