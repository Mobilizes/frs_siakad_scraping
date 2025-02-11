import time
from bs4 import BeautifulSoup
import requests
import pandas as pd
import streamlit as st

URL = "https://akademik.its.ac.id/list_frs.php"
SESSION_COOKIE = "kvds2aclksbtstn3h8eha3tov1"

# Use login credential
session = requests.Session()
session.cookies.setdefault('PHPSESSID', SESSION_COOKIE)

# Get HTML data
response = session.get(URL)
print('Status code:', response.status_code)
soup = BeautifulSoup(response.text, 'lxml')

# Select data mata kuliah
rows = soup.find_all('table', class_='FilterBox')
data = rows[1].find_all('tr')
td_matkul = data[0].find_all('td')
matkul_depart = td_matkul[2].find_all('option')

# Create list for dataframe
dataMK = {'kode': [], 'nama_mk': [], 'kelas': [], 'ketersediaan': []}

# Insert data to dataframe
for matkul in matkul_depart:
    raw = matkul.text.split()
    dataMK['kode'].append(raw[0])
    dataMK['nama_mk'].append(' '.join(raw[1:-2]))
    dataMK['kelas'].append(raw[-2])
    dataMK['ketersediaan'].append(raw[-1])

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
mksem4 = dataMK[dataMK['nama_mk'].str.contains(pattern)].reset_index(drop=True)


# Display data
st.header("FRS Mata Kuliah Semester 4")

tab1, tab2 = st.tabs(["Semester 4 Courses", "All Courses"])

with tab1:
    selected_course = st.selectbox("Select Course", mksem4['nama_mk'].unique())
    st.table(mksem4[mksem4['nama_mk'] == selected_course])
    
with tab2:
    selected_course_all = st.selectbox("Select Course", dataMK['nama_mk'].unique())
    st.table(dataMK[dataMK['nama_mk'] == selected_course_all])