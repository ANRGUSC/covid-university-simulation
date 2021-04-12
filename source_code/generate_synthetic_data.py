import pandas as pd
import sys
import random
from datetime import time, timedelta, datetime
import string


# This function generate some random locations as the buildings and rooms of the university. The location is being
# considered with a 6 coded string "BBBRRR", where "BBB" represent the building code and "RRR" represent the room
# number.
def generate_random_location():
    building =  ''.join(random.choices(string.ascii_uppercase, k=3))
    room = ''.join(random.choices(string.digits, k=3))
    location = building + room
    return location


# This function generates the location information of the university buildings. This information includes the
# location, area, air change rate of the rooms. Finally, the generated rooms data will be stored at the provided path.
def generate_room_data(num_locations, min_area, max_area, min_ach, max_ach, output_path):
    rooms_data = pd.DataFrame()

    for i in range(num_locations):
        location = generate_random_location()
        area = random.randint(min_area, max_area)
        ach = round(random.uniform(min_ach, max_ach), 8)
        rooms_data = rooms_data.append({"LOCATION": location, "AREA": area, "AIR_CHANGE_RATE": ach}, ignore_index=True)

    rooms_data = rooms_data[["LOCATION", "AREA", "AIR_CHANGE_RATE"]]
    print(rooms_data)
    rooms_data.to_csv(output_path, index=False)
    return rooms_data


# This function generate some random time for the start time of the courses given the start and time of the schedule
# and also the minimum and maximum duration of the courses.
def generate_time(start_time, end_time, min_duration, max_duration):
    start_time = pd.to_timedelta(start_time)
    end_time = pd.to_timedelta(end_time)
    min_duration = pd.to_timedelta(min_duration)
    max_duration = pd.to_timedelta(max_duration)

    time_s = 0
    time_e = 0
    while(True):
        time_s = random.randint(start_time.total_seconds(), end_time.total_seconds())
        time_s = time_s - time_s % 60
        time_s = timedelta(seconds=time_s)
        duration = random.randint(min_duration.total_seconds(), max_duration.total_seconds())
        duration = duration - duration % 60
        duration = timedelta(seconds=duration)
        time_e = time_s + duration
        if time_e < end_time:
            break

    return time_s, time_e


# This function check whether the selected room for a course is available for the given time
def check_room_available(course_schedule, location, days, time_s, time_e):

    if course_schedule.empty:
        return True
    course_schedule["START_TIME"] = pd.to_timedelta(course_schedule["START_TIME"])
    course_schedule["END_TIME"] = pd.to_timedelta(course_schedule["END_TIME"])

    for day in days:
        temp = course_schedule.loc[(course_schedule["LOCATION"] == location) &
                                   (course_schedule["LOCATION"].str.contains(day)) &
                                   (course_schedule["START_TIME"] < time_e) &
                                   (course_schedule["END_TIME"] > time_s)]

        if not(temp.empty):
            return False

    return True


# This function generates the course schedule given the number of courses, randomly generated locations, maximum number
# of sessions per course, start and end time of the schedule and also the maximum and minimum duration of the course.
def generate_course_schedule(num_courses, locations, max_num_sessions, start_time, end_time, min_duration,
                             max_duration, output_path):

    course_schedule = pd.DataFrame()
    weekdays = ["M", "T", "W", "H", "F"]
    for section in range(num_courses):
        num_sessions = random.randint(1, max_num_sessions)
        days = random.sample(weekdays, num_sessions)
        location = ""
        time_s = ""
        time_e = ""
        while (True):
            location = random.choice(locations)
            time_s, time_e = generate_time(start_time, end_time, min_duration, max_duration)
            if check_room_available(course_schedule, location, days, time_s, time_e):
                break
        days = ''.join(days)
        course_schedule = course_schedule.append({"SECTION": str(section), "LOCATION": location,
                                                  "DAYS": days, "START_TIME": time_s, "END_TIME": time_e},
                                                 ignore_index=True)

    course_schedule = course_schedule[["SECTION", "LOCATION", "DAYS", "START_TIME", "END_TIME"]]
    save_dataset(course_schedule, output_path)
    print(course_schedule)
    return course_schedule


# This function generates the schedule of the students give the course schedule and also the maximum number of courses
# that each student may take.
def generate_students_schedule(num_students, course_schedule, max_num_courses, output_path):

    students_schedule = pd.DataFrame()
    courses = list(course_schedule["SECTION"])
    course_schedule = course_schedule.set_index(["SECTION"])

    for id in range(num_students):
        num_courses = random.randint(1, max_num_courses)
        sections = random.sample(courses, num_courses)
        for section in sections:
            location = course_schedule.loc[section, "LOCATION"]
            days = course_schedule.loc[section, "DAYS"]
            start_time = course_schedule.loc[section, "START_TIME"]
            end_time = course_schedule.loc[section, "END_TIME"]
            students_schedule = students_schedule.append({"STUDENT_ID": str(id), "SECTION": section,
                                                          "LOCATION": location, "DAYS": days, "START_TIME": start_time,
                                                          "END_TIME": end_time}, ignore_index=True)

    students_schedule = students_schedule[["STUDENT_ID", "SECTION", "LOCATION", "DAYS", "START_TIME", "END_TIME"]]
    students_schedule.to_csv(output_path, index=False)
    print(students_schedule)
    return students_schedule


# This function helps with saving the data with a correct format.
def save_dataset(data, path):
    # Convert the columns to string
    data["START_TIME"] = data["START_TIME"].astype(str)
    data["END_TIME"] = data["END_TIME"].astype(str)

    # Get the hour part of the day from the string
    data["START_TIME"] = (data["START_TIME"].str[7:15])
    data["END_TIME"] = (data["END_TIME"].str[7:15])

    data.to_csv(path, index=False)
