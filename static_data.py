STATIC_QUESTIONS = {
    "Dates":[
        {"id": 1,"text": "Policy effective date:", "type": "date"} 
    ],
    "Renewal Meeting":[
        {"id": 2, "text": "Was a renewal meeting held?:", "type": "boolean"},
        {"id": 3, "text": "Was a renewal Agenda shared with the client", "type": "boolean"},
        {"id": 4, "text": "If No renewal meeting was held – Give a reason (briefly):", "requires_reason": False}
    ],
    "Client training & Education":[
        {"id": 5, "text": "Did the RM give the client Insurance training on relevant issues?", "type": "boolean"},
        {"id": 6, "text": "Did the RM give the client Insurance training on relevant issues?", "type": "boolean"}
    ],
    "Other Client Meetings / Engagements including client entertainment":[
        {"id": 7, "text": "During the policy period, were client meetings held?", "type": "boolean"},
        {"id": 8, "text": "Were minutes taken of these meetings and shared with the client?", "type": "boolean"}
    ],
    "Service Level":[
        {"id": 9, "text": "Do we have SLA with the client?", "type": "boolean"},
        {"id": 10, "text": "Did the client review Minet’s SLA and feedback given?", "type": "boolean"}
    ],
    "Policy Document":[
        {"id": 11, "text": "Are the copies of policy documents / Endorsements in the various files.", "type": "boolean"},
        {"id": 12, "text": "Have these policy documents been reviewed and confirmed that they correspond with the risk notes?", "type": "boolean"}
    ],
    "Reimbursement":[
        {"id": 13, "text": "ct?", "type": "boolean"}
    ],
    "Filing & Documentation":[
        {"id": 23, "text": "Has the AH filed the following documents?", "type": "static"},
        {"id": 14, "text": "Renewal Minutes:", "type": "boolean"},
        {"id": 15, "text": "Renewal Notice/Agenda:", "type": "boolean"},
        {"id": 16, "text": "Policy documents", "type": "boolean"},
        {"id": 17, "text": "Policy forwarding letter:", "type": "boolean"},
        {"id": 18, "text": "Policy document review form:", "type": "boolean"},
        {"id": 19, "text": "Minutes for other meetings held with the client:", "type":"boolean"}
    ],
    "Credit Control":[
        {"id": 20, "text": "Does the client have any outstanding balance over 365 days?", "type": "boolean"},
        {"id": 21, "text": "Does the client have any outstanding balance over 60 days", "type": "boolean"},
        {"id": 22, "text": "Is there a documented payment plan for the pending balances?", "type": "boolean"}
    ]
}
COVER_TYPES = ["Insured", "Hybrid", "Funded"]
