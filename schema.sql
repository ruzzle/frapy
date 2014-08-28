-- Tables --
CREATE TABLE IF NOT EXISTS forums (forum_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                   domain TEXT NOT NULL);
                                   
CREATE TABLE IF NOT EXISTS categories (category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                       forum_id INTEGER NOT NULL,
                                       parent_id INTEGER,
                                       title TEXT NOT NULL,
                                       url TEXT NOT NULL);
                                       
CREATE TABLE IF NOT EXISTS threads (thread_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    category_id INTEGER NOT NULL,
                                    title TEXT NOT NULL,
                                    url TEXT NOT NULL,
                                    FOREIGN KEY(category_id) REFERENCES categories(category_id));
									
CREATE TABLE IF NOT EXISTS posts (post_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                  user_id INTEGER NOT NULL,
                                  thread_id INTEGER NOT NULL,
                                  content TEXT NOT NULL,
                                  timestamp TEXT NOT NULL,
                                  FOREIGN KEY(user_id) REFERENCES users(user_id),
                                  FOREIGN KEY(thread_id) REFERENCES users(thread_id));

CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                  forum_id INTEGER NOT NULL,
                                  nickname TEXT NOT NULL,
                                  name TEXT,
                                  join_date TEXT,
                                  location TEXT,
                                  FOREIGN KEY(forum_id) REFERENCES forums(forum_id));
								  
-- CREATE VIEW users_detailed AS (
--     SELECT u.user_id, u.name, COUNT(p.post_id), u.join_date, u.location
--     FROM users u, posts p
--     WHERE p.user_id = u.user_id
-- );    

-- Indices --
CREATE UNIQUE INDEX IF NOT EXISTS forums_index ON forums(domain);
CREATE UNIQUE INDEX IF NOT EXISTS categories_index ON categories(title, url, forum_id, parent_id);
CREATE UNIQUE INDEX IF NOT EXISTS threads_index ON threads(title, url, category_id); -- We assume that this combination is unique enough
CREATE UNIQUE INDEX IF NOT EXISTS posts_index ON posts(timestamp, user_id, thread_id); -- A user can actually post the same thing twice
CREATE UNIQUE INDEX IF NOT EXISTS users_index ON users(nickname, forum_id);
