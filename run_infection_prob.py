import infection_probability_distribution as ipd
import pandas as pd
import generate_synthetic_data as gsd
import pre_process_data as ppd


# This function generate synthetic data based on the given parameters
def generate_data(num_students, num_courses, room_min_area, room_max_area, room_min_ach, room_max_ach,
                  schedule_start_time, schedule_end_time, course_min_duration, course_max_duration,
                  max_num_sessions_per_course, max_num_courses_per_student, room_data_path, course_schedule_path,
                  student_schedule_path):

    rooms_data = gsd.generate_room_data(10, room_min_area, room_max_area, room_min_ach, room_max_ach, room_data_path)

    locations = list(rooms_data["LOCATION"])
    course_schedule = gsd.generate_course_schedule(num_courses, locations, max_num_sessions_per_course,
                                                   schedule_start_time, schedule_end_time,
                                                   course_min_duration, course_max_duration, course_schedule_path)

    student_schedule = gsd.generate_students_schedule(num_students, course_schedule, max_num_courses_per_student,
                                                      student_schedule_path)

    return student_schedule


# This function calculate and save the infection probability distribution of the students for the given dataset
def calculate_infection_probability(
        dataset_path_rooms_data, dataset_path_student_schedule, dataset_path_course_schedule,
        occupancy_ratio, student_initial_infection_prob, teacher_initial_infection_prob,
        h, Q, QCa, QCp, mask, HVAC_E, p_a_t, p_a_s, D0, num_simulation_days, dataset_name, output_path):

    rooms_data = pd.read_csv(dataset_path_rooms_data)
    course_schedule = pd.read_csv(dataset_path_course_schedule)
    student_schedule = pd.read_csv(dataset_path_student_schedule)

    dataset_path = ipd.simulate_mixed_room_model_student_teacher_binomial(
        student_schedule, course_schedule, rooms_data, occupancy_ratio,student_initial_infection_prob,
        teacher_initial_infection_prob, h, Q, QCa, QCp, mask, HVAC_E, p_a_t, p_a_s, D0,
        num_simulation_days, dataset_name, output_path)

    output_path = "./Output/students_infection_prob_histogram.png"
    ipd.plot_infec_prob_dist(dataset_path, output_path)

    return output_path


# This function runs the whole program to 1) generate synthetic data 2) create course schedule based on the
# students schedule (whether synthetic or not) 3) calculate and store the infection probability distribution of the
# students
def main():

    # Set room parameters
    room_min_area = 140                 # Unit: SQFT
    room_max_area = 3668                # Unit: SQFT
    room_min_ach = 0.0005               # Air change rate per hour
    room_max_ach = 0.005                # Air change rate per hour

    # Set schedule parameters
    schedule_start_time = "06:00:00"
    schedule_end_time = "23:00:00"
    course_min_duration = "01:00:00"
    course_max_duration = "04:00:00"

    num_courses = 500
    max_num_sessions_per_course = 3

    num_students = 5000
    max_num_courses_per_student = 3

    # Set output path for the generated synthetic dataset
    room_data_path = "./Output/Synthetic_Data/Rooms_Data.csv"
    course_schedule_path = "./Output/Synthetic_Data/Course_Schedule.csv"
    student_schedule_path = "./Output/Synthetic_Data/Student_Schedule.csv"

    # Generate synthetic data
    student_schedule = generate_data(num_students, num_courses, room_min_area, room_max_area, room_min_ach, room_max_ach,
                  schedule_start_time, schedule_end_time, course_min_duration, course_max_duration,
                  max_num_sessions_per_course, max_num_courses_per_student, room_data_path, course_schedule_path,
                  student_schedule_path)

    # Calculate the infection probability distribution of the students for a given dataset (whether synthetic or not)

    # Calculate the duration of the courses
    output_path = "./Output/Student_Schedule.csv"
    student_schedule = ppd.calculate_course_durations(student_schedule_path, output_path)

    # Generate course schedule based on the provided dataset of the student schedule
    output_path = "./Output/Course_Schedule.csv"
    ppd.generate_course_schedule(student_schedule, output_path)

    # Set up information for calculating the infection probability distribution of the students
    dataset_path_rooms_data = "./Output/Synthetic_Data/Rooms_Data.csv"
    dataset_path_course_schedule = "./Output/Course_Schedule.csv"
    dataset_path_student_schedule = "./Output/Student_Schedule.csv"

    occupancy_ratio = 0.5
    mask = 0.5                                  # Mask Filtration Efficiency
    f_in = mask                                 # Mask Filtration Efficiency (In)
    f_out = mask                                # Mask Filtration Efficiency (Out)
    D0 = 1000
    student_initial_infection_prob = 0.01       # Initial infection probability of the students
    teacher_initial_infection_prob = 0.01       # Initial infection probability of the teachers
    h = 2.7                                     # Room Height
    Q = 2*10**-4                                # Breathing Rate
    QCa = 40                                    # Emission rate for active infected occupants
    QCp = 1                                     # Emission rate for passive infected occupants
    HVAC_E = 0.8                                # HVAC Filter Efficiency
    p_a_t = 0.9                                 # Fraction of time infectious teacher is active
    p_a_s = 0.05                                # Fraction of time infectious students are active

    num_simulation_days = 7                     # Number of days to run the simulation (here we considered one week)
    dataset_name = "Fall_2020"                  # The name of the dataset used
    output_path = "./Output/"                   # The path for storing the output


    output_path = calculate_infection_probability(
        dataset_path_rooms_data, dataset_path_student_schedule, dataset_path_course_schedule,
        occupancy_ratio, student_initial_infection_prob, teacher_initial_infection_prob,
        h, Q, QCa, QCp, mask, HVAC_E, p_a_t, p_a_s, D0, num_simulation_days, dataset_name, output_path)

    print(output_path)


main()