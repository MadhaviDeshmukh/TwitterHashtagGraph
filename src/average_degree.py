import sys
import json
import time

""" A function to truncate a float to "n" digits without rounding
    f: The float to be truncated
    n: Number of decimal points to maintain
    source: http://stackoverflow.com/questions/783897/truncating-floats-in-python
    @author: Madhavi Deshmukh	
"""
def truncate(f, n):
    '''Truncates/pads a float f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d+'0'*n)[:n]])

""" A class to calculate the average degree of a
twitter graph formed from hashtags
"""
class AverageDegree:

    def __init__(self, input_file, output_file):

        # Input and Output files
        self.input_file = input_file
        self.output_file = output_file

        # Tweet graph is stored in a hashmap.
        # Each node of the hash maps to a set of its neighbor nodes.
        # The neighbors are themselves stored in a hash for fast lookup.
        self.tweet_graph = {}

        # Edge list is a list of all the edges in the tweet graph and their corresponding tweet time.
        # The list is sorted from the most recent to the oldest edge.
        # New edges are added to the front of the list, while old edges outside the 60s window is dropped from the end.
        self.edge_list = []

        # most_recent_tweet_time tracks the most recent tweet received.
        self.most_recent_tweet_time = 0

    """ Parse the tweet stream and extract the hashtags and tweet creation_time """
    def parse_tweet(self, tweet_json):

        tweet_obj = json.loads(tweet_json.strip())

        # We are only interested in the "entities" element which encapsulates the hashtags
        # and the created_at timestamp.
        # If entities is not found, return "None"
        if tweet_obj.has_key('entities'):

            # Extract the hashtags
            hashtag_list=[]
            hashtag_list = [hashtag['text'] for hashtag in tweet_obj['entities']['hashtags']]

            # Extract the creation time
            timecreated = tweet_obj['created_at']

            # Convert the created_at time to a unix timestamp.
            c = time.strptime(timecreated.replace("+0000",''), '%a %b %d %H:%M:%S %Y')
            tweet_unixtime = int(time.mktime(c))

            # Return the hashtag list, timestamp tuple.
            return hashtag_list, tweet_unixtime
        else:
            return "", 0

    """ Generate all possible combinations of hashtags
    Return the hashtag pairs, or None if we cannot form hashtag pair. for e.g.
    when there is just a single hashtag in the tweet.
    """
    def generate_hashtag_combinations(self, hashtag_list, tweet_unixtime):
        # Generate the hashtag pairs if we have atlease 2 hashtags
        # else return None
        if len(hashtag_list) > 1:
            hashtag_pairs = []
            for i in range(0, len(hashtag_list)):
                for j in range(i + 1, len(hashtag_list)):
                    hashtag_pairs.append((hashtag_list[i], hashtag_list[j],tweet_unixtime))
            return hashtag_pairs

    # Given a new edge, update the Tweet graph.
    def add_to_tweet_graph(self,first,second) :

        # To make the logic easier and also to reduce the graph memory consumption in half,
        # I  normalize the edges by sorting them alphabetically.
        # e.g. (Scala, Hadoop) -> (Hadoop, Scala)
        # This makes it easier to match both versions of the edge.
        # Also, we just need to maintain an edge from Hadoop -> Scala in the graph.
        # the edge from Scala -> Hadoop is implied when computing Scala's degree.
	if second < first :
            first, second = second, first

        # Check if the first node is present in the graph
	if self.tweet_graph.has_key(first):
            # If first is found, check if an edge exists to second.
            # If the edge already exists, just increament the edge
            # count to keep track of duplicates.
            if self.tweet_graph[first].has_key(second):
                self.tweet_graph[first][second] += 1
            else:
                # If the edge to second does not exist, create it.
                self.tweet_graph[first][second] = 1
	else:
            # If the first node is not found in the graph,
            # add it and create an edge to the second node.
            self.tweet_graph[first] = {}
            self.tweet_graph[first][second] = 1

    """ Add a new edge to the edge list.
    The edge list keeps track of all the edges that are within the 60s window.

    Effifiency Note: To improve efficiency,we prepend the latest edge instead of appending since most of the time the tweets are in order. A significant improvement would be to use a list/double linked list and insert the new edge at the right point using a binary search.
    """
    def add_to_edge_list(self, first, second, time) :

        # If first element in the edge list, just insert it.
        if len(self.edge_list) == 0:
	    self.edge_list.insert(0, [first, second, time])
        else:
            # If there are other elements, check if this edge is in order.
            # If in order, then just insert it at the beginning.
            if time >= self.edge_list[0][2]:
	        self.edge_list.insert(0, [first, second, time])
            else:
                # If out of order, then insert at the beginning and sort the list
                # based on created_at timestamp.
	        self.edge_list.insert(0, [first, second, time])
	        self.edge_list.sort(key = lambda x:int(x[2]),reverse = True)

        # Record the most recent tweet time.
        self.most_recent_tweet_time = self.edge_list[0][2]

	##self.edge_list.append([first, second, time])
	#self.edge_list.insert(0, [first, second, time])
	#self.edge_list.sort(key = lambda x:int(x[2]),reverse = True)
	#self.most_recent_tweet_time = self.edge_list[0][2]

    """ Remove nodes and edges that are outside the 60s window. """
    def update_graph_and_list(self):

        # Since the edge list is sorted, the oldest tweet and the one that is possibly
        # outside our 60s window is at the end.
        last_element = self.edge_list[-1]

        # Keep scanning the list from the end until we reach a tweet/edge that is still
        # within the 60s window.
        while(True):
            # Found an edge that is outside the 60s window.
            if last_element[2] < (self.most_recent_tweet_time - 60):
                element_to_delete = last_element
                last_element = self.edge_list[-2]

                # Remove it from the tweet graph and also delete it from the edge list.
                self.remove_from_tweet_graph(element_to_delete[0], element_to_delete[1])
                del self.edge_list[-1]
            else:
                break

    """ Remove an edge from the tweet graph """
    def remove_from_tweet_graph(self, first, second) :

        # Sort the edge to make sure the nodes are normalized.
	if second < first :
		first, second = second, first

        # Check if the first node is present in the tweet graph.
        if self.tweet_graph.has_key(first):
            # Check if the second node is present in the list of first's neighbors.
            if self.tweet_graph[first].has_key(second):

                # If there was only one edge from first->second, delete it.
                if self.tweet_graph[first][second] == 1:
                    del self.tweet_graph[first][second]

                    # If first has no more neighbors, delete it too.
                    if len(self.tweet_graph[first]) == 0:
                        del self.tweet_graph[first]

                else:
                    # If there were duplicate edges from first -> second, just
                    # decrement the edge count and proceed. We'll delete the node
                    # when the last edge from first->second is deleted.
                    self.tweet_graph[first][second] -= 1

    """ calculate the rolling average """
    def calculate_rolling_average(self):
	unique_hashtags = set()
	total = 0

        # count the number of unique hashtags in the graph.
	for key in self.tweet_graph:
            unique_hashtags.add(key)

            # Also count the number of edges in the tweet graph.
            total = total + len(self.tweet_graph[key])

            for second in self.tweet_graph[key]:
                unique_hashtags.add(second)

        # Since we only track the edge from first -> second and not from second->first,
        # We double the rolling average we calculate.
	rolling_average = 2*float(total)/len(unique_hashtags)

        # Write the truncated result to output file.
        self.output_io.write(truncate(rolling_average, 2))
	#self.output_io.write(format(2*float(total)/len(unique_hashtags),'.2f'))
	self.output_io.write("\n")

    """ The main driver for this proram """
    def run(self):

        # Open the input file for reading.
        try:
            self.input_io = open(self.input_file)
        except IOError:
            print 'Cannot open:', self.input_file

        # Open the output file for writing.
        try:
            self.output_io = open(self.output_file, 'w')
            self.output_io.truncate()
        except IOError:
            print 'Cannot open:', self.output_file

        # each tweet is in JSON format and is on a single line in the input file.
        for line in self.input_io:
            # Parse the json and extract the tweet hashtag and created time.
            hashtag_list, tweet_unixtime = self.parse_tweet(line)

            # If there are no hashtags, move on to the next tweet.
            if len(hashtag_list) == 0:
                continue

            # Generate the hashtag pair combinations.
            hashtag_pairs = self.generate_hashtag_combinations(hashtag_list, tweet_unixtime)

            if hashtag_pairs is not None:
                graph_updated = False
                for tweet_pair in hashtag_pairs:
                    # If this tweet pair is within our 60s window, add it to the graph and edge list.
                    # If the pair is outside the 60s window, silently ignore it.
	            if tweet_pair[2] >= (self.most_recent_tweet_time - 60):
            	        self.add_to_tweet_graph(tweet_pair[0], tweet_pair[1])
            	        self.add_to_edge_list(tweet_pair[0], tweet_pair[1], tweet_pair[2])
		        self.update_graph_and_list()
                        graph_updated = True

                # If the graph was updated, then print the rolling average.
                if graph_updated == True:
	            self.calculate_rolling_average()
            else:
                # If the tweet had just a single hashtag, we cannot really add it to the graph, but
                # the tweet was still within the 60s window, so we print the rolling average.
	        self.calculate_rolling_average()

        # Close the input and output files.
        self.input_io.close()
        self.output_io.close()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        averages = AverageDegree(sys.argv[1], sys.argv[2])
        averages.run()
    else:
        print "Syntax: ", sys.argv[0], " <tweets file> <output file>"
