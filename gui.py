# gui testing


import customtkinter

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

root = customtkinter.CTk()
root.geometry("500x350")

def get_user_input():
    print("test")


frame = customtkinter.CTkFrame(master = root)
frame.pack(pady = 20, padx = 60, fill = 'both', expand = True)

label = customtkinter.CTkLabel(master = frame, text = 'user input') #, text_font = ('Roboto', 24))
label.pack(pady = 12, padx = 10 )

entry1 = customtkinter.CTkEntry(master=frame, placeholder_text = 'total hours to study')
entry1.pack(pady = 12, padx = 10)

entry2 = customtkinter.CTkEntry(master=frame, placeholder_text = 'topics to study')
entry2.pack(pady = 12, padx = 10)

button=customtkinter.CTkButton(master = frame, text= "Next", command=get_user_input)
button.pack(pady = 12, padx = 10)

root.mainloop()