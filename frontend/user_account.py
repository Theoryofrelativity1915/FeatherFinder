import sqlite3

class user_account():
    def __init__(self, username, id):
        self.id = int(id)
        self.username = str(username)
        c = sqlite3.connect(self.username + "_account.db")
        db = c.cursor()
        db.execute(
        """
        CREATE TABLE IF NOT EXISTS my_account (
            username TEXT,
            bird_name TEXT UNIQUE
        )
        """
        )
        c.commit()
        c.close()

    def collectBird(self, birdName):
        c = sqlite3.connect(self.username + "_account.db")
        db = c.cursor()
        db.execute(
            "INSERT OR IGNORE INTO my_account (username, bird_name) VALUES (?, ?)", 
            (self.username, birdName))
        c.commit()
        c.close()

    def displayBirds(self):
        c = sqlite3.connect(self.username + "_account.db")
        db = c.cursor()
        db.execute("SELECT bird_name FROM my_account where username = ?", (self.username,))
        collectedBirds = db.fetchall()
        print(collectedBirds)