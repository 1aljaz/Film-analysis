from bs4 import BeautifulSoup as bs
import pandas as pd
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
    'Accept-Language': 'en-US, en;q=0.5'
}

url = "https://www.the-numbers.com/box-office-records/worldwide/all-movies/cumulative/all-time"

class Film:
    def __init__(self):
        self.film_data = []
        self.aud_score = 'N/A'
        self.crit_score = 'N/A'
        self.name = ""
        self.gross = ""
        self.rank = ""
        self.director = ""
        self.release_date = ""
        self.genre = ""
        self.dist = ""

    def get_data_numbers(self, num=""):
        response = requests.get(url+"/"+num, headers=headers)
        if response.status_code != 200:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
            return

        soup = bs(response.text, 'html.parser')
        
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables on the page")

        for table in tables:
            rows = table.find_all('tr')
            print(f"Analyzing table with {len(rows)} rows")
            
            for row in rows[1:]:  # Skip the header row
                try:
                    columns = row.find_all('td')
                    if len(columns) >= 4:
                        self.rank = columns[0].text.strip()
                        name_element = columns[2].find('a')
                        self.name = name_element.text.strip() if name_element else "N/A"
                        self.gross = columns[3].text.strip()
                        
                        # Get Rotten Tomatoes data
                        self.get_data_rotten(self.name)
                        
                        movie_data = {
                            'Rank': self.rank,
                            'Name': self.name,
                            'Gross Income': self.gross,
                            'Audience Score': self.aud_score,
                            'Critics Score': self.crit_score,
                            'Genre' : self.genre,
                            'Director' : self.director,
                            'Distributor' : self.dist,
                            'Release date': self.release_date
                        }
                        
                        self.film_data.append(movie_data)
                        
                        print(f"Processed: Rank: {self.rank}, Name: {self.name}, Gross: {self.gross}, Audience: {self.aud_score}, Critics: {self.crit_score}, Dist: {self.dist}, Direc: {self.director}, Date: {self.release_date}")
                    else:
                        print(f"Row doesn't have enough columns: {columns}")
                except Exception as e:
                    print(f"Error processing row: {e}")
        
        print(f"Total movies processed: {len(self.film_data)}")

    def correct_name(self, name:str):
        s = name.replace(" ", "_")
        s = s.replace(":", "")
        return s 

    def get_data_rotten(self, name):
        corrected_name = self.correct_name(name)
        url = f"https://www.rottentomatoes.com/m/{corrected_name}"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to retrieve Rotten Tomatoes page for {name}. Status code: {response.status_code}")
            self.aud_score = 'N/A'
            self.crit_score = 'N/A'
            self.genre = 'N/A'
            self.director = 'N/A'
            self.dist = 'N/A'
            self.release_date = 'N/A'
            return
        
        soup = bs(response.text, 'html.parser')
        info_dl = soup.find('dl')

        if info_dl:
            for div in info_dl.find_all('div', class_='category-wrap'):
                key = div.find('dt', class_='key').text.strip()
                value = div.find('dd')

                if key == "Director":
                    self.director = value.text.strip().replace("/r/n", "")
                elif key == "Release Date (Theaters)":
                    self.release_date = value.text.strip().replace("Wide", "")
                elif key == "Distributor":
                    self.dist = value.text.strip()
                elif key == "Genre":
                    self.genre = ', '.join([a.text.strip() for a in value.find_all('a')])

        def extract_score(slot_name):
            button = soup.find('rt-button', attrs={'slot': slot_name})
            if button:
                rt_text = button.find('rt-text')
                if rt_text:
                    return str(rt_text.text.strip())
                    
            return "N/A"

        self.aud_score = extract_score('audienceScore')
        self.crit_score = extract_score('criticsScore')



    def save_to_csv(self, filename='movie_data.csv'):
        if not self.film_data:
            print("No data to save")
            return
        
        df = pd.DataFrame(self.film_data)
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")

f = Film()
for i in range(0, 505, 101):
    f.get_data_numbers(str(i))
f.save_to_csv()