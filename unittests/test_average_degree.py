import unittest
import sys
import os
import difflib

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../src/')
from average_degree import *

class TestAverageDegree(unittest.TestCase):

    def assertFilesEqual(self, output_file, expected_file, msg=None):

        with open(output_file, 'r') as output_content_file:
            output_content = output_content_file.read()
        #print "Output:", output_content

        with open(expected_file, 'r') as expected_content_file:
            expected_content = expected_content_file.read()
        #print "expected:", expected_content

        if output_content != expected_content:
            message = ''.join(difflib.ndiff(output_file.splitlines(True), expected_content.splitlines(True)))
            if msg:
                message += " : " + msg
            self.fail("Multi-line strings are unequal:\n" + message)

    def __init__(self, *args, **kwargs):
        super(TestAverageDegree, self).__init__(*args, **kwargs)
        self.file_dir = os.path.dirname(os.path.realpath(__file__))
        #print self.file_dir

    def test_tweets_all_distinct(self):
        input_file = self.file_dir + '/input/tweet_2_tweets_all_distinct.txt'
        output_file = self.file_dir + '/output/tweet_2_tweets_all_distinct.txt'
        expected_file = self.file_dir + '/expected/tweet_2_tweets_all_distinct.txt'

        average_degree = AverageDegree(input_file, output_file)
        average_degree.run()

        self.assertFilesEqual(output_file, expected_file)

    def test_everything_out_of_order(self):
        input_file = self.file_dir + '/input/everything_out_of_order_tweets.txt'
        output_file = self.file_dir + '/output/everything_out_of_order_output.txt'
        expected_file = self.file_dir + '/expected/everything_out_of_order.txt'

        average_degree = AverageDegree(input_file, output_file)
        average_degree.run()

        self.assertFilesEqual(output_file, expected_file)

    def test_large_tweet_stream(self):
        input_file = self.file_dir + '/input/large_tweet_stream.txt'
        output_file = self.file_dir + '/output/large_tweet_stream.txt'
        expected_file = self.file_dir + '/expected/large_tweet_stream.txt'

        average_degree = AverageDegree(input_file, output_file)
        average_degree.run()

        self.assertFilesEqual(output_file, expected_file)

    def test_example_from_description(self):
        input_file = self.file_dir + '/input/example_from_description.txt'
        output_file = self.file_dir + '/output/example_from_description.txt'
        expected_file = self.file_dir + '/expected/example_from_description.txt'

        average_degree = AverageDegree(input_file, output_file)
        average_degree.run()

        self.assertFilesEqual(output_file, expected_file)

if __name__ == '__main__':
    unittest.main()
