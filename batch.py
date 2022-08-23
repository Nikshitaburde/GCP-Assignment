import argparse
import logging
import re

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

class DataIngestion:
    def parse_method(self, string_input):
        values = re.split(",", re.sub('\r\n', '', re.sub('"', '',
                                                         string_input)))
        row = dict(
            zip(('Transaction ID', 'Date', 'Product SKU', 'Product', 'Product Category', 'Quantity','Avg Price','Revenue','Tax','Delivery'),
                values))
        return row
        
def run(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input',
        dest='input',
        required=False,
        help='Input file to read. This can be a local file or '
        'a file in a Google Storage Bucket.',
        # This example file contains a total of only 10 lines.
        # Useful for developing on a small set of data.
        default='gs://my-firstbucket1/Online.csv')
    
    parser.add_argument('--output',
                        dest='output',
                        required=False,
                        help='Output BQ table to write results to.',
                        default='lake.Online')

    # Parse arguments from the command line.
    known_args, pipeline_args = parser.parse_known_args(argv)
    
    data_ingestion = DataIngestion()
    
    p = beam.Pipeline(options=PipelineOptions(pipeline_args))
    (p| 'Read from a File' >> beam.io.ReadFromText(known_args.input,skip_header_lines=1)
    | 'String To BigQuery Row' >>
     beam.Map(lambda s: data_ingestion.parse_method(s)) |
     'Write to BigQuery' >> beam.io.Write(
          beam.io.BigQuerySink(
               known_args.output,
               schema='Transaction ID:INTEGER,Date:INTEGER,Product SKU:STRING,Product:STRING,Product Category:STRING,Quantity:INTEGER,'
               'Avg Price:FLOAT','Revenue:FLOAT','Tax:FLOAT','Delivery:FLOAT',
             # Creates the table in BigQuery if it does not yet exist.
             create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
             # Deletes all data in the BigQuery table before writing.
             write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE)))
    p.run().wait_until_finish()
    
if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
    
                                                  
