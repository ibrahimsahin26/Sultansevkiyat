import pandas as pd
import os

def load_data(path):
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            return df
        except Exception as e:
            print(f"Veri yükleme hatası: {e}")
            return pd.DataFrame()
    else:
        return pd.DataFrame()

def save_data(df, path):
    try:
        df.to_csv(path, index=False)
    except Exception as e:
        print(f"Veri kaydetme hatası: {e}")
