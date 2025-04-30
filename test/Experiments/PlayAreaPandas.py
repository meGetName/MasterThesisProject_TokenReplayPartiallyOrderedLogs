import pandas as pd
from datetime import datetime

data = pd.read_csv("Example.csv")

print(data.head())

now = datetime.now()
print(now)

