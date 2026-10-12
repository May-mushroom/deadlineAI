# Task.status values
STATUS_UNASSIGNED = 0  # no day chosen yet (week pool)
STATUS_ASSIGNED = 1  # has a TaskDistribution row (a specific day)
STATUS_PENDING = 2 # pending: just a task no pool, no deadlines
STATUS_DONE = 3 # done

SRC_MANUAL = "manual"
SRC_GOOGLE = "google_calendar"
