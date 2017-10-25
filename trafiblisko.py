#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Marek Wajdzik <wajdzik.m@gmail.com>
# 25.10.2017
# This is only a proof of concept
# Do not use it, as it may lock your traficar account
# I'm not responsible for damage done by this script
# License: MIT License

import requests
import random
import logging
import coloredlogs
import json
import click
import threading
import time
from math import cos, asin, sqrt
from urllib.parse import urljoin

logger = logging.getLogger(__name__)
coloredlogs.install(level="DEBUG")

class Traficar(object):
    API_URL = "https://api.traficar.pl/eaw-rest-api/"
    def __init__(self, username, password, lat, lon):
        self.lat = lat
        self.lon = lon
        self.logger = logging.getLogger("traficar")
        self.logger.debug("Logger installed")
        self.username = username
        self.password = password
        # I'ts not possible that traficar will be further than length of equator
        self.selected_distance = 400751234.0
        self.selected_car = {}
        self.logindata = {}
        self.reserved = False
        self.cookies = []
        self.logger.debug("Variables are now set")
        # Requests API Session
        self.sess = requests.Session()
        self.logger.debug("Requests session set up.")
    
    def _distance(self, lat1, lon1, lat2, lon2):
        #Fuckin Haversine formula
        p = 0.017453292519943295
        a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p)*cos(lat2*p) * (1-cos((lon2-lon1)*p)) / 2
        return 12742000 * asin(sqrt(a))

    def _request(self, url, data=None, method="POST", params=None):
        url = urljoin(self.API_URL, url) #Join with api url
        self.logger.debug("Request to Traficar API {0}".format(url))
        # Prepare request ass app/json
        req = requests.Request(
            method,
            url,
            params=params,
            headers={
                "content-type": "application/json;charset=UTF-8",
                "user-agent": "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
                "origin": "https://www.traficar.pl",
                "referer": "https://www.traficar.pl/booking"
                },
            cookies=self.cookies,
            json=data
        ).prepare()
        #And send it
        response = self.sess.send(req)
        #Hack for prepared requests. Set cookie if there's Set-Cookie
        if len(response.cookies)>0:
            self.cookies = response.cookies
        return response

    def login(self):
        response = self._request(
            "user/login",
            data = {
                "email": self.username,
                "password": self.password,
                "rememberMe": True,
            }
        )
        try:
            self.logindata = json.loads(response.text)
        except json.decoder.JSONDecodeError:
            raise Exception("Provided login was probably incorrect as I cannot parse response!")

    def cancel_reservation(self):
        self.logger.debug("Cancelling reservation")
        response = self._request(
            "reservation/cancel",
            data = {
                "reason": 5, 
                "reasonDescription": "reason5" # This is a "stealth-mode" - default reason for timeout
            }
        )
        self.reserved = False

    def get_reservation_status(self):
        self.logger.debug("Getting reservation info")
        response = self._request(
            "reservation",
            method="GET"
        )  
        try:
            reservation_data = json.loads(response.text)
        except json.decoder.JSONDecodeError:
            raise Exception("Cannot parse reservation data")
        return reservation_data

    def reserve_car(self):
        self.logger.info("Reservation of {} [ {} ] on {} with {} liters of fuel".format(
            self.selected_car["model"],
            self.selected_car["regNumber"],
            self.selected_car["location"],
            self.selected_car["fuel"]
        ))
        #Let's book a car
        response = self._request(
            "reservation/add",
            data = {
                "carId": self.selected_car["id"]
            }
        )
        self.reserved=True

    def get_nearest_car(self):
        response = self._request(
            "car",
            method="GET"
        )
        try:
            cars = json.loads(response.text)["cars"]
        except json.decoder.JSONDecodeError:
            raise Exception("Response from cars api was invalid")
        #Now we want to search nearest car
        #Set some wierd distance, eg equator length approx
        if len(cars)==0:
            raise Exception("API returned 0 available cars!")
        for car in cars:
            distance = self._distance(
                self.lat,
                self.lon,
                car["latitude"],
                car["longitude"]
            )
            if distance < self.selected_distance:
                self.selected_car = car
                self.selected_distance = distance    
        self.logger.info("Closest car for now is {} [ {} ] on {} with {} liters of fuel".format(
            self.selected_car["model"],
            self.selected_car["regNumber"],
            self.selected_car["location"],
            self.selected_car["fuel"]
        ))
    
    def book_nearest_car(self):
        if self.reserved:
            # Check if really reserved:
            reservation = self.get_reservation_status()
            self.logger.info("Reservation response status: {}".format(reservation["reservations"][0]["status"]))
            # Reservation is active
            if reservation["reservations"][0]["status"]=="ADDED":
                if self.selected_car["id"]!=reservation["reservations"][0]["reservedCar"]["id"]:
                    self.logger.info("Found better car!")
                    #Found better car, cancel current and reserve new one
                    self.cancel_reservation()
                    self.reserve_car()
            elif reservation["reservations"][0]["status"]=="STARTED":
                # Do nothing, I'm driving now
                self.logger.info("User is driving right now")
                return True
            else:
                #No reservation, do a reservation
                self.reserve_car()
        else:
            #No reservation, do a reservation
            self.reserve_car()

    def car_refresh_thread(self, timer):
        prev_selected = self.selected_car
        self.get_nearest_car()
        # If there's a new car, book it!
        if prev_selected != self.selected_car:
            self.book_nearest_car()
        threading.Timer(timer, self.car_refresh_thread, [timer]).start()

    def booking_refresh_thread(self, timer):
        self.book_nearest_car()
        threading.Timer(timer, self.booking_refresh_thread, [timer]).start()

    def main_loop(self, recheck, reservation_recheck):
        self.logger.info("Entered main thread loop")
        #Find and book nearest car before entering threads
        self.get_nearest_car()
        self.book_nearest_car()
        #Enter threads
        self.car_refresh_thread(recheck)
        self.booking_refresh_thread(reservation_recheck)
        while True:
            time.sleep(0.05)
        
# Setup command line options
@click.command()
@click.option("--login", help="Your traficar login (email)", prompt="Please type your traficar login",)
@click.option("--password", help="Your traficar password", prompt="Please type your traficar password", hide_input=True)
@click.option("--lat", help="Your latitude", prompt="Please specify your latitude", type=float)
@click.option("--lon", help="Your longitude", prompt="Please specify your longitude", type=float)
@click.option("--recheck", help="How often check (in seconds) if there's a car in neighboorhod or better one than reserved (default is 20 sec)", type=float, default=20.0)
@click.option("--reservation-recheck", help="How often check for reservation (default is 15min 03s)", type=float, default=903.0)
def find_traficar(login, password, lat, lon, recheck, reservation_recheck):
    """Simple script that locks traficar nearest to you ;)"""
    #Create traficar class instance and login to service
    t = Traficar(login, password, lat, lon)
    t.login()
    #Enter main thread loop
    t.main_loop(recheck, reservation_recheck)

if __name__=="__main__":
    find_traficar()