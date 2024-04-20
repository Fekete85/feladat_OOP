from abc import ABC
import tkinter as tk
from tkinter import messagebox, Toplevel, Listbox
from tkinter.ttk import Combobox
from tkcalendar import Calendar
import datetime

class Szoba(ABC):
    def __init__(self, szobaszam, ar):
        self.szobaszam = szobaszam
        self.ar = ar

class EgyagyasSzoba(Szoba):
    def __init__(self, szobaszam, ar=100):
        super().__init__(szobaszam, ar)

class KetagyasSzoba(Szoba):
    def __init__(self, szobaszam, ar=150):
        super().__init__(szobaszam, ar)



class Szalloda:
    def __init__(self, nev):
        self.nev = nev
        self.szobak = []
        self.foglalasok = []
        
    def add_szoba(self, szoba):
        self.szobak.append(szoba)
        
    def foglal(self, szobaszam, datum):
        for szoba in self.szobak:
            if szoba.szobaszam == szobaszam:
                self.foglalasok.append(Foglalas(szoba, datum))
                return szoba.ar
        return None

    def foglalas_lemondas(self, szobaszam, datum):
        for foglalas in self.foglalasok:
            if foglalas.szoba.szobaszam == szobaszam and foglalas.datum == datum:
                self.foglalasok.remove(foglalas)
                return True
        return False

    def list_foglalasok(self):
        return [(f.szoba.szobaszam, f.datum) for f in self.foglalasok]



class Foglalas:
    def __init__(self, szoba, datum):
        self.szoba = szoba
        self.datum = datum



class HotelApp:
    def __init__(self, szalloda):
        self.szalloda = szalloda
        self.root = tk.Tk()
        self.root.title("Szálloda Foglalási Rendszer")

        tk.Button(self.root, text="Foglalás", command=self.create_foglalas).pack(fill='x', padx=20, pady=10)
        tk.Button(self.root, text="Foglalások Listázása", command=self.list_foglalasok).pack(fill='x', padx=20, pady=10)
        tk.Button(self.root, text="Foglalások és Lemondás", command=self.listaz_es_lemond).pack(fill='x', padx=20, pady=10)

    def update_calendar(self, cal, szobaszam):
        cal.calevent_remove('all')
        for foglalas in self.szalloda.foglalasok:
            if foglalas.szoba.szobaszam == szobaszam:
                foglalasi_datum = datetime.datetime.strptime(foglalas.datum, "%Y-%m-%d")
                cal.calevent_create(foglalasi_datum, 'Foglalt', 'foglalt')
                cal.tag_config('foglalt', background='red', foreground='white')

    def create_foglalas(self):
        window = Toplevel(self.root)
        window.title("Új Foglalás")

        szobak = [szoba.szobaszam for szoba in self.szalloda.szobak]
        combobox = Combobox(window, values=szobak, state="readonly")
        combobox.pack(pady=10)

        cal = Calendar(window, selectmode='day', year=datetime.datetime.now().year, month=datetime.datetime.now().month, day=datetime.datetime.now().day)
        cal.pack(pady=10)
        combobox.bind('<<ComboboxSelected>>', lambda event: self.update_calendar(cal, combobox.get()))

        tk.Button(window, text="Foglalás", command=lambda: self.foglal(combobox.get(), cal.get_date(), window)).pack(pady=10)

    def foglal(self, szobaszam, datum, window):
        datum = datum.strip().replace('. ', '-').rstrip('.')
        try:
            foglalasi_datum = datetime.datetime.strptime(datum, "%Y-%m-%d").date()
        except ValueError as e:
            messagebox.showerror("Foglalás", "Érvénytelen dátum formátum!")
            return

        today = datetime.datetime.now().date()
        if foglalasi_datum < today:
            messagebox.showerror("Foglalás", "Nem lehet a múltba foglalni!")
            return

        if any(f.szoba.szobaszam == szobaszam and f.datum == datum for f in self.szalloda.foglalasok):
            messagebox.showerror("Foglalás", "Ez a szoba ezen a napon már foglalt!")
            return

        ar = self.szalloda.foglal(szobaszam, datum)
        if ar is not None:
            messagebox.showinfo("Foglalás", f"A foglalás sikeres. Ár: {ar} Ft")
            window.destroy()
        else:
            messagebox.showerror("Foglalás", "A foglalás sikertelen.")

    def list_foglalasok(self):
        window = Toplevel(self.root)
        window.title("Összes Foglalás")

        lb = Listbox(window, width=50, height=10)
        foglalasok = self.szalloda.list_foglalasok()
        for i, (szobaszam, datum) in enumerate(foglalasok):
            lb.insert(i, f"Szoba: {szobaszam}, Dátum: {datum}")
        lb.pack(pady=10)

    def listaz_es_lemond(self):
        window = Toplevel(self.root)
        window.title("Foglalások Listája és Lemondás")

        lb = Listbox(window, width=50, height=10)
        foglalasok = self.szalloda.list_foglalasok()
        for i, (szobaszam, datum) in enumerate(foglalasok):
            lb.insert(i, f"Szoba: {szobaszam}, Dátum: {datum}")
        lb.pack(pady=10)

        tk.Button(window, text="Lemondás", command=lambda: self.lemond(lb, window)).pack(pady=10)

    def lemond(self, listbox, window):
        selection = listbox.curselection()
        if selection:
            index = selection[0]
            szobaszam, datum = listbox.get(index).split(", ")
            szobaszam = szobaszam.split(": ")[1]
            datum = datum.split(": ")[1]
            if self.szalloda.foglalas_lemondas(szobaszam, datum):
                messagebox.showinfo("Lemondás", "A foglalás lemondva.")
                listbox.delete(index)
                window.update()
            else:
                messagebox.showerror("Lemondás", "Nem létező foglalás.")
        else:
            messagebox.showerror("Lemondás", "Válassz ki egy foglalást a listából!")

    def run(self):
        self.root.mainloop()



szalloda = Szalloda("Best Hotel")
szalloda.add_szoba(EgyagyasSzoba("101"))
szalloda.add_szoba(KetagyasSzoba("102"))
szalloda.add_szoba(EgyagyasSzoba("103"))

szalloda.foglal("101", "2024-05-01")
szalloda.foglal("101", "2024-05-02")
szalloda.foglal("102", "2024-05-03")
szalloda.foglal("103", "2024-05-04")
szalloda.foglal("102", "2024-05-05")

app = HotelApp(szalloda)
app.run()
