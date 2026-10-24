from app.services.resume.onet_skills import ONET_SKILLS


RECOMMENDATION_GUIDE = {

    # Cloud
    "Amazon Web Services": "Learn core AWS services (EC2, S3, IAM) and deploy one full-stack project on AWS.",
    "Microsoft Azure": "Understand Azure fundamentals and deploy a web application using Azure App Services.",
    "Google Cloud Platform": "Learn GCP basics and deploy a backend service using Cloud Run or Compute Engine.",

    # Programming
    "Java": "Build a REST API using Spring Boot and connect it with a relational database.",
    "Python": "Practice advanced Python concepts and build backend APIs using FastAPI or Django.",

    # Frameworks
    "Django": "Build a CRUD web application using Django and deploy it.",
    "Spring Boot": "Develop a backend microservice using Spring Boot with authentication.",
    "Angular.js": "Create a responsive frontend dashboard using Angular.",
    "Vue.js": "Build a small interactive frontend application using Vue.js.",

    # Tools
    "npm": "Understand npm package management and build a Node.js project with dependency management.",
    "GitLab": "Practice CI/CD pipelines using GitLab CI.",

    # Soft Skills
    "Teamwork": "Participate in collaborative projects or open-source contributions to improve teamwork skills."
}


def generate_recommendations(critical_missing, moderate_missing):

    recommendations = []

    for skill in critical_missing + moderate_missing:

        suggestion = RECOMMENDATION_GUIDE.get(
            skill,
            f"Consider gaining practical experience in {skill} through projects or certification."
        )

        recommendations.append({
            "skill": skill,
            "suggestion": suggestion
        })

    return recommendations
