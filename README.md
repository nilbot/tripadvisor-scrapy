# Tripadvisor Crawler

This project contains python source code to crawl hotel reviews for tripadvisor.ie

## How to Run:

### First time setup python with virtualenv
```bash
virtualenv --python=python2.7 .
source bin/activate
pip install -r requirements.txt
```


## Legacy Content
1. From the terminal, go the the `scrapers/tripadvisor/tripadvisorCrawler` directory
2. Run the following command:
    ```bash
        scrapy crawl taspider -a urls=/path/to/file
    ```

## Remarks

## [Clearlake Hotel](http://www.tripadvisor.ie/Hotel_Review-g186338-d193616-Reviews-Clearlake_Hotel-London_England.html)
testing hotel 1, 22 reviews, can get 19 reviews, 3 reviews are from google translate (can not get it)
	
## [Palmerstown Lodge](http://www.tripadvisor.ie/Hotel_Review-g186605-d1136060-Reviews-Palmerstown_Lodge-Dublin_County_Dublin.html)
testing hotel 2, 31 reviews, can get 19 reviews, a few reviews are from google translate, and a few of others also can not get for some reason
for example, when download the first page, only can get 6 reviews, but if check form browser, there is 10 reviews there, other four review might from its partner

