import tkinter as tk
from tkinter import ttk
from index import *


class Table:
    def __init__(self):
        self.scores = tk.Tk()
        self.scores.resizable(False, False)
        self.cols = ('No.', 'Document Name', 'Document Title')
        self.listBox = ttk.Treeview(
            self.scores, columns=self.cols, show='headings', height=25)

    def display_Table(self, answer_list):
        if not answer_list:
            self.listBox.insert("", "end", values=(
                '-', '-', '-'))
        for i, doc_id in enumerate(answer_list):
            file_name = str(doc_id+1)+".txt"
            f = open('ShortStories/'+file_name, "r" , encoding="utf-8")
            title = f.readline()
            self.listBox.insert("", "end", values=(
                i+1, file_name, title))

    def create_Gui(self, indexer):
        self.scores.geometry("820x600")
        self.scores.title('Indexer')

        self.label = tk.Label(self.scores, text="Query Search", font=(
            "Arial Narrow", 30)).grid(row=0, columnspan=3)

        answer = tk.StringVar()
        searchQuery = tk.Entry(
            self.scores, width=70, textvariable=answer).grid(row=1, column=0)

        vsb = ttk.Scrollbar(
            self.scores, orient="vertical", command=self.listBox.yview)
        vsb.place(x=804, y=79, height=460)
        vsb.configure(command=self.listBox.yview)
        self.listBox.configure(yscrollcommand=vsb.set)

        for col in self.cols:
            self.listBox.heading(col, text=col)
        self.listBox.grid(row=2, column=0, columnspan=2)
        self.listBox.column(self.cols[0], minwidth=50, width=50, stretch=tk.NO)
        self.listBox.column(
            self.cols[1], minwidth=50, width=150, stretch=tk.NO)
        self.listBox.column(self.cols[2], minwidth=50, width=600)

        showScores = tk.Button(self.scores, text="Search", width=20,
                               command=lambda:
                               [
                                   self.listBox.delete(
                                       *self.listBox.get_children()),
                                   tb.display_Table(
                                       indexer.search_query(answer.get()))
                               ]).grid(row=1, column=1)

        closeButton = tk.Button(self.scores, text="Close", width=15,
                                command=exit).grid(row=4, column=0, columnspan=2)
        self.scores.mainloop()


if __name__ == "__main__":
    indexer = Indexer()
    indexer.read_file('ShortStories/')
    indexer.index_to_file('files/')

    tb = Table()
    tb.create_Gui(indexer)
