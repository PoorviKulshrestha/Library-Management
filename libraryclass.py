from collections import Counter
from pymongo import MongoClient
from datetime import datetime, timedelta

client = MongoClient("mongodb://localhost:27017/")
db = client["library_db"]
books_col = db["books"]
trans_col = db["transactions"]

class Library:
    def __init__(self):
        
        if books_col.count_documents({}) == 0:
            initial_books = [
                {"title": "Harry Potter",               "count": 25},
                {"title": "Godan",                      "count": 13},
                {"title": "Around the world in 80 days", "count": 4},
                {"title": "Gaban",                      "count": 12},
                {"title": "Wings of fire",              "count": 16},
                {"title": "Atomic Habits",              "count": 13},
                {"title": "Rangbhoomi",                 "count": 12},
                {"title": "Jujutsu Kaisen",             "count": 4},
                {"title": "Animal Farm",                "count": 5},
                {"title": "Ikigai",                     "count": 12},
                {"title": "1984",                       "count": 14},
                {"title": "Merchant of Venice",         "count": 12},
                {"title": "Metamorphosis",              "count": 3},
                {"title": "The Alchemist",              "count": 4},
                {"title": "Autobiography of a Yogi",    "count": 12},
                {"title": "Source code",                "count": 11},
                {"title": "The courage to be disliked", "count": 3},
                {"title": "Rich Dad Poor Dad",          "count": 15},
            ]
            start_id = 1001
            books_col.insert_many([
                {
                    "book_id": f"{start_id + i}",
                    "title": b["title"],
                    "total_count": b["count"],
                    "available_count": b["count"],
                    "view_count": 0
                }
                for i, b in enumerate(initial_books)
            ])

    
    def display(self):
        print("\nBooks in Library:")
        for doc in books_col.find().sort("book_id", 1):
            print(
                f"ID: {doc.get('book_id')} | {doc.get('title')} | "
                f"Total: {doc.get('total_count')} | "
                f"Available: {doc.get('available_count')} | "
                f"Views: {doc.get('view_count', 0)}"
            )
        print()

    
    def view_book(self):
        book_id = input("Enter the 4-digit Book-ID you want to view: ").strip()
        book = books_col.find_one({"book_id": book_id})
        if book:
            books_col.update_one({"book_id": book_id}, {"$inc": {"view_count": 1}})

            if book["available_count"] > 0:
                b = input("Do you want to borrow this book? Enter 1 to borrow, 2 otherwise: ")
                if b.strip() == "1":
                    self.borrow_book(book_id)
                else:
                    print("Book not issued.\n")
            else:
                print("All copies currently borrowed.\n")
        else:
            print("Book ID not found.\n")

    
    def count_views(self):
        choice = input("Press 1 for ascending order or 2 for descending: ").strip()
        order = 1 if choice == "1" else -1
        print("\nBook Views:")
        for doc in books_col.find().sort("view_count", order):
            print(f"{doc['title']} -> {doc.get('view_count',0)} views")
        print()

    
    def borrow_book(self, book_id):
        name = input("Enter your name: ").strip()
        uid = input("Enter your unique 6-digit library ID: ").strip()
        phone = input("Enter your phone number: ").strip()
        email = input("Enter your email address: ").strip()

        res = books_col.update_one(
            {"book_id": book_id, "available_count": {"$gt": 0}},
            {"$inc": {"available_count": -1}}
        )
        if res.modified_count:
            book = books_col.find_one({"book_id": book_id})

            borrow_date = datetime.utcnow()
            due_date = borrow_date + timedelta(days=30)

            trans_col.insert_one({
                "user": name,
                "library_id": uid,
                "phone": phone,
                "email": email,
                "book_id": book_id,
                "title": book["title"],
                "action": "borrow",
                "borrow_date": borrow_date,
                "due_date": due_date
            })
            print(f"You have borrowed '{book['title']}'. Return within 30 days.\n")
        else:
            print("Requested book not available or wrong ID.\n")

    
    def return_book(self, book_id):
        name = input("Enter your name: ").strip()
        uid = input("Enter your unique 6-digit library ID (must match borrow ID): ").strip()

        borrow_record = trans_col.find_one(
            {
                "book_id": book_id,
                "user": name,
                "action": "borrow",
                "library_id": uid
            },
            sort=[("_id", -1)]
        )
        if not borrow_record:
            print("\nNo matching borrow record found for this Book-ID and User-ID.")
            return

        now = datetime.utcnow()
        due_date = borrow_record.get("due_date")
        overdue_days = 0
        if due_date and now > due_date:
            overdue_days = (now - due_date).days
            print(f"Overdue by {overdue_days} day(s).")

        phone = borrow_record.get("phone")
        email = borrow_record.get("email")
        books_col.update_one({"book_id": book_id}, {"$inc": {"available_count": 1}})
        trans_col.insert_one({
            "user": name,
            "library_id": uid,
            "phone": phone,
            "email": email,
            "book_id": book_id,
            "title": borrow_record["title"],
            "action": "return",
            "return_date": now,
            "overdue_days": overdue_days
        })
        print(f"Thank you for returning '{borrow_record['title']}'.\n")

    
    def sort_books(self):
        choice = input("Enter 1 to sort ascending or 2 descending: ").strip()
        order = 1 if choice == "1" else -1
        print("\nBooks in ascending order:" if order == 1 else "\nBooks in descending order:")
        for doc in books_col.find().sort("title", order):
            status = (
                f"{doc['available_count']} of {doc['total_count']} available, "
                f"{doc.get('view_count',0)} views"
            )
            print(f"ID: {doc['book_id']} | {doc['title']} ({status})")
        print()


    def donate_book(self):
        donor = input("Enter your name: ").strip()
        donor_id = input("Enter your 6-digit Library ID: ").strip()
        new_title = input("Enter the title of the book you wish to donate: ").strip()

        existing = books_col.find_one({"title": new_title})
        if existing:
            books_col.update_one(
                {"title": new_title},
                {"$inc": {"total_count": 1, "available_count": 1}}
            )
            new_id = existing["book_id"]
        else:
            last_book = books_col.find_one(sort=[("book_id", -1)])
            next_id = 1001 if not last_book else int(last_book["book_id"]) + 1
            books_col.insert_one({
                "book_id": f"{next_id}",
                "title": new_title,
                "total_count": 1,
                "available_count": 1,
                "view_count": 0
            })
            new_id = f"{next_id}"

        trans_col.insert_one({
            "user": donor,
            "library_id": donor_id,
            "book_id": new_id,
            "title": new_title,
            "action": "donate",
        })
        print(f"Thank you {donor}! '{new_title}' added. Book-ID: {new_id}\n")
