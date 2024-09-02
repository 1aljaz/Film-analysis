# Graf
import matplotlib.pyplot as plt
import pandas as pd

def graf(filmi):

    filmi['Numerično ocena občinstva'] = pd.to_numeric(filmi['Ocena občinstva'].astype(str).str.rstrip('%'), errors='coerce')
    filmi['Numerično zaslužek'] = pd.to_numeric(filmi['Zaslužek'].str.replace('[$,]', '', regex=True), errors='coerce')

    filmi_clean = filmi.dropna(subset=['Numerično ocena občinstva', 'Numerično zaslužek'])

    # Ustvari scatter plot
    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(filmi_clean['Numerično ocena občinstva'], filmi_clean['Numerično zaslužek'], alpha=0.5)
    plt.yscale('log')

    plt.title('Ocena občinstva vs Zaslužek')
    plt.xlabel('Ocena občinstva')
    plt.ylabel('Zaslužek ($)')

    #Formatira ordinatno os
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

    plt.tight_layout()
    plt.show()

    correlation = filmi_clean['Numerično ocena občinstva'].corr(filmi_clean['Numerično zaslužek'])
    print(f"Koleracija med oceno občinstva in zaslužkom {correlation:.2f}")

    print("\nStatistics:")
    print(filmi_clean[['Numerično ocena občinstva', 'Numerično zaslužek']].describe())

    print(f"\nŠtevilo filmov, ki so bili uporabljeni v analizi: {len(filmi_clean)}")

# Razpredelnica studijev in zasluzkov
def studijo(filmi):
    filmi['Numerično ocena občinstva'] = pd.to_numeric(filmi['Ocena občinstva'].astype(str).str.rstrip('%'), errors='coerce')
    filmi['Numerično ocena kritikov'] = pd.to_numeric(filmi['Ocena kritikov'].astype(str).str.rstrip('%'), errors='coerce')

    distributor_groups = filmi.groupby('Studio').agg({
        'Naslov': 'count',
        'Zaslužek': lambda x: pd.to_numeric(x.astype(str).str.replace('[$,]', '', regex=True), errors='coerce').sum(),
        'Numerično ocena občinstva': 'mean',
        'Numerično ocena kritikov': 'mean'
    }).sort_values('Zaslužek', ascending=False)

    distributor_groups = distributor_groups.rename(columns={
        'Naslov': 'Število filmov',
        'Zaslužek': 'Total zaslužek',
        'Numerično ocena občinstva': 'Povprečna ocena občinstva',
        'Numerično ocena kritikov': 'Povprečna ocena kritikov'
    })

    distributor_groups['Total zaslužek'] = distributor_groups['Total zaslužek'].apply(lambda x: f'${x:,.0f}')

    distributor_groups['Povprečna ocena občinstva'] = distributor_groups['Povprečna ocena občinstva'].apply(lambda x: f'{x:.1f}%' if pd.notnull(x) else 'N/A')
    distributor_groups['Povprečna ocena kritikov'] = distributor_groups['Povprečna ocena kritikov'].apply(lambda x: f'{x:.1f}%' if pd.notnull(x) else 'N/A')

    return distributor_groups


__all__ = ['graf', 'studijo']