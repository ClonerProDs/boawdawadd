from commands.db import conn, cursor
from decimal import Decimal


async def give_money_db(user_id, r_user_id, summ, st):
    if st == 'adm':
        limit = 150000000000000  # лимит выдачи денег у статуса админ (4)
        per = cursor.execute(f"SELECT issued FROM users WHERE user_id = ?", (user_id,)).fetchone()[0]
        if (per + summ) >= limit: return 'limit'  # изменено на >=
        cursor.execute(f'UPDATE users SET issued = issued + ? WHERE user_id = ?', (summ, user_id))

    balance = cursor.execute('SELECT balance FROM users WHERE user_id = ?', (r_user_id,)).fetchone()[0]
    summ = Decimal(balance) + Decimal(summ)

    cursor.execute(f'UPDATE users SET balance = ? WHERE user_id = ?', (str(summ), r_user_id))
    conn.commit()


async def give_bcoins_db(r_user_id, summ):
    cursor.execute(f'UPDATE users SET ecoins = ecoins + ? WHERE user_id = ?', (summ, r_user_id))
    conn.commit()


async def upd_ads(txt):
    cursor.execute(f'UPDATE sett SET ads = ?', (txt,))
    conn.commit()


async def new_promo_db(data):
    res = cursor.execute(f"SELECT name FROM promo WHERE name = ?", (data[0],)).fetchone()
    if res:
        return 'error'

    cursor.execute('INSERT INTO promo (name, summ, activ, data) VALUES (?, ?, ?, ?)', (data[0], str(data[1]), data[2], data[3]))
    conn.commit()


async def dell_promo_db(name):
    res = cursor.execute(f"SELECT name FROM promo WHERE name = ?", (name,)).fetchone()
    if not res:
        return 'error'

    cursor.execute('DELETE from promo WHERE name = ?', (name,))
    cursor.execute('DELETE from promo_activ WHERE name = ?', (name,))
    conn.commit()


async def activ_promo_db(name, user_id):
    data = cursor.execute(f"SELECT * FROM promo WHERE name = ?", (name,)).fetchone()
    if not data:
        return 'no promo'

    if data[2] <= 0:
        return 'activated'

    res = cursor.execute(f"SELECT * FROM promo_activ WHERE name = ? AND user_id = ?", (name, user_id)).fetchone()
    if res:
        return 'used'

    parts = data[3].split()[0].split('/')
    table, column = parts[0], parts[1]

    balance = cursor.execute(f'SELECT {column} FROM {table} WHERE user_id = ?', (user_id,)).fetchone()[0]
    summ = int(Decimal(balance) + Decimal(int(data[1])))

    if table == 'users' and column in ['balance']:
        summ = str(summ)

    cursor.execute(f'UPDATE {table} SET {column} = ? WHERE user_id = ?', (summ, user_id))
    cursor.execute(f'UPDATE promo SET activ = activ - 1 WHERE name = ?', (name,))
    cursor.execute('INSERT INTO promo_activ (user_id, name) VALUES (?, ?)', (user_id, name))
    conn.commit()
    return data


async def promo_info_db(name):
    return cursor.execute(f"SELECT * FROM promo WHERE name = ?", (name,)).fetchone()


async def get_users_chats():
    d1 = cursor.execute(f"SELECT user_id FROM users").fetchall()
    d2 = cursor.execute(f"SELECT chat_id FROM chats").fetchall()
    return d1, d2
