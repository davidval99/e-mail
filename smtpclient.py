import sys
from twisted.internet import reactor
from twisted.mail.smtp import sendmail
from twisted.python import log
from tkinter.filedialog import askopenfilename
from email.mime.text import MIMEText
import csv

log.startLogging(sys.stdout)


from tkinter import *


def fetch_inputs():
    """
    Obtains user inputs from entries
    """
    from_info = _from.get()
    recepient_info = recepient
    title_info = title.get()
    message_info = str(message.get())
    print(from_info, "\t", recepient_info, "\t", title_info, "\t", message_info)
    host = "localhost"

    addresses = []

    with open(recepient_info, 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter='\n', quotechar='|')
        for row in spamreader:
            new = row[0].split(sep=',')
            addresses = addresses + new
        print(addresses)


    msg = MIMEText(message_info)
    msg["Title"] = title_info
    msg["From"] = from_info
    recipients = addresses
    msg["To"] = ", ".join(recipients)
    deferred = sendmail(host, from_info, recipients, msg, port=2525)
    deferred.addBoth(lambda result : reactor.stop())

    reactor.run()

    from_entry.delete(0, END)
    title_entry.delete(0, END)
    message_entry.delete(0, END)

def file_explorer():

    global recepient
    Tk().withdraw()
    recepient = askopenfilename()


#Window init
window_gui = Tk()
window_gui.geometry("800x800")
window_gui.title("ITCR SMTP Mail Client")
window_gui.resizable(False, False)
window_gui.config(background="#afeeff")
main_title = Label(text="New Message", font=("Arial", 25), bg="#afeeff", fg="#000000", width="500",
                   height="2")
main_title.pack()

#Labels
from_label = Label(text="From",font=("Arial", 12), fg="#000000", bg="#afeeff")
from_label.place(x=370, y=100)

recepient_label = Label(text="Recipients", font=("Arial", 12), fg="#000000",bg="#afeeff")
recepient_label.place(x=360, y=200)

title_label = Label(text="Title", font=("Arial", 12),  fg="#000000",bg="#afeeff")
title_label.place(x=370, y=300)

message_label = Label(text="Message", font=("Arial, 12"), fg="#000000",bg="#afeeff")
message_label.place(x=370, y=400)

_from = StringVar()
recepient = StringVar()
title = StringVar()
message = StringVar()

#inputs
from_entry = Entry(textvariable=_from, width="50")
from_entry.place(x=200, y=130,height=40)

recepient_entry = Button(window_gui, text="Select CSV", width="15", height="2", command=file_explorer, bg="#3383ff",fg="white")
recepient_entry.place(x=320, y=230,height=40)

title_entry = Entry(textvariable=title, width="50")
title_entry.place(x=200, y=330,height=40)

message_entry = Entry(textvariable=message,width="50")
message_entry.place(x=200, y=430,height=180)


submit_btn = Button(window_gui, text="Send", width="20", height="4", command=fetch_inputs, bg="#3383ff",fg="white")
submit_btn.place(x=300, y=650)

window_gui.mainloop()
