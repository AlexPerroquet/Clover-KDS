# Make sure to add an .env in the same folder as where your .oy is running with 

API_KEY = "YOUR_AI_KEY"
MERCHANT_ID = "YOUR_MERCHANT_ID"

# to run the program you'll need to run: python kds_display.py

this will open the port 5000 on your localhost that you can afterward push to the web.


## Docker
build: `docker build -t kds:2.2.3 .`    

run: `docker run -p 5000:5000 -d kds:2.2.3`

show docker process: `docker ps -a`

show logs: `docker logs {container ID}`
