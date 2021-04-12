import infection_probability_distribution as ipd
import pandas as pd
import generate_synthetic_data as gsd
import pre_process_data as ppd


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


# This function runs the whole program to 1) create course schedule based on the
# students schedule (whether synthetic or not) 3) calculate and store the infection probability distribution of the
# students
def main():


    # Set up information for calculating the infection probability distribution of the students
    dataset_path_rooms_data = "../Dataset/Rooms_Data.csv"
    dataset_path_student_schedule = "../Dataset/Student_Schedule.csv"


    # Calculate the duration of the courses
    output_path = "./Output/Student_Schedule.csv"
    dataset_path_student_schedule = ppd.calculate_course_durations(dataset_path_student_schedule, output_path)

    # Generate course schedule based on the provided dataset of the student schedule
    output_path = "./Output/Course_Schedule.csv"
    dataset_path_course_schedule = ppd.generate_course_schedule(dataset_path_student_schedule, output_path)


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


if __name__ == "__main__":
    main()