
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
 
from collections import defaultdict
 
from mrjob.job import MRJob
from mrjob.job import MRStep

import re, string

line_counts = dict()
word_counts = dict()

class NaiveBayesTrainerLess3(MRJob):
 
    def __init__(self, *args, **kwargs):
        super(NaiveBayesTrainerLess3, self).__init__(*args, **kwargs)
        
    def jobconf(self):
        orig_jobconf = super(NaiveBayesTrainerLess3, self).jobconf()        
        custom_jobconf = {
            'mapred.reduce.tasks': '1',
        }
        combined_jobconf = orig_jobconf
        combined_jobconf.update(custom_jobconf)
        self.jobconf = combined_jobconf
        return combined_jobconf
    
     
    def configure_options(self):
        super(NaiveBayesTrainerLess3, self).configure_options()
        self.add_passthrough_option(
            '--smoothmethod', default='nosmooth', choices=['nosmooth', 'laplace', 'jelinekmercer']
        )
        
        self.add_passthrough_option(
            '--jmlambda', default=0.3, dest='jmlambda', type='float'
        )
        
    def steps(self):
        out = [
            MRStep(
                mapper = self.mapper,
                combiner = self.combiner,
                reducer = self.reducer_pre
            )
        ]
        
        if self.options.smoothmethod == 'laplace': 
            out.append(MRStep(
                reducer = self.reducer_laplace
            ))
        
        elif self.options.smoothmethod == 'jelinekmercer':
            out.append(MRStep(
                reducer = self.reducer_jelinekmercer
            ))
            
        else:
            out.append(MRStep(
                reducer = self.reducer_nosmooth
            ))
        
        return out
 
    def mapper(self, _, line):
        regex = re.compile('[%s]' % re.escape(string.punctuation))
        _, classifier, token = line.strip().split('\t', 2)
        token = regex.sub(' ', token.lower())
        token = re.sub( '\s+', ' ', token )
        words = token.split()
        yield (('line', classifier), 1)
 
        for word in set(words):                
            yield ((word, classifier), words.count(word))
            yield (('word', classifier), words.count(word))
 
 
    def combiner(self, word_classifier, counts):
        yield (word_classifier, sum(counts))
 
    def reducer_pre(self, word_classifier, counts):
        total_count = sum(counts)
        word, classifier = word_classifier

        if word == 'word':
            if classifier not in word_counts:
                word_counts[classifier] = 0
                
            word_counts[classifier] += total_count
            return

        if word == 'line':
            line_counts[classifier] = total_count
            word = 'PriorProb'

        if total_count <= 3:

            if classifier not in word_counts:
                word_counts[classifier] = 0
            word_counts[classifier] -= total_count
        else:
            yield (word, {classifier: total_count})
            
    def reducer_nosmooth(self, word, classified_counts):
        combined = defaultdict(lambda: 0)

        for entry in classified_counts:
            for classifier, count in entry.items():
                combined[classifier] += count

        for classifier in line_counts.keys():
            count = combined.get(classifier, 0)
 
            if word == 'PriorProb':
                probability = count / sum(line_counts.values())
            else:
                probability = count / word_counts[classifier]
 
            yield (word, classifier), probability
    
    def reducer_laplace(self, word, classified_counts):
        combined = defaultdict(lambda: 0)
        for entry in classified_counts:
            for classifier, count in entry.items():
                combined[classifier] += count
 
        for classifier in line_counts.keys():
            count = combined.get(classifier, 0)
 
            if word == 'PriorProb':
                probability = count / sum(line_counts.values())
            else:
                probability = (count + 1) / (word_counts[classifier]+ 1)
 
            yield (word, classifier), probability
    
    def reducer_jelinekmercer(self, word, classified_counts):
        combined = defaultdict(lambda: 0)
        
        for entry in classified_counts:
            for classifier, count in entry.items():
                combined[classifier] += count
 
        for classifier in line_counts.keys():
            count = combined.get(classifier, 0)

        for classifier in line_counts.keys():
            count = combined.get(classifier, 0)
            jmlambda = self.options.jmlambda
        
            if word == 'PriorProb':
                probability = count / sum(line_counts.values())
            else:
                probability = (
                    (1 - jmlambda) * (count / word_counts[classifier]) +
                    (jmlambda * sum(combined.values()) / sum(word_counts.values()))
                )
                
            yield (word, classifier), probability 

if __name__ == '__main__':
    NaiveBayesTrainerLess3.run()