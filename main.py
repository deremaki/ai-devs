from dotenv import load_dotenv
from s01e02.s01e02 import run_verification

if __name__ == "__main__":
    load_dotenv()
     
    result = run_verification()
   
    if result is None:
        print("❌ Verification failed.")
    else:
        print(f"🎉 Verification success. Robot says:\n\n{result}")