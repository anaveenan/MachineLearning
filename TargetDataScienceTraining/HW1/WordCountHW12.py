
from mrjob.job import MRJob
import re, string

class MRJobWordCount(MRJob):

    def mapper(self, _, line):
        regex = re.compile('[%s]' % re.escape(string.punctuation))
        token = line.strip().split('\t', 2)[-1]
        token = regex.sub(' ', token.lower())
        token = re.sub( '\s+', ' ', token )
        words = token.split()

        for word in words:
            if len(word) > 1:
                yield (word, 1)

    def combiner(self, word, counts):
        yield(word, sum(counts))

    def reducer(self, word, counts):
        yield word, sum(counts)
    
if __name__ == '__main__':
    MRJobWordCount.run()