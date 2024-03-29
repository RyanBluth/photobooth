#!/bin/sh

# print-selphy-postcard
# 
# Print postcard-sized (148x100mm, 5.8 x 3.9in) images
# on a Canon Selphy CP1200 and compatible photo printers
#
# Usage: print-selphy-postcard [--border] <file>
#
# This script requires ImageMagick, GNU sed and other text processing
# utilities, and CUPS.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#  
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#  
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Configuration parameters:

# Printer name
# Set Wi-Fi printer name, as seen by CUPS.
#
# Corresponding printer entry in CUPS configuration should be something like:
# dnssd://Canon%20SELPHY%20CP1200._ipp._tcp.local/?uuid=<uuid>
#
# To produce that entry for a new printer, use CUPS printer autodetection
# (usually http://localhost:631 , Administration / Add Printer menu) while
# mDNS service discovery is enabled.
#
PRINTER="CP1200-TurboPrint"

# End of configuration parameters.

check="true"
for ex in \
 identify convert grep tr head lpq lpr
  do
    loc=`which "${ex}"`
    if [ "${loc}" = "" ]
      then
        echo "${ex} is missing"
        check="false"
    fi
done

if [ "${check}" = "false" ]
  then
    echo "Some utilities are missing"
    exit 1
fi

lpq -P "${PRINTER}" >/dev/null 2>&1 || check="false"

if [ "${check}" = "false" ]
  then
    echo "Can't check printer ${PRINTER} status"
    exit 1
fi

imggeom="1760x1190^"

if [ "${1}" = "--border" ]
  then
    shift 1
    imggeom="1700x1130"
fi

if [ -f "${1}" ]
  then
    if \
    echo $(($(identify "${1}" | tr ' ' '\n' | \
              grep '^[0-9]\+x[0-9]\+$' | \
              head -n 1 | tr 'x' '-'))) | \
    grep -q - 
      then
        rotateopt="-rotate" 
        rot="90"
      else
        rotateopt=""
        rot=""
    fi

    convert ${rotateopt} ${rot} -define filter:blur=0.8 \
	    -filter Gaussian -resize "${imggeom}" \
	    -gravity center -extent "1760x1190" "${1}" png:- | \
	convert -page "+46+34" -background white -flatten \
		-extent "1872x1248" png:- -quality 97 jpg:- | \
	lpr -o raw -P "${PRINTER}"

  else
    echo "No input file" 1>&2
    exit 1 
fi