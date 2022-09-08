import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import csv
import time


start = time.time()

# webpages are classed into read, unread or broken
# read pages have been crawled, broken pages caused exception
read = []
unread = []
broken = []

with open("urls.csv", newline="\n") as urls:
    reader = csv.reader(urls)
    
    for i in reader:
        if i[1] == "unread":
            unread.append(i[0])
        elif i[1] == "read":
            read.append(i[0])
        else:
            broken.append(i[0])

# only crawl 10 pages at a time
i = 0
while i < 10:
    url = ""

    try:
        url = unread.pop()
        response = requests.get(url)
        text = response.text
        anchors = BeautifulSoup(text, features="html.parser").find_all("a", href = True)
        
        j = 0

        for anchor in anchors:
            href = anchor.get("href")
            
            if href[:8] == "https://":
                parsed = urlparse(href)
                # taking the path leads to most pages crawled being from the same site
                link = parsed.scheme + "://" + parsed.netloc
                
                # don't take links we already have
                if link not in read and link not in unread and link != url:
                    unread.append(link)
                    j += 1

            if j > 5:
                break
        
        read.append(url)
        
        i += 1
    except requests.RequestException as e:
        print(e)
        print(url)
        broken.append(url)
    except IndexError as e: # unread was empty
        print(e)
        break
    except Exception as e: # whatever
        broken.append(url)
        print(e)
        print(url)
        break

with open("urls.csv", "w", newline="\n") as urls:
    writer = csv.writer(urls)

    for j in read:
        writer.writerow([j, "read"])
    
    for j in unread:
        writer.writerow([j, "unread"])
        
    for j in broken:
        writer.writerow([j, "broken"])

print("Synchronously read {} pages in {} seconds".format(i, round(time.time()-start)))
