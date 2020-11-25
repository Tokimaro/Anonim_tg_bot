import sqlite3

__connection = None


def ensure_connections(func):
    def inner(*args, **kwargs):
        with sqlite3.connect('users.db') as conn:
            res = func(*args, conn=conn, **kwargs)
        return res

    return inner


@ensure_connections
def init_db(conn, force: bool = False):
    c = conn.cursor()
    if force:
        c.execute('DROP TABLE IF EXISTS users')
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id           INTEGER PRIMARY KEY,
            user_id      INTEGER NOT NULL,
            name         STRING,
            old          INTEGER,
            gender       STRING,
            change     STRING NOT NULL
        )
    ''')

    conn.commit()


@ensure_connections
def reg_db(conn, user_id: int, name: str, old: int, gender: str, change: str):
    c = conn.cursor()
    c.execute('INSERT INTO users (user_id, name, old, gender, change) VALUES (?,?,?,?,?)',
              (user_id, name, old, gender, change))
    conn.commit()

@ensure_connections
def edit_db(conn, user_id: int, name: str, old: int, gender: str, change: str):
    c = conn.cursor()
    c.execute('UPDATE users SET name=?,old=?,gender=?,change=? WHERE user_id = ?',(name, old, gender, change,user_id))
    conn.commit()

@ensure_connections
def check_user(conn, user_id: int):
    c = conn.cursor()
    c.execute('SELECT EXISTS(SELECT * FROM users WHERE user_id = ?)', (user_id,))
    return c.fetchone()


@ensure_connections
def delete_user(conn, user_id: int):
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE user_id=?', (user_id,))
    conn.commit()


@ensure_connections
def get_info(conn, user_id: int):
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE user_id=?', (user_id,))
    return c.fetchone()


@ensure_connections
def init_queue(conn, force: bool = False):
    c = conn.cursor()
    if force:
        c.execute('DROP TABLE IF EXISTS queue')
    c.execute('''
             CREATE TABLE IF NOT EXISTS queue (
                 id           INTEGER PRIMARY KEY,
                 first_id     INTEGER,
                 second_id    INTEGER,
                 status       STRING
             )
         ''')


@ensure_connections
def add_user(conn, first_id: int):
    c = conn.cursor()
    c.execute('INSERT INTO queue (first_id) VALUES (?)', (first_id, ))
    conn.commit()


@ensure_connections
def select_free(conn):
    c = conn.cursor()
    c.execute('SELECT first_id FROM queue WHERE second_id IS NULL or second_id = "" and first_id IS NOT NULL')
    return c.fetchall()


@ensure_connections
def add_second_user(conn, first_id: int, second_id: int):
    c = conn.cursor()
    c.execute('UPDATE queue SET second_id=?,status = "Open" WHERE first_id=?', (second_id, first_id))
    conn.commit()


@ensure_connections
def check_status(conn, first_id: int, second_id: int):
    if check_change(first_id=first_id, second_id=second_id):
        c = conn.cursor()
        c.execute(
            'SELECT EXISTS(SELECT * FROM queue WHERE (second_id=? AND first_id=?) OR (first_id=? AND second_id=?))',
            (first_id, second_id, first_id, second_id))
        return c.fetchall()
    else:
        return False


@ensure_connections
def check_change(conn, first_id: int, second_id: int):
    c = conn.cursor()
    first_change = False
    c.execute('SELECT change FROM users WHERE user_id=?', (first_id,))
    change = c.fetchone()[0]
    print(change)
    if not change == "Всех":
        if change == "Мужчин":
            c.execute('SELECT EXISTS(SELECT * FROM users WHERE user_id=? AND gender = "Мужчина")', (second_id,))

            if c.fetchone()[0]:
                first_change = True
            else:
                return False
        elif change == "Женщин":
            c.execute('SELECT EXISTS(SELECT * FROM users WHERE user_id=? AND gender = "Женщина")', (second_id,))
            if c.fetchone()[0]:
                first_change = True
            else:
                return False
    else:
        first_change = True
    print(first_change)
    second_change = False
    c.execute('SELECT change FROM users WHERE user_id=?', (second_id,))
    change = c.fetchone()[0]
    print(change)
    if not change == "Всех":
        if change == "Мужчин":
            c.execute('SELECT EXISTS(SELECT * FROM users WHERE user_id=? AND gender = "Мужчина")', (first_id,))

            if c.fetchone()[0]:
                second_change = True
            else:
                return False
        elif change == "Женщин":
            c.execute('SELECT EXISTS(SELECT * FROM users WHERE user_id=? AND gender = "Женщина")', (first_id,))
            if c.fetchone()[0]:
                second_change = True
            else:
                return False
    else:
        second_change = True
    print(second_change)
    if second_change and first_change:
        return True
    else:
        return False


@ensure_connections
def check_companion(conn, first_id: int):
    c = conn.cursor()
    c.execute(
        'SELECT first_id,second_id FROM queue WHERE( second_id=? OR first_id=? )AND status = "Open"',
        (first_id, first_id))
    change = c.fetchall()
    print(change)

    if first_id == change[0][0]:
        return change[0][1]
    else:
        return change[0][0]

@ensure_connections
def check_open(conn, first_id: int):
    c = conn.cursor()
    c.execute('SELECT EXISTS (SELECT * FROM queue WHERE first_id=? AND status = "Open" OR second_id=? AND status = "Open" ORDER BY id DESC LIMIT 1)', (first_id,first_id ))
    return c.fetchall()

@ensure_connections
def close_chat(conn, first_id: int):
    c = conn.cursor()
    c = conn.execute('UPDATE queue SET status="Close" WHERE first_id=? or second_id=? and status = "Open"', (first_id,first_id ))
    conn.commit()



if __name__ == '__main__':
    init_db()
    init_queue()

