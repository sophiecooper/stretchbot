import os
import time
from repeated_timer import RepeatedTimer
from random import randint, choice 
from time import sleep
from slackclient import SlackClient


# strechbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

#initiate timer
repeated_timer = None

# constants
AT_BOT = "<@" + BOT_ID + ">"
STRETCH_COMMAND = "stretch"
TIMER_COMMAND = "timer"
STOP_COMMAND = "stop"
STRETCHES = {"calf_stretch": "your calves by doing some toe raises.", 
	         "hip_stretch":  "your hips by doing a seated figure four stretch.", 
	         "ham_stretch":  "your hamstrings by doing a forward fold. Try to touch your toes!",
	         "neck_stretch": "your neck by looking to the left and right, then do some gentle neck rolls.",
	         "ob_stretch":   "your obliques by doing a side bend for 10 seconds on each side",
	         "wrist_strech": "your wrists and shoulders by interlacing your fingers with straight arms in front of you",
	         "back_stretch": "your back by doing a seated twist on each side", 
             "quad_stretch": "your quads by doing a standing quad stretch."
             }
IMAGES = {"calf_stretch": "https://goo.gl/Qk8beF",
          "hip_stretch": "https://goo.gl/71mVav",
          "ham_stretch": "https://goo.gl/rTIOJV",
          "neck_stretch": "https://goo.gl/92dq5z",
          "ob_stretch": "https://goo.gl/zMH6tt",
          "wrist_stretch": "goo.gl/Qk8beF",
          "back_stretch": "https://goo.gl/3lKlgl", 
          "quad_stretch": "https://goo.gl/vpvUgg"
          }

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


def handle_command(command, channel, repeated_timer):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "I'm not sure what you mean. Use the *" + STRETCH_COMMAND + \
               "* command for a random stretch, or the *" + TIMER_COMMAND + \
               "* command to get stretches on an interval."

    if command.startswith(STRETCH_COMMAND):
    	# stretch = STRETCHES[randint(0,len(STRETCHES)-1)]
        img_name, stretch = choice(list(STRETCHES.items()))
        img_attachment = [{"title": "Do this stretch!", 
                           "image_url": IMAGES[img_name]}]
        response = "Sure! Why don't you stretch " + stretch 
        slack_client.api_call("chat.postMessage", channel=channel,
                                              text=response, 
                                              as_user=True, 
                                              attachments=img_attachment)
    if command.startswith(TIMER_COMMAND):
        delay = 5
        response = "Okay! I will send you a new stretch every " + str(delay) + " minutes. Type 'stop' to stop receiving stretches."
        slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)
        repeated_timer = RepeatedTimer(delay, send_stretch, channel)
        sleep(5)
    if command.startswith(STOP_COMMAND):
        if repeated_timer is None:
            return
        else:
            repeated_timer.stop()
            return

def send_stretch(channel):
    print("in sendstretch")
    img_name, stretch = choice(list(STRETCHES.items()))
    response = "Sure! Why don't you stretch " + stretch
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)

def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel, repeated_timer)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")