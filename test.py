#%%
from datetime import datetime as dt
from collections import defaultdict
import numpy as np
import unicodecsv


def parse_date(date):
    if date == '':
        return None
    else:
        return dt.strptime(date, '%Y-%m-%d')


def parse_maybe_int(i):
    if i == '':
        return None
    else:
        return int(i)


def read_csv(filename):
    with open(filename, 'rb') as file:
        reader = unicodecsv.DictReader(file)
        return list(reader)

# Takes a student's join date and the date of a specific engagement record,
# and returns True if that engagement record happened within one week
# of the student joining.


def within_one_week(join_date, engagement_date):
    time_delta = engagement_date - join_date
    return time_delta.days < 7 and time_delta.days >= 0


def clean_enrollments(enrollments):
    for enrollment in enrollments:
        enrollment['cancel_date'] = parse_date(enrollment['cancel_date'])
        enrollment['days_to_cancel'] = parse_maybe_int(
            enrollment['days_to_cancel'])
        enrollment['is_canceled'] = enrollment['is_canceled'] == 'True'
        enrollment['is_udacity'] = enrollment['is_udacity'] == 'True'
        enrollment['join_date'] = parse_date(enrollment['join_date'])
    return enrollments


def clean_engagements(daily_engagement):
    for engagement_record in daily_engagement:
        engagement_record['lessons_completed'] = int(
            float(engagement_record['lessons_completed']))
        engagement_record['num_courses_visited'] = int(
            float(engagement_record['num_courses_visited']))
        engagement_record['projects_completed'] = int(
            float(engagement_record['projects_completed']))
        engagement_record['total_minutes_visited'] = float(
            engagement_record['total_minutes_visited'])
        engagement_record['utc_date'] = parse_date(
            engagement_record['utc_date'])
        engagement_record['account_key'] = engagement_record['acct']
        del engagement_record['acct']
    return daily_engagement


def clean_submissions(project_submissions):
    for submission in project_submissions:
        submission['completion_date'] = parse_date(submission['completion_date'])
        submission['creation_date'] = parse_date(submission['creation_date'])
    return project_submissions


def list_udacity_test_accounts(enrollments):
    udacity_test_accounts = set()
    for enrollment in enrollments:
        if enrollment['is_udacity']:
            udacity_test_accounts.add(enrollment['account_key'])
    return udacity_test_accounts


def remove_udacity_accounts(udacity_test_accounts, data):
    non_udacity_data = []
    for data_point in data:
        if data_point['account_key'] not in udacity_test_accounts:
            non_udacity_data.append(data_point)
    return non_udacity_data


def list_paid_students(enrollments):
    paid_students = {}
    for enrollment in enrollments:
        stid = enrollment['account_key']
        if not enrollment['is_canceled'] or enrollment['days_to_cancel'] > 7:
            if not(stid in paid_students and paid_students[stid] > enrollment['join_date']):
                paid_students[stid] = enrollment['join_date']
    return paid_students


def group_engagements_by_account(engagements):
    engagement_by_account = defaultdict(list)
    for engagement_record in engagements:
        account_key = engagement_record['account_key']
        engagement_by_account[account_key].append(engagement_record)
    return engagement_by_account


def get_stats_by_account(engagement_by_account, attribute):
    stats = {}
    for account_key, engagement_for_student in engagement_by_account.items():
        attribute_total = 0
        for engagement_record in engagement_for_student:
            attribute_total += engagement_record[attribute]
        stats[account_key] = attribute_total
    return stats

def get_dictionary_values(dictionary):
    return list(dictionary.values())

def print_stats(engagements, attribute):
    engagement_by_account = group_engagements_by_account(engagements)
    totals = get_dictionary_values(get_stats_by_account(engagement_by_account, attribute))
    print(attribute, 'stats')
    print('Mean:', np.mean(totals))
    print('Standard deviation:', np.std(totals))
    print('Minimum:', np.min(totals))
    print('Maximum:', np.max(totals))

def main():
    enrollments = clean_enrollments(read_csv('enrollments.csv'))
    daily_engagement = clean_engagements(read_csv('daily_engagement.csv'))
    project_submissions = clean_submissions(read_csv('project_submissions.csv'))
    udacity_test_accounts = list_udacity_test_accounts(enrollments)
    non_udacity_enrollments = remove_udacity_accounts(udacity_test_accounts, enrollments)
    non_udacity_engagements = remove_udacity_accounts(udacity_test_accounts, daily_engagement)
    non_udacity_submissions = remove_udacity_accounts(udacity_test_accounts, project_submissions)

    paid_students = list_paid_students(non_udacity_enrollments)

    paid_engagement_in_first_week = []
    for eng in non_udacity_engagements:
        student = eng['account_key']
        if student in paid_students and within_one_week(paid_students[student], eng['utc_date']):
            paid_engagement_in_first_week.append(eng)

    # Summarize the data about minutes spent in the classroom
    print_stats(paid_engagement_in_first_week, 'total_minutes_visited')
    print_stats(paid_engagement_in_first_week, 'num_courses_visited')
    print_stats(paid_engagement_in_first_week, 'lessons_completed')
    print_stats(paid_engagement_in_first_week, 'projects_completed')


main()
