from flask import Flask, render_template, request, jsonify, session, redirect
import pandas as pd
import pickle
import math
import sqlite3
import re
import numpy as np

app = Flask(__name__)
app.secret_key = "cinematch_secret"

# ---------------- LOAD DATA ----------------

movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# ---------------- SAFETY CHECKS ----------------

if "vote_average" not in movies.columns:
    movies["vote_average"] = 0

if "poster_url" not in movies.columns:
    movies["poster_url"] = ""

if "genres" not in movies.columns:
    movies["genres"] = ""

if "release_date" not in movies.columns:
    movies["release_date"] = ""

movies["vote_average"] = pd.to_numeric(movies["vote_average"], errors="coerce").fillna(0)

MOVIES_PER_PAGE = 15

# ---------------- SQLITE DATABASE ----------------

def get_db():
    conn = sqlite3.connect("cinematch.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        username TEXT PRIMARY KEY,
        email TEXT,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS favorites(
        username TEXT,
        movie TEXT
    )
    """)

    conn.commit()
    conn.close()


create_tables()

# ---------------- POSTER ----------------

def fetch_poster(title):
    movie = movies[movies["title"] == title]

    if not movie.empty:
        return movie.iloc[0].get("poster_url", "")

    return ""

# ---------------- DISPLAY CLEANERS ----------------

def add_spaces_to_name(text):
    """
    Convert CamelCase names to readable names.
    Example: JasonStatham -> Jason Statham
             RicRomanWaugh -> Ric Roman Waugh
    """
    if text is None:
        return ""
    text = str(text).strip()
    if not text:
        return ""
    text = re.sub(r'(?<!^)(?=[A-Z])', ' ', text)
    return text.strip()


def clean_list_display(value):
    """
    Convert list / numpy array / weird string list to clean comma-separated text.
    Removes brackets, quotes, extra spaces, and newlines properly.
    """

    if value is None:
        return "N/A"

    if isinstance(value, float) and pd.isna(value):
        return "N/A"

    # numpy array -> list
    if isinstance(value, np.ndarray):
        value = value.tolist()

    # normal python list
    if isinstance(value, list):
        cleaned = []
        for item in value:
            item = str(item).strip()
            item = item.replace("'", "").replace('"', "")
            item = item.replace("[", "").replace("]", "")
            item = re.sub(r"\s+", " ", item).strip()

            if item:
                cleaned.append(add_spaces_to_name(item))

        return ", ".join(cleaned) if cleaned else "N/A"

    # convert to string
    value = str(value).strip()

    if not value:
        return "N/A"

    # remove brackets + quotes
    value = value.replace("[", "").replace("]", "")
    value = value.replace("'", "").replace('"', "")

    # split by comma OR newline
    if "," in value:
        parts = [x.strip() for x in value.split(",")]
    else:
        parts = [x.strip() for x in value.splitlines()]

    cleaned = []
    for part in parts:
        part = re.sub(r"\s+", " ", part).strip()
        if part:
            cleaned.append(add_spaces_to_name(part))

    return ", ".join(cleaned) if cleaned else "N/A"


def clean_sentence(value):
    """
    Convert tokenized list into proper sentence.
    """
    if value is None:
        return "N/A"

    if isinstance(value, float) and pd.isna(value):
        return "N/A"

    if isinstance(value, np.ndarray):
        value = value.tolist()

    if isinstance(value, list):
        words = [str(v).strip() for v in value if str(v).strip()]
        return " ".join(words) if words else "N/A"

    value = str(value).strip()
    return value if value else "N/A"

# ---------------- HELPER FUNCTIONS ----------------

def safe_series_to_string(series):
    return series.astype(str).fillna("")


def get_genre_set(value):
    """
    Convert genres/tags style value to a normalized set of genre words.
    Works with list / array / string.
    """
    if value is None:
        return set()

    if isinstance(value, float) and pd.isna(value):
        return set()

    if isinstance(value, np.ndarray):
        value = value.tolist()

    if isinstance(value, list):
        parts = [str(x).strip().lower() for x in value if str(x).strip()]
        return set(parts)

    value = str(value).strip().lower()
    if not value:
        return set()

    value = value.replace("[", "").replace("]", "").replace("'", "").replace('"', "")
    value = value.replace(",", " ")
    parts = [x.strip() for x in value.split() if x.strip()]
    return set(parts)


def get_movie_genre_set(row):
    """
    Prefer genres column; fallback to tags.
    """
    genres = set()

    if "genres" in row.index:
        genres = get_genre_set(row["genres"])

    if not genres and "tags" in row.index:
        genres = get_genre_set(row["tags"])

    return genres

# ---------------- RECOMMEND ----------------

def recommend(movie_name):
    """
    Return top 10 better similar movies:
    - uses cosine similarity
    - removes duplicates / same movie
    - prefers genre overlap
    - does NOT destroy similarity ranking with heavy re-sorting
    """

    temp_df = movies.copy()
    temp_df["title_lower"] = temp_df["title"].astype(str).str.lower().str.strip()

    movie_name = str(movie_name).lower().strip()

    if movie_name not in temp_df["title_lower"].values:
        return pd.DataFrame()

    idx = temp_df[temp_df["title_lower"] == movie_name].index[0]
    base_movie = temp_df.loc[idx]

    distances = similarity[idx]

    # take larger candidate pool first for better filtering
    candidate_list = sorted(
        list(enumerate(distances)),
        key=lambda x: x[1],
        reverse=True
    )[1:60]

    base_title = str(base_movie["title"]).strip().lower()
    base_genres = get_movie_genre_set(base_movie)

    selected_indices = []
    seen_titles = set()

    # First pass: prioritize movies with genre overlap
    for i, sim_score in candidate_list:
        row = temp_df.iloc[i]
        title = str(row["title"]).strip().lower()

        if title == base_title:
            continue

        if title in seen_titles:
            continue

        row_genres = get_movie_genre_set(row)
        genre_overlap = len(base_genres.intersection(row_genres))

        # Prefer genre overlap if base movie genres exist
        if base_genres:
            if genre_overlap <= 0:
                continue

        seen_titles.add(title)
        selected_indices.append(i)

        if len(selected_indices) == 10:
            break

    # Second pass fallback: if not enough movies found, fill from top similarity
    if len(selected_indices) < 10:
        for i, sim_score in candidate_list:
            row = temp_df.iloc[i]
            title = str(row["title"]).strip().lower()

            if title == base_title:
                continue

            if title in seen_titles:
                continue

            seen_titles.add(title)
            selected_indices.append(i)

            if len(selected_indices) == 10:
                break

    if not selected_indices:
        return pd.DataFrame()

    rec_movies = temp_df.iloc[selected_indices].copy()

    # Safe poster column
    if "poster_url" in rec_movies.columns:
        rec_movies["poster"] = rec_movies["poster_url"]
    else:
        rec_movies["poster"] = ""

    rec_movies["poster"] = rec_movies["poster"].fillna("")

    # Remove helper column
    if "title_lower" in rec_movies.columns:
        rec_movies = rec_movies.drop(columns=["title_lower"])

    return rec_movies

# ---------------- HOME ----------------

@app.route("/")
def home():

        # ✅ Welcome screen (only first time)
    if "welcome_shown" not in session:
        session["welcome_shown"] = True
        return render_template("welcome.html")

    if "user" not in session:
        return redirect("/account")

    page = request.args.get("page", 1, type=int)
    if page < 1:
        page = 1

    # Pagination
    start = (page - 1) * MOVIES_PER_PAGE
    end = start + MOVIES_PER_PAGE

    page_movies = movies.iloc[start:end].copy()

    # Safe poster + rating
    if "poster_url" in page_movies.columns:
        page_movies["poster"] = page_movies["poster_url"].fillna("")
    else:
        page_movies["poster"] = ""

    if "vote_average" in page_movies.columns:
        page_movies["vote_average"] = pd.to_numeric(page_movies["vote_average"], errors="coerce").fillna(0)
    else:
        page_movies["vote_average"] = 0

    total_pages = math.ceil(len(movies) / MOVIES_PER_PAGE)

    if page == 1:
        start_page = 1
        end_page = min(5, total_pages)
    else:
        start_page = page
        end_page = min(page + 3, total_pages)

    # 🔥 Trending only on first page
    trending = None
    show_trending = False

    if page == 1:
        trending = movies.copy()

        # Safe numeric conversions
        if "release_date" in trending.columns:
            trending["release_year"] = pd.to_numeric(
                trending["release_date"].astype(str).str[:4],
                errors="coerce"
            )
        else:
            trending["release_year"] = 0

        if "vote_average" in trending.columns:
            trending["vote_average"] = pd.to_numeric(
                trending["vote_average"], errors="coerce"
            ).fillna(0)
        else:
            trending["vote_average"] = 0

        if "vote_count" not in trending.columns:
            trending["vote_count"] = 0

        trending["vote_count"] = pd.to_numeric(
            trending["vote_count"], errors="coerce"
        ).fillna(0)

        if "popularity" in trending.columns:
            trending["popularity"] = pd.to_numeric(
                trending["popularity"], errors="coerce"
            ).fillna(0)
        else:
            trending["popularity"] = 0

        # Prefer NEW movies (2024+), fallback if less results
        recent_movies = trending[trending["release_year"] >= 2024].copy()

        if len(recent_movies) < 8:
            recent_movies = trending[trending["release_year"] >= 2023].copy()

        # Remove rows with no poster
        if "poster_url" in recent_movies.columns:
            recent_movies = recent_movies[recent_movies["poster_url"].notna()]
            recent_movies = recent_movies[recent_movies["poster_url"].astype(str).str.strip() != ""]

        # Better trending logic = recent + popular + rated + enough votes
        recent_movies["trending_score"] = (
            (recent_movies["popularity"] * 0.50) +
            (recent_movies["vote_average"] * 8) +
            (recent_movies["vote_count"] * 0.02)
        )

        trending = recent_movies.sort_values(
            by=["trending_score", "release_date"],
            ascending=False
        ).head(8).copy()

        # Alias for HTML
        if "poster_url" in trending.columns:
            trending["poster"] = trending["poster_url"].fillna("")
        else:
            trending["poster"] = ""

        # Cleanup optional helper columns
        for col in ["release_year", "trending_score"]:
            if col in trending.columns:
                trending = trending.drop(columns=[col])

        show_trending = not trending.empty

    return render_template(
        "index.html",
        movies=page_movies,
        trending=trending,
        show_trending=show_trending,
        similar_movies=None,
        main_movie=None,
        page=page,
        total_pages=total_pages,
        start_page=start_page,
        end_page=end_page,
        current_filter=None
    )

# ---------------- SEARCH ----------------

@app.route("/search", methods=["POST"])
def search():
    if "user" not in session:
        return redirect("/account")

    query = request.form.get("movie", "").strip()

    if not query:
        return redirect("/")

    query_lower = query.lower()

    # Safe title search (partial match)
    matches = movies[
        movies['title'].astype(str).str.lower().str.contains(query_lower, na=False, regex=False)
    ].copy()

    if matches.empty:
        return render_template(
            "index.html",
            movies=[],
            trending=None,
            show_trending=False,
            similar_movies=[],
            main_movie=None,
            page=1,
            total_pages=1,
            start_page=1,
            end_page=1,
            current_filter=f"No results found for '{query}'"
        )

    # Safe numeric columns
    if "popularity" in matches.columns:
        matches["popularity"] = pd.to_numeric(matches["popularity"], errors="coerce").fillna(0)
    else:
        matches["popularity"] = 0

    if "vote_average" in matches.columns:
        matches["vote_average"] = pd.to_numeric(matches["vote_average"], errors="coerce").fillna(0)
    else:
        matches["vote_average"] = 0

    if "poster_url" in matches.columns:
        matches["poster"] = matches["poster_url"].fillna("")
    else:
        matches["poster"] = ""

    # Best match = most popular
    matches = matches.sort_values(by="popularity", ascending=False)

    main_movie_row = matches.iloc[0]
    main_movie_title = str(main_movie_row["title"])

    # Main movie data
    main_movie = main_movie_row.to_dict()
    main_movie["poster"] = main_movie.get("poster_url", "") or ""
    main_movie["vote_average"] = float(main_movie.get("vote_average", 0) or 0)

    # Similar movies
    similar_movies = []

    try:
        # Exact title match in main movies dataframe
        exact_match = movies[movies['title'].astype(str).str.lower().str.strip() == main_movie_title.lower().strip()]

        if not exact_match.empty:
            matched_index = exact_match.index[0]
            distances = similarity[matched_index]

            movie_list = sorted(
                list(enumerate(distances)),
                reverse=True,
                key=lambda x: x[1]
            )[1:11]

            for i in movie_list:
                if i[0] < len(movies):
                    m = movies.iloc[i[0]].copy()
                    movie_dict = m.to_dict()
                    movie_dict["poster"] = movie_dict.get("poster_url", "") or ""

                    try:
                        movie_dict["vote_average"] = float(movie_dict.get("vote_average", 0) or 0)
                    except:
                        movie_dict["vote_average"] = 0

                    similar_movies.append(movie_dict)

    except Exception as e:
        print("SEARCH SIMILAR MOVIES ERROR:", e)
        similar_movies = []

    return render_template(
        "index.html",
        movies=matches.head(20),
        trending=None,
        show_trending=False,
        similar_movies=similar_movies,
        main_movie=main_movie,
        page=1,
        total_pages=1,
        start_page=1,
        end_page=1,
        current_filter=f"Search results for '{main_movie_title}'"
    )

# ---------------- GENRE ----------------

@app.route("/genre/<genre>")
def genre(genre):

    if "user" not in session:
        return redirect("/account")

    if "tags" not in movies.columns:
        filtered = pd.DataFrame(columns=movies.columns)
    else:
        filtered = movies[movies['tags'].astype(str).str.contains(genre, case=False, na=False)].copy()

    if not filtered.empty:
        filtered["poster"] = filtered["poster_url"]

    return render_template(
        "index.html",
        movies=filtered,
        trending=None,
        show_trending=False,
        main_movie=None,
        similar_movies=None,
        page=1,
        total_pages=1,
        start_page=1,
        end_page=1,
        current_filter=f"Genre: {genre}"
    )

# ---------------- YEAR ----------------

@app.route("/year/<year>")
def year(year):

    if "user" not in session:
        return redirect("/account")

    filtered = movies[movies['release_date'].astype(str).str.startswith(year)].copy()

    if not filtered.empty:
        filtered["poster"] = filtered["poster_url"]

    return render_template(
        "index.html",
        movies=filtered,
        trending=None,
        show_trending=False,
        main_movie=None,
        similar_movies=None,
        page=1,
        total_pages=1,
        start_page=1,
        end_page=1,
        current_filter=f"Year: {year}"
    )

# ---------------- ANIMATION ----------------

@app.route("/genre/Animation")
def animation():

    if "user" not in session:
        return redirect("/account")

    if "tags" not in movies.columns:
        filtered = pd.DataFrame(columns=movies.columns)
    else:
        filtered = movies[movies['tags'].astype(str).str.contains("animation", case=False, na=False)].copy()

    if not filtered.empty:
        filtered["poster"] = filtered["poster_url"]

    return render_template(
        "index.html",
        movies=filtered,
        trending=None,
        show_trending=False,
        main_movie=None,
        similar_movies=None,
        page=1,
        total_pages=1,
        start_page=1,
        end_page=1,
        current_filter="Genre: Animation"
    )

# ---------------- MOVIE DETAILS ----------------

@app.route("/movie/<title>")
def movie_detail(title):

    movie_rows = movies[movies["title"] == title]

    if movie_rows.empty:
        return "Movie not found"

    movie = movie_rows.iloc[0].copy()

    # safe poster
    movie["poster"] = movie["poster_url"] if "poster_url" in movie.index else ""

    # clean fields for display
    if "tagline" in movie.index:
        movie["tagline"] = clean_sentence(movie["tagline"])
    else:
        movie["tagline"] = "N/A"

    if "overview" in movie.index:
        movie["overview"] = clean_sentence(movie["overview"])
    else:
        movie["overview"] = "N/A"

    if "genres" in movie.index:
        movie["genres"] = clean_list_display(movie["genres"])
    else:
        movie["genres"] = "N/A"

    if "spoken_languages" in movie.index:
        movie["spoken_languages"] = clean_list_display(movie["spoken_languages"])
    else:
        movie["spoken_languages"] = "N/A"

    # cast and director
    movie["genres"] = clean_list_display(movie["genres"]) if "genres" in movie.index else "N/A"
    movie["spoken_languages"] = clean_list_display(movie["spoken_languages"]) if "spoken_languages" in movie.index else "N/A"

    cast = clean_list_display(movie["cast"]) if "cast" in movie.index else "N/A"
    director = clean_list_display(movie["director"]) if "director" in movie.index else "N/A"

    # recommendations
    recs = recommend(title)

    return render_template(
        "details.html",
        movie=movie,
        cast=cast,
        director=director,
        recs=recs
    )

# ---------------- FAVORITES ----------------

@app.route("/favorite", methods=["POST"])
def favorite():

    if "user" not in session:
        return jsonify({"status": "login_required"})

    title = request.json.get("title")
    username = session["user"]

    conn = get_db()

    conn.execute(
        "INSERT INTO favorites(username,movie) VALUES (?,?)",
        (username, title)
    )

    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

# ---------------- FAVORITE PAGE ----------------

@app.route("/favorites")
def show_favorites():

    if "user" not in session:
        return redirect("/account")

    username = session["user"]

    conn = get_db()

    fav_list = conn.execute(
        "SELECT movie FROM favorites WHERE username=?",
        (username,)
    ).fetchall()

    conn.close()

    # remove duplicates while keeping order
    titles = []
    seen = set()

    for x in fav_list:
        movie_title = x["movie"]
        if movie_title not in seen:
            seen.add(movie_title)
            titles.append(movie_title)

    fav_movies = movies[movies["title"].isin(titles)].copy()

    # optional: preserve saved order
    if not fav_movies.empty:
        fav_movies["poster"] = fav_movies["poster_url"] if "poster_url" in fav_movies.columns else ""
        fav_movies["poster"] = fav_movies["poster"].fillna("")

        title_order = {title: i for i, title in enumerate(titles)}
        fav_movies["fav_order"] = fav_movies["title"].map(title_order)
        fav_movies = fav_movies.sort_values("fav_order").drop(columns=["fav_order"])

    return render_template("favorites.html", movies=fav_movies)

# ---------------- REMOVE FAVORITE ----------------

@app.route("/remove_favorite", methods=["POST"])
def remove_favorite():

    if "user" not in session:
        return jsonify({"status": "login_required"})

    title = request.json.get("title")
    username = session["user"]

    conn = get_db()

    conn.execute(
        "DELETE FROM favorites WHERE username=? AND movie=?",
        (username, title)
    )

    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

# ---------------- ACCOUNT ----------------

@app.route("/account")
def account():

    if "user" in session:
        return redirect("/")

    return render_template("account.html")

@app.route("/signup", methods=["POST"])
def signup():

    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]

    conn = get_db()

    conn.execute(
        "INSERT OR IGNORE INTO users VALUES (?,?,?)",
        (username, email, password)
    )

    conn.commit()
    conn.close()

    session["user"] = username

    return redirect("/")

@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    conn = get_db()

    user = conn.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    ).fetchone()

    conn.close()

    if user:
        session["user"] = username
        return redirect("/")

    return redirect("/account")

@app.route("/logout")
def logout():

    session.pop("user", None)
    session.pop("welcome_shown", None)
    return redirect("/account")

# ---------------- PROFILE ----------------

@app.route("/profile")
def profile():

    if "user" not in session:
        return redirect("/account")

    username = session["user"]

    conn = get_db()

    user = conn.execute(
        "SELECT * FROM users WHERE username=?",
        (username,)
    ).fetchone()

    fav_count = conn.execute(
        "SELECT COUNT(*) as total FROM favorites WHERE username=?",
        (username,)
    ).fetchone()["total"]

    conn.close()

    return render_template("profile.html", user=user, fav_count=fav_count)

# ---------------- ABOUT PAGE ----------------

@app.route("/about")
def about():
    if "user" not in session:
        return redirect("/account")
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)