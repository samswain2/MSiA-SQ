echo "scan 'tlewis', {COLUMNS => ['to', 'body'], FILTER => \"SingleColumnValueFilter('to', 'to', = ,'binary:pete.davis@enron.com') AND ValueFilter(= ,'substring:schedule')\"}" | hbase shell > pete_schedule.txt

echo "disable 'tlewis'"

echo "drop 'tlewis'"

exit