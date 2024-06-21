import mysql.connector 
from mysql.connector import errorcode
import pickle

try:
    connect = mysql.connector.connect(
        user = 'root',
        password = '-------',
        host = 'localhost',
        database = 'GameRL',
        port = '3306'
    )
except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
             print('Invalid credentials')
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
             print('Database not found')
        else:
             print('Cannot connect to database:', err)

conn = connect.cursor()

def create_gametype():
    conn.execute('INSERT INTO GameType (name) VALUES ("TicTacToe")')
    conn.execute('INSERT INTO GameType (name) VALUES ("Checkers")')
    conn.execute('INSERT INTO GameType (name) VALUES ("ConnectFour")')
    connect.commit()

def create_agent():
    for i in range(1, 4):
        names = ['Q-Learning', 'SARSA', 'MC Off-Policy','MC On-Policy']
        for name in names:  
            conn.execute(f'INSERT INTO Agent (name, gametype_id) VALUES ("{name}", {i})')
        connect.commit()

def convert_dict(i_start):
    paths = ['q_agent.pkl', 'sarsa_agent.pkl', 'mcoff_agent.pkl','mcon_agent.pkl']
    i = i_start
    for path in paths:
        with open(f'Dictionaries/{path}', 'rb') as f:
            Q = pickle.load(f)

        for action, board_dict in Q.items():
            for boardstate, value in board_dict.items():
                realvalue = ("%.25f" % value).rstrip('0').rstrip('.')
                realaction = str(action)
                print(f"boardstate: {boardstate}\naction: {action}\nvalue: {realvalue}\n\n")
                conn.execute("INSERT INTO QValue (agent_id, boardstate, action, value) VALUES (%s, %s, %s, %s)", (i, f'{boardstate}', realaction, realvalue))
        connect.commit()
        i += 1

def convert_checkers(i_start):
    paths = ['q_agent.pkl', 'sarsa_agent.pkl', 'mcoff_agent.pkl','mcon_agent.pkl']
    i = i_start
    count = 0
    for path in paths:
        with open(f'Dictionaries/{path}', 'rb') as f:
            Q = pickle.load(f)

        for boardstate, board_dict in Q.items():
            for action, value in board_dict.items():
                realvalue = ("%.25f" % value).rstrip('0').rstrip('.')
                realaction = str(action)
                conn.execute("INSERT INTO QValue (agent_id, boardstate, action, value) VALUES (%s, %s, %s, %s)", (i, f'{boardstate}', realaction, realvalue))
            count += 1
            if count % 10000 == 0:
                print(f"Count: {count}")
            connect.commit()
        i += 1
        print(f"Agent {i} finished")

create_gametype()
create_agent()
convert_dict(1) # TicTacToe
convert_dict(9) # ConnectFour
convert_checkers(5) # Checkers