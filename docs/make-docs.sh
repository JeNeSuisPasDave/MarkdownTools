#! /bin/bash
#

# build the styles
#
pushd ../docs-support > /dev/null
./make-docs.sh
popd > /dev/null

# update the styles and JavaScript in this docs folder
#
[ -d "css" ] || mkdir css
[ -d "js" ] || mkdir js
[ -d "styles" ] || mkdir styles
curDir=`pwd`
rootDir=${curDir%/*}
rsync -a $rootDir/docs-support/css/ $curDir/css
rsync -a $rootDir/docs-support/js/ $curDir/js
rsync -a $rootDir/docs-support/styles/ $curDir/styles

# generate the html
#
mdmerge devguide.mmd | multimarkdown > devguide.html