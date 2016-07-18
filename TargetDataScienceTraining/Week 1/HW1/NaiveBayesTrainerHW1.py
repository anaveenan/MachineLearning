
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

class NaiveBayesTrainer(MRJob):
 
    def __init__(self, *args, **kwargs):
        super(NaiveBayesTrainer, self).__init__(*args, **kwargs)
        
    def jobconf(self):
        orig_jobconf = super(NaiveBayesTrainer, self).jobconf()        
        custom_jobconf = {
            'mapred.reduce.tasks': '1',
        }
        combined_jobconf = orig_jobconf
        combined_jobconf.update(custom_jobconf)
        self.jobconf = combined_jobconf
        return combined_jobconf
    
     
    def configure_options(self):
        super(NaiveBayesTrainer, self).configure_options()
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

if __name__ == '__main__':
    NaiveBayesTrainer.run()