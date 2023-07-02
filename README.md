# 🎞️Movie Recommendation🍿
Now deployed on google cloud platform!
[Link](https://movie-recommendation-386906.an.r.appspot.com/)

# Table of Contents

- [Overview](#overview)
- [Backstory](#backstory)
- [Technologies](#technologies)
- [Features](#features)
- [Get Started](#get_started)
- [Notes](#notes)
- [Acknowledgements](#acknowledgements)
- [Contact](#contact)

# Overview
This project is my first portfolio, which is improved version of my final project for CS50, which I finished last year. It's designed to show what I learned through the course: basic web programming with python, javascript and HTML/CSS; data manipulation of SQL database etc. The application is a movie-recommendation system where users can search and get recommendations from [imdb dataset](https://www.imdb.com/?ref_=nv_home). 

このプロジェクトは私の最初のポートフォリオで、昨年修了したCS50の修了プロジェクトの改良版です。コースで学習したPython、javascript、HTML/CSSを使った基本的なウェブプログラミング、SQLデータベースのデータ操作などのスキルを活かしています。アプリケーションの機能としては、ユーザーが[imdb dataset](https://www.imdb.com/?ref_=nv_home)から映画を検索してお勧めの映画を表示できるレコメンダーシステムです。

# Backstory
At the time I built it for CS50, the recommendation algorithm was [content-based filtering](https://developers.google.com/machine-learning/recommendation/content-based/basics), which simply shows users movie titles that stars user's favorite actors/actresses. 

After completed CS50, I was keen to learn more about data engineering since I was fascinated when the first moment I saw fetched data, but what I built was far from something useful. I learned some pyhton libraries for data processing such as pandas and numpy. Now this project uses [collaborative filtering](https://en.wikipedia.org/wiki/Collaborative_filtering), which enables users to find new interests. For other user's liking data, which I don’t have actual one, I created a sample data from [MovieLens Latest Datasets(ml-latest-small.zip)](https://grouplens.org/datasets/movielens/latest/). Please check the details on [my kaggle notebook](https://www.kaggle.com/code/hajiiz/collab-sample-data)

Additionally, I decided to change SQL language from SQLite to MYSQL since it seems to be [the most popular language](https://www.datacamp.com/blog/sql-server-postgresql-mysql-whats-the-difference-where-do-i-start). 

CS50のために作った当時のレコメンデーション・アルゴリズムは、[コンテンツベースフィルタリング](https://developers.google.com/machine-learning/recommendation/content-based/basics)というもので、単純にユーザーの好きな俳優が出演している映画を表示するものでした。

CS50修了後、クエリに引っ張られてきたデータを見たときに感動する一方、私が作ったものは役に立つものから程遠いものだったため、データエンジニアリングについてもっと学びたいと思いました。実際にpandasやnumpyといったデータ処理用のPyhtonライブラリをいくつか学び、本プロジェクトでは[協調フィルタリング](https://en.wikipedia.org/wiki/Collaborative_filtering)を使っています。とはいえ、実際のユーザーのライキングに関するデータは持ち合わせていないので、[MovieLens Latest Datasets(ml-latest-small.zip)](https://grouplens.org/datasets/movielens/latest/)からサンプルデータを作成しました。詳しくは[こちらのKaggleノート](https://www.kaggle.com/code/hajiiz/collab-sample-data)をご覧ください。

さらに、SQL言語をSQLiteから[最も人気のあるSQL言語](https://www.datacamp.com/blog/sql-server-postgresql-mysql-whats-the-difference-where-do-i-start)であるMYSQLに変更することにしました。

# Technologies
<span style="color:#44D62C"> + technology additionally used </span><br />
<span style="color:red"> - technology previously used </span>
|Category| Contents |
|:---|:---|
|Programming|  <span style="color:#44D62C">+ Data Processing (<a href="https://pandas.pydata.org/" style="color:#44D62C; text-decoration: underline;text-decoration-style: dotted;">pandas</a>, <a href="https://numpy.org/doc/stable/index.html" style="color:#44D62C; text-decoration: underline;text-decoration-style: dotted;">numpy</a>)</span><br />Python 3.10.11, JavaScript, HTML/CSS |
|Framework|<a href="https://flask.palletsprojects.com/en/2.3.x/" style="color:#44D62C text-decoration: underline;text-decoration-style: dotted;">Flask 2.3.2</a>|
|Database|<span style="color:red"> - SQLite </span> -> <span style="color:#44D62C"> + MYSQL </span><br /><span style="color:#44D62C">+ DB Connecion & Execution(<a href="https://www.sqlalchemy.org/" style="color:#44D62C; text-decoration: underline;text-decoration-style: dotted;"> SQLAlchemy </a>, <a href="https://pypi.org/project/pymysql/" style="color:#44D62C; text-decoration: underline;text-decoration-style: dotted;"> PyMySQL </a>)</span>|
|Version Control|<a href="https://git-scm.com/" style="color:#44D62C; text-decoration: underline;text-decoration-style: dotted;"> + git </a>|
|Hosting|<a href="https://cloud.google.com/" style="color:#44D62C; text-decoration: underline;text-decoration-style: dotted;"> + Google Cloud Platform(App Engine & Cloud SQL)</a>|
|Recommender Algorithm|<span style="color:red"> - Content-based Filtering</span> -> <span style="color:#44D62C"> + Collaborative Filtering(<a href="https://scikit-learn.org/stable/" style="color:#44D62C; text-decoration: underline;text-decoration-style: dotted;">scikit-learn</a>) |
|CSS|<a href="https://getbootstrap.com/"> Bootstrap 5.1.3</a>|

# Features
| Features|機能|
|:----|:----|
|User Registration & Authentication |ユーザー登録と認証|
|Query |クエリ|
|Liking　|ライク機能|
|Collaborative Filtering　|協調フィルタリング|

# Get Started
## 
1. Visit [https://movie-recommendation-386906.an.r.appspot.com/](https://movie-recommendation-386906.an.r.appspot.com/)
2. Create your account
3. Search your favorite titles or actors, and like some
4. Check the recommendation for you!(Click "Collaborative Filtering")

# Notes
- [Configuration Flask-Session for app deployed on GAE with Memorystore for Redis](https://dev.to/seemoreseaglass/configuration-flask-session-for-app-deployed-on-gae-with-memorystore-for-redis-49pa)

# Contact
Please message me if you find bugs or technical issues in my codes. That helps a lot.

コードにバグや技術的な問題を見つけたら、ご連絡をいただけると大変助かります。
<!-- TODO: Include icons and links to your RELEVANT, PROFESSIONAL 'DEV-ORIENTED' social media. LinkedIn and dev.to are minimum. -->
[![LinkedIn](https://img.shields.io/badge/linkedin-%230077B5.svg?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/hajime-ozawa-041884155/)

# Acknowledgements

<!-- TODO: List any blog posts, tutorials or plugins that you may have used to complete the project. Only list those that had a significant impact. Obviously, we all 'Google' stuff while working on our things, but maybe something in particular stood out as a 'major contributor' to your skill set for this project. -->
- CS: [CS50](https://pll.harvard.edu/course/cs50-introduction-computer-science)
- Dev Environment Setup: [Your Python Coding Environment on Windows: Setup Guide](https://realpython.com/python-coding-setup-windows/#understanding-the-path-environment-variable)
- Collaborative Filtering: [Build a Recommendation Engine With Collaborative Filtering](https://realpython.com/build-recommendation-engine-collaborative-filtering/)
- Jaccard Index: [Wikipedia: Jaccard Index](https://en.wikipedia.org/wiki/Jaccard_index)
- Git: [Ry's Git Tutorial](https://hamwaves.com/collaboration/doc/rypress.com/index.html)
- App Deployment on GCP: [Medium: Deploying a Flask app to Google App Engine by Doug Mahugh](https://medium.com/@dmahugh_70618/deploying-a-flask-app-to-google-app-engine-faa883b5ffab)
<br />
<br />
<br />
<br />
<a href="#top">Back to top</a>
