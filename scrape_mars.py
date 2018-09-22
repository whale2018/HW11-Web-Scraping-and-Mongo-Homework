# Import dependencies
from bs4 import BeautifulSoup as bs
import pymongo
from splinter import Browser
import pandas as pd
from selenium import webdriver
import time

# Set up Splinter
def init_browser():
    executable_path = {'executable_path': 'chromedriver.exe'}
    return Browser('chrome', **executable_path, headless=False)

def scrape():
    # create content dict that we can insert into mongo
    content = {}

    browser = init_browser()

    # Scrape the NASA Mars News Site and collect the latest News Title and Paragraph Text.
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)
    #time.sleep(2)
    html = browser.html

    # Create a Beautiful Soup object
    soup = bs(html, 'html.parser')

    # Save latest news title and summary
    content["news_title"] = soup.find('div', class_='content_title').text
    content["news_blurb"] = soup.find("div", class_="article_teaser_body").text

    # Scrape the JPL Mars Space Images and collect the Featured Image
    url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url)
    #time.sleep(2)
    html = browser.html

    # Create a Beautiful Soup object
    soup = bs(html, 'html.parser')

    # Find the link to the featured image details page
    #partial_link = soup.find("a", class_="button")["data-link"]
    #root_url = "https://www.jpl.nasa.gov"
    #details_link = root_url + partial_link

    # Go to the image details page and create Beautiful Soup object
    #browser.visit(details_link)
    #time.sleep(2)
    #html = browser.html
    #soup = bs(html, 'html.parser')

    # Find image url
    #image_url = soup.find('figure', class_="lede").a["href"]

    # Save the featured image url
    #content["featured_image_url"] = root_url + image_url

    #soup = bs(html, 'html.parser')
    #soup.title.text

    item_list = soup.find("ul", class_="articles")

    articles = item_list.find('li', class_='slide')
    
    content["featured_image_url"] = "https://www.jpl.nasa.gov" + articles.find("a")["data-thumbnail"]

    # Scrape the latest Mars weather tweet from the Mars Weather Twitter page
    url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(url)
    #time.sleep(2)
    html = browser.html

    # Create a Beautiful Soup object
    soup = bs(html, 'html.parser')

    # Save the Mars weather tweet
    content["mars_weather"] = soup.find('p', class_="tweet-text").text

    # Use Pandas to scrape the table containing facts about the planet including Diameter, Mass, etc.
    url = "http://space-facts.com/mars/"
    browser.visit(url)
    #time.sleep(3)
    html = browser.html

    # Create a Beautiful Soup object
    soup = bs(html, 'html.parser')

    # Scrape all the tables into a pandas dataframe, take the first table and change the column names
    mars_facts = pd.read_html(url)[0]
    mars_facts.columns = ["Description", "Value"]

    # Remove the index column
    mars_facts.set_index("Description", inplace = True)

    # Convert to HTML
    mars_facts_html = mars_facts.to_html(classes="table table-striped")
    
    # Save the Mars facts table
    content["mars_facts_html"]= mars_facts_html

    # Visit the USGS Astrogeology site to obtain high resolution images for each of Mar's hemispheres.
    url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(url)
    #time.sleep(2)
    html = browser.html

    # Create a Beautiful Soup object
    soup = bs(html, 'html.parser')
    
    # Design an XPATH selector to find the headers
    xpath = "//div[@class='description']//a[@class='itemLink product-item']/h3"

    # The results are the 4 headers to the detail pages
    results = browser.find_by_xpath(xpath)

    # Placeholder
    hemisphere_image_urls = []

    # Loop through all 4 links
    for i in range(4):
        
        # Load the html from the browser again and create Beautiful Soup object
        html = browser.html
        soup = bs(html, 'html.parser')
        
        # find the new Splinter elements
        results = browser.find_by_xpath(xpath)
        
        # Save the name of the hemisphere
        header = results[i].html

        # Click on the header to go to the hemisphere details page 
        details_link = results[i]
        details_link.click()
        #time.sleep(2)
        
        # Load hemisphere details page into Beautiful Soup
        html = browser.html
        soup = bs(html, 'html.parser')
        
        # Save the image url
        hemisphere_image_urls.append({"title": header, "image_url": soup.find("div", class_="downloads").a["href"]})
        
        # Go back to the original page
        browser.back()
        #time.sleep(2)

    content["hemisphere_image_urls"] = hemisphere_image_urls

    browser.quit()

    return content

