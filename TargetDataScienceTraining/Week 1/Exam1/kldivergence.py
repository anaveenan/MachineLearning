from mrjob.job import MRJob
import re
import numpy as np
class kldivergence(MRJob):
    def mapper1(self, _, line):
        index = int(line.split('.',1)[0])
        letter_list = re.sub(r"[^A-Za-z]+", '', line).lower()
        count = {}
        for l in letter_list:
            if count.has_key(l):
                count[l] += 1
            else:
                count[l] = 1
        for key in count:
            yield key, [index, count[key]*1.0/len(letter_list)]


    def reducer1(self, key, values):
        a = np.asarray(values[1])
    
#     def reducer2(self, key, values):
#         kl_sum = 0
#         for value in values:
#             kl_sum = kl_sum + value
#         yield None, kl_sum
            
    def steps(self):
        return [self.mr(mapper=self.mapper1,
                         reducer=self.reducer1)
#                 self.mr(reducer=self.reducer2)
               ]

if __name__ == '__main__':
    kldivergence.run()