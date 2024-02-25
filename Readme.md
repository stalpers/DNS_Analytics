# Bulk DNS query tools #
## Perform analytics or OSINT on a DNS infrastructure ##

DNS offers a wide range of information for OSINT or analytics - these scripts are intended to compile huge DNS datasets, perform efficient DNS lookups and prepare the output for further processing

### Performing DNS lookups ###

The async_lookup.py script performs asynchronous DNS lookups based on a input file containing a list of domains.  

```
$ python ./async_lookup.py --help
Usage: async_lookup.py [OPTIONS]

Options:
  --input_file TEXT     Input file.  [required]
  --start_at INTEGER    Chunk to start (including)  querying at.
  --stop_at INTEGER     Chunk to stop (including) querying at.
  --chunk_size INTEGER  Chunk size.
  --concur INTEGER      Concurrency limit.
  --activity_log TEXT   Activity log file when running in background mode
  --background          Enable or disable background mode.
  --help                Show this message and exit.
```



```
python .\async_lookup.py --input_file=domains.example --concur=50 --chunk_size=500
Domain list 0000000000/2: 100%|███████████████████████████████████████| 154/154 [00:00<00:00, 157.68it/s]
```

### Compiling Domain data ###

The directory ```prepare``` hosts the necessary infrastructure to generate huge DNS data dictionaries as a foundation for analytics.
While the script ```prepare.sh``` will take care of all downloading an normalizing the final result will be stored as ```all_domains.txt``` in tthe ```normalize``` directory 
Note: ```prepare.sh``` is limited to a number of "top1 million" lists. If you are considering an even broader view, ```prepare_full.sh``` might be a better choice sionce it will incorporate a "Top 10 million". But be aware that the lookup will take a considerable amount of time!