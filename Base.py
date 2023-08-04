import sqlite3
import datetime as dat


cnn1 = sqlite3.connect(r"the path to the database", check_same_thread=False)
cursor1 = cnn1.cursor()

def av_in_db(user_id):
    result=cursor1.execute("SELECT User_id from User WHERE User_id = ?",(user_id,))
    return bool(len(result.fetchall()))

def new_user(user_id,username,kol_req, date_end):
    cursor1.execute('INSERT INTO User (User_id, username, kol_req, date_end) VALUES (?, ?, ?, ?)', (user_id, username, kol_req, date_end))
    return cnn1.commit()

def new_kol_req(user_id,username,kol_req):
    cursor1.execute('UPDATE User SET username = ?, kol_req = ? WHERE User_id = ?', (username,kol_req,user_id))
    return cnn1.commit()


def new_kol_req_max_d(user_id,username,date_end):
    cursor1.execute('UPDATE User SET username = ?, date_end = ? WHERE User_id = ?', (username,date_end,user_id))
    return cnn1.commit()

def kol_req_r(user_id):
    cursor1.execute('SELECT kol_req from User WHERE User_id = ?',(user_id,))
    rez=cursor1.fetchone()[0]
    return int(rez)

def date_p_s(user_id):
    cursor1.execute('SELECT date_end from User WHERE user_id = ?',(user_id,))
    rez=cursor1.fetchone()[0]
    return dat.datetime.strptime(rez,'%Y-%m-%d')

def new_all_kol_req(kol_req):
    cursor1.execute('UPDATE User SET kol_req = ?', (kol_req,))
    return cnn1.commit()
