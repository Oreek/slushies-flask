# Oreek's Forum
A really bbasic and simple forum app made using Flask + MySQL.

## Features
It currently has the following features:
- Create or Login to user accounts present in db
- A very basic protected routes implementation.
- Ability to view posts and reply to them.
- Can edit and delete posts after their creation.

---
# Screenshots
![Home](/ss1.png)

![Messages/Replies](/ss2.png)

---
## IMPORTANT NOTE REGARDING AI USAGE
I've used AI to debug a lot of issues while deploying to **Railway** as I only checked it out and got to know while deploying that MySQL is not that great for deploying easily... :|

So I'm mentioning below the commits which HAVE AI CODE:
- Everything commited **after** the commit `ready for deployment` at `4:42 PM` on `2/22/26` should be assumed as work by AI and not considered as part of the work done by me!

---
## Installation and Local Setup
I'm actually not that good with words and explaining things so I suggest you go through the following guide to setup your environment and running instructions and just copy everything from my repo to your directory manually.
- https://code.tutsplus.com/creating-a-web-app-from-scratch-using-python-flask-and-mysql--cms-22972t

Use the folloeing commands in your mysql console after being logged in to create the following tables:
```mysql
CREATE DATABASE IF NOT EXISTS forums;
USE forums;
```

```mysql
CREATE TABLE forum_users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    email VARCHAR(200) NOT NULL,
    password VARCHAR(300) NOT NULL,
    usergroup VARCHAR(100) DEFAULT 'user',
    created DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

```mysql
CREATE TABLE forum_category (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    created DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

```mysql
CREATE TABLE forum_topics (
    topic_id INT AUTO_INCREMENT PRIMARY KEY,
    subject VARCHAR(300) NOT NULL,
    category_id INT NOT NULL,
    user_id INT NOT NULL,
    created DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

```mysql
CREATE TABLE forum_posts (
    post_id INT AUTO_INCREMENT PRIMARY KEY,
    message TEXT NOT NULL,
    topic_id INT NOT NULL,
    user_id INT NOT NULL,
    name VARCHAR(200),
    created DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

Insert some sample Categories aswell:
```mysql
INSERT INTO forum_category (name, description) VALUES 
('General Discussion', 'Talk about anything and everything'),
('Help & Support', 'Get help with technical issues'),
('Announcements', 'Official announcements and news');
```

Verify your entries:
```mysql
SELECT * FROM forum_users;
SELECT * FROM forum_category;
```

---
_The README.md is written and updated by me only with no AI used in this whatsoever!!_