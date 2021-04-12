import pandas as pd
import sys


# This function calculates the course duration of the courses
def calculate_course_durations(student_schedule_path, output_path):
    student_schedule = pd.read_csv(student_schedule_path)
    student_schedule["START_TIME"] = pd.to_timedelta(student_schedule["START_TIME"].astype(str))
    student_schedule["END_TIME"] = pd.to_timedelta(student_schedule["END_TIME"].astype(str))
    student_schedule["DURATION"] = student_schedule["END_TIME"] - student_schedule["START_TIME"]

    save_dataset(student_schedule, output_path)
    return output_path


# This function generates course schedule given the uploaded student schedule (whether synthetic or not)
def generate_course_schedule(dataset_path_student_schedule, output_path):
    student_schedule = pd.read_csv(dataset_path_student_schedule)
    student_schedule["ENROLLMENT"] = 1
    student_schedule["STUDENT_ID"] = student_schedule["STUDENT_ID"].astype(str)

    registered_students = student_schedule.groupby(["SECTION", "LOCATION", "DAYS", "START_TIME", "END_TIME",
                                                    "DURATION"])["STUDENT_ID"].apply(lambda x: ','.join(x)).reset_index()
    #print(registered_students)
    course_schedule = student_schedule.groupby(["SECTION", "LOCATION", "DAYS", "START_TIME", "END_TIME",
                                                "DURATION"]).ENROLLMENT.count().reset_index()
    course_schedule["STUDENT_ID"] = registered_students["STUDENT_ID"]
    print(course_schedule)

    course_schedule = course_schedule.reset_index(drop=True)
    course_schedule = course_schedule[["SECTION", "LOCATION", "DAYS", "START_TIME", "END_TIME",
                                       "DURATION", "ENROLLMENT", "STUDENT_ID"]]
    course_schedule.to_csv(output_path, index=False)

    return output_path


# This function helps with saving the data with a correct format.
def save_dataset(data, path):
    # Convert the columns to string
    data["START_TIME"] = data["START_TIME"].astype(str)
    data["END_TIME"] = data["END_TIME"].astype(str)
    data["DURATION"] = data["DURATION"].astype(str)

    # Get the hour part of the day from the string
    data["START_TIME"] = (data["START_TIME"].str[7:15])
    data["END_TIME"] = (data["END_TIME"].str[7:15])
    data["DURATION"] = (data["DURATION"].str[7:15])

    data.to_csv(path, index=False)
