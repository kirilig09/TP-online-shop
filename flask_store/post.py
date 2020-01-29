from database import DB
from datetime import date

class Post:
    def __init__(self, id, name, author, content, price, datestamp, active, buyer):
        self.id = id
        self.name = name
        self.author = author
        self.content = content
        self.price = price
        self.datestamp = date.today()
        self.active = active
        self.buyer = buyer

    @staticmethod
    def all():
        with DB() as db:
            rows = db.execute('SELECT * FROM posts').fetchall()
            return [Post(*row) for row in rows]

    @staticmethod
    def find(id):
        with DB() as db:
            row = db.execute(
                'SELECT * FROM posts WHERE id = ?',
                (id,)
            ).fetchone()
            return Post(*row)

    def create(self):
        with DB() as db:
            values = (self.name, self.author, self.content, self.price)
            db.execute('''
                INSERT INTO posts (name, author, content, price)
                VALUES (?, ?, ?, ?)''', values)
            return self

    def save(self):
        with DB() as db:
            values = (
                self.name,
                self.author,
                self.content,
                self.price,
                self.datestamp,
                self.active,
                self.buyer,
                self.id
            )
            db.execute(
                '''UPDATE posts
                SET name = ?, author = ?, content = ?, price = ?, datestamp = ?, active = ?, buyer = ?
                WHERE id = ?''', values)
            return self

    def delete(self):
        with DB() as db:
            db.execute('DELETE FROM posts WHERE id = ?', (self.id,))

