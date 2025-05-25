import pandas as pd
import os
import zipfile
import requests
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

os.makedirs("plots", exist_ok=True)


# url = "https://archive.ics.uci.edu/static/public/858/rocket+league+skillshots.zip"
# print("Downloading dataset...")
# response = requests.get(url)
# with zipfile.ZipFile(BytesIO(response.content)) as z:
#     z.extractall("rl_data")

csv_path = "rl_data/rocket_league_skillshots.data"
df = pd.read_csv(csv_path, delimiter=r"\s+")
df.dropna(inplace=True)

print("Columns:", df.columns.tolist())

print("\nClass balance (goal):")
print(df["goal"].value_counts())


plt.figure(figsize=(6, 4))
sns.countplot(x="goal", data=df)
plt.title("Кількість ударів по воротах (goal vs. no goal)")
plt.savefig("plots/class_balance.png")
plt.close()

plt.figure(figsize=(12, 10))
sns.heatmap(df.corr(), annot=True, fmt=".2f", cmap="coolwarm")
plt.title("Матриця кореляції")
plt.tight_layout()
plt.savefig("plots/correlation_matrix.png")
plt.close()

for col in df.columns[:6]:
    plt.figure(figsize=(6, 4))
    sns.histplot(data=df, x=col, hue="goal", kde=True, bins=30)
    plt.title(f"Розподіл ознаки '{col}' за goal")
    plt.tight_layout()
    plt.savefig(f"plots/distribution_{col}.png")
    plt.close()

X = df.drop(columns=["goal"])
y = df["goal"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)
preds = model.predict(X_test)

print("\nClassification Report:")
print(classification_report(y_test, preds))

conf = confusion_matrix(y_test, preds)
plt.figure(figsize=(5, 4))
sns.heatmap(conf, annot=True, fmt="d", cmap="Blues")
plt.title("Матриця помилок")
plt.xlabel("Предикція")
plt.ylabel("Факт")
plt.tight_layout()
plt.savefig("plots/confusion_matrix.png")
plt.close()

feat_imp = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)
print("\nFeature Importance:")
print(feat_imp)

plt.figure(figsize=(8, 5))
sns.barplot(x=feat_imp.values, y=feat_imp.index)
plt.title("Важливість ознак (RandomForest)")
plt.tight_layout()
plt.savefig("plots/feature_importance.png")
plt.close()
