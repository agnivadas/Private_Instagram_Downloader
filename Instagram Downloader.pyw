import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import json
import urllib.parse
import os
import asyncio
import aiohttp
import re
import queue
import requests
import time

# Constants for download process
RETRY_COUNT = 3
RETRY_DELAY = 2
LOG_BATCH_INTERVAL = 3000  #  seconds




class InstagramDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Instagram Downloader")
        self.log_queue = queue.Queue()
        # Start a periodic task to update the log output every 5 seconds
        self.root.after(LOG_BATCH_INTERVAL, self.update_log_output)
        # Set up GUI elements
        self.setup_gui()

        self.root.after(100, self.process_log_queue)

    def setup_gui(self):
        # Font settings
        label_font = ("Helvetica", 12, "bold")
        text_font = ("Courier", 10)
        button_font = ("Arial", 10)

        # Input Data Label and Textbox
        self.input_label = tk.Label(self.root, text="Input Data:", font=label_font, bg="#f0f0f0")
        self.input_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.input_text = tk.Text(self.root, height=10, width=55, font=text_font, bg="#ffffff", fg="#000000")
        self.input_text.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        # Paste Data Button to the right of Input Textbox
        self.paste_button = tk.Button(self.root, text="Paste Data", command=self.paste_from_clipboard, font=button_font, bg="#d1d1e0")
        self.paste_button.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Generated URL Label and Textbox
        self.url_label = tk.Label(self.root, text="Generated URL:", font=label_font, bg="#f0f0f0")
        self.url_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)

        self.url_output = tk.Text(self.root, height=2, width=55, font=text_font, bg="#e6e6fa", fg="#000000")
        self.url_output.grid(row=3, column=0, padx=5, pady=5, sticky="w")

        # Copy to Clipboard Button to the right of URL Textbox
        self.copy_button = tk.Button(self.root, text="Copy to Clipboard", command=self.copy_to_clipboard, font=button_font, bg="#d1d1e0")
        self.copy_button.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # Log Output Label and ScrolledText Box with larger width, aligned to the left
        self.log_label = tk.Label(self.root, text="Log Output:", font=label_font, bg="#f0f0f0")
        self.log_label.grid(row=4, column=0, sticky="w", padx=5, pady=5)

        self.log_output = scrolledtext.ScrolledText(self.root, height=10, width=55, font=text_font, bg="#f5f5f5", fg="#000000")
        self.log_output.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # Start Scraping and Reset Buttons
        self.start_button = tk.Button(self.root, text="Start Scraping", command=self.start_thread, font=button_font, bg="#add8e6")
        self.start_button.grid(row=6, column=0, padx=5, pady=5)

        self.reset_button = tk.Button(self.root, text="Reset", command=self.reset, font=button_font, bg="#ffcccb")
        self.reset_button.grid(row=6, column=1, padx=5, pady=5)

    def copy_to_clipboard(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.url_output.get("1.0", "end").strip())

    def paste_from_clipboard(self):
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", self.root.clipboard_get())
        
    def process_log_queue(self):
        while not self.log_queue.empty():
            message = self.log_queue.get_nowait()
            self.log_output(message)
        
        self.root.after(100, self.process_log_queue)

    def log_output(self, message):
        # Update the text box with the message
        self.log_output.insert(tk.END, message + "\n")
        self.log_output.see(tk.END)
    
    def start_thread(self):
        input_data = self.input_text.get("1.0", "end").strip()
        if input_data:  # Ensure there's data to process
            self.input_text.delete("1.0", "end")  # Clear the input field to prevent lag
            thread = threading.Thread(target=self.process_data, args=(input_data,))
            thread.start()
    
    def process_data(self, input_data):
         # Save the input data to a file
        with open("sourcecode.txt", "w", encoding="utf-8") as file:
            file.write(input_data)

        # Load JSON data from the file
        with open("sourcecode.txt", "r", encoding="utf-8") as file:
            json_dict = json.load(file)

        # Extract user_id and scrape user posts
        user_id = self.read_user_id_from_file('user_id.txt')
        full_url = self.scrape_user_posts(user_id, json_dict)
        
        # Update the URL output in the GUI
        self.url_output.delete("1.0", "end")
        self.url_output.insert("1.0", full_url)
        self.url_output.configure(state="normal")
        
        # Start the download process in a new thread
        threading.Thread(target=self.run_download_process).start()

    def run_download_process(self):
        file_path = 'sourcecode.txt'
        links_file = 'urls.txt'
        
        self.extract_and_save_display_urls(file_path, filename=links_file)

        most_frequent_username, count = self.get_usernames(file_path)
        if most_frequent_username:
            download_dir = most_frequent_username
            with open(links_file, 'r') as f:
                links = [line.strip() for line in f.readlines()]

            # Create a new event loop for the thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            proxy_host = "your_proxy_host"  # Replace with actual proxy details if needed
            proxy_port = "your_proxy_port"
            proxy_username = "your_proxy_username"
            proxy_password = "your_proxy_password"           
            # Run the download process asynchronously in the new event loop
            loop.run_until_complete(self.download_images(links, download_dir, proxy_host, proxy_port, proxy_username, proxy_password))
            
            # Run the download_remaining_images method in the same event loop

            self.download_remaining_images(links_file, download_dir, proxy_host, proxy_port, proxy_username, proxy_password)

            loop.close()

            self.log_output.insert(tk.END, "All downloads completed.\n")
            self.log_output.configure(state="disabled")
            

    def scrape_user_posts(self,user_id,json_dict):
        base_url = "https://www.instagram.com/graphql/query/?query_hash=e769aa130647d2354c40ea6a439bfc08&variables="
        variables = {
            "id": user_id,
            "first": 12,
            "after": None,
        }
        full_url = ""  # Initialize full_url to avoid UnboundLocalError
        def capture_end_cursor(json_dict):
            """
            Capture the first end_cursor from the Instagram JSON response.
            """
            end_cursor1 = None
            try:
                posts = json_dict["data"]["user"]["edge_owner_to_timeline_media"]
                page_info = posts["page_info"]
                end_cursor1 = page_info.get("end_cursor")
                
                # If end_cursor is a list, get the first value
                if isinstance(end_cursor1, list) and end_cursor1:
                    end_cursor1 = end_cursor1[0]
            except (KeyError, TypeError) as e:
                print(f"Error capturing end_cursor: {e}")
    
            return end_cursor1
        end_cursor = capture_end_cursor(json_dict)
        # Construct the URL if `end_cursor` is available
        if end_cursor:
            variables["after"] = end_cursor
            json_string = json.dumps(variables)
            encoded_variables = urllib.parse.quote(json_string)
            full_url = base_url + encoded_variables
        else:
           self.url_output.delete("1.0", "end")
           self.url_output.insert(tk.END, "No more pages available.\n")
           self.url_output.configure(state="normal")

        

        return full_url
    

    def read_user_id_from_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                user_id = file.read().strip()
            return user_id
        except FileNotFoundError:
            print(f"File {file_path} not found.")
            return None

    def extract_and_save_display_urls(self, file_path, filename="urls.txt"):
        with open(file_path, 'r', encoding="utf-8") as file:
            text_data = file.read()

        json_dict = json.loads(text_data)  # Convert the JSON string into a dictionary
        pretty_json = json.dumps(json_dict, indent=4)  # Prettify the JSON output

        def extract_image_urls(json_dict):
            image_urls = []
            try:
                for reel in json_dict['data']['reels_media']:
                    for item in reel['items']:
                        for resource in item['video_resources']:
                            image_url = resource['src']
                            image_urls.append(image_url)
            except (KeyError, TypeError) as e:
                print(f"No reel video found")
            return image_urls
        def post(json_dict):
            image_urls = []
            try:
                items = json_dict.get('items', [])

                for item in items:
                    image_versions2 = item.get('image_versions2', {})
                    candidates = image_versions2.get('candidates', [])
                    if candidates:
                        image_url = candidates[0].get('url')
                        if image_url:
                            image_urls.append(image_url)
            except (KeyError, TypeError) as e:
              print(f"Error: {e}")
            return image_urls
        def reel(json_dict):
            image_urls = []
            try:
                items = json_dict.get('items', [])
                for item in items:
                    image_versions2 = item.get('video_versions', [])
                    if image_versions2:
                        image_url = image_versions2[0].get('url')
                        if image_url:
                            image_urls.append(image_url)
            except (KeyError, TypeError) as e:
                print(f"Error: {e}")
            return image_urls    

        urls1 = extract_image_urls(json_dict)
        urls2 = post(json_dict)
        urls3 = reel(json_dict)
        urls = []
        video_url_regex = r'"video_url":\s+"([^"]+)"'
        http_url_regex = r'"display_url":\s+"([^"]+)"'  
        video_urls = re.findall(video_url_regex, pretty_json)
        http_urls = re.findall(http_url_regex, pretty_json)
        urls.extend(video_urls)
        urls.extend(http_urls)
        urls.extend(urls1)
        urls.extend(urls2)
        urls.extend(urls3)


        with open(filename, "w") as file:
            for url in urls:
                file.write(url + "\n")

    async def download_images(self, links, download_dir, proxy_host, proxy_port, proxy_username, proxy_password):
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        connector = aiohttp.TCPConnector()
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = [self.download_image(session, link, download_dir, proxy_host, proxy_port, proxy_username, proxy_password) for link in links]
            for task in asyncio.as_completed(tasks):
                result = await task
                if result:
                    self.log_output.insert(tk.END, result + "\n")
                    self.log_output.yview(tk.END)

    async def download_image(self, session, link, download_dir, proxy_host, proxy_port, proxy_username, proxy_password):
        filename = os.path.basename(link).split('?')[0]
        filename = re.sub(r'[\\/:*?"<>|]', '_', filename)
        download_path = os.path.join(download_dir, filename)

        if os.path.exists(download_path):
            self.log_output.insert(tk.END, f"{filename} already exists\n")
            self.log_output.yview(tk.END)
            return

        attempt = 0
        while attempt < RETRY_COUNT:
            CONCURRENT_DOWNLOADS = 5
            semaphore = asyncio.Semaphore(CONCURRENT_DOWNLOADS)
            async with semaphore:
                try:
                    proxies = f'http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}'
                    async with session.get(link, proxy=None) as response:
                        if response.status == 200:
                            with open(download_path, 'wb') as f:
                                while True:
                                    chunk = await response.content.read(1024)
                                    if not chunk:
                                        break
                                    f.write(chunk)
                            self.log_output.insert(tk.END, f"Downloaded {filename}\n")
                            self.log_output.yview(tk.END)
                            await asyncio.sleep(0.1)
                            return filename
                except aiohttp.ClientError as e:
                    pass

            attempt += 1
            if attempt < RETRY_COUNT:
                await asyncio.sleep(RETRY_DELAY)

        return None
    def download_remaining_images(self, links_file, download_dir, proxy_host, proxy_port, proxy_username, proxy_password):
        """Downloads images from URLs in a text file.

        Args:
        links_file: Path to the text file containing image URLs.
        download_dir: Directory to save downloaded images.
        """
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        with open(links_file, 'r') as f:
            links = f.readlines()

        RETRY_COUNT = 3
        RETRY_DELAY = 2  # seconds

        for link in links:
            link = link.strip()
            filename = os.path.basename(link).split('?')[0]
            filename = re.sub(r'[\\/:*?"<>|]', '_', filename)
            download_path = os.path.join(download_dir, filename)

            if os.path.exists(download_path):
                self.log_output.insert(tk.END, f"File already exists: {download_path}\n")
                self.log_output.yview(tk.END)
                continue  # Skip to the next link

            attempt = 0
            while attempt < RETRY_COUNT:
                try:
                    # Set up proxy if provided
                    proxies = {}
                    if proxy_host and proxy_port:
                        if proxy_username and proxy_password:
                            proxies = {
                                'http': f'http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}',
                                'https': f'http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}'
                            }
                        else:
                            proxies = {
                                'http': f'http://{proxy_host}:{proxy_port}',
                                'https': f'http://{proxy_host}:{proxy_port}'
                            }
                    response = requests.get(link, proxies=None, stream=True)
                    response.raise_for_status()

                    with open(download_path, 'wb') as out_file:
                        for chunk in response.iter_content(chunk_size=1024):
                            if chunk:
                                out_file.write(chunk)
                    self.log_output.insert(tk.END, f"Downloaded: {filename}\n")
                    self.log_output.yview(tk.END)
                    break  # Exit retry loop if successful
                except requests.exceptions.RequestException as e:
                    attempt += 1
                    if attempt < RETRY_COUNT:
                        self.log_output.insert(tk.END, f"Retrying in {RETRY_DELAY} seconds...\n")
                        self.log_output.yview(tk.END)
                        time.sleep(RETRY_DELAY)  # Delay before retrying

    
    def get_usernames(self, file_path):
        with open(file_path, 'r', encoding="utf-8") as file:
            text_data = file.read()

        regex_pattern = r'"username": "(.*?)"'
        json_dict = json.loads(text_data)  # Convert the JSON string into a dictionary
        pretty_json = json.dumps(json_dict, indent=4)
        matches = re.findall(regex_pattern, str(pretty_json))

        if matches:
            username_counts = {}
            for username in matches:
                username_counts[username] = username_counts.get(username, 0) + 1

            most_frequent_username = max(username_counts, key=username_counts.get)
            most_frequent_count = username_counts[most_frequent_username]
            return most_frequent_username, most_frequent_count
        else:
            return None, 0

    def update_log_output(self):
        # Flush the queue and update the log output
        while not self.log_queue.empty():
            log_message = self.log_queue.get_nowait()
            self.log_output.insert(tk.END, log_message)
            self.log_output.yview(tk.END)
        
        # Schedule the next batch update
        self.root.after(LOG_BATCH_INTERVAL, self.update_log_output)

    def reset(self):
        # Clear the output fields and enable the start button for a new session
        self.url_output.delete("1.0", "end")
        self.log_output.configure(state="normal")
        self.log_output.delete("1.0", "end")
        self.start_button.configure(state="normal")
        self.log_output.insert(tk.END, "Ready for the next session.\n")
        self.log_output.yview(tk.END)
        
if __name__ == "__main__":
    root = tk.Tk()
    app = InstagramDownloaderApp(root)
    root.mainloop()
