#!/usr/bin/env python3
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
ULTRASONIC_SENSOR_PORT = 8005
CAMERA_PORT = 8000
REMOTE_CONTROL_PORT = 8010
CAMERA_SETTINGS = {
    'FRAMERATE': 32,
    'RESOLUTION': (640, 480),
    'ROTATION': 180,
    'FORMAT': 'h264'
}