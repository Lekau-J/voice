import speech_recognition as sr
import playsound
from gtts import gTTS
import MySQLdb
import uuid
import sys
import time

lang = 'en'

# Connect to MySQL database
db_connection = MySQLdb.connect(
    host="localhost",
    user="root",
    password="",
    database="bank"
)

def speak(text):
    tts = gTTS(text=text, lang=lang, slow=False)
    audio_file = f"response_{str(uuid.uuid4())}.mp3"
    tts.save(audio_file)
    playsound.playsound(audio_file, block=True)  # Wait for the audio to finish playing

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone(device_index=1) as source:
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
            print(said)
            return said.strip()

        except Exception as e:
            print("Sorry, I didn't catch that.")
            return ""

def authenticate_user():
    cursor = db_connection.cursor()

    speak("Welcome to the voice banking system.")
    speak("Please say your account number.")
    account_no = get_audio()

    speak("Please say your pin.")
    pin = get_audio()

    query = "SELECT * FROM bank_mock_data WHERE  pin = %s AND account_number = %s"
    cursor.execute(query, (pin, account_no))
    user = cursor.fetchone()

    if user:
        return user[0]   # Return user ID after successful authentication
    else:
        speak("Authentication failed. Please try again.")
        return None

# def select_transaction_type():
#     cursor = db_connection.cursor()

#     speak(f"Authentication successful. Hello, what can I help you with today")
#     help_void = get_audio()

#     if "transfer" in help_void.lower():
#         speak("Please say your account number again.")
#         account_no = get_audio()

#         speak(f"How much you want to transfer")
#         amount = get_audio()

#         speak("Please say the account number that you want to transfer to.")
#         transfer_account_no = get_audio()

#         cursor = db_connection.cursor()

#         # Assuming 'amount' and 'account_no' are already defined
#         amount = 100.0
#         account_no = "123456789"

#         # Execute the insert query
#         query = "INSERT INTO transfer (amount, account_no) VALUES (%s, %s);"
#         cursor.execute(query, (amount, account_no))

#         # Commit the transaction
#         db_connection.commit()

#         # Close cursor and database connection
#         cursor.close()
#         db_connection.close()

#     else:
#         speak("Please say your account number again.")
#         account_no = get_audio()

#         query = "SELECT * FROM client WHERE account_no = %s"
#         cursor.execute(query, (account_no))
#         user = cursor.fetchone()

#         amount = user[4]  # Assuming user is the result from the previous query
#         speak(f"The amount in your account is {amount} rand.")
#         return Pla

#     return None

def select_transaction_type(cursor):
    option_selected = None
    speak("Authentication successful. Hello, what can I help you with today?")
    help_void = get_audio()

    # key word is transfer
    if "transfer" in help_void.lower():
        speak("Please say your account number again.")
        account_no = get_audio()

        speak("Please select the type of transaction you would like to make by saying the option number.")
        time.sleep(1)  

        speak("Option 1. Balance inquiry")
        speak("Option 2. Transfer funds")
        speak("Option 3. Payment")

        option_selected = None
        while option_selected is None:
            user_response = get_audio().lower()

            if "1" in user_response or "balance" in user_response:
                option_selected = "balance inquiry"
            elif "2" in user_response or "transfer" in user_response:
                option_selected = "transfer funds"
            elif "3" in user_response or "payment" in user_response:
                option_selected = "payment"
            else:
                speak("I'm sorry, I didn't understand. Please select again.")

        speak(f"You have selected {option_selected}.")

        speak("How much would you like to transfer?")
        amount = get_audio()

        # Validate amount input (e.g., check if it's a valid number)

        speak("Please say the account number that you want to transfer to.")
        transfer_account_no = get_audio()

        # Validate transfer account number (e.g., check if it's a valid account number)

        try:
            cursor.execute("INSERT INTO transfer (amount, account_no, user_account_id) VALUES (%s, %s, %s);",
                           (amount, account_no, transfer_account_no))
            db_connection.commit()
            speak("The transfer was successful.")
        except Exception as e:
            db_connection.rollback()
            speak("An error occurred during the transfer. Please try again later.")

    else:
        speak("Please say your account number again.")
        account_no = get_audio()

        query = "SELECT * FROM client WHERE account_no = %s"
        cursor.execute(query, (account_no,))
        user = cursor.fetchone()

        if user:
            amount = user[4]  # Assuming user is the result from the previous query
            speak(f"The amount in your account is {amount} rand.")
        else:
            speak("Sorry, we couldn't find your account. Please check your account number and try again.")

    return option_selected


# Main program loop
while True:
    cursor = db_connection.cursor()  # Assuming db_connection is established somewhere in your code
    user_id = authenticate_user()
    if user_id is not None:
        selected_option = select_transaction_type(cursor)
        # Now you can implement logic based on the selected option
    cursor.close()
