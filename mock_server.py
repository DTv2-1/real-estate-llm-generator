import http.server
import socketserver
import json
import time
import os

PORT = 8000
DIRECTORY = "/Users/1di/kp-real-estate-llm-prototype"

class MockHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_POST(self):
        if self.path == '/ingest/url/':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Simulate processing time
            time.sleep(2)
            
            # Mock response data
            response_data = {
                "id": 123,
                "property_name": "Luxury Ocean View Villa (DEMO)",
                "price_usd": 450000,
                "price_formatted": "$450,000",
                "listing_type": "Sale",
                "property_type": "House/Villa",
                "bedrooms": 3,
                "bathrooms": 2.5,
                "area_sqm": 250,
                "location": "Tamarindo, Guanacaste",
                "description": "This is a SIMULATED response from the Data Collector demo. In the real system, this text would be extracted from the property website using AI. Includes stunning ocean views, infinity pool, and modern amenities.",
                "confidence_score": 0.95,
                "source_url": "https://example.com/property",
                "status": "processed"
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
        else:
            self.send_error(404, "Endpoint not found in mock server")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

print(f"🚀 Mock Server running at http://localhost:{PORT}")
print("📂 Serving files from:", DIRECTORY)
print("⚡️ API Endpoint ready: /ingest/url/")

with socketserver.TCPServer(("", PORT), MockHandler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped.")
