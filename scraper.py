#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json
from datetime import datetime, timedelta, timezone
import csv
import time
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email Configuration - UPDATE THESE
EMAIL_SENDER = "hello@atomparish.com"
EMAIL_PASSWORD = "fVqGk3ZsL3479"  # Generate an App Password if using Gmail
EMAIL_RECEIVER = "hello@atomparish.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Endpoint
base_url = "https://api.buywander.com/api/site/auction/list"

# Specific interests keywords
INTERESTS = {
    "Networking/Homelab": ["server", "switch", "router", "ubiquiti", "unifi", "cisco", "rack", "ethernet", "nas", "synology", "qnap", "patch panel"],
    "Benz S550": ["mercedes", "benz", "s550", "w222"],
    "Ram 1500": ["ram 1500", "dodge ram", "hemi"],
    "Auto Tools": ["socket", "wrench", "jack", "diagnostic", "scanner", "milwaukee", "dewalt", "makita", "snap-on", "impact driver", "torque wrench"],
    "Pool": ["pool", "pump", "filter", "skimmer", "chlorinator", "vacuum", "dolphin"],
    "Headphones": ["headphone", "sony", "bose", "sennheiser", "audio-technica", "beyerdynamic", "focal", "hifiman"],
    "Projectors": ["projector", "epson", "optoma", "benq", "sony", "jvc", "4k projector"]
}

# Categories to fetch (broad set to catch all interests)
CATEGORIES = [
    "Automotive",
    "Computer & Office",
    "Electronics",
    "Garden & Tools",
    "Outdoors",
    "Industrial"
]

req_body = {
    "pageNumber": 1,
    "pageSize": 48,
    "conditions": [],
    "itemTypes": None,
    "categories": CATEGORIES,
    "additionalCategories": [],
    "filter": None,
    "losing": False,
    "maxRetailPrice": None,
    "minRetailPrice": None,
    "myAuctions": False,
    "search": "",
    "sortBy": "BidsHighest",
    "storeLocationIds": ["08dd87d1-4832-58a3-00d8-6156d6200000"],  # Spokane
    "watching": False,
    "winning": False
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def fetch_all_auctions():
    all_items = []
    page = 1
    while True:
        req_body["pageNumber"] = page
        try:
            response = requests.post(base_url, json=req_body, headers=headers)
            response.raise_for_status()
            data = response.json()
            all_items.extend(data.get("items", []))
            if not data.get("hasNextPage", False):
                break
            page += 1
            # Random delay (2-4 seconds) to mimic human behavior and avoid rate limits
            time.sleep(random.uniform(2, 4))
        except Exception as e:
            print(f"Error on page {page}: {e}")
            break
    return all_items

def get_interest_match(title):
    title_lower = title.lower()
    matches = []
    for category, keywords in INTERESTS.items():
        for keyword in keywords:
            if keyword in title_lower:
                matches.append(category)
                break # Found a match in this category, move to next
    return ", ".join(matches) if matches else None

def is_interesting_deal(item):
    title = item["item"].get("title", "N/A")
    interest_match = get_interest_match(title)
    
    # If it matches our specific interests, we want to see it regardless of "deal" status
    # But we can still flag if it's a good price
    if interest_match:
        return True, interest_match
        
    return False, None

def send_email(items):
    if not items:
        return

    subject = f"BuyWander Alert: {len(items)} Items Found"
    
    # Create HTML body
    html = """
    <html>
      <body>
        <h2>BuyWander Deal Alert</h2>
        <p>Found {} items matching your interests:</p>
        <table style="border-collapse: collapse; width: 100%;">
          <tr style="background-color: #f2f2f2;">
            <th style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">Category</th>
            <th style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">Title</th>
            <th style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">Price</th>
            <th style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">Link</th>
          </tr>
    """.format(len(items))

    # Add top 20 items to email to keep it readable
    for item in items[:20]:
        title = item["item"].get("title", "N/A")
        price = item.get("winningBid", {}).get("amount", 0) if item.get("winningBid") else 0
        url = f"https://buywander.com/auction/{item['id']}"
        category = item.get('interest_category', 'Unknown')
        
        html += f"""
          <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{category}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{title}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">${price}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><a href="{url}">View</a></td>
          </tr>
        """

    html += """
        </table>
        <p>Check the CSV file for the full list.</p>
      </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = subject
    msg.attach(MIMEText(html, 'html'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def monitor_deals():
    print("Fetching auctions...")
    auctions = fetch_all_auctions()
    print(f"Fetched {len(auctions)} auctions total")
    
    interesting_items = []
    
    for item in auctions:
        is_interesting, interest_category = is_interesting_deal(item)
        if is_interesting:
            item['interest_category'] = interest_category
            interesting_items.append(item)

    if interesting_items:
        # Save to CSV
        filename = 'buywander_interests.csv'
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Interest Category', 'Title', 'Retail', 'Current Bid', 'Bids', 'End Date', 'URL', 'Image URL'])
            
            for item in interesting_items:
                title = item["item"].get("title", "N/A")
                retail = item["item"].get("price", 0)
                winning_bid = item.get("winningBid")
                bid = winning_bid.get("amount", 0) if winning_bid else 0
                bids_count = winning_bid.get("bids", 0) if winning_bid else 0
                end_date = item.get("endDate", "N/A")
                url = f"https://buywander.com/auction/{item['id']}"
                interest = item.get('interest_category', 'Unknown')
                
                # Try to get image URL
                images = item["item"].get("images", [])
                image_url = ""
                if images and isinstance(images, list) and len(images) > 0:
                    first_image = images[0]
                    if isinstance(first_image, str):
                        image_url = first_image
                    elif isinstance(first_image, dict):
                        image_url = first_image.get("url", "")

                writer.writerow([interest, title, retail, bid, bids_count, end_date, url, image_url])
        
        print(f"Found {len(interesting_items)} interesting items! Saved to {filename}")
        
        # Print a summary
        print("\n--- Summary of Findings ---")
        for item in interesting_items[:5]: # Show first 5
             title = item["item"].get("title", "N/A")
             price = item.get("winningBid", {}).get("amount", 0) if item.get("winningBid") else 0
             print(f"- {title} (Bid: ${price})")
             
        # Send email notification
        send_email(interesting_items)
             
    else:
        print("No items matching your specific interests found today.")

if __name__ == "__main__":
    monitor_deals()
