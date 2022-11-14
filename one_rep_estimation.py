# from database_methods import get_most_recent_bodyweight

# import database_methods


# class OneRepEstimation:
#     # * https://en.wikipedia.org/wiki/One-repetition_maximum
#     # * Brzycki Formula
#     @staticmethod
#     def estimate_one_rep_max(weight, reps):
#         MAX_REP_LIMIT = 20
#         if reps <= 0 or reps > MAX_REP_LIMIT:
#             return 0
#         return 36 * weight / (37 - reps)

#     @staticmethod
#     def estimate_weight(one_rep_max, reps):
#         MAX_REP_LIMIT = 20
#         if reps <= 0 or reps > MAX_REP_LIMIT:
#             return 0
#         return (37 - reps) * one_rep_max / 36

#     @staticmethod
#     def estimate_reps(one_rep_max, weight):
#         MAX_REP_LIMIT = 20
#         rep_estimation = 37 - 36 * weight / one_rep_max

#         if rep_estimation <= 0 or rep_estimation > MAX_REP_LIMIT:
#             return 0

#         return rep_estimation

#     # * For bodyweight workouts, use weight = bodyweight + weight added
#     @staticmethod
#     def bodyweight_estimate_one_rep_max(
#         session, user_name, weight_added, reps
#     ):
#         MAX_REP_LIMIT = 20
#         curr_bodyweight = get_most_recent_bodyweight(session, user_name)
#         total_weight = weight_added + curr_bodyweight

#         if reps <= 0 or reps > MAX_REP_LIMIT:
#             return 0
#         return 36 * total_weight / (37 - reps) - curr_bodyweight

#     @staticmethod
#     def bodyweight_estimate_weight(
#         session, user_name, one_rep_max, reps
#     ):
#         MAX_REP_LIMIT = 20
#         curr_bodyweight = get_most_recent_bodyweight(session, user_name)
#         total_weight = one_rep_max + curr_bodyweight

#         if reps <= 0 or reps > MAX_REP_LIMIT:
#             return 0
#         return (37 - reps) * total_weight / 36 - curr_bodyweight

#     @staticmethod
#     def bodyweight_estimate_reps(
#         session, user_name, one_rep_max, weight_added
#     ):
#         MAX_REP_LIMIT = 20
#         curr_bodyweight = get_most_recent_bodyweight(session, user_name)

#         rep_estimation = 37 - 36 * (weight_added + curr_bodyweight) / (
#             one_rep_max + curr_bodyweight
#         )

#         if rep_estimation <= 0 or rep_estimation > MAX_REP_LIMIT:
#             return 0

#         return rep_estimation
