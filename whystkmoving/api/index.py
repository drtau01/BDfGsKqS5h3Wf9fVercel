from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests
from bs4 import BeautifulSoup
import json
import re

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

                why_moving_text = ""
                try:
                    why_moving_element = soup.find(class_="js-why-stock-moving-static")
                    why_moving_text = why_moving_element.get_text(strip=True) if why_moving_element else ""
                    why_moving_text = re.sub(r".+:\d\d (AM|PM)", r"\g<0>aa", why_moving_text, 1)
                except Exception as e:
                    why_moving_text = f"Error: {str(e)}"

                results.append({
                    "ticker": ticker, 
                    "status": why_moving_text
                })
            except Exception as e:
                results.append({
                    "ticker": ticker, 
                    "status": f"Error: {str(e)}"
                })

        # 2. Return JSON Response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*') # Allow index.html to read this
        self.end_headers()
        self.wfile.write(json.dumps(results).encode())
