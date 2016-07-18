 
from mrjob.job import MRJob
import sys, re, string, operator, math, os


regex = re.compile('[%s]' % re.escape(string.punctuation))

class MRNaiveBayesClassifier(MRJob):


    def __init__(self, *args, **kwargs):
        super(MRNaiveBayesClassifier, self).__init__(*args, **kwargs)
        self.zeroProb = 0

    def jobconf(self):
        orig_jobconf = super(MRNaiveBayesClassifier, self).jobconf()        
        custom_jobconf = {
            'mapred.output.key.comparator.class': 'org.apache.hadoop.mapred.lib.KeyFieldBasedComparator',
            'mapred.text.key.comparator.options': '-k1rn',
            'mapred.reduce.tasks': '1',
        }
        combined_jobconf = orig_jobconf
        combined_jobconf.update(custom_jobconf)
        self.jobconf = combined_jobconf
        return combined_jobconf    

    def mapper_init(self):
        self.modelStats = {}
        
        recordStrs = [s.split('\n')[0].split('\t') for s in open("StatelessModel1.txt").readlines()]
        for word, statsStr in recordStrs:
            self.modelStats[word] = map(float, statsStr.split(","))
        
        self.prC0 = math.log(self.modelStats["PriorProbs"][2])
        self.prC1 = math.log(self.modelStats["PriorProbs"][3])
        

    
    def mapper(self, _, line):
        
        docID, docClass,text = line.split("\t",2)
        text = text.strip()
        text = regex.sub(' ', text.lower())
        text = re.sub( '\s+', ' ', text )
        words = text.split()
        
        for word in words:
            p0 = self.modelStats[word][2]
            if self.modelStats[word][2] == 0.0:
                self.zeroProb += 1
            p1 = self.modelStats[word][3]
            if self.modelStats[word][3] == 0.0:
                self.zeroProb += 1
            wordGivenHam = math.log(p0) if p0>0.0 else math.log(1)
            wordGivenSpam = math.log(p1) if p1>0.0 else math.log(1)
            prHAMGivenDoc = self.prC0 + wordGivenHam
            prSPAMGivenDoc = self.prC1 + wordGivenSpam
        
        predictedClass = 1 #SPAM
        if(prHAMGivenDoc > prSPAMGivenDoc):
            predictedClass = 0 #HAM
        if int(docClass) == predictedClass:
            yield (docID, 0)  #no error
        else: 
            yield (docID, 1) # error    
        yield("zero", self.zeroProb)
    
    def combiner(self, word, values):
        for value in values:
            yield ("t", value)
            
    def reducer(self, word, values):
        zero = 0
        numberOfRecords = 0
        numberWrong = 0
        for value in values:
            if value > 1:
                zero = value
            else:    
                numberOfRecords += 1
                numberWrong += value
        #print (numberOfRecords, numberWrong)
        print ('Error rate: %.4f' %(1.0*numberWrong/float(numberOfRecords)))
        print ('Number Wrong %d, Total Records %d'  %(numberWrong, numberOfRecords))
        print ('number of word|class with 0 probability: %d' %(zero))

if __name__ == '__main__':
    MRNaiveBayesClassifier.run()