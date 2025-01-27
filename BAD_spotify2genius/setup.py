from setuptools import setup
setup(
    name='spotify2genius',
    version='0.1.0',
    description='get lyrics from matches of songs between spotify playlist and genius',
    packages=["spotify2genius"],
    install_requiermnets=[
        'python-dotenv',
        'google-cloud-storage',
        'python-Levenshtein-wheels',
        'spotipy',
        'lyricsgenius'],
)
