import tkinter as tk
from tkinter import ttk
import pandas as pd
from rapidfuzz import fuzz, process
from pandastable import Table, TableModel, config
from jobspy import scrape_jobs
import pandas as pd
import time
import os.path
from jobScrape import JobScraper

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

LARGEFONT = ("Verdana", 35)


class jobSearch_app(tk.Tk):

    # __init__ function for class tkinterApp
    def __init__(self, *args, **kwargs):

        # __init__ function for class Tk
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Job Insight")

        # Container
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Initializing frames
        self.frames = {}

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        for F in (Dashboard, Insight, AllJobs):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(Dashboard)

    # Display Current Frame
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def start_search(self):
        # search_text = self.entry.get()
        search_text = "UX Designer"
        self.search(search_text, search_column="title")

    def search(self, search_term, search_column):
        if search_term != '':
            text, index, match = self.fuzzy_find(search_term, search_column)
            print(
                f"Best match for {search_term} is {text} with a score of {match}%")
            # Optional: clear the text widget
            self.text_widget.delete("1.0", "end")

            # if there is a > 50% match, print the job information,
            if match > 50:
                # get the row of the best match using the index
                row = self.df.iloc[index]
                jobTitle = row['title']     # get the title from the row
                location = row['location']  # get the location of the job
                jobType = row['job_type']  # get the job type
                datePosted = row['date_posted']  # get the date posted
                # Radius = "Placeholder"

                # Present the total number of job found
                # If no zipcode set
                self.text_widget.insert(
                    "end", f"The total number of {jobTitle} jobs availble today is: ")

                # If zipcode set
                # self.text_widget.insert("end", f"The total number of {jobTitle} jobs in {Zipcode} availble today is: ")

                # If zipcode and radius set
                # self.text_widget.insert("end", f"The total number of {jobTitle} jobs {Radius} miles within {Zipcode} availble today is: ")

                # Compare the number today to prvious days
                # If higher
                # self.text_widget.insert("end", f"It is {jobTitle} more than yesterday.")
                # If lower
                # self.text_widget.insert("end", f"It is {jobTitle} less than yesterday. ")

                # Add chart of change in daily number of jobs available.

            else:
                self.text_widget.insert(
                    "end", f"No match found for {search_term} jobs")

    def fuzzy_find(self, search_term, column_name, n=1):
        matches = process.extract(
            search_term, self.df[column_name], scorer=fuzz.token_set_ratio, limit=n)
        # print("DEBUG", search_term, matches) # DEBUG a list of tuples (text, similarity score, index)
        text = matches[0][0]  # the text of the best match
        # the similarity score of the best match (0-100)
        match_score = matches[0][1]
        index = matches[0][2]  # the index in the data frame of the best match
        return text, index, match_score

    # Convert City to Zipcode
    def City_to_Zipcode(self, search_city: str) -> str:
        return

    # Calculate Radius
    def Calculate_Radius(self, search_radius: int, search_city: str) -> int:
        return

    # Plot result (https://www.geeksforgeeks.org/how-to-embed-matplotlib-charts-in-tkinter-gui/)
    def Draw_Graph(self, total_number: list, range: str) -> None:
        return

    def scrapeJob(self):
        print("Scraping UX jobs from Linkedin")

        offset = 0
        chunk_size = 50
        chunk = 0
        num_chunks = 3  # change this to get more

        # for chunk in range(0, num_chunks):
        while chunk < num_chunks:
            try:
                print(f"Scraping chunk {chunk+1}...")
                jobs = scrape_jobs(
                    # neither linkedin nor indeed worked for me
                    site_name=["Linkedin"],
                    search_term="ux",
                    # location="60640",
                    results_wanted=chunk_size,
                    offset=offset,
                    # location='USA',
                    # country_indeed='USA'  # only needed for indeed
                )
            except:
                print("End of Search. Scraping Stopped.")
                break

            else:
                print(
                    f"Found {len(jobs)} UX jobs on Linkedin in chunk {chunk+1}")
                print("offset: ", offset)
                offset += len(jobs)
                chunk += 1

            # Check if file exists
            if not os.path.isfile("jobs.csv"):
                # Create file if doesn't exist
                print("Results saved to a new file jobs.csv")
                jobs.to_csv("jobs.csv", index=False)
            else:
                # Add results to existing file
                print("Adding results in existing file jobs.csv")
                jobs.to_csv("jobs.csv", mode="a", index=False, header=False)
            time.sleep(5)

        # Read jobs.csv
        df_state = pd.read_csv("jobs.csv")
        print("Total number of jobs: ",  len(df_state))

        # Find Duplicated rows
        Dup_Rows = df_state[df_state.duplicated()]
        print("Number of duplicate Rows: ", len(Dup_Rows))

        DF_RM_DUP = df_state.drop_duplicates(keep='first')
        print('Number of jobs after duplicate removed: ', len(DF_RM_DUP))
        DF_RM_DUP.to_csv("jobs.csv", index=False)

    def on_closing(self):
        self.quit()
        self.destroy()

# Dashboard Frame


class Dashboard(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        # Dashboard Label
        label = ttk.Label(self, text="Dashboard", font=LARGEFONT)
        label.grid(row=0, column=1, columnspan=4, padx=10, pady=10)

        # Read jobs.csv
        self.df = pd.read_csv("jobs.csv")

        # Read the last updated date
        self.df['date_posted'] = pd.to_datetime(self.df['date_posted'])
        self.max_date_year = self.df['date_posted'].max()

        # Format the date
        self.max_date = self.max_date_year.strftime("%b %d")
        self.max_year = self.max_date_year.strftime('%Y')

        ### Nav Bar ###
        # Dashboard Button
        dashboardBtn = ttk.Button(self, text="Dashboard",
                                  command=lambda: controller.show_frame(Dashboard))
        dashboardBtn.grid(row=1, column=0, padx=10, pady=10)

        # Insight Button
        insightBtn = ttk.Button(self, text="Insight",
                                command=lambda: controller.show_frame(Insight))
        insightBtn.grid(row=2, column=0, padx=10, pady=10)

        # All Jobs Button
        AllJobsBtn = ttk.Button(self, text="All Jobs",
                                command=lambda: controller.show_frame(AllJobs))
        AllJobsBtn.grid(row=3, column=0, padx=10, pady=10)

        ### Dashboard Content ###

        # Total Number
        label = ttk.Label(self, text="Total of")
        label.grid(row=1, column=1, columnspan=2)

        label = ttk.Label(self, text=len(self.df), font=LARGEFONT)
        label.grid(row=2, column=1, columnspan=2)

        label = ttk.Label(self, text="jobs")
        label.grid(row=3, column=1, columnspan=2)

        # Last Updated
        label = ttk.Label(self, text="Last Updated:")
        label.grid(row=1, column=4, columnspan=2)

        label = ttk.Label(self, text=self.max_date, font=LARGEFONT)
        label.grid(row=2, column=4, columnspan=2)

        label = ttk.Label(self, text=self.max_year)
        label.grid(row=3, column=4, columnspan=2)

        # Job Scrape Button
        self.scraper = JobScraper()
        update_button = tk.Button(
            self, text="Update", command=self.scraper.scrapeJob)
        update_button.grid(row=1, column=6, rowspan=3, sticky="nesw", padx=10)

        # Job Trend Chart
        fig, ax = plt.subplots()
        job_counts_monthly = self.df.resample('M', on='date_posted').size()
        ax.plot(job_counts_monthly.index, job_counts_monthly.values)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.set_xlabel('Month')
        ax.set_ylabel('Number of jobs')

        chart_frame = tk.Frame(self, background="white", height=7)
        chart_frame.grid(row=4, column=1, columnspan=6,
                         sticky="nesw", padx=10, pady=10, ipady=50)
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Insight Frame


class Insight(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Insigh Label
        label = ttk.Label(self, text="Insight", font=LARGEFONT)
        label.grid(row=0, column=1, columnspan=4, padx=10, pady=10)

        ### Nav Bar ###
        # Dashboard Button
        dashboardBtn = ttk.Button(self, text="Dashboard",
                                  command=lambda: controller.show_frame(Dashboard))
        dashboardBtn.grid(row=1, column=0, padx=10, pady=10)

        # Insight Button
        insightBtn = ttk.Button(self, text="Insight",
                                command=lambda: controller.show_frame(Insight))
        insightBtn.grid(row=2, column=0, padx=10, pady=10)

        # All Jobs Button
        AllJobsBtn = ttk.Button(self, text="All Jobs",
                                command=lambda: controller.show_frame(AllJobs))
        AllJobsBtn.grid(row=3, column=0, padx=10, pady=10)

        ### Insiht Content ###
        # Total Number
        label = ttk.Label(self, text="Total of")
        label.grid(row=1, column=1, columnspan=2)

        label = ttk.Label(self, text="200", font=LARGEFONT)
        label.grid(row=2, column=1, columnspan=2)

        label = ttk.Label(self, text="jobs")
        label.grid(row=3, column=1, columnspan=2)

        # Last Updated
        label = ttk.Label(self, text="Last Updated:")
        label.grid(row=1, column=4, columnspan=2)

        label = ttk.Label(self, text="Nov. 6", font=LARGEFONT)
        label.grid(row=2, column=4, columnspan=2)

        label = ttk.Label(self, text="2023")
        label.grid(row=3, column=4, columnspan=2)

        # Update Button
        update_button = tk.Button(self, text="Update", command="")
        update_button.grid(row=1, column=6, rowspan=3, sticky="nesw", padx=10)

        # Job Trend Chart
        chart_frame = tk.Frame(self, background="white", height=7)
        chart_frame.grid(row=4, column=1, columnspan=6,
                         sticky="nesw", padx=10, pady=10, ipady=50)

        # Read jobs.csv
        self.df = pd.read_csv("jobs.csv")

        # Select and rename columns
        self.df = self.df[['title', 'company', 'location', 'job_type', 'date_posted']].rename(
            columns={'title': 'Job Title', 'company': 'Company', 'location': 'Location', 'job_type': 'Job Type', 'date_posted': 'Date Posted'})

        # Pandas Table
        table_frame = tk.Frame(self)
        table_frame.grid(row=1, column=1, columnspan=6,
                         rowspan=4, sticky="nesw")

        pandasTable = Table(table_frame, dataframe=self.df)
        pandasTable.show()

# All Jobs Frame


class AllJobs(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # All Jobs Label
        label = ttk.Label(self, text="All Jobs", font=LARGEFONT)
        label.grid(row=0, column=1, columnspan=4, padx=10, pady=10)

        ### Nav Bar ###
        # Dashboard Button
        dashboardBtn = ttk.Button(self, text="Dashboard",
                                  command=lambda: controller.show_frame(Dashboard))
        dashboardBtn.grid(row=1, column=0, padx=10, pady=10)

        # Insight Button
        insightBtn = ttk.Button(self, text="Insight",
                                command=lambda: controller.show_frame(Insight))
        insightBtn.grid(row=2, column=0, padx=10, pady=10)

        # All Jobs Button
        AllJobsBtn = ttk.Button(self, text="All Jobs",
                                command=lambda: controller.show_frame(AllJobs))
        AllJobsBtn.grid(row=3, column=0, padx=10, pady=10)

        ### All Job Content ###

        # Read jobs.csv
        self.df = pd.read_csv("jobs.csv")

        # Select and rename columns
        self.df = self.df[['title', 'company', 'location', 'job_type', 'date_posted']].rename(
            columns={'title': 'Job Title', 'company': 'Company', 'location': 'Location', 'job_type': 'Job Type', 'date_posted': 'Date Posted'})

        # Pandas Table
        table_frame = tk.Frame(self)
        table_frame.grid(row=1, column=1, columnspan=6,
                         rowspan=4, sticky="nesw")

        pandasTable = Table(table_frame, dataframe=self.df)
        pandasTable.show()


if __name__ == "__main__":
    app = jobSearch_app()
    app.mainloop()
