# Import libraries
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import numpy as np

# Load the CSV
data = pd.read_csv("data_test1.csv")

# Preprocess the release date
data['Release Date'] = pd.to_datetime(data['Release Date'], format='%b %d, %Y')

# Extract year and month features
data['Year'] = data['Release Date'].dt.year
data['Month'] = data['Release Date'].dt.month

# Convert release date into a numerical trend (months since the first release)
data['Months Since Start'] = (data['Year'] - data['Year'].min()) * 12 + data['Month']

# Handle missing or empty Passive Skills
data['Passive Skill'] = data['Passive Skill'].fillna("No Passive Skill")  # Replace NaN with placeholder
data.loc[data['Passive Skill'].str.strip() == "", 'Passive Skill'] = "No Passive Skill"  # Handle empty strings

# Encode Passive Skill using TF-IDF
vectorizer = TfidfVectorizer(max_features=100)  # Adjust max_features for more detail
passive_skill_features = vectorizer.fit_transform(data['Passive Skill']).toarray()

# Combine features
X = pd.DataFrame(passive_skill_features)
X.columns = X.columns.astype(str)  # Convert all column names to strings
X['Months Since Start'] = data['Months Since Start']

# Set target variable
y = passive_skill_features  # Predict the skill vector itself

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict future passive skills
def predict_passive_skill(year, month, vectorizer, model, data):
    # Calculate months since start
    months_since_start = (year - data['Year'].min()) * 12 + month

    # Create input feature for the date
    future_features = np.zeros((1, vectorizer.max_features + 1))  # 1 row with zeros
    future_features[0, -1] = months_since_start  # Add months since start to the last column

    # Predict the skill vector
    predicted_vector = model.predict(future_features)

    # Decode skill from vector (optional)
    skill_words = vectorizer.inverse_transform(predicted_vector)
    return " ".join(skill_words[0]) if skill_words else "Unknown skill"

# Example prediction for May 2025
predicted_skill = predict_passive_skill(2025, 5, vectorizer, model, data)
print(f"Predicted Passive Skill for May 2025: {predicted_skill}")
