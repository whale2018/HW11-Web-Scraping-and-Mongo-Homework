# import necessary libraries
from flask import Flask, render_template, redirect
#from flask_pymongo import PyMongo
import scrape_mars
import pymongo

# create instance of Flask app
app = Flask(__name__)
#app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)
db = client.mars_data

# Use flask_pymongo to set up mongo connection
#mongo = PyMongo(app)

# create route that renders index.html template and finds documents from mongo
@app.route("/")
def home():

    # Find data
    news_content = db.news_content.find()

    # return template and data
    return render_template("index.html", news_content=news_content)


# Route that will trigger scrape functions
@app.route("/scrape")
def scrape():


    # Run scraping function
    news = scrape_mars.scrape()
    
    # Store results into a dictionary
    content = {
        "news_title": news["news_title"],
        "news_blurb": news["news_blurb"],
        "featured_image_url": news["featured_image_url"],
        "mars_weather": news["mars_weather"],
        "mars_facts": news["mars_facts_html"],
        "hemisphere_image_urls": news["hemisphere_image_urls"]
    }

    # Delete previous news content, if it exists
    db.news_content.drop()

    # Insert new content into database
    db.news_content.insert_one(content)

    # Redirect back to home page
    #return redirect("http://localhost:5000/", code=302)
    return redirect("/", code=302)


if __name__ == "__main__":
    app.run(debug=True)
