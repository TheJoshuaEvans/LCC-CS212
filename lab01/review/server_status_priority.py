# Maksym Kholodenko, Group B, Lab 1, Problem 2 Solution: Server Status and Priority Alert
# This program determines the alert priority for a server based on its health code and the time since the last check.



def determine_alert_priority(health_code, hours_since_last_check):
    priority = "N/A"

    print("\n--- Server Status and Priority Alert ---")
    print(f"Health Code: {health_code}")
    print(f"Time Since Last Check: {hours_since_last_check} hour(s)")

    # Health Code 1 means Critical, so the priority is always HIGH
    if health_code == 1:
        priority = "HIGH"

    # Health Code 2 means Warning
    elif health_code == 2:
        if hours_since_last_check > 4:
            priority = "HIGH"
        else:
            priority = "MEDIUM"

    # Health Code 3 means Optimal
    elif health_code == 3:
        if hours_since_last_check > 10:
            priority = "LOW"
        else:
            priority = "CLEAR"

    # Any other health code is invalid
    else:
        priority = "Error: Invalid health code."

    print(f"Alert Priority: {priority}")
    print("----------------------------------------")


# Example 1: Critical server, time does not matter
determine_alert_priority(1, 2)

# Example 2: Warning server, more than 4 hours since last check
determine_alert_priority(2, 5)

# Example 3: Warning server, 4 hours or less since last check
determine_alert_priority(2, 4)

# Example 4: Optimal server, more than 10 hours since last check
determine_alert_priority(3, 12)

# Example 5: Optimal server, 10 hours or less since last check
determine_alert_priority(3, 8)