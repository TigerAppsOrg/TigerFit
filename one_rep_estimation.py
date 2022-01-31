class OneRepEstimation:
    # https://en.wikipedia.org/wiki/One-repetition_maximum
    # Brzycki Formula
    @staticmethod
    def estimate_one_rep_max(weight, reps):
        MAX_REP_LIMIT = 16
        if reps <= 0 or reps > MAX_REP_LIMIT:
            return 0
        return 36 * weight / (37 - reps)

    @staticmethod
    def estimate_weight(one_rep_max, reps):
        MAX_REP_LIMIT = 16
        if reps <= 0 or reps > MAX_REP_LIMIT:
            return 0
        return (37 - reps) * one_rep_max / 36

    @staticmethod
    def estimate_reps(one_rep_max, weight):
        # ! use max rep limit in this method?
        return 37 - 36 * weight / one_rep_max
