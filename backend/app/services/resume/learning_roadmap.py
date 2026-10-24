LEARNING_GUIDE = {

    # -------- CLOUD --------
    "Amazon Web Services": {
        "roadmap": [
            "Understand AWS core services (EC2, S3, IAM).",
            "Learn VPC and networking basics.",
            "Deploy a full-stack application on AWS.",
            "Explore AWS certifications (Cloud Practitioner)."
        ],
        "youtube_links": [
            "https://www.youtube.com/watch?v=3hLmDS179YE",  # AWS Full Course
            "https://www.youtube.com/watch?v=ulprqHHWlng"
        ]
    },

    "Microsoft Azure": {
        "roadmap": [
            "Learn Azure fundamentals.",
            "Understand Azure App Services.",
            "Deploy backend service on Azure.",
            "Study Azure certification roadmap."
        ],
        "youtube_links": [
            "https://www.youtube.com/watch?v=NKEFWyqJ5XA"
        ]
    },

    "Google Cloud Platform": {
        "roadmap": [
            "Learn GCP core services.",
            "Understand Compute Engine and Cloud Run.",
            "Deploy backend API on GCP.",
            "Explore GCP IAM and security."
        ],
        "youtube_links": [
            "https://www.youtube.com/watch?v=JPc-H1r7kL8"
        ]
    },

    # -------- PROGRAMMING --------
    "Java": {
        "roadmap": [
            "Revise Java basics and OOP concepts.",
            "Learn Spring Boot fundamentals.",
            "Build REST APIs using Spring Boot.",
            "Connect with MySQL or PostgreSQL database."
        ],
        "youtube_links": [
            "https://www.youtube.com/watch?v=eIrMbAQSU34"
        ]
    },

    # -------- FRAMEWORKS --------
    "Spring Boot": {
        "roadmap": [
            "Understand Spring Boot architecture.",
            "Create REST APIs.",
            "Add JWT authentication.",
            "Deploy Spring Boot app."
        ],
        "youtube_links": [
            "https://www.youtube.com/watch?v=vtPkZShrvXQ"
        ]
    },

    "Django": {
        "roadmap": [
            "Learn Django project structure.",
            "Build CRUD application.",
            "Implement authentication.",
            "Deploy Django app."
        ],
        "youtube_links": [
            "https://www.youtube.com/watch?v=F5mRW0jo-U4"
        ]
    }
}

def generate_learning_roadmap(critical_missing, moderate_missing):

    learning_plan = []

    for skill in critical_missing:

        entry = {
            "skill": skill,
            "priority": "High",
        }

        if skill in LEARNING_GUIDE:
            entry["roadmap_steps"] = LEARNING_GUIDE[skill]["roadmap"]
            entry["youtube_resources"] = LEARNING_GUIDE[skill]["youtube_links"]
        else:
            entry["roadmap_steps"] = [
                f"Start with fundamentals of {skill}.",
                f"Build one practical project using {skill}.",
                f"Deploy or showcase the project publicly."
            ]
            entry["youtube_resources"] = []

        learning_plan.append(entry)

    for skill in moderate_missing:

        entry = {
            "skill": skill,
            "priority": "Medium",
        }

        if skill in LEARNING_GUIDE:
            entry["roadmap_steps"] = LEARNING_GUIDE[skill]["roadmap"]
            entry["youtube_resources"] = LEARNING_GUIDE[skill]["youtube_links"]
        else:
            entry["roadmap_steps"] = [
                f"Learn fundamentals of {skill}.",
                f"Build one small project.",
                f"Add it to your resume."
            ]
            entry["youtube_resources"] = []

        learning_plan.append(entry)

    return learning_plan
