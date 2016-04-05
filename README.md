# TwitterHashtagGraph
Calculate the average degree of a vertex in a Twitter hashtag graph for the last 60 seconds, and update this each time a new tweet appears.
===========================================================
@author: Madhavi Deshmukh 

## Challenge Summary

This challenge requires you to:

Calculate the average degree of a vertex in a Twitter hashtag graph for the last 60 seconds, and update this each time a new tweet appears.  You will thus be calculating the average degree over a 60-second sliding window.

To clarify, a Twitter hashtag graph is a graph connecting all the hashtags that have been mentioned together in a single tweet.  Examples of Twitter hashtags graphs are below.

## Details of Implementation

This solution is implemented in Python. The syntax for running this code is

```
    python src/average_degree.py <tweet_input_file> <tweet_output_file>
```

It is assumed that `<tweet_input_file>` contains a json dump of the tweets ingested via Twitter API.

## Algorithm

These are the steps that execute in order to generate the rolling average.

1. Parse the `<tweet_input_file>`
   - iterate over the json, skipping over mallformed or metadata not relevant to tweets.
   - extract the hashtags and the creation time for each tweet.
   - convert the creation time to an integer (unix timestamp).
2. Generate all combinations of the hashtags.
3. If the creation time is within the 60s rolling window
   - If the tweet has at least 2 hashtags
       - Add it to the tweet graph and edge list
       - iterate over the edge list looking for edges/tweets that are now outside the 60s window.
          - Remove each of these edges from the tweet graph and edge list.
   - If the tweet has just a single hashtag (we cannot create an edge from this)
       - Ignore the hashtag
   - Calculate and print rolling average
4. If the creation time is outside the 60s window, silently ignore the tweet
   - No rolling average will be printed

## Data structures used
### Edge list
The edge list is a list of all the hashtag pairs and their creation time. for e.g.:

```
    [['Kafka', 'Apache', 1458841940], ['Hadoop', 'Apache', 1458841932], ['Flink', 'HBase', 1458841930], ['Spark', 'HBase', 1458841918], ['Flink', 'Spark', 1458841915], ['Hadoop', 'Storm', 1458841875], ['Apache', 'Storm', 1458841875], ['Apache', 'Hadoop', 1458841875]]
```

- The edge list is used to keep track of all the edges that are still within the 60s window.
- It is assumed that most of the tweets will be in order, so new edges are prepended/inserted to the beginning of the list if its timestamp is earlier than the first element in the list.
- If we receive an edge that is out of order, but still within the 60s window, we still insert the new edge at the beginning and then sort the list.
    - Sort was primarily used because of lack of time for a better implementation.
    - A better implementation would be to find the correct index by doing a binary search.
- Since the list is sorted with the oldest tweet/edge at the end, we scan the list from the end looking for edges that are outside the 60s window.
    - Any edge found will be deleted from the tweet graph and the edge list itself before calculating the rolling average.

#### Improvements
- The whole edge list would be more efficient if we used a double linked list with a binary search

### Tweet graph
The tweet graph is a nested hashmap.
- The first hashmap is to track all the nodes in the graph.
- Each node has a hash that maintains all its neighbors and count of how many times this edge has occurred (in case of duplicate hastags from different tweets).
    - the edge count is required to make sure the edge is only deleted from the graph after all the duplicate nodes are outside the 60s window.

for e.g.

```
    {'Apache': {'Hadoop': 2, 'Storm': 1, 'Kafka': 1}, 'HBase': {'Spark': 1}, 'Flink': {'Spark': 1, 'HBase': 1}, 'Hadoop': {'Storm': 1}}
```

### Testing the code

4 unit tests were written to test some of the conditions and edge cases. The unit tests can be run from the `run_test.sh` script.

These test cases were also added to the insight_testsuite. They can be run simply by calling `insight_testsuite/run_tests.sh`

=======


