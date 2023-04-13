#PYTHON
from datetime import datetime
import tkinter.messagebox
#PIP
import customtkinter
from customtkinter import filedialog
#LOCAL
import driver_hours_calculator.report as report
import driver_hours_calculator.drivers as drivers
from driver_hours_calculator.helper_functions import get_previous_sunday
import driver_hours_calculator.config as config

customtkinter.set_appearance_mode('Dark')  # Modes: 'System' (standard), 'Dark', 'Light'
customtkinter.set_default_color_theme('blue')  # Themes: 'blue' (standard), 'green', 'dark-blue'

class UserInterface(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.file_name = None
        self.default_email_recipients = '; '.join(config.EMAIL_RECIPIENTS)

        # configure window
        self.title('Driver Hours')
        self.geometry(f'{900}x{350}')

        # # configure grid layout (4x4)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.main_frame.grid_columnconfigure([0,1], weight=1)
        self.main_frame.grid_rowconfigure(4, weight=1)
        self.main_frame.grid(row=0, column=0, sticky='nsew')

        self.title_label = customtkinter.CTkLabel(self.main_frame, text="Driver Hours Calculator", font=customtkinter.CTkFont(size=40, weight="bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, padx=20, sticky='nsew')

        self.file_frame = customtkinter.CTkFrame(self.main_frame, corner_radius=0)
        self.file_frame.columnconfigure(0, weight=1)
        self.file_frame.grid(row=2, column=0, columnspan=3, sticky='nsew', pady=5)

        self.file_label = customtkinter.CTkLabel(self.file_frame, text='Upload Raw Driver Hours CSV: ', font=customtkinter.CTkFont(size=30, weight='bold'))
        self.file_label.grid(row=0, column=0, columnspan=2, padx=20, sticky='nsw')
        self.file_entry = customtkinter.CTkEntry(self.file_frame)
        self.file_entry.grid(row=1, column=0, padx=5, pady=10, sticky='nsew')
        self.get_file_button = customtkinter.CTkButton(self.file_frame, text='Browse', font=customtkinter.CTkFont(size=15, weight='bold'), command=self.open_file_search_dialog)
        self.get_file_button.grid(row=1, column=1, padx=5, pady=10, sticky='nsew')

        self.email_frame = customtkinter.CTkFrame(self.main_frame, corner_radius=0)
        self.email_frame.columnconfigure(1, weight=1)
        self.email_frame.grid(row=3, column=0, columnspan=3, sticky='nsew', pady=5)

        self.email_label = customtkinter.CTkLabel(self.email_frame, text='Email Options: ', font=customtkinter.CTkFont(size=30, weight='bold'))
        self.email_label.grid(row=0, column=0, columnspan=3, padx=20,sticky='nsw')
        self.email_recipients_label = customtkinter.CTkLabel(self.email_frame,text='Recipients: ', font=customtkinter.CTkFont(size=15, weight='bold'))
        self.email_recipients_label.grid(row=1, column=0, pady=10, padx=5)
        self.email_recipients_entry = customtkinter.CTkEntry(self.email_frame)
        self.email_recipients_entry.grid(row=1, column=1, pady=10, padx=5, sticky='nsew')
        self.email_recipients_entry.insert(0, self.default_email_recipients)
        self.send_email_checkbox = customtkinter.CTkCheckBox(self.email_frame, text='Send Email?', command=self.enable_disable_email)
        self.send_email_checkbox.grid(row=1, column=2, pady=10, padx=5)
        self.send_email_checkbox.select()

        self.create_report_button = customtkinter.CTkButton(
            self.main_frame,
            text='Create Hours Report',
            font=('Helvetica',40,'bold'),
            fg_color='#49ab81',
            hover_color='#419873',
            command=self.create_final_hours_report
        )
        self.create_report_button.grid(row=4, column=0, columnspan=2, padx=5, pady=10, sticky='nsew')

    def open_file_search_dialog(self):
        self.file_name = filedialog.askopenfilename()
        self.file_entry.insert(0, self.file_name)    

    def enable_disable_email(self):
        send_email = self.send_email_checkbox.get()
        if send_email:
            self.email_recipients_entry.configure(state='normal')
            print(self.email_recipients_entry.get().split('; '))
        else:
            self.email_recipients_entry.configure(state='disabled')

    def create_final_hours_report(self):
        #Check weather send email is selected or not
        send_email = self.send_email_checkbox.get()
        self.update_button_text('Creating Report . . .')
        if self.file_name:
            start_date = get_previous_sunday(1)
            raw_hours_report = report.RawHoursReport(self.file_name, week_start=start_date)
            all_drivers = drivers.AllDrivers(raw_hours_report.raw_hours_dataframe)
            final_report = report.FinalHoursReport(raw_hours_report=raw_hours_report, all_drivers=all_drivers)
            file_name = final_report.generate_hours_report()

            if send_email:
                recipients = self.email_recipients_entry.get().split('; ')
                final_report.send_report_email(
                    subject=f'Driver Hours {start_date.date()}',
                    message='See attached sheet for drivers hours',
                    recipients=recipients,
                    attachment=file_name
                )
                tkinter.messagebox.showinfo('File Created', 'New file created and email sent!')
            else:
                tkinter.messagebox.showinfo('File Created', 'New file created!')
        else:
            tkinter.messagebox.showerror('Error', 'No File Selected!')

        self.update_button_text('Create Hours Report')
 
    def update_button_text(self, text: str):
        """ Changes buttons text and calls update to refresh screen """
        self.create_report_button.configure(text=text)
        self.update()