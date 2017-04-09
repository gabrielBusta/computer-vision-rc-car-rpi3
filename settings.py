#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author: Gabriel Bustamante
Email: gabrielbusta@gmail.com

Selfdriving GoPiGo: An open source self-driving robot application.
This app was built using the GoPiGo robotics platform for the Raspberry Pi.

Copyright (C) 2017 Gabriel Bustamante
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/gpl-3.0.txt>.
"""
ROBOT_IP = '192.168.1.107'
# ROBOT_IP = '192.168.42.15'
# ROBOT_IP = '10.42.0.62'

DEBUG = False

CAMERA_ON = True
ULTRASONIC_SENSOR_ON = True
REMOTE_CONTROL_ON = True

CAMERA_PORT = 8000
ULTRASONIC_SENSOR_PORT = 8005
REMOTE_CONTROL_PORT = 8010

CAMERA_FRAMERATE = 32
CAMERA_RESOLUTION = (640, 480)
CAMERA_VIDEO_FORMAT = 'h264'
CAMERA_ROTATION = 180
