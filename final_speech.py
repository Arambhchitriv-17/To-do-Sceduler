import time
import speech_recognition as sr
import pyttsx3
import parsedatetime
from datetime import datetime, timedelta
from threading import Timer  # Add this line


# Initialize Text-to-Speech Engine
engine = pyttsx3.init()

def speak(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

class ToDoList:
    def __init__(self):
        self.tasks = []
        self.cal = parsedatetime.Calendar()

    def add_task(self, task, reminder_time=None):
        """Add a new task to the to-do list with an optional reminder."""
        self.tasks.append({"task": task, "completed": False, "reminder_time": reminder_time})
        speak(f'Task "{task}" added successfully!')
        print(f'Task "{task}" added successfully!')

        if reminder_time:
            delay = self.calculate_delay(reminder_time)
            if delay > 0:
                speak(f"Reminder scheduled for task '{task}' in {delay:.2f} seconds.")
                print(f"Reminder scheduled for task '{task}' in {delay:.2f} seconds.")
                Timer(delay, self.remind_task, [task]).start()
            else:
                speak(f"Reminder time for task '{task}' is invalid or in the past.")
                print(f"Reminder time for task '{task}' is invalid or in the past.")

    def calculate_delay(self, reminder_time):
        try:
            reminder_timestamp = time.mktime(reminder_time.timetuple())
            current_timestamp = time.time()
            return reminder_timestamp - current_timestamp
        except Exception as e:
            print(f"Error calculating delay: {e}")
            return -1

    def remind_task(self, task):
        """Send a reminder about a task."""
        speak(f"\nReminder: It's time to complete the task: {task}")
        print(f"\nReminder: It's time to complete the task: {task}")

    def view_tasks(self):
        """Display all tasks in the to-do list."""
        if not self.tasks:
            speak("Your to-do list is empty.")
            print("Your to-do list is empty.")
        else:
            speak("\nTo-Do List:")
            print("\nTo-Do List:")
            for index, task in enumerate(self.tasks, start=1):
                status = "[X]" if task["completed"] else "[ ]"
                reminder = f' (Reminder: {task["reminder_time"]})' if task["reminder_time"] else ""
                print(f'{index}. {status} {task["task"]}{reminder}')

    def mark_completed(self, task_number):
        """Mark a task as completed."""
        if 0 < task_number <= len(self.tasks):
            self.tasks[task_number - 1]["completed"] = True
            speak(f'Task {task_number} marked as completed!')
            print(f'Task {task_number} marked as completed!')
        else:
            speak("Invalid task number.")
            print("Invalid task number.")

    def delete_task(self, task_number):
        """Delete a task from the to-do list."""
        if 0 < task_number <= len(self.tasks):
            removed_task = self.tasks.pop(task_number - 1)
            speak(f'Task "{removed_task["task"]}" deleted successfully!')
            print(f'Task "{removed_task["task"]}" deleted successfully!')
        else:
            speak("Invalid task number.")
            print("Invalid task number.")

    def listen_for_command(self):
        """Listen for a voice command from the user and process it."""
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening for a command...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
            try:
                # Recognize the speech using Google Speech Recognition
                command = recognizer.recognize_google(audio)
                print(f"You said: {command}")
                return command.lower()  # Normalize command to lowercase
            except sr.UnknownValueError:
                speak("Sorry, I didn't catch that.")
                print("Sorry, I didn't catch that.")
                return None
            except sr.RequestError:
                speak("Could not request results from speech recognition service.")
                print("Could not request results from speech recognition service.")
                return None

    def process_task_command(self, command):
        """Process the command to determine if it includes a task."""
        if "task" in command or "schedule" in command:
            task_start = command.find("task") + 5 if "task" in command else command.find("schedule") + 9
            task_end = command.find("reminder") if "reminder" in command else len(command)
            task = command[task_start:task_end].strip()
            reminder_time = None

            # Check if reminder time is specified in the command, e.g., "after 5 minutes"
            reminder_start = command.find("after")
            if reminder_start != -1:
                time_phrase = command[reminder_start + len("after"):].strip()  # e.g., "5 minutes"
                time_struct, parsed = self.cal.parse(time_phrase)
                if parsed:
                    reminder_time = datetime.fromtimestamp(time.mktime(time_struct))
                    speak(f"Reminder set for {reminder_time}")
                else:
                    speak("Sorry, I couldn't understand the reminder time.")

            self.add_task(task, reminder_time)
            return True
        return False

    def process_reminder_query(self, command):
        """Handle queries related to reminders."""
        if "reminder" in command or "show me reminders" in command or "what reminders" in command:
            speak("Here are your reminders:")
            print("Here are your reminders:")
            reminders = [task for task in self.tasks if task["reminder_time"]]
            if reminders:
                for index, task in enumerate(reminders, start=1):
                    print(f"{index}. {task['task']} - Reminder at {task['reminder_time']}")
                    speak(f"{task['task']} at {task['reminder_time']}")
            else:
                speak("You have no reminders set.")
                print("You have no reminders set.")
            return True
        return False

def main():
    todo_list = ToDoList()

    speak("Welcome to your to-do list manager.")
    
    while True:
        # Display available commands
        print("\nAvailable Commands:")
        print("- Add task [task name] with optional reminder")
        print("- View tasks")
        print("- Mark completed [task number]")
        print("- Delete task [task number]")
        print("- Query reminders")
        print("- Exit")
        
        speak("\nListening for commands...")
        command = todo_list.listen_for_command()

        if command:
            if todo_list.process_task_command(command):
                speak("Task added successfully!")
            elif todo_list.process_reminder_query(command):
                pass  # Handled reminder query
            elif "view tasks" in command:
                todo_list.view_tasks()
            elif "mark completed" in command:
                speak("Please say the task number to mark as completed.")
                task_number = todo_list.listen_for_command()
                if task_number:
                    try:
                        task_number = int(task_number)
                        todo_list.mark_completed(task_number)
                    except ValueError:
                        speak("That's not a valid task number.")
                        print("That's not a valid task number.")
            elif "delete task" in command:
                speak("Please say the task number to delete.")
                task_number = todo_list.listen_for_command()
                if task_number:
                    try:
                        task_number = int(task_number)
                        todo_list.delete_task(task_number)
                    except ValueError:
                        speak("That's not a valid task number.")
                        print("That's not a valid task number.")
            elif "exit" in command:
                speak("Goodbye!")
                print("Goodbye!")
                break
            else:
                speak("Sorry, I didn't understand that command.")
                print("Sorry, I didn't understand that command.")

if __name__ == "__main__":
    main()
