import customtkinter as ctk

root = ctk.CTk()

root.title("Rental Manager")
root.geometry("900x550+100+80")
root.resizable(False, False)
main_frame = ctk.CTkFrame(master= root, fg_color= "white")
main_frame.pack(side="top", fill="both", expand=True)

def login():
 heading_lb = ctk.CTkLabel(master=main_frame, text="Login",  text_color=("black", "black"),font = ctk.CTkFont(size=40, weight="bold") )
 heading_lb.place(relx=0.5, y=120, anchor="center")

 loginId_entry = ctk.CTkEntry(master=main_frame, width=230, height= 40, placeholder_text='Login Id',border_width= 2, border_color= 'black',fg_color ='white')
 loginId_entry.place(relx=0.5, y=200, anchor="center")

 loginPwd_entry = ctk.CTkEntry(master=main_frame, width=230, height= 40, placeholder_text='Password',border_width= 2, border_color= 'black',fg_color ='white')
 loginPwd_entry.place(relx=0.5, y=250, anchor="center")

 login_btn = ctk.CTkButton(master=main_frame, fg_color ='#d9d9d9', text="Login", width=150, height= 30, text_color="black", hover_color="#a0a0a0")
 login_btn.place(relx=0.5, y=300, anchor="center")

login()
root.mainloop()

