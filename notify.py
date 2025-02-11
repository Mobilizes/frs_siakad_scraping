import time
from bs4 import BeautifulSoup
import requests
import pandas as pd
import setup
import pywhatkit
from data.data import kelas_list

URL = "https://akademik.its.ac.id/list_frs.php"

counter = 0
lecturer_list = pd.DataFrame(kelas_list)
old_mksem4 = pd.DataFrame(columns=['Kode', 'Nama MK', 'Kelas', 'Ketersediaan', 'Status', 'Kode Dosen'])

while True:
    try:
        # Use login credential
        session = requests.Session()
        session.cookies.setdefault('PHPSESSID', setup.SESSION_COOKIE)

        # Get HTML data
        response = session.get(URL)
        print('Status code:', response.status_code)
        soup = BeautifulSoup(response.text, 'lxml')

        # Get SiAkad Real Time
        form = soup.find_all('form')
        tr = form[0].find_all('tr')
        siakad_time = tr[1].find_all('td')[0].text.split('Tanggal: ')[1]

        # Select data mata kuliah
        rows = soup.find_all('table', class_='FilterBox')
        data = rows[1].find_all('tr')
        td_matkul = data[0].find_all('td')
        matkul_depart = td_matkul[2].find_all('option')

        # Create list for dataframe
        dataMK = {'Kode': [], 'Nama MK': [], 'Kelas': [], 'Ketersediaan': [], 'Status': [], 'Kode Dosen': []}

        # Insert data to dataframe
        for matkul in matkul_depart:
            raw = matkul.text.split()
            dataMK['Kode'].append(raw[0])
            dataMK['Nama MK'].append(' '.join(raw[1:-2]))
            dataMK['Kelas'].append(raw[-2])
            dataMK['Ketersediaan'].append(raw[-1])
            
            kode_dosen = lecturer_list[(lecturer_list['nama_mata_kuliah'] == ' '.join(raw[1:-2])) & (lecturer_list['kelas'] == raw[-2])]['kode_dosen'].values
            if len(kode_dosen) > 0:
                dataMK['Kode Dosen'].append(kode_dosen[0])
            else:
                dataMK['Kode Dosen'].append('-')
            
            status = raw[-1].split('/')
            if int(status[0]) < int(status[1]):
                dataMK['Status'].append('Tersedia')
            else:
                dataMK['Status'].append('Penuh')

        # Convert list to dataframe
        dataMK = pd.DataFrame(dataMK)

        # Data matakuliah sem 4
        courses = [
            "Pemrograman Jaringan",
            "Probabilitas dan Statistik",
            "Otomata",
            "Manajemen Basis Data",
            "Perancangan dan Analisis Algoritma",
            "Pembelajaran Mesin",
            "Perancangan Perangkat Lunak"
        ]

        # Filtering data
        pattern = '|'.join(courses)
        mksem4 = dataMK[dataMK['Nama MK'].str.contains(pattern)].reset_index(drop=True)
        
        # Looking for changes
        num_mk = int(mksem4.shape[0])
        changes = ['Perubahan pada mata kuliah semester 4:']
            
        if counter == 0:
            old_mksem4 = mksem4
        else:
            for i in range(0, num_mk):
                if mksem4['Ketersediaan'][i] != old_mksem4['Ketersediaan'][i]:
                    matkul_changed = f"{mksem4['Nama MK'][i]} {mksem4['Kelas'][i]} {mksem4['Ketersediaan'][i]} {mksem4['Kode Dosen'][i]}"
                    changes.append(matkul_changed)
                    print(matkul_changed)

        # Send notification to WhatsApp
        if len(changes) > 1:
            msg = '\n'.join(changes)
            pywhatkit.sendwhatmsg_instantly(setup.PHONE_NUMBER, msg, wait_time=10, tab_close=True)
            # pywhatkit.sendwhatmsg_to_group_instantly(setup.GROUP_ID, msg, wait_time=10, tab_close=True)
    except Exception as e:
        print(e)
    
    # Wait for desired minutes
    time.sleep(setup.RELOAD_WAIT_TIME)
    old_mksem4 = mksem4
    counter += 1