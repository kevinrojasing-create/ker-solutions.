import sqlite3

conn = sqlite3.connect('ker_v62.db')
c = conn.cursor()
c.execute('SELECT COUNT(*) FROM users')
count = c.fetchone()[0]
print(f'\nTotal users: {count}')

if count > 0:
    c.execute('SELECT id, email, full_name, role FROM users')
    users = c.fetchall()
    for u in users:
        print(f'User {u[0]}: {u[1]} - {u[2]} ({u[3]})')
else:
    print('No users yet')

conn.close()
