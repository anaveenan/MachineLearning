
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from mrjob.job import MRJob
from mrjob.step import MRStep
import os, re, string, math

counts = []

class NaiveBayesClassifier(MRJob):

    def __init__(self, *args, **kwargs):
        super(NaiveBayesClassifier, self).__init__(*args, **kwargs)
        
    def steps(self):
        return [
            MRStep(
                mapper_init=self.mapper_init, 
                mapper=self.mapper,
                combiner=self.combiner,
                reducer=self.reducer  
            ),
            MRStep(reducer=self.reducer_final)
        ]

    def configure_options(self):
        super(NaiveBayesClassifier, self).configure_options()
        
        self.add_file_option('--model')
        
    def mapper_init(self): 
        self.model_stats = {}

        with open(self.options.model, "r") as f:
            lines = f.read().split('\n')
        
        split_lines = [line.split('\t') for line in lines]
        
        for entry in split_lines:
            word = entry[0]
            probs = [float(p) for p in entry[1:]]
            self.model_stats[word] = probs
    
    def mapper(self, _, line):
        regex = re.compile('[%s]' % re.escape(string.punctuation))
        _, classifier, token = line.strip().split('\t', 2)
        token = regex.sub(' ', token.lower())
        token = re.sub( '\s+', ' ', token )

        p0 = math.log10(self.model_stats['PriorProb'][0])
        p1 = math.log10(self.model_stats['PriorProb'][1])
        
        for word in token.split():

            probs = self.model_stats.get(word, [0, 0]) 
            probs = [p if p > 0 else 1 for p in probs] 
           
            p0 += math.log10(probs[0])
            p1 += math.log10(probs[1])

        if p0 > p1:
            prediction = 0
        elif p1 > p0:
            prediction = 1
        else:
            prediction = -1 

        if prediction == int(classifier):
            key = 'correct'
        else:
            key = 'incorrect'
            
        yield (key, 1)

    def combiner(self, key, values):
        yield (key, sum(values))
        
    def reducer(self, key, values):
        values = list(values)
        count = sum(values)
        counts.append(count)
        yield (key, count)
      
    def reducer_final(self, key, values):
        values = list(values)

        rate = sum(values) / sum(counts)
        output = 'Inaccuracy Rate' if key == 'incorrect' else 'Accuracy Rate'
        
        yield (output, rate)

if __name__ == '__main__':
    NaiveBayesClassifier.run()