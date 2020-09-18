# from footypicks.gameweek.models import Prediction

def calculate_score(predicted_score, actual_score, joker, rule_set):

    def correct_score(predicted_score, actual_score, potential_points):
        if predicted_score == actual_score:
            return potential_points
        else:
            return 0

    def correct_result(predicted_score, actual_score, potential_points):

        def get_result(score):
            score = score.split("-")
            try:
                score = int(score[0]) - int(score[1])
            except:
                score = 0

            if score == 0:
                return "D"
            elif score < 0:
                return "A"
            else:
                return "H"

        if get_result(predicted_score) == get_result(actual_score):
            return potential_points
        else:
            return 0

    def correct_home_score(predicted_score, actual_score, potential_points):
        if predicted_score[0] == actual_score[0]:
            return potential_points
        else:
            return 0

    def correct_away_score(predicted_score, actual_score, potential_points):
        if predicted_score[-1] == actual_score[-1]:
            return potential_points
        else:
            return 0

    correct_score = correct_score(predicted_score, actual_score, rule_set["correct_score"])
    correct_result = correct_result(predicted_score, actual_score, rule_set["correct_result"])
    correct_home_score = correct_home_score(predicted_score, actual_score, rule_set["correct_home_score"])
    correct_away_score = correct_away_score(predicted_score, actual_score, rule_set["correct_away_score"])

    return (correct_score + correct_result + correct_away_score + correct_home_score) \
           * (rule_set["joker_multiplier"] if joker else 1)


def calculate_gameweek_scores(gw_id):
    preds = Prediction.objects.filter(game=gw_id)
    for pred in preds:
        pred.points = pred.get_points()
        pred.save()


def tests():
    print("Correct Result: " + str(calculate_score(predicted_score="2-1",
                                                   actual_score="2-0",
                                                   joker=True,
                                                   rule_set={"correct_score": 2,
                                                             "correct_result": 1,
                                                             "correct_home_score": 0,
                                                             "correct_away_score": 0,
                                                             "joker_multiplier": 2})))
    print("Correct Score: " + str(calculate_score(predicted_score="2-1",
                                                  actual_score="2-1",
                                                  joker=False,
                                                  rule_set={"correct_score": 2,
                                                            "correct_result": 1,
                                                            "correct_home_score": 0,
                                                            "correct_away_score": 0,
                                                            "joker_multiplier": 2})))
    print("Correct home score: " + str(calculate_score(predicted_score="2-1",
                                                       actual_score="2-1",
                                                       joker=False,
                                                       rule_set={"correct_score": 0,
                                                                 "correct_result": 0,
                                                                 "correct_home_score": 3,
                                                                 "correct_away_score": 0,
                                                                 "joker_multiplier": 2})))
    print("Correct away score: " + str(calculate_score(predicted_score="2-1",
                                                       actual_score="2-1",
                                                       joker=False,
                                                       rule_set={"correct_score": 0,
                                                                 "correct_result": 0,
                                                                 "correct_home_score": 0,
                                                                 "correct_away_score": 1,
                                                                 "joker_multiplier": 2})))


if __name__ == "__main__":
    print(Prediction.objects.game_leaderboard(1))
    #TODO: move these to tests
