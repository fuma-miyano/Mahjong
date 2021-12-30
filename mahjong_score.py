'''
麻雀のスコア集計アプリです。
大会を作成し、大会ごとにスコアを管理できるようにしました。
部分的に友達と協力して作っています。ScoreOutputのクラスは友達が作ってくれて、他の部分を私が作りました。
自分たちで使うことをメインで考えて作りました。
'''

import tkinter as tk
from tkinter import font
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import os
import numpy as np
import datetime
import math

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mahjong Score")
        self.uma_list=["ウマなし","5-10","10-20","10-30","20-30"]
        self.oka_list=["25000点持ちオカなし","25000点持ち30000点返し"]
        self.preset()
        self._frame = None
        self.switch_frame(Toppage,0)

    #画面切り替えの関数。切り替える関数はtk_Frameを継承。
    def switch_frame(self, frame_class,property):
        new_frame = frame_class(self,property)  #プロパティで属性（大会名など）を与える
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()

    #クラスをポップアップさせたい時の関数。ポップアップするクラスはtk_Toplevelを継承。
    def popup_frame(self,frame_class,property):
        window=frame_class(self,property)

    #データベースを生成。
    def preset(self):
        #score.dbがないときに生成する。
        if not os.path.exists('score.db'):
            dbname='score.db'
            conn=sqlite3.connect(dbname)
            cur=conn.cursor()
            cur.execute('CREATE TABLE game(id integer Primary key AUTOINCREMENT,name TEXT,uma INTEGER,oka INTEGER)')
            cur.execute('CREATE TABLE member(id integer Primary key AUTOINCREMENT,name TEXT,game_id INTEGER)')
            cur.execute('CREATE TABLE score(id integer Primary key AUTOINCREMENT,game_id INTEGER,name TEXT,seat INTEGER,score INTEGER,rank INTEGER,date TEXT,game_number INTEGER,date_number INTEGER)')   #game_idは大会、game_numberは何半荘目か.seatは東,南,西,北=0,1,2,4
            cur.execute('CREATE TABLE uma(id integer Primary key AUTOINCREMENT,uma_id INTEGER,rank INTEGER,uma REAL)')
            uma_data=[(0,1,0),(0,2,0),(0,3,0),(0,4,0),(1,1,10.0),(1,2,5.0),(1,3,-5.0),(1,4,-10.0),(2,1,20.0),(2,2,10.0),(2,3,-10.0),(2,4,-20.0),(3,1,30.0),(3,2,10.0),(3,3,-10.0),(3,4,-30.0),(4,1,30.0),(4,2,20.0),(4,3,-20.0),(4,4,-30.0)]
            cur.executemany('INSERT INTO uma(uma_id,rank,uma) VALUES(?,?,?)',uma_data)
            cur.execute('CREATE TABLE oka(id integer Primary key AUTOINCREMENT,oka_id INTEGER,rank INTEGER,oka REAL)')
            oka_data=[(0,1,0),(0,2,0),(0,3,0),(0,4,0),(1,1,15.0),(1,2,-5.0),(1,3,-5.0),(1,4,-5.0)]
            cur.executemany('INSERT INTO oka(oka_id,rank,oka) VALUES(?,?,?)',oka_data)
            conn.commit()
            conn.close()

#トップページ作成
class Toppage(tk.Frame):
    #継承元クラスの初期化と設定
    def __init__(self,master,propety):
        super().__init__(master)
        self.game_list=[]   #大会リストを用意、初期化
        self.create_widgets(master)

    #ウィジェットを作成
    def create_widgets(self,master):
        #各ウィジェットを用意
        self.logo_font=font.Font(family="Ubuntu",size=40)
        self.logo=tk.Label(self,text="Mahjong Score",font=self.logo_font)
        self.game_select_combo=ttk.Combobox(self,state="readonly")
        self.game_select_combo["values"]=self.readlist()
        self.ok_button=tk.Button(self,text="OK",command=lambda:self.go_main(master))
        self.new_button=tk.Button(self,text="NEW",command=lambda:self.registration(master))
        self.delete_button=tk.Button(self,text="DELETE",command=lambda:self.delete_registration())

        #ウィジェットを配置
        self.logo.grid(row=0,column=0,columnspan=4,padx=20,pady=10)
        self.game_select_combo.grid(row=1,column=0)
        self.ok_button.grid(row=1,column=1,padx=5,columnspan=2,sticky=tk.W+tk.E)
        self.new_button.grid(row=2,column=1,padx=5,pady=5,sticky=tk.W+tk.E)
        self.delete_button.grid(row=2,column=2,padx=5,pady=5,sticky=tk.W+tk.E)

    #リストの読み込み。大会名データベースからリストに読み込んでいる。
    def readlist(self):
        self.game_list=[]
        dbname='score.db'
        conn=sqlite3.connect(dbname)
        cur=conn.cursor()
        for game in cur.execute("select * from game"):
            self.game_list.append(game[1])
        conn.close()
        return self.game_list

    #コンボボックスから属性を取得しメインページへ遷移
    def go_main(self,master):
        select=self.game_select_combo.get()
        if select==(""):
            messagebox.showerror('エラー', '大会を選択してください')
        else:
            master.switch_frame(Mainpage,select)

    #大会登録ページ
    def registration(self,master):
        window=tk.Toplevel(self)
        self.newgame_box=tk.Entry(window,width=40)
        self.registration_button=tk.Button(window,text="Registration",command=lambda:self.registration_action(master,window))
        self.uma_label=tk.Label(window,text="ウマ")
        self.oka_label=tk.Label(window,text="オカ")
        self.uma_combo=ttk.Combobox(window,state="readonly",values=master.uma_list)
        self.oka_combo=ttk.Combobox(window,state="readonly",values=master.oka_list)

        self.newgame_box.grid(row=0,column=0,columnspan=2)
        self.uma_label.grid(row=1,column=0)
        self.uma_combo.grid(row=1,column=1)
        self.oka_label.grid(row=2,column=0)
        self.oka_combo.grid(row=2,column=1)
        self.registration_button.grid(row=3,column=0,columnspan=2)

    #登録ページで登録ボタンを押した後の挙動。データベースに大会を登録し、ポップアップを削除。
    def registration_action(self,master,window):
        newgame=self.newgame_box.get()
        uma=self.uma_combo.get()
        oka=self.oka_combo.get()
        for game in self.game_list:
            if newgame==game:
                     messagebox.showerror('エラー','同じ名前が存在します')
                     return
        if newgame==(""):
            messagebox.showerror('エラー', '名前を入力してください')
            return
        elif uma==(""):
            messagebox.showerror('エラー', 'ウマを選択してください')
            return
        elif oka==(""):
            messagebox.showerror('エラー', 'オカを選択してください')
            return
        else:
            for i in range(len(master.uma_list)):
                if uma==master.uma_list[i]:
                    uma_id=i
                    break
            for i in range(len(master.oka_list)):
                if oka==master.oka_list[i]:
                    oka_id=i
                    break
            dbname='score.db'
            conn=sqlite3.connect(dbname)
            cur=conn.cursor()
            cur.execute('INSERT INTO game(name,uma,oka) values(?,?,?)',[newgame,uma_id,oka_id])
            conn.commit()
            conn.close()
            self.game_select_combo["values"]=self.readlist()
            window.destroy()

    #コンボボックスで選択している大会を削除。
    def delete_registration(self):
        select=self.game_select_combo.get()
        if select=="":
            return
        else:
            ret=messagebox.askyesno('確認','本当に'+select+'を削除しますか?')
            if ret==True:
                dbname='score.db'
                conn=sqlite3.connect(dbname)
                cur=conn.cursor()
                cur.execute('DELETE FROM game WHERE name=?',[self.game_select_combo.get()])
                conn.commit()
                conn.close()
                self.game_select_combo["values"]=self.readlist()
                self.game_select_combo.selection_clear()
                self.game_select_combo.set("")

#メインページのクラス
class Mainpage(tk.Frame):
    def __init__(self,master,property):
        super().__init__(master)
        self.create_widgets(master,property)

    #ウィジェットの配置
    def create_widgets(self,master,property):
        self.game_name=tk.Label(self,text=property)
        count=0
        self.input_button=tk.Button(self,text="スコア入力",width=20,pady=3,command=lambda:master.popup_frame(ScoreInput,property))
        self.output_button=tk.Button(self,text="結果",width=20,pady=3,command=lambda:master.popup_frame(ScoreOutput,property))
        self.rank_button=tk.Button(self,text="ランキング",width=20,pady=3,command=lambda:master.popup_frame(Ranking,property))
        self.option_button=tk.Button(self,text="設定",width=20,pady=3,command=lambda:master.popup_frame(Option,property))
        self.back_button=tk.Button(self,text="大会選択に戻る",width=20,pady=3,command=lambda:master.switch_frame(Toppage,0))

        self.game_name.pack()
        self.input_button.pack()
        self.output_button.pack()
        self.rank_button.pack()
        self.option_button.pack()
        self.back_button.pack()

#スコア入力ページをポップアップ
class ScoreInput(tk.Toplevel):  #継承はtk.Toplevel
    def __init__(self,master,property):
        super().__init__(master)
        self.count=0    #スコア入力欄の段をカウント
        self.name_list=[]
        self.year_list=[]
        self.month_list=[]
        self.day_list=[]
        self.num=[]
        self.name_combo_list=[]
        self.seat_list=["東","南","西","北"]
        self.frame_top=tk.Frame(self)
        self.frame_middle=tk.Frame(self)
        self.get_id(property)
        self.create_widgets(master,property)
        self.frame_top.pack(fill="x")
        self.frame_middle.pack()

    #propertyから大会のidを取得。大会名で操作したくないから一応。
    def get_id(self,property):
        dbname='score.db'
        conn=sqlite3.connect(dbname)
        cur=conn.cursor()
        cur.execute('SELECT * FROM game WHERE name=?',[property])
        row=cur.fetchone()
        self.id=row[0]
        conn.close()

    #メンバーリストを取得
    def readlist(self):
        self.name_list=[]
        dbname='score.db'
        conn=sqlite3.connect(dbname)
        cur=conn.cursor()
        for member in cur.execute("SELECT * FROM member WHERE game_id=?",[self.id]):
            self.name_list.append(member[1])
        conn.close()
        return self.name_list

    #1桁の日にちに0をつける
    def date(self,A):
        if int(A)<10:
            return str("0"+str(A))
        else:
            return A

    #スコア入力
    def create_widgets(self,master,property):
        dt_now=datetime.datetime.now()
        #name_combo_listにコンボボックスを追加していってリストを作る。リスト番号からコンボボックスを指定可能。
        self.date_label=tk.Label(self.frame_top,text="日付：")

        #日付のコンボボックス の要素を用意
        for i in range(100):
            self.year_list.append(str(2000+i))
        self.year_combo=ttk.Combobox(self.frame_top,state="readonly",values=self.year_list,width=6)
        self.year_label=tk.Label(self.frame_top,text="年")
        self.year_combo.current(str(self.year_list.index(str(dt_now.year))))

        for i in range(9):
            self.month_list.append("0"+str(1+i))
        for i in range(3):
            self.month_list.append(str(10+i))
        self.month_combo=ttk.Combobox(self.frame_top,state="readonly",values=self.month_list,width=3)
        self.month_label=tk.Label(self.frame_top,text="月")
        self.month_combo.current(str(self.month_list.index(str(self.date(dt_now.month)))))

        for i in range(9):
            self.day_list.append("0"+str(1+i))
        for i in range(22):
            self.day_list.append(str(10+i))
        self.day_combo=ttk.Combobox(self.frame_top,state="readonly",values=self.day_list,width=3)
        self.day_label=tk.Label(self.frame_top,text="日")
        self.day_combo.current(str(self.day_list.index(str(self.date(dt_now.day)))))

        self.add_button=tk.Button(self.frame_top,text="追加",command=lambda:self.add_scorebox())
        self.delete_button=tk.Button(self.frame_top,text="削除",command=lambda:self.delete_scorebox())
        self.save_button=tk.Button(self.frame_top,text="保存",command=lambda:self.save_scorebox())
        self.score_registration_button=tk.Button(self.frame_top,text="メンバー登録",command=lambda:self.member_registration(property))

        self.date_label.pack(side="left")
        self.year_combo.pack(side="left")
        self.year_label.pack(side="left")
        self.month_combo.pack(side="left")
        self.month_label.pack(side="left")
        self.day_combo.pack(side="left")
        self.day_label.pack(side="left")
        self.score_registration_button.pack(side="right")
        self.save_button.pack(side="right")
        self.delete_button.pack(side="right")
        self.add_button.pack(side="right")

        for i in range(4):
            self.name_combo_list.append(ttk.Combobox(self.frame_middle,state="readonly",values=self.readlist(),width=21))
            self.name_combo_list[i].grid(row=0,column=(2*i+1),columnspan=2,padx=0,pady=5)
        #score_entry_listに二次元の入力欄リストを入れていく。スコア取得まだ作ってないから正しく挙動するかは確かめてない。
        self.score_entry_list=np.empty((0,4),int)
        self.seat_combo_list=np.empty((0,4),int)
        self.add_scorebox()

    #大会メンバー追加関数
    def member_registration(self,property):
        window=tk.Toplevel(self)
        self.newmember_box=tk.Entry(window,width=40)
        self.newmember_box.pack()
        self.member_registration_button=tk.Button(window,text="Registration",command=lambda:self.member_registration_action(window))
        self.member_registration_button.pack()

    #登録時の挙動
    def member_registration_action(self,window):
        new=self.newmember_box.get()
        for i in range(len(self.name_list)):
            if new==(self.name_list[i]):
                     messagebox.showerror('エラー','同じ名前が存在します')
                     return
                     break
        if new==(""):
            messagebox.showerror('エラー', '名前を入力してください')
            return
        else:
            dbname='score.db'
            conn=sqlite3.connect(dbname)
            cur=conn.cursor()
            cur.execute('INSERT INTO member(name,game_id) values(?,?)',[new,self.id])
            conn.commit()
            conn.close()
            for i in range(4):
                self.name_combo_list[i]["values"]=self.readlist()
            window.destroy()

#スコアボックスの追加
    def add_scorebox(self):
        self.count+=1
        self.num_font=font.Font(family="Ubuntu",size=10)
        self.num.append(tk.Label(self.frame_middle,text=str(self.count),font=self.num_font))
        self.num[self.count-1].grid(row=(self.count),column=0)
        #score_entry_row_listに一次元のリストを作り、score_entry_listに追加して二次元配列を作る。
        score_entry_row_list=np.empty((0),int)
        seat_combo_row_list=np.empty((0),int)
        for i in range(4):
            score_entry_row_list=np.append(score_entry_row_list,tk.Entry(self.frame_middle,width=17))
            seat_combo_row_list=np.append(seat_combo_row_list,ttk.Combobox(self.frame_middle,width=3,values=self.seat_list))
            seat_combo_row_list[i].set(self.seat_list[i])
            score_entry_row_list[i].grid(row=(self.count),column=(2*i+1),padx=0,pady=5)
            seat_combo_row_list[i].grid(row=(self.count),column=(2*i+2),padx=0,pady=5)
        self.score_entry_list=np.append(self.score_entry_list,
        [score_entry_row_list],axis=0)
        self.seat_combo_list=np.append(self.seat_combo_list,
        [seat_combo_row_list],axis=0)

    #スコアボックスの行を削除
    def delete_scorebox(self):
        if self.count==1:
            return
        self.count-=1
        self.num[self.count].grid_forget()
        del self.num[self.count]
        for i in range(4):
            self.score_entry_list[self.count,i].grid_forget()
            self.seat_combo_list[self.count,i].grid_forget()
        self.score_entry_list=np.delete(self.score_entry_list,self.count,axis=0)
        self.seat_combo_list=np.delete(self.seat_combo_list,self.count,axis=0)

    #以下エラーチェック
    def save_scorebox(self):
        member=[]
        for i in range(4):
            member.append(self.name_combo_list[i].get())
            if member[i]==(""):
                messagebox.showerror('エラー','メンバーを選択して下さい')
                return
        for i in range(3):
            for j in range(3-i):
                if member[i]==member[i+j+1]:
                    messagebox.showerror('エラー','メンバーが重複しています')
                    return

        year=self.year_combo.get()
        month=self.month_combo.get()
        day=self.day_combo.get()
        if year==(""):
            messagebox.showerror('エラー', '年を選択してください')
            return
        if month==(""):
            messagebox.showerror('エラー', '月を選択してください')
            return
        if day==(""):
            messagebox.showerror('エラー', '日を選択してください')
            return

        self.day_count=0
        self.date_list=[]
        self.date_number_list=[]
        dbname='score.db'
        conn=sqlite3.connect(dbname)
        cur=conn.cursor()
        for date in cur.execute('SELECT * FROM score WHERE game_id=? AND date=? ',[self.id,year+"-"+month+"-"+day]):
                self.date_number_list.append(date[8])
                self.day_count=max(self.date_number_list)+1
        conn.close()

        for i in range(3):
            for j in range(3-i):
                if self.name_combo_list[i].get()==self.name_combo_list[j+i+1].get():
                    messagebox.showerror('エラー','メンバーが重複しています')
                    return
        for i in range(self.count):
            for j in range(4):
                if self.score_entry_list[i,j].get()==(""):
                    messagebox.showerror('エラー','スコアを全て入力してください')
                    return

        for i in range(self.count):
            for j in range(3):
                if self.seat_combo_list[i,j].get()==(""):
                    messagebox.showerror('エラー','方角を全て選択してください')
                    return
                for k in range(3-j):
                    if self.seat_combo_list[i,j].get()==self.seat_combo_list[i,j+k+1].get():
                        messagebox.showerror('エラー','方角が重複しています')
                        return

        #以下順位計算およびデータベース登録
        for i in range(self.count):
            hanchan=[]
            seat=[]
            rank=[0,0,0,0]
            for j in range(4):
                hanchan.append(int(self.score_entry_list[i,j].get()))
                if self.seat_combo_list[i,j].get()=="東":
                    seat.append(0)
                elif self.seat_combo_list[i,j].get()=="南":
                    seat.append(1)
                elif self.seat_combo_list[i,j].get()=="西":
                    seat.append(2)
                else:
                    seat.append(3)
            for j in range(4):
                high=0
                for k in range(4):
                    if hanchan[j]>hanchan[k]:
                        high+=1
                    elif hanchan[j]==hanchan[k] and seat[j]<seat[k]:
                        high+=1

                if high==3:
                    rank[j]=1
                elif high==2:
                    rank[j]=2
                elif high==1:
                    rank[j]=3
                else:
                    rank[j]=4

                dbname='score.db'
                conn=sqlite3.connect(dbname)
                cur=conn.cursor()
                cur.execute('INSERT INTO score (game_id,name,seat,score,rank,date,game_number,date_number) VALUES(?,?,?,?,?,?,?,?)',[self.id,member[j],seat[j],hanchan[j],rank[j],year+"-"+month+"-"+day,i+1,self.day_count])
                conn.commit()
                conn.close()

        self.destroy()

class ScoreOutput(tk.Toplevel):
    def __init__(self,master,property,height=300,width=400):
        super().__init__(master)
        self.frame_top=tk.Frame(self)
        self.frame_middle=tk.Frame(self)
        self.frame_bottom=tk.Frame(self)
        self.get_id(property)
        self.create_widgets(master,property)
        self.switch=0

    def get_id(self,property):
        dbname='score.db'
        conn=sqlite3.connect(dbname)
        cur=conn.cursor()
        cur.execute('SELECT * FROM game WHERE name=?',[property])
        row=cur.fetchone()
        self.uma=row[2]
        self.oka=row[3]
        self.id=row[0]
        conn.close()

    def date_list_create(self):
        dbname='score.db'
        conn=sqlite3.connect(dbname)
        cur=conn.cursor()
        self.date=[]
        self.date_number=[]
        for date in cur.execute('SELECT * FROM score WHERE game_id=? ORDER BY date DESC,date_number ASC',[self.id]):
            self.date.append(date[6])
            self.date_number.append(date[8])
        conn.close()
        k=0
        self.replace_date=[]
        for i in self.date_number:
            if i>0:
                self.replace_date.append(self.date[k])
                self.date[k]=(self.date[k]+" ("+str(i+1)+")")
            k+=1
        for i in set(self.replace_date):
            for j in range(len(self.date)):
                if i==self.date[j] :
                    self.date[j]+=" (1)"
        return sorted(set(self.date),key=self.date.index)

    def create_widgets(self,master,property):
        self.value_list=list(self.date_list_create())
        self.date_combo=ttk.Combobox(self.frame_top,state="readonly",values=self.value_list)
        self.button_display=tk.Button(self.frame_top,text="表示",command=lambda:self.score_display1(master,property))
        self.button_switch=tk.Button(self.frame_top,text="表示切替",command=lambda:self.switch_score(master,property,self.switch))
        self.date_combo.pack(side="left")
        self.button_display.pack(side="left")
        self.button_switch.pack(side="left")
        self.frame_top.pack()

    def readlist(self,date,type):
        dbname='score.db'
        conn=sqlite3.connect(dbname)
        cur=conn.cursor()
        date_number=0
        if "(" in date:
            date_imf=list(date.strip("(").split())
            date=date_imf[0]
            date_number=int(date_imf[1][1:2])-1

        self.output_score=[]
        self.original_score=[]
        self.name=[]
        k=0
        for i in cur.execute('SELECT (CAST(score AS REAL)/1000+uma.uma+oka.oka-25.0),score,score.name FROM score JOIN game ON score.game_id=game.id LEFT JOIN uma ON game.uma=uma.uma_id and score.rank=uma.rank LEFT JOIN oka ON game.oka=oka.oka_id and score.rank=oka.rank WHERE game_id=? AND date=? AND date_number=?',[self.id,date,date_number]):
            self.output_score.append(i[0])
            self.original_score.append(i[1])
            self.name.append(i[2])
            k+=1
        conn.close()
        if type=='name':
            return self.name
        elif type=='score':
            return np.array(self.output_score).reshape(-1,4)
        elif type=='score_original':
            return np.array(self.original_score).reshape(-1,4)

    def score_display1(self,master,property):
        self.frame_middle.destroy()
        self.frame_middle=tk.Frame(self)
        self.frame_bottom.destroy()
        self.frame_bottom=tk.Frame(self)
        self.button_delete=tk.Button(self.frame_bottom,text="削除",command=lambda:self.delete_score(master,property))
        date=self.date_combo.get()
        if date==(""):
            messagebox.showerror('エラー', '日にちを選択してください')
            return
        self.user1_label=tk.Label(self.frame_middle,text=self.readlist(date,'name')[0])
        self.user2_label=tk.Label(self.frame_middle,text=self.readlist(date,'name')[1])
        self.user3_label=tk.Label(self.frame_middle,text=self.readlist(date,"name")[2])
        self.user4_label=tk.Label(self.frame_middle,text=self.readlist(date,"name")[3])
        self.user1_label.grid(row=0,column=1)
        self.user2_label.grid(row=0,column=2)
        self.user3_label.grid(row=0,column=3)
        self.user4_label.grid(row=0,column=4)
        self.hanchan_su=[]
        self.score_list=[[]for i in range(len(self.readlist(date,"score")))]
        sum=[0]*4
        for i in range(len(self.readlist(date,"score"))):
            self.hanchan_su.append(tk.Label(self.frame_middle,text=str(i+1)))
            for j in range(4):
                sum[j]=round((sum[j]+self.readlist(date,"score")[i][j]),1)
                self.score_list[i].append(tk.Label(self.frame_middle,text=round(self.readlist(date,"score")[i][j],1)))
                self.score_list[i][j].grid(row=i+1,column=j+1)
                self.hanchan_su[i].grid(row=i+1,column=0)
        self.sum_score=[]
        for i in range(4):
            self.sum_score.append(tk.Label(self.frame_middle,text=str(sum[i])))
            self.sum_score[i].grid(row=len(self.readlist(date,"score"))+2,column=i+1)
        self.switch=1
        self.frame_middle.pack()
        self.button_delete.pack()
        self.frame_bottom.pack()

    def score_display2(self,master,property):
        self.frame_middle.destroy()
        self.frame_middle=tk.Frame(self)
        self.frame_bottom.destroy()
        self.frame_bottom=tk.Frame(self)
        self.button_delete=tk.Button(self.frame_bottom,text="削除",command=lambda:self.delete_score(master,property))
        date=self.date_combo.get()
        self.user1_label=tk.Label(self.frame_middle,text=self.readlist(date,'name')[0])
        self.user2_label=tk.Label(self.frame_middle,text=self.readlist(date,'name')[1])
        self.user3_label=tk.Label(self.frame_middle,text=self.readlist(date,"name")[2])
        self.user4_label=tk.Label(self.frame_middle,text=self.readlist(date,"name")[3])
        self.user1_label.grid(row=0,column=1)
        self.user2_label.grid(row=0,column=2)
        self.user3_label.grid(row=0,column=3)
        self.user4_label.grid(row=0,column=4)
        self.hanchan_su=[]
        self.score_list=[[]for i in range(len(self.readlist(date,"score")))]
        sum=[0]*4
        for i in range(len(self.readlist(date,"score"))):
            self.hanchan_su.append(tk.Label(self.frame_middle,text=str(i+1)))
            for j in range(4):
                self.score_list[i].append(tk.Label(self.frame_middle,text=str(self.readlist(date,"score_original")[i][j])))
                self.score_list[i][j].grid(row=i+1,column=j+1)
            self.hanchan_su[i].grid(row=i+1,column=0)
        self.switch=0
        self.frame_middle.pack()
        self.button_delete.pack()
        self.frame_bottom.pack()

    def switch_score(self,master,property,switch):
        if switch==1:
            self.score_display2(master,property)
        else:
            self.score_display1(master,property)

    def delete_score(self,master,property):
        date=self.date_combo.get()
        date_num=0
        self.flg=0
        if "(" in date:
            date_imf=list(date.strip("(").split())
            date=date_imf[0]
            date_num=int(date_imf[1][1:2])-1
            self.flg=1
        ret=messagebox.askyesno('確認','本当に'+date+'のスコアを削除しますか?')
        if ret==True:
            dbname='score.db'
            conn=sqlite3.connect(dbname)
            cur=conn.cursor()
            cur.execute('DELETE FROM score WHERE game_id=? AND date=? AND date_number=?',[self.id,date,date_num])
            if self.flg==1:
                self.date_number=[]
                for i in cur.execute('SELECT * FROM score WHERE game_id=? AND date=?',[self.id,date]):
                    self.date_number.append(i[8])
                for num in self.date_number:
                    if int(num)>date_num:
                        cur.execute('UPDATE score SET date_number=? WHERE game_id=? AND date=?',[int(num)-1,self.id,date])
            conn.commit()
            conn.close()
            self.frame_middle.destroy()
            self.date_combo["values"]=list(self.date_list_create())
            self.date_combo.selection_clear()
            self.date_combo.set("")

#ウマ、オカの設定を変更。
class Option(tk.Toplevel):
    def __init__(self,master,property):
        super().__init__(master)
        self.current_get(master,property)
        self.create_widgets(master,property)

    def current_get(self,master,property):
        dbname='score.db'
        conn=sqlite3.connect(dbname)
        cur=conn.cursor()
        cur.execute("SELECT * FROM game WHERE name=?",[property])
        row=cur.fetchone()
        conn.close()
        self.current_uma=master.uma_list[row[2]]
        self.current_oka=master.oka_list[row[3]]

    def create_widgets(self,master,property):
        self.umaoka_label_font=font.Font(family="Ubuntu",size=20)
        self.umaoka_label=tk.Label(self,text="点数設定",font=self.umaoka_label_font)
        self.current_label=tk.Label(self,text="現在の設定")
        self.current_uma_label=tk.Label(self,text=self.current_uma)
        self.current_oka_label=tk.Label(self,text=self.current_oka)
        self.uma_label=tk.Label(self,text="ウマ")
        self.oka_label=tk.Label(self,text="オカ")
        self.uma_combo=ttk.Combobox(self,state="readonly",values=master.uma_list)
        self.oka_combo=ttk.Combobox(self,state="readonly",values=master.oka_list)
        self.registration_button=tk.Button(self,text="適用",command=lambda:self.registration_action(master,property))

        self.umaoka_label.grid(row=0,column=0,columnspan=2)
        self.current_label.grid(row=1,column=0,columnspan=2,sticky=tk.W)
        self.current_uma_label.grid(row=2,column=0,columnspan=2,sticky=tk.W)
        self.current_oka_label.grid(row=3,column=0,columnspan=2,sticky=tk.W)
        self.uma_label.grid(row=4,column=0)
        self.uma_combo.grid(row=4,column=1)
        self.oka_label.grid(row=5,column=0)
        self.oka_combo.grid(row=5,column=1)
        self.registration_button.grid(row=6,column=0,columnspan=2)

    def registration_action(self,master,property):
        uma=self.uma_combo.get()
        oka=self.oka_combo.get()
        if uma==(""):
            messagebox.showerror('エラー', 'ウマを選択してください')
            return
        elif oka==(""):
            messagebox.showerror('エラー', 'オカを選択してください')
            return
        else:
            for i in range(len(master.uma_list)):
                if uma==master.uma_list[i]:
                    uma_id=i
                    break
            for i in range(len(master.oka_list)):
                if oka==master.oka_list[i]:
                    oka_id=i
                    break
            dbname='score.db'
            conn=sqlite3.connect(dbname)
            cur=conn.cursor()
            cur.execute('UPDATE game SET uma=?,oka=? WHERE name=?',[uma_id,oka_id,property])
            conn.commit()
            conn.close()
            self.destroy()

#スコアのランキング
class Ranking(tk.Toplevel):
    def __init__(self,master,property):
        super().__init__(master,height=300,width=400)
        self.get_id(property)
        self.frame_top=tk.Frame(self)
        self.frame_middle=tk.Frame(self)
        self.create_widgets(master,property)

    #大会のidを取得
    def get_id(self,property):
        dbname='score.db'
        conn=sqlite3.connect(dbname)
        cur=conn.cursor()
        cur.execute('SELECT * FROM game WHERE name=?',[property])
        row=cur.fetchone()
        self.id=row[0]
        conn.close()

    def create_widgets(self,master,property):
        self.rank_type_select=ttk.Combobox(self.frame_top,state="readonly",values=["合計ポイント","最高スコア","4着回避率"])
        self.rank_button=tk.Button(self.frame_top,text="表示",command=lambda:self.score_rank_create(master,property))
        self.detail_button=tk.Button(self.frame_top,text="詳細",command=lambda:self.score_detail_create(master,property))
        self.rank_type_select.pack(side="left")
        self.rank_button.pack(side="left")
        self.detail_button.pack(side="left")
        self.frame_top.pack()

    #ランキングのウィジェット作成
    def score_rank_create(self,master,property):
        self.frame_middle.destroy()
        self.frame_middle=tk.Frame(self)

        #コンボボックスで選択したランキング（合計ポイント、最高スコア、四着回避率）を表示
        if self.rank_type_select.get()=="合計ポイント":
            self.rank_label=tk.Label(self.frame_middle,text="順位")
            self.user_label=tk.Label(self.frame_middle,text="ユーザー名")
            self.sum_pt_label=tk.Label(self.frame_middle,text="合計pt")

            self.rank_label.grid(row=0,column=0)
            self.user_label.grid(row=0,column=1)
            self.sum_pt_label.grid(row=0,column=2)

            self.num=[]
            self.user=[]
            self.sum_pt=[]
            dbname='score.db'
            conn=sqlite3.connect(dbname)
            cur=conn.cursor()
            exe=cur.execute('SELECT round(SUM(CAST(score AS REAL)/1000+uma.uma+oka.oka-25.0),1) AS point,score.name FROM score JOIN game ON score.game_id=game.id LEFT JOIN uma ON game.uma=uma.uma_id and score.rank=uma.rank LEFT JOIN oka ON game.oka=oka.oka_id and score.rank=oka.rank WHERE score.game_id=? GROUP BY score.name ORDER BY point DESC',[self.id])
            i=0
            for row in exe:
                self.num.append(tk.Label(self.frame_middle,text=str(i+1)))
                self.user.append(tk.Label(self.frame_middle,text=row[1]))
                self.sum_pt.append(tk.Label(self.frame_middle,text=str(row[0])))

                self.num[i].grid(row=i+1,column=0)
                self.user[i].grid(row=i+1,column=1)
                self.sum_pt[i].grid(row=i+1,column=2)
                i+=1

            conn.close()

        elif self.rank_type_select.get()=="最高スコア":
            self.rank_label=tk.Label(self.frame_middle,text="順位")
            self.user_label=tk.Label(self.frame_middle,text="ユーザー名")
            self.max_score_label=tk.Label(self.frame_middle,text="最高スコア")

            self.rank_label.grid(row=0,column=0)
            self.user_label.grid(row=0,column=1)
            self.max_score_label.grid(row=0,column=2)

            self.num=[]
            self.user=[]
            self.max_score=[]
            dbname='score.db'
            conn=sqlite3.connect(dbname)
            cur=conn.cursor()
            exe=cur.execute('SELECT MAX(score) AS max,name FROM score WHERE game_id=? GROUP BY name ORDER BY max DESC',[self.id])
            i=0
            for row in exe:
                self.num.append(tk.Label(self.frame_middle,text=str(i+1)))
                self.user.append(tk.Label(self.frame_middle,text=row[1]))
                self.max_score.append(tk.Label(self.frame_middle,text=str(row[0])))

                self.num[i].grid(row=i+1,column=0)
                self.user[i].grid(row=i+1,column=1)
                self.max_score[i].grid(row=i+1,column=2)
                i+=1

            conn.close()

        elif self.rank_type_select.get()=="4着回避率":
            self.rank_label=tk.Label(self.frame_middle,text="順位")
            self.user_label=tk.Label(self.frame_middle,text="ユーザー名")
            self.kaihi_label=tk.Label(self.frame_middle,text="4着回避率")

            self.rank_label.grid(row=0,column=0)
            self.user_label.grid(row=0,column=1)
            self.kaihi_label.grid(row=0,column=2)

            self.num=[]
            self.user=[]
            self.kaihi=[]
            dbname='score.db'
            conn=sqlite3.connect(dbname)
            cur=conn.cursor()
            exe=cur.execute('SELECT name,round(CAST(COUNT(DISTINCT CASE WHEN rank=1 or rank=2 or rank=3 then id END) AS REAL)/COUNT(*),3) AS kaihi FROM score WHERE game_id=? GROUP BY name ORDER BY kaihi DESC',[self.id])
            i=0
            for row in exe:
                self.num.append(tk.Label(self.frame_middle,text=str(i+1)))
                self.user.append(tk.Label(self.frame_middle,text=row[0]))
                self.kaihi.append(tk.Label(self.frame_middle,text=str(row[1])))

                self.num[i].grid(row=i+1,column=0)
                self.user[i].grid(row=i+1,column=1)
                self.kaihi[i].grid(row=i+1,column=2)
                i+=1

            conn.close()

        self.frame_middle.pack()

    #詳細ボタンを押したときにより詳しいデータを表示
    def score_detail_create(self,master,property):
        self.frame_middle.destroy()
        self.frame_middle=tk.Frame(self)
        self.label=["順位","ユーザー名","総局数","合計pt","最高スコア","平着","1着","2着","3着","4着","トップ率","連対率","4着回避率"]
        self.detail_list=np.empty((0),int)
        for num in range(13):
            self.detail_list=np.append(self.detail_list,tk.Label(self.frame_middle,text=self.label[num]))
            self.detail_list[num].grid(row=0,column=num)

        dbname='score.db'
        conn=sqlite3.connect(dbname)
        cur=conn.cursor()
        exe=cur.execute('SELECT score.name,COUNT(*),round(SUM(CAST(score AS REAL)/1000+uma.uma+oka.oka-25.0),1) AS point,MAX(score),round(AVG(CAST(score.rank AS REAL)),3),COUNT(DISTINCT CASE WHEN score.rank=1 then score.id END),COUNT(DISTINCT CASE WHEN score.rank=2 then score.id END),COUNT(DISTINCT CASE WHEN score.rank=3 then score.id END),COUNT(DISTINCT CASE WHEN score.rank=4 then score.id END),round(CAST(COUNT(DISTINCT CASE WHEN score.rank=1 then score.id END) AS REAL)/COUNT(*),3),round(CAST(COUNT(DISTINCT CASE WHEN score.rank=1 or score.rank=2 then score.id END) AS REAL)/COUNT(*),3),round(CAST(COUNT(DISTINCT CASE WHEN score.rank=1 or score.rank=2 or score.rank=3 then score.id END) AS REAL)/COUNT(*),3) FROM score JOIN game ON score.game_id=game.id LEFT JOIN uma ON game.uma=uma.uma_id and score.rank=uma.rank LEFT JOIN oka ON game.oka=oka.oka_id and score.rank=oka.rank WHERE score.game_id=? GROUP BY score.name ORDER BY point DESC',[self.id])

        i=1
        for row in exe:
            self.temp_list=np.empty((0),int)
            self.temp_list=np.append(self.temp_list,tk.Label(self.frame_middle,text=str(i)))
            self.temp_list[0].grid(row=i,column=0)
            self.temp_list=np.append(self.temp_list,tk.Label(self.frame_middle,text=row[0]))
            self.temp_list[1].grid(row=i,column=1)
            for num in range(11):
                self.temp_list=np.append(self.temp_list,tk.Label(self.frame_middle,text=str(row[num+1])))
                self.temp_list[num+2].grid(row=i,column=num+2)

            i+=1

        conn.close()

        self.frame_middle.pack()

#アプリを稼働させるメイン関数
def main():
    app=App()
    app.mainloop()

if __name__ == "__main__":
    main()
