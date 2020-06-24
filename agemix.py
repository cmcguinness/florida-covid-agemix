"""
    Generate Age Mix charts of new infections in Florida

    It will work either at the state level (in which case the chart is daily new posities),
    or at the county level (in which case the chart is of weekly new positives)

    Charles McGuinness @socialseercom

"""
import requests
import datetime
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time


#   Basically, all the work is in this class

def timestamp2week(t: pd.Timestamp):
    return t.to_pydatetime().date().isocalendar()[1]


#   These are functions I use to show the timing of various steps in the process,
#   not so important now but critical when I was optimizing the code
class mytime:
    def __init__(self, msg: str, newline=''):
        self.time_start = time.time()
        print(msg + ' ... ', end=newline)

    def tend(self, msg='done'):
        print('{} in {:6.2f} seconds'.format(msg, time.time() - self.time_start))

class age_analysis:

    # _county is either the name of a county (e.g., Orange) or is None for all-Florida
    def __init__(self, _county: str):
        self.county = _county
        self.age_groups = []
        self.age_buckets = []
        self.weeks = []
        self.df = None

        self.init_age_groups()
        self.fetch_data()

        self.counties = self.df.County.unique()
        self.counties.sort()

        self.dr = pd.date_range(start=self.df['Date'].min(), end=self.df['Date'].max())

    def week2datetime(self, w):
        d = '2020-W' + str(w)
        return datetime.datetime.strptime(d + '-7', '%G-W%V-%u')

    def init_age_groups(self):
        self.age_groups = ['0-4 years',
                           '5-14 years',
                           '15-24 years',
                           '25-34 years',
                           '35-44 years',
                           '45-54 years',
                           '55-64 years',
                           '65-74 years',
                           '75-84 years',
                           '85+ years']

    def fetch_data(self):
        url = 'https://opendata.arcgis.com/datasets/37abda537d17458bae6677b8ab75fcb9_0.geojson'
        tmr = mytime('Fetching data')
        page = requests.get(url)
        tmr.tend()

        if not page.ok:
            page.raise_for_status()

        tmr = mytime('Getting JSON')
        json_data = json.loads(page.content)
        tmr.tend()

        # Now lets convert this into a useful Pandas DataFrame
        tmr = mytime('Creating DataFrame')
        self.df = pd.DataFrame((pd.DataFrame(json_data['features'])['properties']).array)
        self.df.to_csv('snapshots/'+str(datetime.datetime.now())+'.csv')

        # If we're only looking at one county's data, drop the rest from the dataframe for performance
        if self.county != None:
            self.df = self.df[self.df['County'] == self.county]
        tmr.tend()

        # Convert the date
        tmr = mytime('Cleaning up dates')
        self.df['Date'] = pd.to_datetime(self.df['EventDate'])
        if self.county is not None:
            self.df['Week'] = None
            self.df['Week'] = self.df.apply(lambda row: row['Date'].to_pydatetime().date().isocalendar()[1], axis=1)
            # for index, row in self.df.iterrows():
            #     self.df.loc[index,'Week'] = self.timestamp2week(row['Date'])

            self.weeks = self.df['Week'].unique()
            self.weeks.sort()
        tmr.tend()

    def create_age_buckets(self):
        tmr = mytime('create_age_buckets')
        ages = []
        for a in self.age_groups:
            datecounts = []
            df_age = self.df[self.df['Age_group'] == a]
            if self.county is not None:
                for w in self.weeks:
                    total = sum(df_age['Week'] == w)
                    datecounts.append(total)
            else:
                for d in self.dr:
                    total = sum(df_age['Date'] == d)
                    datecounts.append(total)
            ages.append(datecounts)
        self.age_buckets = ages
        tmr.tend()

    def plot_ages(self):
        tmr = mytime('plot_ages')
        ys = np.array(self.age_buckets, dtype=float)
        for i in range(len(ys[0])):
            total = 0
            for j in range(len(ys)):
                total += ys[j][i]
            if total != 0:
                for j in range(len(ys)):
                    ys[j][i] = 100.0 * ys[j][i] / float(total)

        start = None
        fig = plt.figure(figsize=(10, 5))

        if self.county is None:
            target = pd.to_datetime('2020-03-01', utc=True)
            for i in range(len(self.dr)):
                if self.dr[i] == target:
                    start = i
                    break

            yt = ys.transpose()
            data = (yt[start:]).transpose()
            plt.stackplot(self.dr[start:], data)

        else:
            target = timestamp2week(pd.to_datetime('2020-03-01', utc=False))
            for i in range(len(self.weeks)):
                if self.weeks[i] == target:
                    start = i
                    break

            yt = ys.transpose()
            data = (yt[start:]).transpose()

            # plt.subplot(111)
            dates = []
            for i in range(start, len(self.weeks)):
                dates.append(self.week2datetime(self.weeks[i]))

            # plt.stackplot(self.weeks[start:].tolist(), data)
            plt.stackplot(dates[:-1], data[:, :-1])

        plt.legend(self.age_groups, loc='center left', bbox_to_anchor=(1, 0.5))
        if self.county is not None:
            plt.title('Florida Covid-19 Positives in ' + self.county + ' County By Age Bracket as % of Week\'s Total')
        else:
            plt.title('Florida Covid-19 Positives By Age Bracket as % of Day\'s Total')

        plt.xlabel("Chart prepared by Charles McGuinness @socialseercom using data from Florida Department of Health")
        # plt.figtext(0.5, 0.02, "Chart prepared by Charles McGuinness @socialseercom using data from Florida Department of Health",
        #             ha="center", fontsize=10)
        fig.subplots_adjust(top=0.95, bottom=0.4)
        plt.tight_layout()
        if self.county is not None:
            plt.savefig('images/' + str(datetime.datetime.now())[:10] + '-ages-FL-' + self.county + '.png', dpi=150)
        else:
            plt.savefig('images/' + str(datetime.datetime.now())[:10] + '-ages-FL.png', dpi=150)

        tmr.tend()


if __name__ == '__main__':
    print('Age analysis of covid-19 positives in Florida, v1.0')
    county = input('County to focus on [default is all]: ')
    if county == '':
        county = None
    tmr = mytime('Starting analysis', newline='\n')
    aa = age_analysis(county)
    aa.create_age_buckets()
    aa.plot_ages()
    tmr.tend('Finished run')
