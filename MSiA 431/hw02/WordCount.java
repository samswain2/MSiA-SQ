import java.io.*;
import java.util.*;

import org.apache.hadoop.fs.Path;
import org.apache.hadoop.conf.*;
import org.apache.hadoop.io.*;
import org.apache.hadoop.mapred.*;
import org.apache.hadoop.util.*;


public class WordCount extends Configured implements Tool {

                                                                    //Mapper Input Key: Byte Offset of Line (IntWritable)
                                                                    //Mapper Input Value: line of file (Text)
                                                                    //Mapper Output Key: Word (Text)
                                                                    //Mapper Output Value: 1 (IntWritable)
	public static class Map extends MapReduceBase implements Mapper<LongWritable, Text, Text, IntWritable> {
		
        //Declare mapper output variables outside of map function
        //If you were mapping one billion rows, this operation would still be completed once per Map initiation,
        	//rather than once per row
		private static final IntWritable one = new IntWritable(1);
    	private Text word = new Text();

		public void configure(JobConf job) {
		}//configure
		protected void setup(OutputCollector<Text, IntWritable> output) throws IOException, InterruptedException {
			//The setup job is ran once in each map task. Here you could initialize a set of words which
			//you want to exclude from word count, like a set of stop words.
				// example: https://stackoverflow.com/questions/25432598/what-is-the-mapper-of-reducer-setup-used-for
		}//setup
                    //  Byte Offset of Line, line text                Word      1
		public void map(LongWritable key, Text value, OutputCollector<Text, IntWritable> output, Reporter reporter) throws IOException {
		    //Read first value (line)
		    String line = value.toString();

		    //tokenize
            StringTokenizer tokenizer = new StringTokenizer(line);

            //Create key, output pair (word, 1) as output
            //Key is word and value is 1
      		while (tokenizer.hasMoreTokens()) {
       			word.set(tokenizer.nextToken());
        		output.collect(word, one);
			  }//loop
		}//mapper
		protected void cleanup(OutputCollector<Text, IntWritable> output) throws IOException, InterruptedException {
			//The cleanup job is ran once in each map task, similar to the setup function
		}//cleanup
	}//Map class
	
	//Begin Reducer class

                                                                        //Reducer Input Key: Word (Text)
                                                                        //Reducer Input Values: 1 (IntWritable)
                                                                        //Reducer Output Key: Word (Text)
                                                                        //Reducer Output Value: Sum of Input Values (IntWritable)
	public static class Reduce extends MapReduceBase implements Reducer<Text, IntWritable, Text, IntWritable> {
		
		public void configure(JobConf job) {
		}//configure
		protected void setup(OutputCollector<Text, IntWritable> output) throws IOException, InterruptedException {
		}//setup
                    //      Word      All values that match key                    Word     Sum of Values
		public void reduce(Text key, Iterator<IntWritable> values, OutputCollector<Text, IntWritable> output, Reporter reporter) throws IOException {
			int sum = 0;
			while (values.hasNext()) {
				sum += values.next().get();
			}
			output.collect(key, new IntWritable(sum));
		}
        protected void cleanup(OutputCollector<Text, IntWritable> output) throws IOException, InterruptedException {
		}//cleanup
	}//Reduce Class

    //configurations
	public int run(String[] args) throws Exception {
		JobConf conf = new JobConf(getConf(), WordCount.class);
		conf.setJobName("wordcount");

		// conf.setNumReduceTasks(0);

		// conf.setBoolean("mapred.output.compress", true);
		// conf.setBoolean("mapred.compress.map.output", true);

		conf.setOutputKeyClass(Text.class);
		conf.setOutputValueClass(IntWritable.class);

		conf.setMapperClass(Map.class);
		conf.setCombinerClass(Reduce.class);
		conf.setReducerClass(Reduce.class);

		conf.setInputFormat(TextInputFormat.class);
		conf.setOutputFormat(TextOutputFormat.class);

		FileInputFormat.setInputPaths(conf, new Path(args[0]));
		FileOutputFormat.setOutputPath(conf, new Path(args[1]));

		JobClient.runJob(conf);
		return 0;
    }//run

    public static void main(String[] args) throws Exception {
		int res = ToolRunner.run(new Configuration(), new WordCount(), args);
		System.exit(res);
    }//main
}//WordCount