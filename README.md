# Movie Recommendation

# Table of Contents

- [Overview](#overview)
- [Technologies](#technologies)
- [Features](#features)
- [Contact](#contact)
- [Acknowledgements](#acknowledgements)

# Overview
This is the improved version of my CS50 final project, movie-recommendation web application where users can search and get recommendation from [imdb dataset](https://www.imdb.com/?ref_=nv_home). The major change is its recommending algorithm (from [content-based filtering](https://developers.google.com/machine-learning/recommendation/content-based/basics) to [collaborative filtering](https://en.wikipedia.org/wiki/Collaborative_filtering)). In order to explore the maximum data of the dataset, I decided to create SQL server and hosted the project on Google Cloud. (Please note that the publishing will end or stop when the my free tier trial ends). 

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
|CSS|<a href="https://getbootstrap.com/" style="color: #44D62C; text-decoration: underline;text-decoration-style: dotted;"> + Bootstrap 5.1.3</a>|

# Features
| |
|:----|
|User Registration & Authentication|
|Query|
|Liking|
|Collaborative Filtering|

# Contact
Please message me if you find bugs or technical issues in my codes. That helps a lot.
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