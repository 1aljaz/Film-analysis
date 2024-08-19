from bs4 import BeautifulSoup as bs
import pandas as pd
import requests

num_of_pages = 30  #number of pages it scrapes on the numbers website

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
    'Accept-Language': 'en-US, en;q=0.5'
}

url_numbers = "https://www.the-numbers.com/box-office-records/worldwide/all-movies/cumulative/all-time"
url_rotten = "https://www.rottentomatoes.com/m/"
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
        self.dist = ""

    def get_data_numbers(self, num=""): # Screjpam podatke iz url_numbers
        response = requests.get(url_numbers+"/"+num, headers=headers)
        if response.status_code != 200:
            print(f"Status code: {response.status_code}")
            return

        soup = bs(response.text, 'html.parser')
        
        tables = soup.find_all('table')

        for table in tables:
            rows = table.find_all('tr')
            
            for row in rows[1:]: # Prve ne upostevam
                try:
                    col = row.find_all('td')
                    if len(col) >= 4:
                        self.rank = col[0].text.strip()
                        name_element = col[2].find('a')
                        self.name = name_element.text.strip() if name_element else "N/A"
                        self.gross = col[3].text.strip()
                        
                        # Dobim podatke iz rotten tomato
                        self.get_data_rotten(self.name)
                        
                        movie_data = {
                            'Rank': self.rank,
                            'Naslov': self.name,
                            'Zasluzek': self.gross,
                            'Ocena občinstva': self.aud_score,
                            'Ocena kritikov': self.crit_score,
                            'Direktor' : self.director,
                            'Studio' : self.dist,
                            'Datum izzida': self.release_date
                        }
                        
                        if self.director != 'N/A':
                            self.film_data.append(movie_data)
                        
                        print(f"Rank: {self.rank}, ime: {self.name}, Zasl.: {self.gross}, Občinstvo: {self.aud_score}, Kritiki: {self.crit_score}, Studio: {self.dist}, Direktor: {self.director}, Datum: {self.release_date}")
                    else:
                        print(f"Row doesn't have enough col: {col}")
                except Exception as e:
                    print(e)
        
        print(f"Št. filmov: {len(self.film_data)}")

    def correct_name(self, name:str): # Pretvori ime filma iz numbers spletne strani v format za iskanje po rotten tomato spletni strani. Avengers: Endgame -> Avengers_Endgame
        s = name.replace(":", "")
        return ''.join('_' if not c.isalpha() else c for c in s)

    def get_data_rotten(self, name):
        corrected_name = self.correct_name(name)
        
        response = requests.get(url_rotten+{corrected_name}, headers=headers)
        if response.status_code != 200:  # Gledam, če je sploh našel veljavno spletno stran
            print(response.status_code)
            self.aud_score = 'N/A'
            self.crit_score = 'N/A'
            self.director = 'N/A'
            self.dist = 'N/A'
            self.release_date = 'N/A'
            return
        
        soup = bs(response.text, 'html.parser')
        dl = soup.find('dl')

        if dl: # Iz rotten tomato spletne strani pobere podatke in jih obdela
            for div in dl.find_all('div', class_='category-wrap'):
                key = div.find('dt', class_='key').text.strip()
                beseda = div.find('dd')
        
                if key == "Director" and beseda != "": # Za vse if stavke pogledam, ce niso slucajno prazni
                    self.director = beseda.text.replace("\r", "").strip()
                    self.director = self.director.replace("\n", "").strip()
                elif key == "Release Date (Theaters)" and beseda != "":
                    self.release_date = beseda.text.strip().replace("Wide", "")
                    self.release_date = self.release_date.strip().replace("Original", "")
                    self.release_date = self.release_date[:-1]
                elif key == "Distributor" and beseda != "":
                    self.dist = beseda.text.strip()
                    self.dist = ', '.join([d.strip() for d in self.dist.split('\n') if d.strip()]) # Iz seznama distributorjev odstrani vse whitespace in jih zdruzi v string

        def extract_score(slot_name): # Iz rotten tomato spletne strani pobere oceno občinstcva in kritikov.
            rt = soup.find('rt-button', attrs={'slot': slot_name})
            if rt:
                rt_text = rt.find('rt-text')
                if rt_text:
                    return str(rt_text.text.strip())
                    
            return "N/A"

        self.aud_score = extract_score('audienceScore')
        self.crit_score = extract_score('criticsScore')



    def save_to_csv(self): # Shranim v csv
        if not self.film_data:
            print("No data to save")
            return
        
        df = pd.DataFrame(self.film_data)
        df.to_csv('movie_data.csv', index=False)

f = Film()
for i in range(0, 101*num_of_pages, 101): 
    f.get_data_numbers(str(i))
f.save_to_csv()