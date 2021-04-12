import math
import pandas as pd
import numpy as np
import sys
from scipy.stats import binom
import matplotlib.pyplot as plt

# This function calculates the infection probability of all of the courses in the schedule of the students
def calculate_course_infection_prob(course_schedule, rooms_data, occupancy_ratio, h, Q, QCa, QCp,
                                    mask, HVAC_E, p_a_t, p_a_s, D0, student_initial_infection_prob,
                                    teacher_initial_infection_prob, dataset_name, output_path):

    f_in = mask         # Mask Filteration Efficiency (In)
    f_out = mask        # Mask Filteration Efficiency (Out)

    rooms_data = rooms_data.set_index(["LOCATION"])

    course_schedule["DURATION"] = pd.to_timedelta(course_schedule["DURATION"])

    course_schedule["OCCUPANCY"] = np.ceil(course_schedule["ENROLLMENT"] * occupancy_ratio)
    course_schedule["OCCUPANCY_RATIO"] = occupancy_ratio
    course_schedule["MASK"] = mask
    course_schedule["D0"] = D0
    course_schedule["YEAR"] = dataset_name
    course_schedule["STUDENT_INFECTION_PROB"] = student_initial_infection_prob
    course_schedule["TEACHER_INFECTION_PROB"] = teacher_initial_infection_prob
    course_schedule["INFECTION_PROB_SESSION"] = 0

    for index, row in course_schedule.iterrows():
        location = str(row["LOCATION"])
        course_duration = course_schedule.loc[index, "DURATION"].total_seconds()

        teacher_occupancy_density = 1 / rooms_data.loc[location, "AREA"] / 0.092903
        dose_one_teacher = (1 - f_in) * (1 - f_out) * (teacher_occupancy_density * Q) / \
                           (h * HVAC_E * rooms_data.loc[location, "AIR_CHANGE_RATE"]) * \
                           (p_a_t * QCa + (1 - p_a_t) * QCp) * course_duration

        student_occupancy_density = 1 / rooms_data.loc[location, "AREA"] / 0.092903
        dose_one_student = (1 - f_in) * (1 - f_out) * (student_occupancy_density * Q) / \
                           (h * HVAC_E * rooms_data.loc[location, "AIR_CHANGE_RATE"]) * \
                           (p_a_s * QCa + (1 - p_a_s) * QCp) * course_duration

        total_transmission_prob = 0
        for i in range(0, (int)(row["OCCUPANCY"])):
            student_infection_prob = binom.pmf(i, row["OCCUPANCY"], student_initial_infection_prob)
            dose_student = i * dose_one_student
            dose_teacher_student = dose_one_teacher + dose_student
            transmission_prob_teacher_student = 1 - math.exp(-dose_teacher_student / D0)
            transmission_prob_student = 1 - math.exp(-dose_student / D0)

            total_transmission_prob += student_infection_prob * (
                    teacher_initial_infection_prob * transmission_prob_teacher_student +
                    (1 - teacher_initial_infection_prob) * transmission_prob_student)

        course_schedule.loc[index, "INFECTION_PROB_SESSION"] = total_transmission_prob

    course_schedule["DURATION"] = course_schedule["DURATION"].astype(str)
    course_schedule["DURATION"] = course_schedule["DURATION"].str[7:15]
    output_path += "course_infection_prob.csv"
    course_schedule.to_csv(output_path, index=False)
    return course_schedule


# This function calculates the infection probability of the students given the infection probability of the courses
def calculate_student_infection_prob(student_schedule, course_infection_prob, occupancy_ratio, h, Q, QCa,
                                     QCp, mask, HVAC_E, p_a_t, p_a_s, D0,
                                     student_initial_infection_prob, teacher_initial_infection_prob,
                                      num_simulation_days, dataset_name, output_path):
    # Use the following command if you use the COMBINE method
    #course_infection_prob = course_infection_prob.set_index(["LOCATION", "DAYS", "START_TIME", "END_TIME"])
    # use the following command if you use the SEPARATE method
    course_infection_prob = course_infection_prob.set_index(["SECTION"])
    student_schedule["OCCUPANCY_RATIO"] = occupancy_ratio
    student_schedule["MASK"] = mask
    student_schedule["HEIGHT"] = h
    student_schedule["RESPIRATORY_RATE"] = Q
    student_schedule["ACTIVE_EMISSION"] = QCa
    student_schedule["PASSIVE_EMISSION"] = QCp
    student_schedule["HVAC"] = HVAC_E
    student_schedule["STUDENT_ACTIVE_TIME"] = p_a_s
    student_schedule["TEACHER_ACTIVE_TIME"] = p_a_t
    student_schedule["DATASET"] = dataset_name
    student_schedule["STUDENT_INFECTION_PROB"] = student_initial_infection_prob
    student_schedule["TEACHER_INFECTION_PROB"] = teacher_initial_infection_prob
    student_schedule["SIMULATION_DAYS"] = num_simulation_days
    student_schedule["INFECTION_PROB_SESSION"] = 0
    student_schedule["HEALTHY_PROB_SESSION"] = 0
    student_schedule["HEALTHY_PROB_TOTAL"] = 0

    week_day_index = {'M': 1, 'T': 2, 'W': 3, 'H': 4, 'F':5, 'S': 6}

    for index, row in student_schedule.iterrows():
        if (row["SECTION"]) not in course_infection_prob.index:
            continue
        student_schedule.loc[index, "INFECTION_PROB_SESSION"] = course_infection_prob.loc[
                                                        (row["SECTION"]), "INFECTION_PROB_SESSION"]

        student_schedule.loc[index, "HEALTHY_PROB_SESSION"] = 1 - student_schedule.loc[index, "INFECTION_PROB_SESSION"]

        num_attended_weeks = (int)(num_simulation_days / 7)
        num_attended_days = num_attended_weeks * len(row["DAYS"])
        num_remaining_days = num_simulation_days % 7
        for ch in row["DAYS"]:
            if week_day_index[ch] <= num_remaining_days:
                num_attended_days += 1

        student_schedule.loc[index, "HEALTHY_PROB_TOTAL"] = student_schedule.loc[index, "HEALTHY_PROB_SESSION"] ** num_attended_days

    output_path += "student_schedule_infection_prob.csv"
    student_schedule.to_csv(output_path, index=False)

    return student_schedule


# This function integrate the calculation of the infection probability of the courses and students
def simulate_mixed_room_model_student_teacher_binomial(
        student_schedule, course_schedule, rooms_data, occupancy_ratio,student_initial_infection_prob,
        teacher_initial_infection_prob, h, Q, QCa, QCp, mask, HVAC_E, p_a_t, p_a_s, D0,
        num_simulation_days, dataset_name, output_path):

    print("START - Occupancy Ratio= " + str(occupancy_ratio) + " - Mask= " + str(mask) + " - D0= " + str(D0) +
    "\n" + "Students Infec Frac= " + str(student_initial_infection_prob) + " - Teachers Infec Prob = " +
    str(teacher_initial_infection_prob) + "\n\n")
    course_schedule = calculate_course_infection_prob(course_schedule, rooms_data, occupancy_ratio, h, Q, QCa, QCp,
                                                      mask, HVAC_E, p_a_t, p_a_s, D0, student_initial_infection_prob,
                                                      teacher_initial_infection_prob, dataset_name, output_path)

    student_schedule = calculate_student_infection_prob(student_schedule, course_schedule, occupancy_ratio, h, Q, QCa,
                                                        QCp, mask, HVAC_E, p_a_t, p_a_s, D0,
                                                        student_initial_infection_prob, teacher_initial_infection_prob,
                                                        num_simulation_days, dataset_name, output_path)

    output_path = save_infec_prob(student_schedule, output_path)

    print("FINISH - Occupancy Ratio= " + str(occupancy_ratio) + " - Mask= " + str(mask) + " - D0= " + str(D0) +
    "\n" + "Students Infec Frac= " + str(student_initial_infection_prob) + " - Teachers Infec Prob = " +
    str(teacher_initial_infection_prob) + "\n\n")
    return output_path


# This function helps with saving the infection probability distribution of the students
def save_infec_prob(data, output_path):
    data = data.loc[data["HEALTHY_PROB_TOTAL"] > 0]
    student_infec_prob = data.groupby(["STUDENT_ID"]).HEALTHY_PROB_TOTAL.prod().reset_index()
    student_infec_prob["INFECTION_PROB_TOTAL"] = 1 - student_infec_prob["HEALTHY_PROB_TOTAL"]

    student_infec_prob = student_infec_prob[["STUDENT_ID", "INFECTION_PROB_TOTAL"]]

    output_path += "student_infection_prob.csv"
    student_infec_prob.to_csv(output_path, index=False)
    return output_path


# This function plot a histogram of the infection probability distribution
def plot_infec_prob_dist(dataset_path, output_path):
    student_infection_prob = pd.read_csv(dataset_path)

    plt.clf()
    plt.hist(student_infection_prob["INFECTION_PROB_TOTAL"], bins=50)
    plt.xlabel("Infection Probability")
    plt.ylabel("Number of Students")
    plt.savefig(output_path)


# This function helps with saving the data with a correct format
def save_dataset(data, path):
    # Convert the columns to string
    data["START_TIME"] = data["START_TIME"].astype(str)
    data["END_TIME"] = data["END_TIME"].astype(str)

    # Get the hour part of the day from the string
    data["START_TIME"] = (data["START_TIME"].str[7:15])
    data["END_TIME"] = (data["END_TIME"].str[7:15])

    data.to_csv(path, index=False)

