import time
from bs4 import BeautifulSoup
import requests
import pandas as pd
import streamlit as st
import setup

URL = "https://akademik.its.ac.id/list_frs.php"

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
dataMK = {'Kode': [], 'Nama MK': [], 'Kelas': [], 'Ketersediaan': [], 'Status': []}

# Insert data to dataframe
for matkul in matkul_depart:
    raw = matkul.text.split()
    dataMK['Kode'].append(raw[0])
    dataMK['Nama MK'].append(' '.join(raw[1:-2]))
    dataMK['Kelas'].append(raw[-2])
    dataMK['Ketersediaan'].append(raw[-1])
    
    status = raw[-1].split('/')
    if status[0] < status[1]:
        dataMK['Status'].append('Tersedia')
    else:
        dataMK['Status'].append('Penuh')

# Convert list to dataframe
dataMK = pd.DataFrame(dataMK)

# Data matakuliah sem 4
courses = [
    "Pemrograman Jaringan",
    "Probabilitas dan Statistika",
    "Otomata",
    "Manajemen Basis Data",
    "Perancangan dan Analisis Algoritma",
    "Pembelajaran Mesin",
    "Perancangan Perangkat Lunak"
]

# Filtering data
pattern = '|'.join(courses)
mksem4 = dataMK[dataMK['Nama MK'].str.contains(pattern)].reset_index(drop=True)


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