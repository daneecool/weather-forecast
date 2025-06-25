import pandas as pd
from scipy.stats import chi2_contingency

# Load your Excel file
df = pd.read_excel("typhoon_predict_pacific_ocean.xlsx")  # Change filename as needed

# Create a contingency table (e.g., region vs weather_main)
contingency_table = pd.crosstab(df["wind_gust"], df["wind_speed"])

# Perform chi-squared test
chi2, p, dof, expected = chi2_contingency(contingency_table)

print("Chi2 statistic:", chi2)
print("p-value:", p)
print("Degrees of freedom:", dof)
print("Expected frequencies:\n", expected)