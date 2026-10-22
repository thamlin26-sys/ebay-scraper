# eBay Scraper ("ebay-dl.py")

"ebay-dl.py" is a Python command-line utility that scrapes product search results from eBay (or parses offline HTML practice files across 10 pages), extracts key listing details, and converts the data into structured JSON files.

# What "ebay-dl.py" Does
The script reads a search term from the command line then processes search result listings, and outputs a JSON file named after the search term. 

For every listing card parsed across all pages, it extracts the following fields:
- 
"name": Title of the item listing.
- "price": Item price converted to cents.
- "status": Condition of the item.
- "shipping": Shipping cost in cents.
- "free_returns": "true" or "false" indicating if returns are free.
- "items_sold": Total number of items sold.

Missing listing fields are retained with "null" values.

# Installation
Install the libraries:
python -m pip install requests beautifulsoup4

# Code ran in terminal
outputs mechanical keyboard, vintage camera, and board game use artificial practice data

# Commands for search terms
python ebay-dl.py --search "mechanical keyboard" --pages-dir practice-pages
python ebay-dl.py --search "vintage camera" --pages-dir practice-pages
python ebay-dl.py --search "board game" --pages-dir practice-pages