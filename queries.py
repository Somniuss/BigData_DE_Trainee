from pymongo import MongoClient
from pprint import pprint
from datetime import datetime
from collections import Counter

# ------------------------------
# Настройка подключения к MongoDB
# ------------------------------
MONGO_URI = "mongodb://localhost:27017"  # адрес MongoDB
DB_NAME = "airflow"
COLLECTION_NAME = "processed_comments"

print("Connecting to MongoDB...")
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]
print("Connected to database:", DB_NAME)
print("Collection to use:", COLLECTION_NAME)
print("="*50, "\n")

# ------------------------------
# 1. Топ 5 самых часто встречающихся комментариев
# ------------------------------
print("Step 1: Top 5 frequently occurring comments\n")

# Извлекаем все комментарии
all_comments = [doc.get("content", "") for doc in collection.find()]
print("Total comments fetched:", len(all_comments))

# Считаем, как часто встречается каждый комментарий
counter = Counter(all_comments)
top5 = counter.most_common(5)

print("Top 5 comments:")
for i, (comment, count) in enumerate(top5, 1):
    print(f"{i}. '{comment}' - {count} times")
print("="*50, "\n")

# ------------------------------
# 2. Все записи, где поле content меньше 5 символов
# ------------------------------
print("Step 2: Comments with content < 5 characters\n")

short_comments = []
for doc in collection.find({"content": {"$exists": True}}):
    content = doc.get("content", "")
    if len(content) < 5:
        short_comments.append(doc)

print(f"Total comments with length < 5: {len(short_comments)}")
print("Sample entries:")
for doc in short_comments:
    pprint(doc)
print("="*50, "\n")

# ------------------------------
# 3. Средний рейтинг за каждый день
# ------------------------------
print("Step 3: Average rating per day\n")

# Пайплайн агрегации для группировки по дате
pipeline = [
    {
        "$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": {"$toDate": "$created_date"}}},
            "average_rating": {"$avg": "$rating"},
            "count": {"$sum": 1}  # сколько записей в этот день
        }
    },
    {"$sort": {"_id": 1}}
]

agg_results = list(collection.aggregate(pipeline))
print(f"Total days with ratings: {len(agg_results)}")
for doc in agg_results:
    print(f"Date: {doc['_id']}, Average rating: {doc['average_rating']:.2f}, Entries: {doc['count']}")
print("="*50, "\n")

print("All steps completed successfully!")
