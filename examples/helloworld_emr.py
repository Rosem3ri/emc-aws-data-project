### First attempt to run a "hello world" file on several instances(?) on AWS

import time
import csv
from datetime import datetime
from boto.emr.step import StreamingStep
from boto.emr.connection import EmrConnection

def get_credentials():
    credentials_file_path = '../myJob.conf'
    credentials_file_list = []    
    with open(credentials_file_path) as f:
        r = csv.reader(f)
        credentials_file_list.append([row for row in r if row])
    credentials_dict = dict(zip(credentials_file_list[0][0],\
        credentials_file_list[0][1]))
    return credentials_dict

credentials = get_credentials()

raw_input(credentials)

job_ts = datetime.now().strftime("%Y%m%d%H%M%S")
# EmrConn() args: aws_access_key_id=None  aws_secret_access_key=None,
emr = EmrConnection(aws_access_key_id= credentials['aws_access_key_id'],\
    aws_secret_access_key = credentials['aws_secret_access_key'])


print "logged in / made new emr?"
raw_input()

# Python files must be hosted on s3 and linked to for execution.
## [ ] TODO(emmagras): Check the docs for StreamingStep and understand
##     the arguments below.

## args for StreamingStep: name, mapper uri, reducer uri=None,
## combiner uri=None, action_on_failure='TERMINATE_JOB_FLOW', 
## cache_files=None, cache_archives=None, step_args=None,
## input=None, output=None, 
## jar='/home/hadoop/contrib/streaming/hadoop-streaming.jar'
wc_step = StreamingStep('wc text', \
  's3://elasticmapreduce/samples/wordcount/wordSplitter.py', \
  'aggregate', input='s3://elasticmapreduce/samples/wordcount/input', \
  output='s3://wc-test-bucket/output/%s' % job_ts)
jf_id = emr.run_jobflow('wc jobflow', 's3n://emr-debug/%s' % job_ts, \
  steps=[wc_step])

while True:
  jf = emr.describe_jobflow(jf_id)
  print "[%s] %s" % (datetime.now().strftime("%Y-%m-%d %T"), jf.state)
  if jf.state == 'COMPLETED':
    break
time.sleep(10)
