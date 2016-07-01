
from mrjob.job import MRJob
from mrjob.job import MRStep
from collections import Counter

import re, string

wordcounts = {}

class MRJobWordCountFreq(MRJob):
    
    def __init__(self, *args, **kwargs):
        super(MRJobWordCountFreq, self).__init__(*args, **kwargs) 

    def jobconf(self):
        orig_jobconf = super(MRJobWordCountFreq, self).jobconf()        
        custom_jobconf = {
            'mapred.reduce.tasks': '1',
        }
        combined_jobconf = orig_jobconf
        combined_jobconf.update(custom_jobconf)
        self.jobconf = combined_jobconf
        return combined_jobconf
        
    def steps(self):
        out = [
            MRStep(
                mapper = self.mapper1,
                combiner = self.combiner
            ),
            MRStep(reducer=self.reducer)
        ]
        
        return out
         
    def mapper1(self, word, line):
        regex = re.compile('[%s]' % re.escape(string.punctuation))
        token = line.strip().split('\t', 2)[-1]
        token = regex.sub(' ', token.lower())
        token = re.sub( '\s+', ' ', token )
        words = token.split()

        for word in words:
            if len(word) > 1:
                yield (word, 1)
                
    def combiner(self, word, counts):
        yield word, sum(counts)
        
    def reducer(self, word, counts):
        yield word, sum(counts)
        print "in reducer"
    
if __name__ == '__main__':
    MRJobWordCountFreq.run()