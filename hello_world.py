import random

def greet_user():
    name = input("What's your name? ").strip()
    if name:
        print(f"Hello, {name}! 👋")
    else:
        print("Hello, mysterious stranger! 😊")
    
    # Some fun logic
    mood = random.choice(["awesome", "fantastic", "great", "wonderful"])
    print(f"You're looking {mood} today!")
    
    # Simple calculation
    year = 2026
    birth_year = int(input("What year were you born? "))
    age = year - birth_year
    print(f"That makes you {age} years old in {year}!")

if __name__ == "__main__":
    greet_user()