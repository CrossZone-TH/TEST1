import spotipy
from spotipy.oauth2 import SpotifyOAuth
from transformers import pipeline
import random
import tkinter as tk
from tkinter import messagebox, scrolledtext

# Initialize Spotify API connection
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="f5a870215f95487ba45a6c9861e480cf",
                                               client_secret="4681dc59cc9b4dd3b816df73ab5ca876",
                                               redirect_uri="http://localhost:3000/callback",
                                               scope=["playlist-read-private"]))

# Function to fetch tracks from a playlist
def get_playlist_tracks(playlist_id):
    results = sp.playlist_tracks(playlist_id)
    tracks = []
    for item in results['items']:
        track = item['track']
        song_details = {
            'title': track['name'],
            'artist': track['artists'][0]['name'],
            'id': track['id'],
            'uri': track['uri']
        }
        tracks.append(song_details)
    return tracks

emotion_analyzer = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

labels = ["anger", "sadness", "love", "motivation", "nostalgia", "happy"]

def analyze_emotion(text, top_k=3):
    result = emotion_analyzer(text, candidate_labels=labels)
    sorted_results = sorted(zip(result['labels'], result['scores']), key=lambda x: x[1], reverse=True)[:top_k]
    formatted_results = [f"{label} {score:.2f}" for label, score in sorted_results]
    return formatted_results, sorted_results

def get_playlist_based_on_emotion(emotion_label):
    playlists = {
        "happy": "4VkJiWWvrZfUEOlkzJ6idt",
        "love": "4YJqWkRoT3xwQG2aFPdxPw",
        "sadness": "4fFgsajnXcyCnCQzA7yKt7",
        "motivation": "1pQl2WledUmwM8wFqaog9K",
        "anger": "4FiN0MEPDuDhAmvBXq7Plg",
        "nostalgia": "27Ds6FXEOvBLyJYP43gqsl"
    }
    playlist_id = playlists.get(emotion_label)
    if playlist_id:
        return get_playlist_tracks(playlist_id)
    else:
        return f"No playlist found for emotion: {emotion_label}"

# Tkinter GUI
class EmotionPlaylistApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Emotion-Based Playlist Recommender")

        # Input Label and Entry
        self.input_label = tk.Label(root, text="Enter a sentence:")
        self.input_label.pack(pady=10)

        self.input_entry = tk.Entry(root, width=50)
        self.input_entry.pack(pady=10)

        # Analyze Button
        self.analyze_button = tk.Button(root, text="Analyze Emotion", command=self.analyze_and_display)
        self.analyze_button.pack(pady=10)

        # Result Display
        self.result_text = scrolledtext.ScrolledText(root, width=60, height=20, wrap=tk.WORD)
        self.result_text.pack(pady=10)

    def analyze_and_display(self):
        user_input = self.input_entry.get()
        if not user_input:
            messagebox.showwarning("Input Error", "Please enter a sentence.")
            return

        # Analyze emotion
        emotion_result, sorted_results = analyze_emotion(user_input, top_k=3)

        # Display detected emotions
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Detected Emotions:\n")
        for result in sorted_results:
            self.result_text.insert(tk.END, f"{result[0]} {result[1]:.2f}\n")

        # Get the top emotion
        top_emotion = sorted_results[0][0]

        # Get playlist based on the detected emotion
        recommended_playlist = get_playlist_based_on_emotion(top_emotion)

        # Display recommended playlist
        if isinstance(recommended_playlist, list):
            random.shuffle(recommended_playlist)
            selected_songs = recommended_playlist[:20]

            self.result_text.insert(tk.END, "\nRecommended Playlist:\n")
            for idx, track in enumerate(selected_songs, start=1):
                self.result_text.insert(tk.END, f"{idx}. {track['title']} by {track['artist']}\n")
        else:
            self.result_text.insert(tk.END, recommended_playlist)

# Run the Tkinter app
if __name__ == "__main__":
    root = tk.Tk()
    app = EmotionPlaylistApp(root)
    root.mainloop()