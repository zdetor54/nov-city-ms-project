import pandas as pd
import json
import os


class CTA_Evaluator:
  def __init__(self, answer_file_path, round=1):
    """
    `round` : Holds the round for which the evaluation is being done. 
    can be 1, 2...upto the number of rounds the challenge has.
    Different rounds will mostly have different ground truth files.
    """
    self.answer_file_path = answer_file_path
    self.round = round

  def _evaluate(self, client_payload, _context={}):
    """
    `client_payload` will be a dict with (atleast) the following keys :
      - submission_file_path : local file path of the submitted file
      - aicrowd_submission_id : A unique id representing the submission
      - aicrowd_participant_id : A unique id for participant/team submitting (if enabled)
    """
    submission_file_path = client_payload["submission_file_path"]
    aicrowd_submission_id = client_payload["aicrowd_submission_id"]
    aicrowd_participant_uid = client_payload["aicrowd_participant_id"]

    cols, col_type = set(), dict()
    gt = pd.read_csv(self.answer_file_path, delimiter=',', names=['tab_id', 'col_id', 'type'],
                     dtype={'tab_id': str, 'col_id': str, 'type': str}, keep_default_na=False)
    for index, row in gt.iterrows():
        col = '%s %s' % (row['tab_id'], row['col_id'])
        gt_type = row['type']
        col_type[col] = gt_type
        cols.add(col)

    annotated_cols = set()
    TP = 0
    valid_annotations = 0
    sub = pd.read_csv(submission_file_path, delimiter=',', names=['tab_id', 'col_id', 'annotation'],
                      dtype={'tab_id': str, 'col_id': str, 'annotation': str}, keep_default_na=False)
    for index, row in sub.iterrows():
        col = '%s_schema %s' % (row['tab_id'], row['col_id'])
        if col in annotated_cols:
            # continue
            raise Exception("Duplicate columns in the submission file")
        else:
            annotated_cols.add(col)
        annotation = row['annotation'].lower()
        if annotation.startswith('https://schema.org/'):
            annotation = annotation.replace('https://schema.org/', 'schema:')
        elif not annotation.startswith('schema:'):
            annotation = 'schema:' + annotation

        if col in cols:
            valid_annotations += 1
            gt = col_type[col]
            if gt.lower() == annotation.lower():
                TP = TP + 1

    precision = TP / valid_annotations if valid_annotations > 0 else 0
    recall = TP / len(cols)
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    main_score = f1
    secondary_score = precision

    print('%.3f %.3f %.3f' % (f1, precision, recall))

    """
    Do something with your submitted file to come up
    with a score and a secondary score.

    if you want to report back an error to the user,
    then you can simply do :
      `raise Exception("YOUR-CUSTOM-ERROR")`

     You are encouraged to add as many validations as possible
     to provide meaningful feedback to your users
    """
    _result_object = {
        "score": main_score,
        "score_secondary": secondary_score
    }
    return _result_object


if __name__ == "__main__":
    # Lets assume the the ground_truth is a CSV file
    # and is present at data/ground_truth.csv
    # and a sample submission is present at data/sample_submission.csv
    answer_file_path = "DataSets/GitTables_CTA_SCH/GitTables_CTA_SCH_gt.csv"
    d = 'DataSets/GitTables_CTA_SCH_Sub/'
    for ff in os.listdir(d):
        _client_payload = {}
        print(ff)
        _client_payload["submission_file_path"] = d + ff
        _client_payload["aicrowd_submission_id"] = 1123
        _client_payload["aicrowd_participant_id"] = 1234
    
        # Instaiate a dummy context
        _context = {}
        # Instantiate an evaluator
        aicrowd_evaluator = CTA_Evaluator(answer_file_path)
        # Evaluate
        result = aicrowd_evaluator._evaluate(_client_payload, _context)
        print(result)
