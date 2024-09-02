import main as m

f = m.Filmi()
for i in range(0, 101*set.NUMBER_OF_PAGES, 101): 
    f.get_data_numbers(str(i))
f.save_to_csv()