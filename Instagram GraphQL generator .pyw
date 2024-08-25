import tkinter as tk
import json
from tkinter import messagebox
import urllib.parse
import httpx

class InstagramURLGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Instagram GraphQL URL Generator")

        # URL Input Field with Sky Blue Background
        self.input_text = tk.Entry(root, width=50, bg="sky blue", font=("Arial", 12))
        self.input_text.grid(row=0, column=0, padx=10, pady=10)

        # Paste Button with Custom Style
        paste_button = tk.Button(root, text="Paste", command=self.paste_from_clipboard, 
                                 fg="black", font=("Arial", 10, "bold"))
        paste_button.grid(row=0, column=1, padx=5, pady=10)

        # Generate URL Button with Custom Style
        generate_button = tk.Button(root, text="Generate URL", command=self.generate_url, 
                                    bg="light blue", fg="black", font=("Arial", 10, "bold"))
        generate_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        # Output Textbox with Sky Blue Background
        self.url_output = tk.Text(root, height=5, width=50, bg="sky blue", font=("Arial", 12))
        self.url_output.grid(row=2, column=0, padx=10, pady=10)

        # Copy to Clipboard Button with Custom Style
        copy_button = tk.Button(root, text="Copy to Clipboard", command=self.copy_to_clipboard, 
                                    fg="black", font=("Arial", 10, "bold"))
        copy_button.grid(row=2, column=1, padx=5, pady=10)

        # Reset Button with Custom Style
        reset_button = tk.Button(root, text="Reset", command=self.reset_fields, 
                                 bg="red", fg="white", font=("Arial", 10, "bold"))
        reset_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    def identify_url_type(self, url):
        if 'stories/highlights' in url:
            return 'highlight'
        elif 'stories' in url:
            return 'story'
        elif '/p/' in url:
            return 'post'
        elif 'reel' in url:
            return 'post'   
        else:
            return 'profile'
        

    def scrape_user(self, username):
        try:
            response = client.get(
                f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}",
            )
            response.raise_for_status()
            data = response.json()
            return data["data"]["user"]
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to retrieve user data: {e}")
            return None

    def generate_url(self):
        url = self.input_text.get()
        url_type = self.identify_url_type(url)

        if url_type == 'profile':
            username = url.rstrip('/').split('/')[-1]
            user_data = self.scrape_user(username)
            if user_data:
                user_id = user_data.get("id")
                if user_id:
                    with open("user_id.txt", "w") as file:
                      file.write(user_id)
                    base_url = "https://www.instagram.com/graphql/query/?query_hash=e769aa130647d2354c40ea6a439bfc08&variables="
                    variables = {
                        "id": user_id,
                        "first": 12,
                        "after": None,
                    }
                    json_string = json.dumps(variables)
                    encoded_variables = urllib.parse.quote(json_string)
                    full_url = base_url + encoded_variables
                    self.url_output.delete(1.0, tk.END)
                    self.url_output.insert(tk.END, full_url)
                else:
                    tk.messagebox.showerror("Error", "User ID not found.")
            else:
                tk.messagebox.showerror("Error", "User data not retrieved.")

        elif url_type == 'highlight':
            reel_id = url.split('/')[-2]
            base_url = "https://www.instagram.com/graphql/query/?query_hash=de8017ee0a7c9c45ec4260733d81ea31&variables="
            variables = {
                "reel_ids": [],
                "tag_names": [],
                "location_ids": [],
                "highlight_reel_ids": [int(reel_id)],
                "precomposed_overlay": False,
                "show_story_viewer_list": True,
                "story_viewer_fetch_count": 50,
                "story_viewer_cursor": ""
            }
            variables_json = json.dumps(variables)
            encoded_variables = urllib.parse.quote(variables_json)
            highlight_url = base_url + encoded_variables
            self.url_output.delete(1.0, tk.END)
            self.url_output.insert(tk.END, highlight_url)

        elif url_type == 'story':
            username = url.rstrip('/').split('/')[-2]
            user_data = self.scrape_user(username)
            if user_data:
                user_id = user_data.get("id")
                if user_id:
                    with open("user_id.txt", "w") as file:
                     file.write(user_id)
                    base_url = "https://www.instagram.com/graphql/query/?query_hash=de8017ee0a7c9c45ec4260733d81ea31&variables="
                    variables ={
                        "reel_ids": [int(user_id)],
                        "tag_names": [],
                        "location_ids": [],
                        "highlight_reel_ids": [],
                        "precomposed_overlay": False,
                        "show_story_viewer_list": True,
                        "story_viewer_fetch_count": 50,
                        "story_viewer_cursor": ""
                    }
                    variables_json = json.dumps(variables)
                    encoded_variables = urllib.parse.quote(variables_json)
                    story_url = base_url + encoded_variables
                    self.url_output.delete(1.0, tk.END)
                    self.url_output.insert(tk.END, story_url)
                else:
                    tk.messagebox.showerror("Error", "User ID not found.")
            else:
                tk.messagebox.showerror("Error", "User data not retrieved.")
        elif url_type == 'post':
            if url.endswith('/'):
              url = url[:-1]  # Remove the trailing slash if present
            addition = f"/?__a=1&__d=dis"
            full_url = f"{url}" + addition
            self.url_output.delete(1.0, tk.END)
            self.url_output.insert(tk.END, full_url)
        else:
            tk.messagebox.showerror("Error", "Unknown URL type.")
        
    def copy_to_clipboard(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.url_output.get("1.0", "end").strip())

    def paste_from_clipboard(self):
            try:
                clipboard_content = self.root.clipboard_get().strip()
                if clipboard_content:
                    self.input_text.delete(0, tk.END)
                    self.input_text.insert(0, clipboard_content)
                else:
                    raise ValueError("Clipboard is empty")
            except ValueError as e:
                messagebox.showerror("Paste Error", str(e))
            except tk.TclError:
                messagebox.showerror("Paste Error", "Failed to access clipboard content.")

    def reset_fields(self):
        self.input_text.delete(0, tk.END)
        self.url_output.delete(1.0, tk.END)

if __name__ == "__main__":
    client = httpx.Client(
        headers={
            "x-ig-app-id": "936619743392459",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "*/*",
        }
    )

    root = tk.Tk()
    app = InstagramURLGenerator(root)
    root.mainloop()
