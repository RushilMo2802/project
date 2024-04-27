from kivymd.app import MDApp
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivy.uix.image import AsyncImage
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
import webbrowser
from deepface import DeepFace
import cv2
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
import random

Window.size = (400, 600)

class GetStartedApp(MDApp):
    def build(self):
        self.root_layout = MDFloatLayout()

        # Background image
        bg_image = AsyncImage(source='bg.jpg', size_hint=(1, 1), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.root_layout.add_widget(bg_image)

        # Mood Me label
        mood_me_label = MDLabel(text="Mood Me", halign='center', font_size='32sp', size_hint_y=None, height=48,
                                pos_hint={'center_x': 0.5, 'top': 0.9})
        self.root_layout.add_widget(mood_me_label)

        # Logo image
        logo = AsyncImage(source='logo.png', size_hint=(None, None), size=(200, 200),
                          pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.root_layout.add_widget(logo)

        # Get Started button
        get_started_button = MDRaisedButton(text="Get Started!", size_hint=(None, None), size=(200, 60),
                                            pos_hint={'center_x': 0.5, 'y': 0.1})
        self.root_layout.add_widget(get_started_button)
        get_started_button.bind(on_release=self.switch_to_emotion_analysis)

        return self.root_layout

    def switch_to_emotion_analysis(self, instance):
        # To capture video from the webcam.
        cap = cv2.VideoCapture(0)

        # Capture a single frame.
        ret, frame = cap.read()

        # Save the image.
        cv2.imwrite('captured_image.jpg', frame)

        # Release the VideoCapture object.
        cap.release()

        # Invert the picture
        frame = cv2.flip(frame, 0)

        # Perform sentiment analysis on the saved image.
        try:
            result = DeepFace.analyze(img_path="captured_image.jpg", actions=['emotion'], enforce_detection=True)
            if result and isinstance(result, list) and 'dominant_emotion' in result[0]:
                dominant_emotion = result[0]['dominant_emotion']

                # Get song suggestions based on the dominant emotion
                english_songs, hindi_songs = get_song_suggestions(dominant_emotion)

                # Get movie suggestions based on the dominant emotion
                english_movies, bollywood_movies = get_movie_suggestions(dominant_emotion)

                # Switch to EmotionAnalysisApp and pass the result, captured image path, and recommendations
                self.root_layout.clear_widgets()
                emotion_analysis_app = EmotionAnalysisApp(result=dominant_emotion, image_path='captured_image.jpg',
                                                           english_songs=english_songs, hindi_songs=hindi_songs,
                                                           english_movies=english_movies, bollywood_movies=bollywood_movies,
                                                           get_started_app=self)
                self.root_layout.add_widget(emotion_analysis_app)
            else:
                print("Emotion analysis failed. Result: ", result)
        except Exception as e:
            print("An error occurred during emotion analysis: ", str(e))

class TransparentButton(Button):
    background_color = (0, 0, 0, 0)
    pass
class RecommendationsWindow(Popup):
    def __init__(self, english_songs=[], hindi_songs=[], english_movies=[], bollywood_movies=[], **kwargs):
        super().__init__(**kwargs)
        self.title = 'Recommendations'

        # Set background image
        self.background = 'bg.jpg'

        # Create a layout to hold the recommendations
        layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        # Add buttons for song recommendations
        english_songs_label = Label(text='English Songs:', size_hint_y=None, height=30)
        layout.add_widget(english_songs_label)
        for song in english_songs:
            song_button = TransparentButton(text=f"- {song['name']} by {', '.join(song['artists'])}", size_hint_y=None, height=30)
            song_button.bind(on_release=lambda btn, url=song['spotify_link']: self.open_url(url))
            layout.add_widget(song_button)

        hindi_songs_label = Label(text='Hindi Songs:', size_hint_y=None, height=30)
        layout.add_widget(hindi_songs_label)
        for song in hindi_songs:
            song_button = TransparentButton(text=f"- {song['name']} by {', '.join(song['artists'])}", size_hint_y=None, height=30)
            song_button.bind(on_release=lambda btn, url=song['spotify_link']: self.open_url(url))
            layout.add_widget(song_button)

        # Add buttons for movie recommendations
        english_movies_label = Label(text='English Movies:', size_hint_y=None, height=30)
        layout.add_widget(english_movies_label)
        for movie in english_movies:
            movie_button = TransparentButton(text=f"- {movie['title']} ({movie['release_year']})", size_hint_y=None, height=30)
            movie_button.bind(on_release=lambda btn, url=movie['google_search_link']: self.open_url(url))
            layout.add_widget(movie_button)

        hindi_movies_label = Label(text='Hindi Movies:', size_hint_y=None, height=30)
        layout.add_widget(hindi_movies_label)
        for movie in bollywood_movies:
            movie_button = TransparentButton(text=f"- {movie['title']} ({movie['release_year']})", size_hint_y=None, height=30)
            movie_button.bind(on_release=lambda btn, url=movie['google_search_link']: self.open_url(url))
            layout.add_widget(movie_button)

        # Add the layout to a ScrollView
        scrollview = ScrollView()
        scrollview.add_widget(layout)

        self.content = scrollview

    def open_url(self, url):
        webbrowser.open(url)
class EmotionAnalysisApp(MDFloatLayout):
    def __init__(self, result='', image_path='', english_songs=None, hindi_songs=None, english_movies=None,
                 bollywood_movies=None, get_started_app=None, **kwargs):
        super().__init__(**kwargs)
        self.result = result
        self.image_path = image_path
        self.english_songs = english_songs
        self.hindi_songs = hindi_songs
        self.english_movies = english_movies
        self.bollywood_movies = bollywood_movies
        self.get_started_app = get_started_app
        self.build()

    def build(self):
        # Background image
        bg_image = AsyncImage(source='bg.jpg', size_hint=(1, 1), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.add_widget(bg_image)

        # Display the captured image
        captured_image = AsyncImage(source=self.image_path, size_hint=(None, None), size=(319, 300),
                                   pos_hint={'center_x': 0.482, 'center_y': 0.6})
        self.add_widget(captured_image)

        # Label for displaying emotion result
        result_label = MDLabel(text=f"Dominant Emotion: {self.result}", size_hint=(None, None), pos_hint={'center_x': 0.5, 'center_y': 0.3})
        self.add_widget(result_label)

        # Button for capturing image and performing sentiment analysis
        retry_button = MDRaisedButton(text='Retry', size_hint=(None, None), size=(150, 50),
                                      pos_hint={'center_x': 0.3, 'y': 0.1})
        self.add_widget(retry_button)
        retry_button.bind(on_release=self.get_started_app.switch_to_emotion_analysis)

        # Button for displaying song and movie recommendations
        show_recommendations_button = MDRaisedButton(text='Continue', size_hint=(None, None), size=(300, 50),
                                         pos_hint={'center_x': 0.7, 'y': 0.1})
        self.add_widget(show_recommendations_button)
        show_recommendations_button.bind(on_release=self.show_recommendations)

    def show_recommendations(self, instance):
        # Create a new instance of RecommendationsWindow
        recommendations_window = RecommendationsWindow(english_songs=self.english_songs, hindi_songs=self.hindi_songs,
                                                       english_movies=self.english_movies,
                                                       bollywood_movies=self.bollywood_movies)
        # Open the RecommendationsWindow
        recommendations_window.open()

def authenticate_spotify():
    # Your Spotify API credentials
    client_id = 'ff034e1be2e84da3ac7feba07bb9ab2c'
    client_secret = 'c64965b21b5b405a9166018f160a9aee'

    # Create Spotify client credentials manager
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)

    # Create a Spotify object
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    return sp

def get_song_suggestions(emotion):
    # Code for getting song suggestions from recommendation.py (same as before)
    # Authenticate with Spotify API
    spotify = authenticate_spotify()

    # Map emotions to seed track IDs (you can customize this mapping)
    emotion_to_seed = {
        'happy': {
            'english': '2dpaYNEQHiRxtZbfNsse99',
            'hindi': '0joXv5niso2T8YXWOlIe1X'
        },
        'sad': {
            'english': '6tNQ70jh4OwmPGpYy6R2o9',
            'hindi': '5Gy67YHzPZTk9Q0D73LAGH'
        },
        'angry': {
            'english': '7kDFbQE78O8SDBzOthsKNM',
            'hindi': '3pjZQfBShK7O01QvtQwmcg'
        },
        'neutral': {
            'english': '1q4BCQssFe74UJmnWt5lov',
            'hindi': '0GQngE2rOYvlKwEQjTAsP8'
        },
        # Add more emotions and corresponding seed track IDs as needed
    }

    # Get recommendations based on the detected emotion
    seed_track_ids = emotion_to_seed.get(emotion.lower(),
                                         {'english': 'default_seed_track_id', 'hindi': 'default_seed_track_id'})

    # Get recommendations for English songs
    english_recommendations = spotify.recommendations(seed_tracks=[seed_track_ids['english']], limit=4)

    # Extract suggested English tracks with Spotify links
    suggested_english_songs = []
    for track in english_recommendations['tracks']:
        suggested_english_songs.append({
            'name': track['name'],
            'artists': [artist['name'] for artist in track['artists']],
            'spotify_link': track['external_urls']['spotify']
        })

    # Get recommendations for Hindi songs
    hindi_recommendations = spotify.recommendations(seed_tracks=[seed_track_ids['hindi']], limit=4)

    # Extract suggested Hindi tracks with Spotify links
    suggested_hindi_songs = []
    for track in hindi_recommendations['tracks']:
        suggested_hindi_songs.append({
            'name': track['name'],
            'artists': [artist['name'] for artist in track['artists']],
            'spotify_link': track['external_urls']['spotify']
        })

    return suggested_english_songs, suggested_hindi_songs


def get_bollywood_movies_from_list():
    # URL of the Bollywood movie list
    list_url = "https://api.themoviedb.org/4/list/13650?page=1&api_key=fe90c00914b3052e2af6bce966838d51"

    # Fetch the list of Bollywood movies
    response = requests.get(list_url)
    movie_list = response.json()

    # Extract relevant information from the list
    suggested_bollywood_movies = []
    for movie in movie_list["results"]:
        title = movie['original_title']
        release_year = movie['release_date'][:4]
        google_search_link = f'https://www.google.com/search?q={title.replace(" ", "+")}+({release_year})+movie'
        suggested_bollywood_movies.append({
            'title': title,
            'release_year': release_year,
            'google_search_link': google_search_link
        })

    return suggested_bollywood_movies
def get_movie_suggestions(emotion):
    # Code for getting movie suggestions from recommendation.py (same as before)
    # Your TMDb API key
    tmdb_api_key = 'fe90c00914b3052e2af6bce966838d51'

    # Map emotions to genre IDs (you can customize this mapping)
    emotion_to_genre = {
        'happy': {
            'english': 35,  # Comedy
        },
        'sad': {
            'english': 18,  # Drama
        },
        'angry': {
            'english': 28,  # Action
        },
        'neutral': {
            'english': 27,  # Horror and romance (or any neutral genre)
        },
        # Add more emotions and corresponding genre IDs as needed
    }

    # Get the genre ID based on the detected emotion
    genre_id = emotion_to_genre.get(emotion.lower(), 18)  # Default to drama if emotion not found

    # Get Bollywood movies from the specific list
    suggested_bollywood_movies = get_bollywood_movies_from_list()

    # Shuffle and select a subset of Bollywood movies
    random.shuffle(suggested_bollywood_movies)
    bollywood_movies_subset = random.sample(suggested_bollywood_movies, min(4, len(suggested_bollywood_movies)))

    # Print detected emotion and corresponding genre IDs
    print("Detected Emotion:", emotion)
    print("Genre IDs:", emotion_to_genre.get(emotion.lower(), {'english': 18, 'hindi': 18}))

    # Get genre IDs based on the detected emotion
    genre_ids = emotion_to_genre.get(emotion.lower(), {'english': 18, 'hindi': 18})

    # Get recommendations for English movies
    discover_url_english = f'https://api.themoviedb.org/3/discover/movie?api_key={tmdb_api_key}&language=en-US&sort_by=popularity.desc&include_adult=false&include_video=false&page=1&with_genres={genre_ids["english"]}'
    print("English Movies URL:", discover_url_english)
    response_english = requests.get(discover_url_english)
    movies_data_english = response_english.json()['results']

    # Extract English movie titles and release years, limiting to 20 movies
    suggested_english_movies = []
    for movie in movies_data_english[:20]:
        title = movie['title']
        release_year = movie['release_date'][:4]
        google_search_link = f'https://www.google.com/search?q={title.replace(" ", "+")}+({release_year})+movie'
        suggested_english_movies.append({
            'title': title,
            'release_year': release_year,
            'google_search_link': google_search_link
        })

    # Shuffling movie lists
    random.shuffle(suggested_english_movies)

    # Select a subset of randomly shuffled movies
    english_movies_subset = random.sample(suggested_english_movies, min(4, len(suggested_english_movies)))

    return english_movies_subset, bollywood_movies_subset

if __name__ == '__main__':
    GetStartedApp().run()
