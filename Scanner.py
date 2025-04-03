import os
import re
import requests
import tkinter as tk
from tkinter import messagebox
from plyer import notification

class Downloader:
    def __init__(self):
        self.downloads = []

    def add_download(self, url):
        self.downloads.append(url)

    def download_file(self, url, destination, callback=None):
        response = requests.get(url, stream=True)
        with open(destination, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        if callback:
            callback(destination)
        return destination

class Scanner:
    def __init__(self):
        self.obfuscated_patterns = [
            (r'eval\(', 'Usage of eval function'),
            (r'exec\(', 'Usage of exec function'),
            (r'base64_decode\(', 'Usage of base64_decode function')
        ]
        self.web_request_patterns = [
            (r'http://', 'HTTP web request'),
            (r'https://', 'HTTPS web request')
        ]

    def scan_file(self, file_path):
        reasons = []
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
            for pattern, reason in self.obfuscated_patterns:
                if re.search(pattern, content):
                    reasons.append(reason)
            for pattern, reason in self.web_request_patterns:
                if re.search(pattern, content):
                    reasons.append(reason)
        return reasons

class DownloadManagerUI:
    def __init__(self, downloader, scanner):
        self.downloader = downloader
        self.scanner = scanner
        self.root = tk.Tk()
        self.root.title("Download Manager")

        self.url_label = tk.Label(self.root, text="Enter the URL to download:")
        self.url_label.pack()
        self.url_entry = tk.Entry(self.root, width=50)
        self.url_entry.pack()

        self.destination_label = tk.Label(self.root, text="Enter the destination file path:")
        self.destination_label.pack()
        self.destination_entry = tk.Entry(self.root, width=50)
        self.destination_entry.pack()

        self.download_button = tk.Button(self.root, text="Download", command=self.start_download)
        self.download_button.pack()

    def run(self):
        self.root.mainloop()

    def start_download(self):
        url = self.url_entry.get()
        destination = self.destination_entry.get()
        self.downloader.add_download(url)
        self.downloader.download_file(url, destination, self.scan_and_prompt)

    def scan_and_prompt(self, file_path):
        reasons = self.scanner.scan_file(file_path)
        if reasons:
            reason_text = "\n".join(reasons)
            notification.notify(
                title="File Detected - Please Review",
                message=f"Detected the following issues:\n{reason_text}",
                timeout=10
            )
            if messagebox.askyesno("Scan Results", f"Detected the following issues:\n{reason_text}\nDo you want to keep the file?"):
                messagebox.showinfo("Download Manager", "Download completed successfully.")
            else:
                os.remove(file_path)
                messagebox.showinfo("Download Manager", "Download canceled and file deleted.")
        else:
            messagebox.showinfo("Download Manager", "Download completed successfully.")

def main():
    downloader = Downloader()
    scanner = Scanner()
    ui = DownloadManagerUI(downloader, scanner)
    ui.run()

if __name__ == "__main__":
    main()
