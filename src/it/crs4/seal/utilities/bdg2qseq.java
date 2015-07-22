
package it.crs4.seal.utilities;

import java.util.List;
import java.util.ArrayList;
import java.io.IOException;
import java.io.PrintStream;

import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.fs.PathFilter;
import org.apache.hadoop.util.Tool;
import org.apache.hadoop.util.ToolRunner;
import org.apache.hadoop.conf.Configured;

import parquet.avro.AvroParquetReader;

import org.bdgenomics.formats.avro.Fragment;
import org.bdgenomics.formats.avro.Sequence;

public class bdg2qseq extends Configured implements Tool
{
	private static class QseqPrinter
	{
		public void printRecord(Fragment fragment, PrintStream out)
		{
			String readName = fragment.getReadName().toString();
			String[] fields;
			if (readName != null)
				 fields = readName.split(":");
			else
				throw new RuntimeException("read is missing 'readName'");

			if (fields.length < 6)
				throw new RuntimeException("format of readName isn't the same as generated by Demux (readName: " + readName + "'");

			List<Sequence> sequenceArray = fragment.getSequences();

			if (sequenceArray == null || sequenceArray.size() <= 0)
				throw new RuntimeException("sequences are missing from record " + readName);

			for (int readIdx = 0; readIdx < sequenceArray.size(); ++readIdx)
			{
				for (int i = 0; i < 6; ++i) {
					out.print(fields[i]);
					out.print('\t');
				}
				out.print(readIdx + 1); out.print('\t');

				Sequence sequence = sequenceArray.get(readIdx);
				if (sequence.getBases() != null)
					out.print(sequence.getBases());
				out.print('\t');

				if (sequence.getQualities() != null)
					out.print(sequence.getQualities());
				out.print('\t');

				out.println('1'); // the quality check 
			}
		}
	}

	private static class StdPathFilter implements PathFilter {
		public boolean accept(Path p) {
			String name = p.getName();
			return !(name.startsWith("_") || name.startsWith(".") || name.equals("_logs"));
		}
	}


	private QseqPrinter printer;
	private PrintStream output;
	private PathFilter filter;

	public bdg2qseq()
	{
		printer = new QseqPrinter();
		output = System.out;
		filter = new StdPathFilter();
	}

	public void printDataset(Path input) throws IOException
	{
		List<Path> expandedInput = expandInputPath(input);
		for (Path p: expandedInput) {
			printFile(p);
		}
	}

	protected List<Path> expandInputPath(Path path) throws IOException
	{
		List<Path> retval = new ArrayList<Path>(10);

		FileSystem fs = path.getFileSystem(getConf());
		if (fs.isDirectory(path))
		{
			for (FileStatus p: fs.listStatus(path, filter)) {
				if (p.isFile())
					retval.add(p.getPath());
				else if (p.isDirectory())
					retval.addAll(expandInputPath(p.getPath()));
				//else ignore it
			}
		}
		else if (fs.isFile(path) && filter.accept(path)) {
			retval.add(path);
		}
		else
			throw new IllegalArgumentException("Invalid input path " + path);

		return retval;
	}

	public void printFile(Path p) throws IOException
	{
		AvroParquetReader<Fragment> reader = new AvroParquetReader<Fragment>(p);
		Fragment nextRecord = reader.read();
		System.err.println("starting to convert...");
		int count = 0;

		while (nextRecord != null) {
			printer.printRecord(nextRecord, output);
			++count;
			nextRecord = reader.read();
		}
		System.err.println("Converted " + count + " records");
	}

	public int run(String[] args) throws Exception
	{
		if (args.length != 1) {
			System.err.println("Usage:  bdg2qseq <INPUT>");
			ToolRunner.printGenericCommandUsage(System.err);
			return 2;
		}

		Path input = new Path(args[0]);
		System.err.println("Reading input from " + input);

		printDataset(input);
		return 0;
	}

	public static void main(String[] args) throws Exception {
		ToolRunner.run(null, new bdg2qseq(), args);
	}
}
