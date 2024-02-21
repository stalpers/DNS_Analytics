#!/bin/bash
# prepare list
source log.sh

export DPATH=./download
export MM=majestic_million.csv
export TRANCO_ZIP=tranco.csv.zip
export TRANCO=top-1m.csv
export ALEXA_ZIP=alexa.csv.zip
export ALEXA=alexa.csv
export DOMCOP_ZIP=top10milliondomains.csv.zip
export DOMCOP=top10milliondomains.csv
export DATA=./normalize/all_domains.txt

#Quiet
export ZIP_FLAGS=-qo
# export ZIP_FLAGS=

log info Download Alexa Top 1000 TLDs to $DPATH/$ALEXA_ZIP
wget -q http://s3-us-west-1.amazonaws.com/umbrella-static/top-1m.csv.zip -O "$DPATH"/"$ALEXA_ZIP"


log info "Download Majestic Million to $MM"
wget -q https://downloads.majestic.com/majestic_million.csv -O "$DPATH"/"$MM"



log info "Download tranco List to $TRANCO_ZIP"

wget -q https://tranco-list.eu/download_daily/Z32PG -O "$DPATH"/"$TRANCO_ZIP"


log info "DomCom Top 10 million Websites to $DOMCOP_ZIP"

 wget -q https://www.domcop.com/files/top/top10milliondomains.csv.zip -O "$DPATH"/"$DOMCOP_ZIP"


log info "Unzip $ALEXA_ZIP"
unzip $ZIP_FLAGS "$DPATH"/"$ALEXA_ZIP"
mv top-1m.csv $ALEXA
log info "Unzip $TRANCO_ZIP"
unzip $ZIP_FLAGS "$DPATH"/"$TRANCO_ZIP"
log info "Unzip $DOMCOP_ZIP"
unzip $ZIP_FLAGS "$DPATH"/"$DOMCOP_ZIP"
cp "$DPATH"/"$MM" .

log info "Normalize $DOMCOP to normalize/01.txt"
perl normalizer.pl --file=$DOMCOP > ./normalize/01.txt
log info "Normalize  Majestic Million to normalize/02.txt"
cat "$MM" | cut -d',' -f2,3  > ./normalize/tmp1
perl normalizer.pl --file=./normalize/tmp1 > ./normalize/02.txt
rm ./normalize/tmp1
log info "Normalize Alexa to normalize/03.txt"
perl normalizer.pl --file=$ALEXA > ./normalize/03.txt
log info "Normalize Tranco to normalize/04.txt"
perl normalizer.pl --file=$TRANCO > ./normalize/04.txt
cat  normalize/0*.txt > $DATA
log info "Total Domain Count `wc -l $DATA`"
log info "Merge and remove duplicates... "

cat $DATA | sort -u | uniq > normalize/tmp
mv normalize/tmp $DATA
log info "Domains after cleanup `wc -l $DATA`"

# sed 's/^[0-9]*/0/g'