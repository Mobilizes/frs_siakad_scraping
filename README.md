## How To Use?

1. Clone to your local machine
    ```
    git clone https://github.com/kev1nandreas/frs_siakad_scraping
    ```

2. Go to the project directory
    ```
    cd frs_siakad_scraping
    ```

2. Install all library dependencies
    ```
    pip install -r requirements.txt
    ```

3. Set up following variables in `setup.example.py` then rename the file to `setup.py`
    ```ruby
    SESSION_COOKIE = 'YOUR_SESSION_COOKIE'
    RELOAD_WAIT_TIME = 10
    ```

4. Run Streamlit (if u want to use streamlit app)
    ```
    streamlit run scrap.py
    ```
