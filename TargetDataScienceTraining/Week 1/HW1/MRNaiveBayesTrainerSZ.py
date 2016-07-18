
"""An implementation of a multinomial Naive Bayes learner as an MRJob.
   This is meant as an example of why mapper_final is useful.
   
   This learning algorithm implementation can be further optimised. HOW?
   
   Use a cool pattern to do this!

"""
from mrjob.job import MRJob

class MRNaiveBayesTrainerStateless(MRJob):

    def __init__(self, *args, **kwargs):
        super(MRNaiveBayesTrainerStateless, self).__init__(*args, **kwargs)
        # now only needed for priors???
        self.modelStats = {}
        self.vocab = 0
        

    def jobconf(self):
        orig_jobconf = super(MRNaiveBayesTrainerStateless, self).jobconf()        
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
        if docID != "D5":
            if docClass == "1":
                yield "PriorProbs", "0,1"
                yield "*classTotalFreq", "0," + str(len(words)) 
                for word in words:
                    yield word, "0,1"                     
                    yield "!vocab"+word, "0,1"
                    if word.startswith("*!"):
                        self.vocab += 1
        yield "Total vocab", str(self.vocab) + ",0"
                    
#             else:
#                 yield "PriorProbs", "1,0"
#                 yield  "*classTotalFreq", str(len(words)) + ",0"
#                 for word in words:
#                     yield word, "1,0"
#                    yield "vocab!"+word, "0,1"
#                 if word.startswith("*!"):
#                     self.vocab += 1
#                 yield "Total vocab", self.vocab               

#     def reducer(self, word, values):
#         w0Total=0
#         w1Total=0
#         for value in values:
#             w0, w1 =  value.split(",")
#             w0Total += float(w0)
#             w1Total += float(w1) 
#         if word == "*classTotalFreq":
#             self.modelStats[word] = [w0Total, w1Total]
#         elif word == 'PriorProbs':
#             yield "PriorProbs", str(w0Total / (w0Total + w1Total)) + "," + str(w1Total / (w0Total + w1Total))
#         else:
#             yield word, str(w0Total / self.modelStats["*classTotalFreq"][0]) + "," + str(w1Total / self.modelStats["*classTotalFreq"][1])

#         for k in self.modelStats.keys():
#             yield(k, ','.join(str(j) for j in [self.modelStats[k][0],
#                       self.modelStats[k][1],
#                       (self.modelStats[k][0] + 1) /(class0Total + vocabularySize), 
#                       (self.modelStats[k][1] +1)/(class1Total+vocabularySize)]))  

#     def reducer_old(self, word, values):
#         #aggregate counts for Pr(Word|Class)
#         #yield("number of values for "+word, str(values))
#         w0Total=0
#         w1Total=0
#         for value in values:
#             w0, w1 =  value.split(",")
#             w0Total += float(w0)
#             w1Total += float(w1)  
#         self.modelStats[word] =  [w0Total, w1Total]

        #yield("JIMI "+word, [w0Total, w1Total])
#     def reducer_final(self):       
#         class0Total = 0
#         class1Total = 0
#         for k in self.modelStats.keys():
#             if k != "TomsPriors":
#                 class0Total += self.modelStats[k][0]
#                 class1Total += self.modelStats[k][1]
#         vocabularySize = len(self.modelStats.keys()) -1  #ignore TomsPriors
#         #some yields to see some model internal parameters
#         #yield ("defaultPrior 0 class", class0Total+vocabularySize)
#         #yield ("defaultPrior 1 class", class1Total+vocabularySize)
#         #yield ("count 0 class", class0Total)
#         #yield ("count 1 class", class1Total)
#         #yield ("vocabularySize", vocabularySize)
        
#         #calculate priors 
#         classCount0, classCount1 = self.modelStats.get("TomsPriors")
#         del self.modelStats["TomsPriors"]
#         total = classCount0 + classCount1
#         yield("TomsPriors", ','.join(str(j) for j in [classCount0, classCount1, classCount0/total, classCount1/total])) 
#         for k in self.modelStats.keys():
#             yield(k, ','.join(str(j) for j in [self.modelStats[k][0],
#                       self.modelStats[k][1],
#                       (self.modelStats[k][0] + 1) /(class0Total + vocabularySize), 
#                       (self.modelStats[k][1] +1)/(class1Total+vocabularySize)]))        

if __name__ == '__main__':
    MRNaiveBayesTrainerStateless.run()