import subprocess
import json
import re

# Function to find the first occurrence of "serializedShareEntity"
def find_serialized_share_entity(d):
    if isinstance(d, dict):
        if "serializedShareEntity" in d:
            return d["serializedShareEntity"]
        for value in d.values():
            found = find_serialized_share_entity(value)
            if found:
                return found
    elif isinstance(d, list):
        for item in d:
            found = find_serialized_share_entity(item)
            if found:
                return found
    return None

def curl(input):
    response = subprocess.run(
        ["sh"], 
        input=input, 
        text=True, 
        capture_output=True
    )

    return response

# Get search input from the user and format it for URL use
search_query = input("Enter search query: ")

# Read the original contents of the search file
with open("./requests/search", "r") as file:
    original_content = file.read()

# Replace the placeholder with the formatted query in memory
search_output = curl(original_content.replace("<!LOVRO!>", search_query))
serialized_entity = find_serialized_share_entity(json.loads(search_output.stdout))

# Read the original contents of the song file
with open("./requests/song", "r") as file:
    song_request = file.read()

# Run the song script using the updated content in memory
song_output = curl(song_request.replace("<!LOVRO!>", serialized_entity))

# Extract the first shortUrl from song_output using regex
match = re.search(r'"shortUrl":"(https://music\.youtube\.com/watch\?v=[^"]+)"', song_output.stdout)
short_url = match.group(1)

# Run yt-dlp to get the direct audio URL
yt_dlp_command = ["yt-dlp", "-f", "bestaudio", "-g", short_url]
audio_url = subprocess.run(yt_dlp_command, capture_output=True, text=True)

# Run VLC with the audio URL
vlc_process = subprocess.Popen(["vlc", audio_url.stdout.strip()])