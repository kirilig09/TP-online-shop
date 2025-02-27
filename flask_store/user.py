import hashlib

from database import DB

from itsdangerous import (
        TimedJSONWebSignatureSerializer as Serializer,
        BadSignature,
        SignatureExpired
        )

SECRET_KEY = 'ncXZyx5cLR7x1$B^Ybtqp1f!E#dG4H3EN@ioYYKoxx'

class User:
    def __init__(self, id, username, password, email, address, phone, bought):
        self.id = id
        self.username = username
        self.password = password
        self.email = email
        self.address = address
        self.phone = phone
        self.bought = bought

    def create(self):
        with DB() as db:
            values = (self.username, self.password, self.email, self.address, self.phone, self.bought)
            db.execute('''
                INSERT INTO users (username, password, email, address, phone, bought)
                VALUES (?, ?, ?, ?, ?, ?)''', values)
            return self


    @staticmethod
    def find_by_username(username):
        if not username:
            return None
        with DB() as db:
            row = db.execute(
                'SELECT * FROM users WHERE username = ?',
                (username,)
            ).fetchone()
            if row:
                return User(*row)

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()


    def verify_password(self, password):
        return self.password == hashlib.sha256(password.encode('utf-8')).hexdigest()

    def generate_token(self):
        s = Serializer(SECRET_KEY, expires_in=600)
        return s.dumps({'username': self.username})

    @staticmethod
    def verify_token(token):
        s = Serializer(SECRET_KEY)
        try:
            s.loads(token)
        except SignatureExpired:
            return False
        except BadSignature:
            return False
        return True

    def save(self):
        with DB() as db:
            values = (
                self.username,
                self.password,
                self.email,
                self.address,
                self.phone,
                self.bought,
                self.id
            )
            db.execute(
                '''UPDATE users
                SET username = ?, password = ?, email = ?, address = ?, phone = ?, bought = ?
                WHERE id = ?''', values)
            return self        

    def delete(self):
        with DB() as db:
            db.execute('DELETE FROM users WHERE id = ?', (self.id,))

    @staticmethod
    def all():
        with DB() as db:
            rows = db.execute('SELECT * FROM users').fetchall()
            return [User(*row) for row in rows] 

    @staticmethod
    def find(id):
        with DB() as db:
            row = db.execute(
                'SELECT * FROM users WHERE id = ?',
                (id,)
            ).fetchone()
            return User(*row)



