import time
import cv2
import os
import numpy as np


class Proctoring:
    def __init__(self, checking_time):
        self.checking_time = checking_time
        self.main_timer = time.time()
        self.people_per_frame = []
        self.smartphones_per_frame = []
        self.people_error = False
        self.smartphone_error = False
        self.error_timer = None
        self.PROCTORING_CLASSES = ['person', 'cell phone']
        self.error_time_to_exit = 15
        self.save_frames_timer = time.time()
        self.error_frames_array = []

        # msgs
        self.people_error_msg = ''
        self.smartphones_error_msg = ''

        self.game_over = False

    def check_time(self):
        if time.time() - self.main_timer > self.checking_time:
            self.main_timer = time.time()
            self.mean_people()
            self.mean_smartphones()
            self.error_timer_work()
    
    def error_timer_work(self):
        if self.any_error():
            if self.error_timer == None:
                self.error_timer = time.time()
        else:
            self.error_timer = None

    def mean_people(self):
        m = [0] * (max(self.people_per_frame) + 1)
        for p in self.people_per_frame:
            m[p] += 1
        m_p = m.index(max(m))
        print("Mean people per time: ", m_p)
        if m_p > 1:
            self.people_error_msg = 'Other people are in the frame!'
            self.people_error = True
        elif m_p == 0:
            self.people_error_msg = 'You are not in frame!'
            self.people_error = True
        else:
            self.people_error = False
        self.people_per_frame = []


    def mean_smartphones(self):
        m = [0] * (max(self.smartphones_per_frame) + 1)
        for p in self.smartphones_per_frame:
            m[p] += 1
        m_s = m.index(max(m))
        print("Mean smartphones per time: ", m_s)
        if m_s > 0:
            self.smartphones_error_msg = 'Smartphone is in the frame!'
            self.smartphone_error = True
        else:
            self.smartphone_error = False
        self.smartphones_per_frame = []
    
    def any_error(self):
        return self.people_error or self.smartphone_error

    def save_error_frames(self):
        path = 'spy_frames'
        self.game_over = True
        
        for i in range(len(self.error_frames_array)):
            cv2.imwrite(f'{path}/{i}.jpg', self.error_frames_array[i])

    def work_with_frame(self, frame):
        color = (255, 0, 0)
        if self.any_error():
            if time.time() - self.save_frames_timer > 1:
                self.save_frames_timer = time.time()
                self.error_frames_array.append(frame)
            
            if self.error_time_to_exit - (time.time() - self.error_timer) < 0:
                print('EXAM IF FAILED...........')
                self.save_error_frames()
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                print('GRAYFrame')
                frame = cv2.putText(frame, 'GAME OVER', (0, 400), cv2.FONT_HERSHEY_SIMPLEX , 2, color, 3, cv2.LINE_AA)
                print('Text is put')
                return frame
            if self.people_error:
                frame = cv2.putText(frame, f'ATTENTION! {self.people_error_msg}', (0, 200), cv2.FONT_HERSHEY_SIMPLEX , 2, color, 3, cv2.LINE_AA)

            if self.smartphone_error:
                frame = cv2.putText(frame, f'ATTENTION! {self.smartphones_error_msg}', (0, 400), cv2.FONT_HERSHEY_SIMPLEX , 2, color, 3, cv2.LINE_AA)
            frame = cv2.putText(frame, f'You have only {int(self.error_time_to_exit - (time.time() - self.error_timer))} seconds to exam stop', (0, 600), cv2.FONT_HERSHEY_SIMPLEX , 2, color, 3, cv2.LINE_AA)
        return frame