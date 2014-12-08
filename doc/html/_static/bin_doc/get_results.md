Get Results Readme
===========================

---------------------------
<a name='toc'>Table of contents:</a>

  * [Get Results Help](#user-content-get-results-help)
  * [Get the results for a saved question](#user-content-get-the-results-for-a-saved-question)
  * [Get the results for a question](#user-content-get-the-results-for-a-question)
  * [Get the results for a action](#user-content-get-the-results-for-a-action)

---------------------------

# Get Results Help

  * Get results from a deploy action, saved question, or question

```bash
get_results.py -h
```

```
usage: get_results.py [-h] -u USERNAME -p PASSWORD --host HOST [--port PORT]
                      [-l LOGLEVEL] -o {saved_question,question,action} -i
                      OBJECT_ID [--file REPORT_FILE] [--dir REPORT_DIR]
                      {csv,json} ...

Get results from a deploy action, saved question, or question

optional arguments:
  -h, --help            show this help message and exit

Handler Authentication:
  -u USERNAME, --username USERNAME
                        Name of user (default: None)
  -p PASSWORD, --password PASSWORD
                        Password of user (default: None)
  --host HOST           Hostname/ip of SOAP Server (default: None)
  --port PORT           Port to use when connecting to SOAP Server (default:
                        444)

Handler Options:
  -l LOGLEVEL, --loglevel LOGLEVEL
                        Logging level to use, increase for more verbosity
                        (default: 0)

Get Result Options:
  -o {saved_question,question,action}, --object {saved_question,question,action}
                        Type of object to get results for (default: )
  -i OBJECT_ID, --id OBJECT_ID
                        id of object to get results for (default: )

Report File Options:
  --file REPORT_FILE    File to save report to (will be automatically
                        generated if not supplied) (default: None)
  --dir REPORT_DIR      Directory to save report to (current directory will be
                        used if not supplied) (default: None)

Export Formats:
  {csv,json}            Export Format choices
    csv                 Produce a CSV report, supply "csv -h" to see CSV
                        options
    json                Produce a JSON report, supply "json -h" to see JSON
                        options

usage: get_results.py csv [-h] [--sort HEADER_SORT | --no-sort | --auto_sort]
                          [--add-sensor | --no-add-sensor]
                          [--add-type | --no-add-type]
                          [--expand-columns | --no-columns]

CSV Export Options

optional arguments:
  -h, --help          show this help message and exit
  --sort HEADER_SORT  Sort headers by given names (default: [])
  --no-sort           Do not sort the headers at all
  --auto_sort         Sort the headers with a basic alphanumeric sort
                      (default)
  --add-sensor        Add the sensor names to each header
  --no-add-sensor     Do not add the sensor names to each header (default)
  --add-type          Add the result type to each header
  --no-add-type       Do not add the result type to each header (default)
  --expand-columns    Expand multi-line cells into their own rows that have
                      sensor correlated columns in the new rows
  --no-columns        Do not add expand multi-line cells into their own rows
                      (default)

usage: get_results.py json [-h]

JSON Export Options

optional arguments:
  -h, --help  show this help message and exit
```

  * Validation Test: exitcode
    * Valid: **True**
    * Messages: Exit Code is 0



[TOC](#user-content-toc)


# Get the results for a saved question

  * Get the results for Saved Question ID 107
  * Save the results to a CSV file

```bash
get_results.py -u 'Tanium User' -p 'T@n!um' --host '172.16.31.128' --loglevel 1 -o "saved_question" --id 107 --file "/var/folders/dk/vjr1r_c53yx6k6gzp2bbt_c40000gn/T/out.csv" csv
```

```
Handler for Session to 172.16.31.128:444, Authenticated: True, Version: 6.2.314.3258
++ Found object: SavedQuestion, name: 'Custom Tags'
++ Found results for object: ResultSet for 2935, ColumnSet: Custom Tags, Count
++ Report file '/var/folders/dk/vjr1r_c53yx6k6gzp2bbt_c40000gn/T/out.csv' written with 77 bytes
```

  * Validation Test: exitcode
    * Valid: **True**
    * Messages: Exit Code is 0

  * Validation Test: file_exist_contents
    * Valid: **True**
    * Messages: File /var/folders/dk/vjr1r_c53yx6k6gzp2bbt_c40000gn/T/out.csv exists, content:

```
Custom Tags
[no results]
TestTag2
TestTag1
TestTag7
TestTag6
TestTag5
```



[TOC](#user-content-toc)


# Get the results for a question

  * Get the results for Question ID 2929
  * Save the results to a CSV file

```bash
get_results.py -u 'Tanium User' -p 'T@n!um' --host '172.16.31.128' --loglevel 1 -o "question" --id 2929 --file "/var/folders/dk/vjr1r_c53yx6k6gzp2bbt_c40000gn/T/out.csv" csv
```

```
Handler for Session to 172.16.31.128:444, Authenticated: True, Version: 6.2.314.3258
++ Found object: Question, id: 2929
++ Found results for object: ResultSet for 2929, ColumnSet: Last Logged In User, Count
++ Report file '/var/folders/dk/vjr1r_c53yx6k6gzp2bbt_c40000gn/T/out.csv' written with 91 bytes
```

  * Validation Test: exitcode
    * Valid: **True**
    * Messages: Exit Code is 0

  * Validation Test: file_exist_contents
    * Valid: **True**
    * Messages: File /var/folders/dk/vjr1r_c53yx6k6gzp2bbt_c40000gn/T/out.csv exists, content:

```
Count,Last Logged In User
1,JTANIUM1\Jim Olsen
5,N/A on Mac
6,N/A on Mac
1,N/A on Mac
```



[TOC](#user-content-toc)


# Get the results for a action

  * Get the results for action ID 122
  * Save the results to a CSV file

```bash
get_results.py -u 'Tanium User' -p 'T@n!um' --host '172.16.31.128' --loglevel 1 -o "action" --id 122 --file "/var/folders/dk/vjr1r_c53yx6k6gzp2bbt_c40000gn/T/out.csv" csv
```

```
Handler for Session to 172.16.31.128:444, Authenticated: True, Version: 6.2.314.3258
++ Found object: Action, name: 'API Deploy Distribute Tanium Standard Utilities'
++ Found results for object: ResultSet for 2922, ColumnSet: Computer Name, Action Statuses, Count
++ Report file '/var/folders/dk/vjr1r_c53yx6k6gzp2bbt_c40000gn/T/out.csv' written with 102 bytes
```

  * Validation Test: exitcode
    * Valid: **True**
    * Messages: Exit Code is 0

  * Validation Test: file_exist_contents
    * Valid: **True**
    * Messages: File /var/folders/dk/vjr1r_c53yx6k6gzp2bbt_c40000gn/T/out.csv exists, content:

```
Action Statuses,Computer Name
122:Completed.,Casus-Belli.local
122:Completed.,jtanium1.localdomain
```



[TOC](#user-content-toc)


###### generated by: `build_bin_doc v1.4.5`, date: Mon Dec  8 12:33:16 2014 EST, Contact info: **Jim Olsen <jim.olsen@tanium.com>**