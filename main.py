import RPi.GPIO as GPIO
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import serial
import json
import os
import sys
import time

from sphero_sdk import SpheroRvrObserver
from sphero_sdk import RawMotorModesEnum


host_name = '192.168.1.123'
host_port = 8000


class MyServer(BaseHTTPRequestHandler):
    """ A special implementation of BaseHTTPRequestHander for reading data from
        and control GPIO of a Raspberry Pi
    """
    rvr = SpheroRvrObserver()

    def do_HEAD(self):
        """ do_HEAD() can be tested use curl command
            'curl -I http://server-ip-address:port'
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _redirect(self, path):
        self.send_response(303)
        self.send_header('Content-type', 'text/html')
        self.send_header('Location', path)
        self.end_headers()

    def do_GET(self):
        """ do_GET() can be tested using curl command
            'curl http://server-ip-address:port'
        """
        self.do_HEAD()
        with open('control.html', 'rb') as file:
            self.wfile.write(file.read())

    def do_POST(self):
        # Post data as dict
        post_data = json.loads(self.rfile.read(int(self.headers['Content-Length'])).decode("utf-8"))
        print("~~~~~~~~~~~~~~~~~~~~~")
        print(post_data)

        if post_data.get('system') == "travel":
            if post_data.get('type') == "on":
                print("on ");
                if post_data.get('command') == "left":
                    # turn left
                    print("left");
                    self.rvr.raw_motors(
                        left_mode=RawMotorModesEnum.reverse.value,
                        left_duty_cycle=128,  # Valid duty cycle range is 0-255
                        right_mode=RawMotorModesEnum.forward.value,
                        right_duty_cycle=128  # Valid duty cycle range is 0-255
                    )
                elif post_data.get('command') == "forward":
                    # go forward
                    print("forward");
                    self.rvr.raw_motors(
                        left_mode=RawMotorModesEnum.forward.value,
                        left_duty_cycle=64,  # Valid duty cycle range is 0-255
                        right_mode=RawMotorModesEnum.forward.value,
                        right_duty_cycle=64  # Valid duty cycle range is 0-255
                    )
                elif post_data.get('command') == "right":
                    # turn right
                    print("right");
                    self.rvr.raw_motors(
                        left_mode=RawMotorModesEnum.forward.value,
                        left_duty_cycle=128,  # Valid duty cycle range is 0-255
                        right_mode=RawMotorModesEnum.reverse.value,
                        right_duty_cycle=128  # Valid duty cycle range is 0-255
                    )
                elif post_data.get('command') == "backward":
                    # go backward
                    print("backward");
                    self.rvr.raw_motors(
                        left_mode=RawMotorModesEnum.reverse.value,
                        left_duty_cycle=64,  # Valid duty cycle range is 0-255
                        right_mode=RawMotorModesEnum.reverse.value,
                        right_duty_cycle=64  # Valid duty cycle range is 0-255
                    )

            if post_data.get('type') == "off":
                print("off");
                self.rvr.raw_motors(
                    left_mode=RawMotorModesEnum.off.value,
                    left_duty_cycle=0,  # Valid duty cycle range is 0-255
                    right_mode=RawMotorModesEnum.off.value,
                    right_duty_cycle=0  # Valid duty cycle range is 0-255
                )
                """
                if post_data.get('command') == "left":
                    print("left");
                elif post_data.get('command') == "forward":
                    print("forward");
                    self.rvr.raw_motors(
                        left_mode=RawMotorModesEnum.off.value,
                        left_duty_cycle=0,  # Valid duty cycle range is 0-255
                        right_mode=RawMotorModesEnum.off.value,
                        right_duty_cycle=0  # Valid duty cycle range is 0-255
                    )
                elif post_data.get('command') == "right":
                    print("right");
                elif post_data.get('command') == "backward":
                    print("backward");
                    self.rvr.raw_motors(
                        left_mode=RawMotorModesEnum.off.value,
                        left_duty_cycle=0,  # Valid duty cycle range is 0-255
                        right_mode=RawMotorModesEnum.off.value,
                        right_duty_cycle=0  # Valid duty cycle range is 0-255
                    )
                """

        elif post_data.get('system') == 'piLED':
            GPIO.output(28, not GPIO.input(28))

        elif post_data.get('system') == 'RVRSetup':
            if post_data.get('command') == "on":
                # setup RVR
                print("Waking RVR")
                self.rvr.wake()
                time.sleep(2)
                self.rvr.reset_yaw()
            elif post_data.get('command') == "off":
                print("shutdown RVR")
                self.rvr.close()

        """
        if post_data == 'On':
            GPIO.output(28, GPIO.HIGH)
            ser.write('on'.encode())
        else:
            GPIO.output(28, GPIO.LOW)
            ser.write('off'.encode())
        """

        self.do_HEAD()
        self.wfile.write("received".encode("utf-8"))


if __name__ == '__main__':
    # GPIO setup
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(28, GPIO.OUT)
    GPIO.output(28, True)



    http_server = HTTPServer((host_name, host_port), MyServer)
    print("Server Starts - %s:%s" % (host_name, host_port))

    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()