from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests
from bs4 import BeautifulSoup
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. Get tickers from URL (e.g., /api?tickers=AAPL,TSLA)
        params = parse_qs(urlparse(self.path).query)
        ticker_list = params.get('tickers', [''])[0].split(',')
        
        results = []
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

        for ticker in ticker_list:
            ticker = ticker.strip().upper()
            if not ticker: continue
            
            try:
                url = f"https://finviz.com/quote.ashx?t={ticker}"
                response = requests.get(url, headers=headers, timeout=5)
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find price and change in the 'snapshot-table2'
                price = soup.find('td', string='Price').find_next_sibling('td').text
                change = soup.find('td', string='Change').find_next_sibling('td').text
                
                results.append({
                    "ticker": ticker,
                    "price": price,
                    "change": change
                })
            except Exception:
                results.append({"ticker": ticker, "price": "Error", "change": "N/A"})

        # 2. Return JSON Response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*') # Allow index.html to read this
        self.end_headers()
        self.wfile.write(json.dumps(results).encode())
