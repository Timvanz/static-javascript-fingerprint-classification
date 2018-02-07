# static_fp_analyser

## Requirements
```
npm install website-scraper
npm install js-beautify
npm install walk
npm install esprima
npm install estraverse
```

## How to use
Execute in the following order:
```
./run-scraper.sh <file_with_URLs>
 python3 parse-js-from-html.py crawler-results/
 nodejs deobfuscation.js crawler-results/
 nodejs scope.js crawler-results/
 python3 count-signs.py crawler-results/
```

