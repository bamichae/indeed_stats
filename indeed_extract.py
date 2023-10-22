import copy
import csv
import json

import numpy as np
import pandas as pd
import requests
from matplotlib import pyplot as plt
from matplotlib.cm import get_cmap
from itertools import cycle

from matplotlib.pyplot import figure
cmap = get_cmap('rainbow')


class IndeedExtract:
    def __init__(self):
        self.indeed_postings_url = 'https://raw.githubusercontent.com/hiring-lab/job_postings_tracker/master/US/job_postings_by_sector_US.csv'
        self.indeed_aggregate_postings_url = 'https://raw.githubusercontent.com/hiring-lab/job_postings_tracker/master/US/aggregate_job_postings_US.csv'

        self.postings_df = self.get_postings()
        self.aggregate_postings_df = self.get_aggregate_postings()
    def get_postings(self):
        df = pd.read_csv(filepath_or_buffer=self.indeed_postings_url)
        # Turn date to datetime
        df['date'] = pd.to_datetime(df['date'])
        return df

    def get_aggregate_postings(self):
        df = pd.read_csv(filepath_or_buffer=self.indeed_aggregate_postings_url)
        df['date'] = pd.to_datetime(df['date'])
        return df

    def calculate_software_development(self):
        software_df = self.postings_df[self.postings_df['display_name'] == 'Software Development']
        software_df['postings_ratio'] = software_df['indeed_job_postings_index'] / software_df['indeed_job_postings_index'].iloc[0]
        return software_df

    def calculate_aggregate_postings(self):
        df = self.aggregate_postings_df[self.aggregate_postings_df['variable'] == 'total postings']
        df['total_ratio'] = df['indeed_job_postings_index_SA'] / df['indeed_job_postings_index_SA'].iloc[0]
        return df

    def plot_postings_ratio(self, software_df):
        plt.plot(software_df['date'], software_df['postings_ratio'], c='blue', label='Software Development')
        plt.xlabel('Date')
        plt.ylabel('Ratio of Postings Since Feb 2020')
        plt.title('Software Development Job Postings vs. Date')
        plt.xticks(rotation=45)
        plt.subplots_adjust(bottom=0.2)
        plt.grid(True)
        plt.legend()
        plt.savefig('figures/software_development_ratio.png')
        plt.close()

    def plot_aggregate_postings_ratio(self, df, software_development_df):
        plt.plot(df['date'], df['total_ratio'], c='orange', label='All Sectors')
        plt.plot(software_development_df['date'], software_development_df['postings_ratio'], c='blue', label='Software Development')
        plt.xlabel('Date')
        plt.ylabel('Ratio of Postings Since Feb 2020')
        plt.title('Total Job Postings vs. Date')
        plt.xticks(rotation=45)
        plt.subplots_adjust(bottom=0.2)
        plt.legend()
        plt.grid(True)
        plt.savefig('figures/total_postings_ratio.png')
        plt.close()

    def plot_sectors_ratios(self):
        df = copy.deepcopy(self.postings_df)
        grouped_df = df.groupby('display_name')
        ratios = []
        names = []

        for name, group in grouped_df:
            final_value = group['indeed_job_postings_index'].iloc[-1]
            initial_value = group['indeed_job_postings_index'].iloc[0]
            ratios.append(final_value / initial_value)
            names.append(name)

        sorted_pairs = sorted(zip(names, ratios), key=lambda pair: pair[1])
        rainbow_colors = [cmap(x) for x in np.linspace(0, 1, len(ratios))]
        colors = ['g' if num > 1 else 'r' for num in ratios]
        heights = [num - 1 for num in ratios]

        fig, ax = plt.subplots(figsize=(8, 7))

        sorted_trips = sorted(zip(names, heights, colors), key=lambda trip: trip[1])
        for i, (name, height, color) in enumerate(sorted_trips):
            if height > 0:
                ax.bar(name, height * 100, color=color, bottom=0)
            else:
                ax.bar(name, height * 100, color=color, bottom= 0)

        plt.xticks(rotation=270)
        plt.tight_layout()
        plt.title("Percent Change in Overall Postings From Feb 2020 to Oct 2023")
        plt.ylabel("Percent Change")
        plt.xlabel("Sectors")
        plt.subplots_adjust(bottom=0.5, top=0.9, left=.1)

        plt.savefig('figures/all_sectors.png')

    def run(self):
        all_aggregate_df = self.calculate_aggregate_postings()
        software_development_df = self.calculate_software_development()

        self.plot_postings_ratio(software_development_df)
        self.plot_aggregate_postings_ratio(all_aggregate_df, software_development_df)
        self.plot_sectors_ratios()

if __name__ == '__main__':
    indeed_extract = IndeedExtract()
    indeed_extract.run()