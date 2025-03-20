# Define the hierarchy (Modify as needed)
HIERARCHY = {
    "Relationship Manager": ["Scheme Administrator"],
    "Scheme Administrator": ["Wellness"],
    "Wellness": ["Reimbursement"],
    "Reimbursement": ["Healthcare AGM"],
    "Healthcare AGM": ["Healthcare GM"],
    "Healthcare GM": []  # No one after GM
}

# Mock function to fetch users for a role
def get_users_by_role(role: str):
    user_emails = {
        "Relationship Manager": ["frankfrankinstine50@gmail.com"],  # ✅ Added email
        "Scheme Administrator": ["francoismogaka@gmail.com"],
        "Wellness": ["wellness1@example.com", "wellness2@example.com"],
        "Reimbursement": ["reim1@example.com", "reim2@example.com"],
        "Healthcare AGM": ["agm1@example.com", "agm2@example.com"],
        "Healthcare GM": ["gm@example.com"]
    }
    print(f"Fetching users for role: {role}")
    print(f"Users: {user_emails.get(role, [])}")  # Debugging output
    return user_emails.get(role, [])

# Fetch next role's users
def get_next_role_users(current_role: str):
    next_roles = HIERARCHY.get(current_role, [])
    recipients = []
    for role in next_roles:
        recipients.extend(get_users_by_role(role))
    return recipients
