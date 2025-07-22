from datetime import datetime

gradient_text_html = """
    <style>
    .gradient-text{
        background: linear-gradient(74deg,#4285f4 0,#9b72cb 9%,#d96570 20%,#d96570 24%,#9b72cb 35%,#4285f4 44%,#9b72cb 50%,#d96570 56%,#131314 75%,#131314 100%);
        -webkit-background-clip: text;
        color: transparent;
        font-size: 3.5rem;
        font-weight: 900;
        margin-bottom:0px;
    }
    </style>

    <div class="gradient-text">
    NeuroNote
    </div>
    """

def get_greeting():
    """
    Returns a greeting message based on the current time of day.

    The function checks the current system time and returns an appropriate 
    greeting message:
        - "Good morning!" for 5:00 AM to 11:59 AM
        - "Good afternoon!" for 12:00 PM to 4:59 PM
        - "Good evening!" for 5:00 PM to 8:59 PM
        - "Good night!" for 9:00 PM to 4:59 AM

    Returns:
        str: A greeting message appropriate for the current time.
    """
    current_hour = datetime.now().hour

    if 5 <= current_hour < 12:
        return "Good morning!"
    elif 12 <= current_hour < 17:
        return "Good afternoon!"
    elif 17 <= current_hour < 21:
        return "Good evening!"
    else:
        return "Good night!"