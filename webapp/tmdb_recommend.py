import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity
from difflib import get_close_matches
import os
import re

def normalize_title(title):
    title = title.lower()
    title = re.sub(r'\b(part|chapter|episode|vol|volume)\s*\d+\b', '', title)
    title = re.sub(r'\b\d+\b', '', title)
    title = title.replace(':', '').strip()
    return title

# =========================================================
# 1. LOAD CSV
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "data", "tmdb_5000_movies.csv")

df = pd.read_csv(CSV_PATH)
df.columns = df.columns.str.lower()



# =========================================================
# 2. NORMALIZE COLUMN NAMES
# =========================================================
COLUMN_MAP = {
    'movie_id': 'id',
    'tmdb_id': 'id',
    'description': 'overview',
    'plot': 'overview',
    'summary': 'overview',
    'genre': 'genres',
    'category': 'genres',
    'rating': 'vote_average',
    'score': 'vote_average',
}

df = df.rename(columns=COLUMN_MAP)

# =========================================================
# 3. ENSURE REQUIRED COLUMNS
# =========================================================
REQUIRED = ['id', 'title', 'overview', 'genres', 'release_date', 'vote_average']
for col in REQUIRED:
    if col not in df.columns:
        df[col] = ""

df = df[REQUIRED].fillna("")

# =========================================================
# 4. IMPROVED TEXT COLUMN (SUBTLE UPGRADE)
# =========================================================
# Title is repeated to give it more weight (human trick)
df['text'] = (
    df['title'] + " " +
    df['title'] + " " +
    df['overview'] + " " +
    df['genres']
)

df['text'] = df['text'].replace('', 'movie film')

# =========================================================
# 5. GENRE PARSING
# =========================================================
def parse_genres(x):
    if isinstance(x, str):
        return [g.strip().lower() for g in x.replace('|', ',').split(',') if g.strip()]
    return []

df['genre_list'] = df['genres'].apply(parse_genres)

# =========================================================
# 6. TF-IDF (SLIGHTLY BETTER FILTERING)
# =========================================================
tfidf = TfidfVectorizer(
    stop_words='english',
    min_df=2  # removes noisy one-off words
)

overview_matrix = tfidf.fit_transform(df['text'])

# =========================================================
# 7. GENRE SIMILARITY
# =========================================================
mlb = MultiLabelBinarizer()
genre_matrix = mlb.fit_transform(df['genre_list'])

# =========================================================
# 8. COMBINED SIMILARITY (MORE BALANCED)
# =========================================================
overview_sim = cosine_similarity(overview_matrix)
genre_sim = cosine_similarity(genre_matrix)

combined_sim = (overview_sim * 0.65) + (genre_sim * 0.35)

# =========================================================
# 9. FUZZY TITLE MATCH (UNCHANGED)
# =========================================================
def find_closest_title(title):
    matches = get_close_matches(title, df['title'].tolist(), n=1, cutoff=0.6)
    return matches[0] if matches else None

# =========================================================
# 10. MAIN FUNCTION (SMARTER FILTER)
# =========================================================
def get_tmdb_recommendations(movie_title, limit=10):
    if not movie_title:
        return []

    movie_title = find_closest_title(movie_title)
    if not movie_title:
        return []

    idx = df[df['title'] == movie_title].index[0]
    scores = list(enumerate(combined_sim[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)

    recommended_titles = []

    for i, score in scores[1:]:
        # skip very weak similarities
        if score < 0.05:
            continue

        title = df.iloc[i]['title']

        # avoid near-duplicate titles
        if title.lower() in movie_title.lower():
            continue

        recommended_titles.append(title)

        if len(recommended_titles) == limit:
            break

    return recommended_titles
