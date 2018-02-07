var url = process.argv[2];
var hostname = require("url").parse(url).hostname;
console.log('Starting scraping ' + url + '...')

var scrape = require('website-scraper');
var options =
{
  urls: [url],
  directory: 'crawler-results/' + hostname,
  sources: [
    {selector: 'script', attr: 'src'}
  ]
};

scrape(options).then().catch(console.log);
