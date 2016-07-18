
from mrjob.job import MRJob
from mrjob.step import MRStep

class MRNaiveBayesTrainerStateless(MRJob):

    def __init__(self, *args, **kwargs):
        super(MRNaiveBayesTrainerStateless, self).__init__(*args, **kwargs)
        self.modelStats = {}
        self.class0DocTotal = 0
        self.class1DocTotal = 0
        self.class0WordTotal = 0
        self.class1WordTotal = 0
        self.vocab = 0
        

    def jobconf(self):
        orig_jobconf = super(MRNaiveBayesTrainerStateless, self).jobconf()        
        custom_jobconf = {
            'mapred.output.key.comparator.class': 'org.apache.hadoop.mapred.lib.KeyFieldBasedComparator',
            'mapred.text.key.comparator.options': '-k1rn'
        }
        combined_jobconf = orig_jobconf
        combined_jobconf.update(custom_jobconf)
        self.jobconf = combined_jobconf
        return combined_jobconf

    def mapper(self, _, line):
 
        docID, docClass,text = line.split("\t",2)   
        words = text.split()
        if docID != "D5":
            if docClass == "1":
                yield "PriorProbs", "0,1"
                yield "classTotalFreq", "0," + str(len(words))
                for word in words:
                    yield "!vocab"+word, 1
                    yield word, "0,1"
            else:
                yield "PriorProbs", "1,0"
                yield "!classTotalFreq", str(len(words)) + ",0"
                for word in words:
                    yield "!vocab"+word, 1
                    yield word, "1,0"
        
            
#     def mapper_final(self):
#         for word, counts in self.modelStats.iteritems():
#             yield word, counts
            
#     def combiner(self, word, values):
#         w0Total=0
#         w1Total=0
#         for value in values:
#             w0Total += float(value[0])
#             w1Total += float(value[1]) 
#         yield word, [w0Total, w1Total]
    
        
        
    def reducer(self, word, values):
        #aggregate counts for Pr(Word|Class)
        #yield("number of values for "+word, str(values))
        w0Total=0
        w1Total=0
        for value in values:
            w0Total += float(value[0])
            w1Total += float(value[1])  
        if word == '*TomsPriors':
            self.class0DocTotal = w0Total
            self.class1DocTotal = w1Total
            # calculate priors and yield them
            total = self.class0DocTotal + self.class1DocTotal
            yield("TomsPriors", ', '.join(str(j) for j in [self.class0DocTotal, self.class1DocTotal, 
                                                          self.class0DocTotal/(1.0*total), self.class1DocTotal/(1.0*total)])) 
        elif word == '*total_word_count':
            # calcuate total word counts for each class
            self.class0WordTotal = w0Total
            self.class1WordTotal = w1Total
            yield("Total Word Counts", ', '.join(str(j) for j in [self.class0WordTotal, self.class1WordTotal])) 
        
        elif word.startswith("*!"):
            self.vocab += 1
                
        else:       
            # Not calculating vocabularySize with no smoothing
            #vocabularySize = len(self.modelStats.keys()) -1  #ignore TomsPriors
            
            yield("vocab size",self.vocab)
            yield(word, ','.join(str(j) for j in [w0Total, w1Total, (w0Total+1)/(1.0*self.class0WordTotal+self.vocab), 
                      (w1Total+1)/(1.0*self.class1WordTotal+self.vocab)]))
    
    def steps(self):
        return [MRStep(mapper=self.mapper, mapper_final=self.mapper_final,
                       combiner=self.combiner,
                       reducer=self.reducer)] 

if __name__ == '__main__':
    MRNaiveBayesTrainerStateless.run()