import os
import tkinter as tk
from tkinter import messagebox, font, filedialog
import json
import ctypes
import sys
from PIL import Image, ImageTk  # Add this import for custom icon support

# Function to set custom app icon
def set_app_icon(root, icon_path):

    icon = Image.open(icon_path)
    photo = ImageTk.PhotoImage(icon)
    root.iconphoto(False, photo)

# You can call this function after creating your root window, like this:
# root = tk.Tk()
# set_app_icon(root, "path/to/your/icon.png")

# Define constants
BLOCKED_SITES_FILE = "blocked_sites.json"
HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts" if sys.platform == "win32" else "/etc/hosts"
ADULT_KEYWORDS = ['adult', 'xxx', 'porn', 'mature', 'sex', 'nsfw']

# Color scheme
BG_COLOR = "#1E1E1E"
FG_COLOR = "#FFFFFF"
ACCENT_COLOR = "#007ACC"
BUTTON_BG = "#3A3A3A"
BUTTON_FG = "#FFFFFF"
ENTRY_BG = "#2D2D2D"
ENTRY_FG = "#FFFFFF"
LISTBOX_BG = "#2D2D2D"
LISTBOX_FG = "#FFFFFF"

# Global variables
blocked_sites = []

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return os.geteuid() == 0

def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

def load_blocked_sites():
    global blocked_sites
    if os.path.exists(BLOCKED_SITES_FILE):
        with open(BLOCKED_SITES_FILE, 'r') as f:
            blocked_sites = json.load(f)
    else:
        blocked_sites = []

def save_blocked_sites():
    with open(BLOCKED_SITES_FILE, 'w') as f:
        json.dump(blocked_sites, f)

def update_hosts_file():
    if not is_admin():
        messagebox.showerror("Error", "Administrator privileges required.")
        return

    try:
        with open(HOSTS_PATH, 'r') as file:
            content = file.readlines()

        new_content = [line for line in content if not line.strip().endswith("# XBlocker")]
        
        for site in blocked_sites:
            new_content.append(f"127.0.0.1 {site} # XBlocker\n")
            new_content.append(f"127.0.0.1 www.{site} # XBlocker\n")

        with open(HOSTS_PATH, 'w') as file:
            file.writelines(new_content)

        messagebox.showinfo("Success", "Hosts file updated successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update hosts file: {str(e)}")

def block_site(url):
    if url not in blocked_sites:
        blocked_sites.append(url)
        save_blocked_sites()
        update_hosts_file()

def block_site_from_entry():
    url = entry.get().strip()
    if url:
        block_site(url)
        messagebox.showinfo("Blocked", f"{url} has been blocked!")
        entry.delete(0, tk.END)
        update_blocked_list()

def block_sites_from_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        with open(file_path, 'r') as file:
            sites = file.read().splitlines()
        for site in sites:
            if site:
                block_site(site)
        messagebox.showinfo("Blocked", f"{len(sites)} sites have been blocked!")
        update_blocked_list()

def update_blocked_list():
    blocked_listbox.delete(0, tk.END)
    for site in blocked_sites:
        blocked_listbox.insert(tk.END, site)

class RoundedButton(tk.Canvas):
    def __init__(self, parent, width, height, cornerradius, padding, color, text='', command=None):
        tk.Canvas.__init__(self, parent, borderwidth=0, 
            relief="flat", highlightthickness=0, bg=BG_COLOR)
        self.command = command

        if cornerradius > 0.5*width:
            cornerradius = 0.5*width
        if cornerradius > 0.5*height:
            cornerradius = 0.5*height

        rad = 2*cornerradius
        def shape():
            self.create_polygon((padding,height-cornerradius-padding,padding,cornerradius+padding,padding+cornerradius,padding,width-padding-cornerradius,padding,width-padding,cornerradius+padding,width-padding,height-cornerradius-padding,width-padding-cornerradius,height-padding,padding+cornerradius,height-padding), fill=color, outline=color)
            self.create_arc((padding,padding+rad,padding+rad,padding), start=90, extent=90, fill=color, outline=color)
            self.create_arc((width-padding-rad,padding,width-padding,padding+rad), start=0, extent=90, fill=color, outline=color)
            self.create_arc((width-padding,height-rad-padding,width-padding-rad,height-padding), start=270, extent=90, fill=color, outline=color)
            self.create_arc((padding,height-padding-rad,padding+rad,height-padding), start=180, extent=90, fill=color, outline=color)

        shape()
        self.create_text(width/2, height/2, text=text, fill=BUTTON_FG, font=('Arial', 12, 'bold'))
        self.configure(width=width, height=height)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _on_press(self, event):
        self.configure(relief="sunken")

    def _on_release(self, event):
        self.configure(relief="raised")
        if self.command is not None:
            self.command()

def main():
    global entry, blocked_listbox
    
    load_blocked_sites()
    
    window = tk.Tk()
    window.configure(bg=BG_COLOR)
    window.title("XBlocker")
    window.geometry("600x700")

    # Update this line with the path to your icon
    set_app_icon(window, "images/icon.png")  # Assuming the icon is in an 'images' subdirectory

    title_font = font.Font(family="Segoe UI", size=28, weight="bold")
    normal_font = font.Font(family="Segoe UI", size=12)
    button_font = font.Font(family="Segoe UI", size=10, weight="bold")

    header_frame = tk.Frame(window, bg=ACCENT_COLOR)
    header_frame.pack(fill=tk.X, ipady=20)

    title_label = tk.Label(header_frame, text="XBlocker", font=title_font, bg=ACCENT_COLOR, fg=FG_COLOR)
    title_label.pack()

    content_frame = tk.Frame(window, bg=BG_COLOR)
    content_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

    input_frame = tk.Frame(content_frame, bg=BG_COLOR)
    input_frame.pack(fill=tk.X, pady=(0, 10))

    label = tk.Label(input_frame, text="Enter URL to block:", font=normal_font, bg=BG_COLOR, fg=FG_COLOR)
    label.pack(side=tk.LEFT, padx=(0, 10))

    entry = tk.Entry(input_frame, width=40, font=normal_font, bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=FG_COLOR)
    entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

    button_frame = tk.Frame(content_frame, bg=BG_COLOR)
    button_frame.pack(fill=tk.X, pady=10)

    block_button = RoundedButton(button_frame, 180, 40, 20, 2, BUTTON_BG, text="Block Site", command=block_site_from_entry)
    block_button.pack(side=tk.LEFT, padx=(0, 10))

    block_file_button = RoundedButton(button_frame, 180, 40, 20, 2, BUTTON_BG, text="Block Sites from File", command=block_sites_from_file)
    block_file_button.pack(side=tk.LEFT, padx=10)

    update_button = RoundedButton(button_frame, 180, 40, 20, 2, BUTTON_BG, text="Update Hosts File", command=update_hosts_file)
    update_button.pack(side=tk.LEFT, padx=(10, 0))

    blocked_label = tk.Label(content_frame, text="Blocked Sites", font=normal_font, bg=BG_COLOR, fg=FG_COLOR)
    blocked_label.pack(pady=(20, 5), anchor='w')

    listbox_frame = tk.Frame(content_frame, bg=LISTBOX_BG, bd=1, relief=tk.SUNKEN)
    listbox_frame.pack(fill=tk.BOTH, expand=True)

    blocked_listbox = tk.Listbox(listbox_frame, font=normal_font, bg=LISTBOX_BG, fg=LISTBOX_FG, selectbackground=ACCENT_COLOR, bd=0, highlightthickness=0)
    blocked_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(listbox_frame, orient="vertical", command=blocked_listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    blocked_listbox.config(yscrollcommand=scrollbar.set)

    update_blocked_list()

    window.mainloop()

if __name__ == "__main__":
    if not is_admin():
        run_as_admin()
    else:
        main()




