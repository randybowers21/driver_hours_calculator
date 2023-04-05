#PYTHON
from datetime import datetime
import tkinter.messagebox
#3RD PARTY
import customtkinter
from customtkinter import filedialog
#LOCAL
from report import RawHoursReport, FinalHoursReport
from driver import AllDrivers
from helper_functions import get_previous_sunday

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class Interface(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.file_name = None

        # configure window
        self.title("Driver Hours")
        self.geometry(f"{500}x{200}")

        # # configure grid layout (4x4)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.main_frame.grid_columnconfigure([0,1], weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        self.title_label = customtkinter.CTkLabel(self.main_frame, text="Upload Raw Driver Hours CSV", font=customtkinter.CTkFont(size=40, weight="bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10))
        self.file_entry = customtkinter.CTkEntry(self.main_frame)
        self.file_entry.grid(row=1, column=0, padx=5, sticky="nsew")
        self.get_file_button = customtkinter.CTkButton(self.main_frame, text='Browse', command=self.open_file_search_dialog)
        self.get_file_button.grid(row=1, column=1, padx=5, sticky="nsew")

        # self.send_email_checkbox = customtkinter.CTkCheckBox()

        self.upload_button = customtkinter.CTkButton(
            self.main_frame,
            text='Create Hours Report',
            font=("Helvetica",40,'bold'),
            fg_color='#49ab81',
            hover_color='#419873',
            command=self.create_final_hours_report
        )
        self.upload_button.grid(row=2, column=0, columnspan=2, padx=5, pady=10, sticky="nsew")

    def open_file_search_dialog(self):
        self.file_name = filedialog.askopenfilename()
        self.file_entry.insert(0, self.file_name)    

    def create_final_hours_report(self):
        if self.file_name:
            start_date = get_previous_sunday(1)
            raw_hours_report = RawHoursReport(self.file_name, week_start=start_date)
            all_drivers = AllDrivers(raw_hours_report.raw_hours_dataframe)
            final_report = FinalHoursReport(raw_hours_report=raw_hours_report, all_drivers=all_drivers)
            final_report.generate_hours_report(send_email=True)
            tkinter.messagebox.showinfo('File Created', 'New File created and email sent!')
        else:
            tkinter.messagebox.showerror('Error', 'No File Selected!')

        #  if send_email:
    #         self.send_report_email(
    #             subject=f'Driver Hours {self.week_start.date()}',
    #             message='See attached sheet for drivers hours',
    #             recipients=config.TEST_EMAIL_RECIPIENTS,
    #             attachment=new_file_name
            # )

app =Interface()
app.mainloop()