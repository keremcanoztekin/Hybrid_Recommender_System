
#############################################
# Hybrid Recommender System
#############################################

# Make a guess for the user whose ID is given, using the item-based and user-based recomennder methods.
# Consider 5 suggestions from the user-based model and 5 suggestions from the item-based model
# and finally make 10 suggestions from 2 models.

#############################################
# Data Preparation
#############################################
import pandas as pd

movie = pd.read_csv("datasets/movie.csv")
rating = pd.read_csv("datasets/rating.csv")
df = movie.merge(rating, how="left", on="movieId")
comment_counts = pd.DataFrame(df["title"].value_counts())
rare_movies = comment_counts[comment_counts["title"] <=1000].index
common_movies = df[~df["title"].isin(rare_movies)]
user_movie_df = common_movies.pivot_table(index=["userId"], columns=["title"], values="rating")

#############################################
# Determining the Movies Watched by the User to Suggest
#############################################
# A random user id is chosen.

random_id = 108170
random_id_df = user_movie_df[user_movie_df.index==random_id]
movies_watched = random_id_df.columns[random_id_df.notna().any()].to_list()

#############################################
# Accessing Data and Ids of Other Users Watching the Same Movies
#############################################

movies_watched_df = user_movie_df[movies_watched]
user_movie_count = movies_watched_df.T.notnull().sum().reset_index()
user_movie_count.columns = ["userId","movie_count"]

# filtering users who watched at least 60% of the movies watched by the user we selected
percentange = len(movies_watched)*60/100
user_same_movies = user_movie_count[user_movie_count["movie_count"] > percentange]["userId"]

#############################################
# Determining the Users to be Suggested and Most Similar Users
#############################################
final_df = pd.concat([movies_watched_df[movies_watched_df.index.isin(user_same_movies)],
                    random_id_df[movies_watched]])

corr_df = final_df.T.corr().unstack().sort_values().drop_duplicates()
corr_df = pd.DataFrame(corr_df, columns=["corr"])
corr_df.index.names = ["user_id_1", "user_id_2"]
corr_df.reset_index(inplace=True)
top_users = corr_df[(corr_df["user_id_1"] == random_id) & (corr_df["corr"]>0.65)][["user_id_2","corr"]].\
    reset_index(drop=True)
top_users = top_users.sort_values("corr", ascending=False)
top_users.rename(columns={"user_id_2":"userId"}, inplace=True)

rating = pd.read_csv("datasets/rating.csv")
top_users_rating = pd.merge(rating[["userId","movieId", "rating"]],top_users,on="userId", how="right")
top_users_rating = top_users_rating[top_users_rating["userId"] != random_id]

#############################################
# Calculating Weighted Average Recommendation Score and Keeping Top 5 Movies
#############################################

top_users_rating["weighted_rating"] = top_users_rating["rating"] * top_users_rating["corr"]
recommendation_df = top_users_rating.groupby("movieId").agg({"weighted_rating":"mean"}).reset_index()

# Filter out those with a weighted average of over 3.
movies_to_be_recommend = recommendation_df[recommendation_df["weighted_rating"] > 3].sort_values("weighted_rating", ascending=False)
movie = pd.read_csv("datasets/movie.csv")
movies_to_be_recommend = movies_to_be_recommend.merge(movie[["movieId", "title"]])

# Recommended Top 5 Films
recommended_top_5 = movies_to_be_recommend["title"][0:5].values.tolist()

#############################################
# Item-Based Recommendation
#############################################

# Make an item-based suggestion based on the name of the movie that the user last watched and gave the highest rating.
user = 108170

#############################################
# Item-Based Recommendation
#############################################
# Step 1: m7

def user_movie_df():
    import pandas as pd
    movie = pd.read_csv("datasets/movie.csv")
    rating = pd.read_csv("datasets/rating.csv")
    df = movie.merge(rating, how="left", on="movieId")
    comment_counts = pd.DataFrame(df["title"].value_counts())
    rare_movies = comment_counts[comment_counts["title"] <= 1000].index
    comman_movies = df[~df["title"].isin(rare_movies)]
    user_movie_df = comman_movies.pivot_table(index=["userId"], columns=["title"], values="rating")
    return  user_movie_df
user_movie_df = user_movie_df()

# Step 2: Obtain the ID of the movie with the most recent rating from the movies that the user being recommended has rated 5.
user_movie_df[user_movie_df.index == user]

current_movie = rating[rating["userId"] == user].sort_values("rating", ascending=False).sort_values("timestamp", ascending=False)["movieId"].values[0]

# Step 3: Filter the user_movie_df dataframe created in the user-based recommendation section by the selected movie ID.
current_movie_name= movie[movie["movieId"] == current_movie]["title"].values[0]

user_df = user_movie_df[current_movie_name]

# Step 4: Using the filtered dataframe, find and sort the correlation between the selected movie and the other movies.
correlation_Df = user_movie_df.corrwith(user_df).sort_values(ascending=False)

# Step 5: Recommend the top 5 movies based on correlation with the selected movie, excluding the selected movie itself.
recommended_top_5 = correlation_Df.index[1:6].tolist()



