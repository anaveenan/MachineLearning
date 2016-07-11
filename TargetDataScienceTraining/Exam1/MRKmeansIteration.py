from numpy import argmin, array, random
from mrjob.job import MRJob
from mrjob.step import MRStep
import os

#Calculate find the nearest centroid for data point 
def MinDist(datapoint, centroid_points):
    datapoint = array(datapoint)
    centroid_points = array(centroid_points)
    diff = datapoint - centroid_points 
    diffsq = diff*diff
    # Get the nearest centroid for each instance
    minidx = argmin(list(diffsq.sum(axis = 1)))
    return minidx


class MRKmeansIteration(MRJob):
    k=3    
    def steps(self):
        return [MRStep(mapper_init = self.mapper_init, 
                       mapper=self.mapper,
                       combiner = self.combiner,
                       reducer=self.reducer)
               ]
#    def jobconf(self):
#        orig_jobconf = super(MRKmeansIteration, self).jobconf()        
#        custom_jobconf = {
#            'mapred.output.key.comparator.class': 'org.apache.hadoop.mapred.lib.KeyFieldBasedComparator',
#            'mapred.text.key.comparator.options': '-k1rn',
#            'mapred.reduce.tasks': '1',
#        }
#        combined_jobconf = orig_jobconf
#        combined_jobconf.update(custom_jobconf)
#        self.jobconf = combined_jobconf
#        return combined_jobconf

    def configure_options(self):
        """Add command-line options specific to this script."""
        super(MRKmeansIteration, self).configure_options()

        self.add_passthrough_option(
            '--centroidsFile', dest='centroidsFile', default="Centroids.txt", type='str',#type='int',
            help=('The location of the centroids file that contains the centroids '
                  ' that will be used for this iteration of KMeans Clustering. Default: %Centroids.txt'))

    #load centroids info from file
    def mapper_init(self):
        print "Current path:", os.path.dirname(os.path.realpath(__file__))
        self.centroid_points = [map(float,s.split('\n')[0].split(',')) for s in open(self.options.centroidsFile).readlines()]
        print "Centroids: ", self.centroid_points
        
    #load data and output the nearest centroid index and data point 
    def mapper(self, _, line):
        D = (map(float,line.split(',')))
        
        # w = 1/(np.sqrt(D[0]**2 + D[1]**2)) # compute weight
        yield int(MinDist(D,self.centroid_points)), (D[0],D[1],1)
        
    #Combine sum of data points locally
    def combiner(self, idx, inputdata):
        sumx = sumy = num = 0
        for x,y,n in inputdata:
            num = num + n
            sumx = sumx + x
            sumy = sumy + y
        yield idx,(sumx,sumy,num)
        
    #Aggregate sum for each cluster and then calculate the new centroids
    def reducer(self, idx, inputdata): 
        sumx = sumy = num = 0
        for x,y,n in inputdata:
            num = num + n
            sumx = sumx + x
            sumy = sumy + y
        # send the centroids back to the driver
        yield idx,(sumx/num, sumy/num)

if __name__ == '__main__':
    MRKmeansIteration.run()