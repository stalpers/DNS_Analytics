#!/bin/bash
# prepare list
source log.sh

export OPTIND=1

export DO_DOMCOP=0
export DEBUG=0

while getopts "h?m?d?:" opt; do
  case "$opt" in
    h|\?)
      echo "Usage: prepare.sh [-d] [-m] [-h]"
      echo "Download, consolidate and normalize DNS information"
      echo " "
      echo "-d      Enable debug messages"
      echo "-m      Include DomCoP Top 10 Million Domain List"
      echo "-h     Show this help message"
      exit 0
      ;;
    m)  DO_DOMCOP=1
      ;;
    d)  DEBUG=1
      ;;
  esac
done


export DPATH=./download
export NPATH=./normalize
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

if [ ! -d "$DPATH" ]; then
  log info "Creating download dir $DPATH"
  mkdir $DPATH
fi

if [ ! -d "$NPATH" ]; then
  log info "Creating download dir $NPATH"
  mkdir $NPATH
fi

log info "Starting to download input data"
log info "Download Alexa Top 1000 TLD..."
wget -q http://s3-us-west-1.amazonaws.com/umbrella-static/top-1m.csv.zip -O "$DPATH"/"$ALEXA_ZIP" && log debug "Successfully downloaded Alexa Top 1000 TLDs to $DPATH/$ALEXA_ZIP" || log err "Failed to download Alexa Top 1000 TLDs"


log info "Download Majestic Million..."
wget -q https://downloads.majestic.com/majestic_million.csv -O "$DPATH"/"$MM" && log debug "Successfully downloaded Majestic Million to $MM" || log err "Failed to download Majestic Million"

log info "Download Tranco List..."
wget -q https://tranco-list.eu/download_daily/Z32PG -O "$DPATH"/"$TRANCO_ZIP"  && log debug "Successfully downloaded Tranco List to $TRANCO_ZIP" || log err "Failed to download Tranco List"

if [ $DO_DOMCOP -gt 0 ]; then
  log info "Download DomCom Top 10 Million Websites..."
  wget -q https://www.domcop.com/files/top/top10milliondomains.csv.zip -O "$DPATH"/"$DOMCOP_ZIP"   && log debug "Successfully downloaded DomCom Top 10 million Websites to $DOMCOP_ZIP" || log err "Failed to download DomCom Top 10 million Websites"
else
  log info "Skipping DomCom Top 10 Million Websites"
fi
unzip $ZIP_FLAGS "$DPATH"/"$ALEXA_ZIP" && log info "$ALEXA_ZIP unzipped successfully" || log err "Failed to unzip $ALEXA_ZIP"
mv top-1m.csv $ALEXA
unzip $ZIP_FLAGS "$DPATH"/"$TRANCO_ZIP" && log info "$TRANCO_ZIP unzipped successfully" || log err "Failed to unzip $TRANCO_ZIP"
unzip $ZIP_FLAGS "$DPATH"/"$DOMCOP_ZIP" && log info "$DOMCOP_ZIP unzipped successfully" || log err "Failed to unzip $DOMCOP_ZIP"
cp "$DPATH"/"$MM" .



log info "Starting to normalize data..."



log info "Normalize  Majestic Million to normalize/02.txt"
cat "$MM" | cut -d',' -f2,3  > $NPATH/tmp1
perl normalizer.pl --file=$NPATH/tmp1 > $NPATH/02.txt
rm $NPATH/tmp1
log info "Normalize Alexa to normalize/03.txt"
perl normalizer.pl --file=$ALEXA > $NPATH/03.txt
log info "Normalize Tranco to normalize/04.txt"
perl normalizer.pl --file=$TRANCO > $NPATH/04.txt

tail -n +2 "$NPATH/02.txt" > $DATA
if [ $DO_DOMCOP -gt 0 ]; then
  log info "Normalize Top 10 Million Domains $DOMCOP to normalize/01.txt"
  perl normalizer.pl --file=$DOMCOP > $NPATH/01.txt
  tail -n +2 "$NPATH/01.txt" >> $DATA
else
  log info "Skipping DomCom Top 10 Million Websites"
fi
cat "$NPATH/03.txt" >> $DATA
cat "$NPATH/04.txt" >> $DATA
log info "Total Domain Count `wc -l $DATA`"
log info "Merge and remove duplicates... "
cat $DATA | sort -u | uniq > $NPATH/tmp
mv $NPATH/tmp $DATA
log info "Domains after cleanup `wc -l $DATA`"
