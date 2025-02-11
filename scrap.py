import time
from bs4 import BeautifulSoup
import requests
import pandas as pd
import streamlit as st
import setup
from data.data import kelas_list

URL = "https://akademik.its.ac.id/list_frs.php"
lecturer_list = pd.DataFrame(kelas_list)

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

    otherrows = soup.find_all('table', class_='GridStyle')
    matkul_terambil = otherrows[0].find_all('tr', valign='top')

    dataMKsendiri = {'kode': [], 'nama_mk': [], 'sks': [], 'kelas': [], 'alih_kredit': []}

    for matkul in matkul_terambil:
        raw = [td.text for td in matkul.find_all('td')]
        dataMKsendiri['kode'].append(raw[0])
        dataMKsendiri['nama_mk'].append(raw[1])
        dataMKsendiri['sks'].append(raw[2])
        dataMKsendiri['kelas'].append(raw[3])
        dataMKsendiri['alih_kredit'].append(raw[4])

    dataMKsendiri = pd.DataFrame(dataMKsendiri)

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
except Exception as e:
    print(e)
    mksem4 = pd.DataFrame(columns=['Kode', 'Nama MK', 'Kelas', 'Ketersediaan', 'Status'])
    dataMK = pd.DataFrame(columns=['Kode', 'Nama MK', 'Kelas', 'Ketersediaan', 'Status'])
    siakad_time = "Error"


# Display data
st.header("FRS Mata Kuliah Semester 4")
st.write("Siakad Time: " + siakad_time)

tab1, tab2, tab3 = st.tabs(["Available" ,"Semester 4 Courses", "All Courses"])

with tab1:
    courses = mksem4['Nama MK'].unique()
    for course in courses:
        st.write(course)
        st.table(mksem4[(mksem4['Nama MK'] == course) & (mksem4['Status'] == 'Tersedia')])

with tab2:
    selected_course = st.selectbox("Select Course", mksem4['Nama MK'].unique())
    st.table(mksem4[mksem4['Nama MK'] == selected_course])
    
with tab3:
    selected_course_all = st.selectbox("Select Course", dataMK['Nama MK'].unique())
    st.table(dataMK[dataMK['Nama MK'] == selected_course_all])

time.sleep(setup.RELOAD_WAIT_TIME)
st.rerun()
