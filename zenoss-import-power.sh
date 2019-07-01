#!/bin/bash
# Description: a shell script you can use from a cronjob to import power usage for a year
# You can set the graph name here to avoid setting on the command line
name="Greystone_Power_Greystone_Interval_Power"
year="2019"
#bulk="01 02 03 04 05 06"
yesterday=$(date -d "yesterday" '+%m/%d/%Y')

while getopts ":b:nh" opt; do
  case ${opt} in
    n ) name=$OPTARG;
      ;;
    b ) bulk=$OPTARG;
      ;;
    h ) echo "Usage: $0 [ DEFAULT: will import yesterday's power usage ]";
         echo " or    $0 Set Graph Name: -n [Name of Graph]"; 
         echo " or    $0 Bulk month import: -b [Months to import]"; 
         echo "Example: $0";
         echo "Example: $0 -n \"Greystone_Power_Greystone_Interval_Power\"";
         echo "Example: $0 -b \"01 02 03 04 05\"";
         echo "Example: $0 -b \"01 02 03 04 05\" -n \"Greystone_Power_Greystone_Interval_Power\"";
         exit 0;
      ;;
    * ) echo "Unknown option, try '$0 -h' for help";
        exit 1;
      ;;
  esac
done

if [[ ! -z "${bulk}" ]]
then
  # Delete old graph, if exists
  if [[ -e "/tmp/${name}.rrd" ]]
  then
    echo "Removing old graph file"
    rm -f "/tmp/${name}.rrd"
  fi

  echo "bulk importing power usage for months ${bulk} for the year ${year}"
  sleep 5
  for month in ${bulk};
  do
    echo "bulk importing power usage for ${month}/${year}"
    ansible-playbook -i inventory -e "import_bulk=true import_month=${month} import_year=${year}" site.yml
  done
else
  ansible-playbook -e "import_bulk=false get_start_date=${yesterday} get_end_date=${yesterday} dates=['${yesterday}']" -i inventory site.yml
fi
