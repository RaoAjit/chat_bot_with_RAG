import time
from database import SessionLocal
from models import User


def watch_database(refresh_time=5):
    while True:
        db = SessionLocal()

        print("\n================ DATABASE SNAPSHOT ================\n")

        users = db.query(User).all()

        for user in users:
            print(f"👤 USER → ID: {user.id} | Email: {user.email}")

            for session in user.sessions:
                print(f"   💬 SESSION → UUID: {session.session_uuid} | Title: {session.title}")

                for msg in session.messages:
                    print(f"      🗨️ {msg.sender.upper()} : {msg.message}")

        db.close()

        print("\n🔄 Refreshing...\n")
        time.sleep(refresh_time)


if __name__ == "__main__":
    watch_database()
