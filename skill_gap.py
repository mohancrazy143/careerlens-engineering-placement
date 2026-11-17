"""
skill_gap.py
============
Skill-gap analysis for a TARGET JOB ROLE, built on top of employability_core.

Flow:  target role  ->  skills the student HAS (resume + confirmations)
                    ->  required skills for the role (core / preferred)
                    ->  gap table, readiness score, learning plan, projects, certs
                    ->  (optional) what-if with the saved model.

Nothing here fits or retrains any model. The role catalog is a hand-written,
editable reference (ROLES / SKILL_DB below), not scraped live job-market data.
"""
import re
import difflib

import numpy as np
import pandas as pd

# =============================================================================
# 1. SKILL DATABASE   name -> (category, [aliases used to find it in resume text])
#    Aliases of length <= 2 (C, R, Go, C#) are matched case-sensitively.
# =============================================================================
SKILL_DB = {
    # Programming
    "Python": ("Programming", ["python", "python3"]),
    "Java": ("Programming", ["java", "core java"]),
    "C": ("Programming", ["C"]),
    "C++": ("Programming", ["C++", "cpp"]),
    "JavaScript": ("Programming", ["javascript", "js", "es6"]),
    "TypeScript": ("Programming", ["typescript"]),
    "SQL": ("Programming", ["sql", "t-sql", "pl/sql"]),
    "R": ("Programming", ["R", "rstudio"]),
    "Kotlin": ("Programming", ["kotlin"]),
    "Dart": ("Programming", ["dart"]),
    "Bash/Shell": ("Programming", ["bash", "shell scripting", "shell script", "shell"]),
    # Core CS
    "Data Structures & Algorithms": ("Core CS", ["data structures", "dsa", "algorithms", "data structures and algorithms"]),
    "OOP": ("Core CS", ["oop", "oops", "object oriented", "object-oriented"]),
    "Operating Systems": ("Core CS", ["operating systems", "operating system"]),
    "Computer Networks": ("Core CS", ["computer networks", "computer networking", "tcp/ip", "networking"]),
    "DBMS": ("Core CS", ["dbms", "database management"]),
    "System Design": ("Core CS", ["system design", "low level design", "high level design", "microservices"]),
    # Data & analytics
    "Excel": ("Data & Analytics", ["excel", "advanced excel", "pivot table", "pivot tables", "vlookup"]),
    "Statistics": ("Data & Analytics", ["statistics", "statistical analysis", "hypothesis testing", "probability"]),
    "Pandas": ("Data & Analytics", ["pandas"]),
    "NumPy": ("Data & Analytics", ["numpy"]),
    "Data Visualization": ("Data & Analytics", ["data visualization", "data visualisation", "matplotlib", "seaborn", "plotly"]),
    "Power BI": ("Data & Analytics", ["power bi", "powerbi"]),
    "Tableau": ("Data & Analytics", ["tableau"]),
    "ETL": ("Data & Analytics", ["etl", "elt", "data pipeline", "data pipelines"]),
    "Data Warehousing": ("Data & Analytics", ["data warehouse", "data warehousing", "snowflake", "redshift", "bigquery"]),
    "Apache Spark": ("Data & Analytics", ["spark", "pyspark", "apache spark"]),
    "Airflow": ("Data & Analytics", ["airflow", "apache airflow"]),
    "Kafka": ("Data & Analytics", ["kafka", "apache kafka"]),
    # AI / ML
    "Machine Learning": ("AI / ML", ["machine learning", "ml models", "supervised learning"]),
    "Scikit-learn": ("AI / ML", ["scikit-learn", "scikit learn", "sklearn"]),
    "Deep Learning": ("AI / ML", ["deep learning", "neural network", "neural networks", "cnn", "rnn", "lstm"]),
    "TensorFlow": ("AI / ML", ["tensorflow", "keras"]),
    "PyTorch": ("AI / ML", ["pytorch", "torch"]),
    "NLP": ("AI / ML", ["nlp", "natural language processing", "text mining", "bert", "spacy", "nltk"]),
    "Computer Vision": ("AI / ML", ["computer vision", "opencv", "image processing", "yolo"]),
    "Generative AI": ("AI / ML", ["generative ai", "genai", "llm", "llms", "large language model", "large language models", "rag"]),
    "Prompt Engineering": ("AI / ML", ["prompt engineering", "prompt design"]),
    "LangChain": ("AI / ML", ["langchain", "llamaindex", "llama index"]),
    "Vector Databases": ("AI / ML", ["vector database", "vector databases", "faiss", "pinecone", "chroma", "chromadb", "weaviate"]),
    "MLOps": ("AI / ML", ["mlops", "mlflow", "model deployment", "kubeflow"]),
    # Web & APIs
    "HTML": ("Web & APIs", ["html", "html5"]),
    "CSS": ("Web & APIs", ["css", "css3", "tailwind", "bootstrap", "sass"]),
    "React": ("Web & APIs", ["react", "reactjs", "react.js", "next.js", "nextjs"]),
    "Node.js": ("Web & APIs", ["node.js", "nodejs", "node js", "express", "express.js"]),
    "REST APIs": ("Web & APIs", ["rest api", "rest apis", "restful", "restful api", "restful apis", "api development", "graphql"]),
    "Django": ("Web & APIs", ["django"]),
    "Flask": ("Web & APIs", ["flask"]),
    "FastAPI": ("Web & APIs", ["fastapi"]),
    "Spring Boot": ("Web & APIs", ["spring boot", "springboot", "spring"]),
    "Responsive Design": ("Web & APIs", ["responsive design", "responsive web", "mobile-first", "media queries"]),
    # Databases
    "MySQL": ("Databases", ["mysql"]),
    "PostgreSQL": ("Databases", ["postgresql", "postgres"]),
    "MongoDB": ("Databases", ["mongodb", "mongo db", "nosql"]),
    "Database Design": ("Databases", ["database design", "schema design", "normalization", "normalisation", "er diagram", "er diagrams"]),
    # DevOps & cloud
    "Git": ("DevOps & Cloud", ["git", "github", "gitlab", "version control"]),
    "Linux": ("DevOps & Cloud", ["linux", "ubuntu", "unix"]),
    "Docker": ("DevOps & Cloud", ["docker", "containerization", "containerisation"]),
    "Kubernetes": ("DevOps & Cloud", ["kubernetes", "k8s", "helm"]),
    "CI/CD": ("DevOps & Cloud", ["ci/cd", "ci cd", "github actions", "gitlab ci", "continuous integration"]),
    "Jenkins": ("DevOps & Cloud", ["jenkins"]),
    "Terraform": ("DevOps & Cloud", ["terraform", "infrastructure as code"]),
    "Ansible": ("DevOps & Cloud", ["ansible"]),
    "AWS": ("DevOps & Cloud", ["aws", "amazon web services", "ec2", "s3", "lambda"]),
    "Azure": ("DevOps & Cloud", ["azure", "microsoft azure"]),
    "GCP": ("DevOps & Cloud", ["gcp", "google cloud"]),
    "Monitoring": ("DevOps & Cloud", ["prometheus", "grafana", "monitoring", "observability", "datadog"]),
    # Security
    "Network Security": ("Security", ["network security", "firewall", "firewalls", "ids/ips", "vpn"]),
    "Penetration Testing": ("Security", ["penetration testing", "pentesting", "pen testing", "ethical hacking", "metasploit", "burp suite"]),
    "Cryptography": ("Security", ["cryptography", "encryption", "pki"]),
    "SIEM": ("Security", ["siem", "splunk", "qradar", "soc analyst"]),
    "Vulnerability Assessment": ("Security", ["vulnerability assessment", "vulnerability scanning", "nessus", "openvas"]),
    "Incident Response": ("Security", ["incident response", "threat hunting", "digital forensics", "forensics"]),
    "OWASP": ("Security", ["owasp", "owasp top 10", "web application security"]),
    "Wireshark": ("Security", ["wireshark", "packet analysis"]),
    "Kali Linux": ("Security", ["kali linux", "kali"]),
    "Nmap": ("Security", ["nmap"]),
    # Testing & process
    "Manual Testing": ("Testing & Process", ["manual testing", "functional testing", "regression testing"]),
    "Test Case Design": ("Testing & Process", ["test case", "test cases", "test plan", "test scenarios", "bug report", "defect tracking"]),
    "Selenium": ("Testing & Process", ["selenium", "webdriver", "cypress", "playwright"]),
    "Test Automation": ("Testing & Process", ["test automation", "automation testing", "automated testing", "testng", "pytest"]),
    "API Testing": ("Testing & Process", ["api testing", "rest assured"]),
    "Postman": ("Testing & Process", ["postman"]),
    "JUnit": ("Testing & Process", ["junit", "unit testing", "unit tests"]),
    "SDLC": ("Testing & Process", ["sdlc", "software development life cycle", "stlc"]),
    "Agile/Scrum": ("Testing & Process", ["agile", "scrum", "kanban", "sprint"]),
    "JIRA": ("Testing & Process", ["jira", "confluence"]),
    # Mobile
    "Android": ("Mobile", ["android", "android studio", "android sdk"]),
    "Flutter": ("Mobile", ["flutter"]),
    "React Native": ("Mobile", ["react native"]),
    "Firebase": ("Mobile", ["firebase", "firestore"]),
    "Jetpack Compose": ("Mobile", ["jetpack compose", "compose ui"]),
    # Business analysis
    "Requirements Gathering": ("Business", ["requirements gathering", "requirement gathering", "requirements analysis", "brd", "frd", "user stories", "use cases"]),
    "UML": ("Business", ["uml", "use case diagram", "use case diagrams", "class diagram", "class diagrams", "bpmn"]),
    "Process Modeling": ("Business", ["process modeling", "process modelling", "process mapping", "workflow design", "visio"]),
    "Documentation": ("Business", ["documentation", "technical writing", "srs", "report writing"]),
    "Stakeholder Management": ("Business", ["stakeholder", "stakeholders", "client communication", "client interaction"]),
    # Embedded
    "Embedded C": ("Embedded", ["embedded c"]),
    "Microcontrollers": ("Embedded", ["microcontroller", "microcontrollers", "arduino", "stm32", "arm cortex", "8051", "esp32", "avr", "pic microcontroller"]),
    "RTOS": ("Embedded", ["rtos", "freertos", "real time operating system", "real-time operating system"]),
    "Communication Protocols": ("Embedded", ["i2c", "spi", "uart", "can bus", "modbus", "serial communication"]),
    "Circuit Design": ("Embedded", ["circuit design", "pcb design", "pcb", "schematic", "altium", "kicad", "proteus", "multisim"]),
    "Raspberry Pi": ("Embedded", ["raspberry pi"]),
    "IoT": ("Embedded", ["iot", "internet of things", "mqtt"]),
    # Design
    "Figma": ("Design", ["figma", "adobe xd", "sketch app"]),
    "Wireframing": ("Design", ["wireframe", "wireframes", "wireframing", "low fidelity", "mockups"]),
    "Prototyping": ("Design", ["prototyping", "prototype", "prototypes", "clickable prototype"]),
    "User Research": ("Design", ["user research", "usability testing", "user interviews", "personas", "persona", "ux research"]),
    "Design Systems": ("Design", ["design system", "design systems", "style guide", "component library"]),
}

# Rough weeks to reach "can use it in a small project" at ~8-10 hrs/week. Default = 3.
WEEKS = {
    "Python": 6, "Java": 8, "C": 6, "C++": 8, "JavaScript": 6, "TypeScript": 3, "SQL": 4, "R": 4, "Kotlin": 5,
    "Dart": 3, "Data Structures & Algorithms": 10, "OOP": 3, "Operating Systems": 5, "Computer Networks": 5,
    "DBMS": 4, "System Design": 6, "Statistics": 6, "Machine Learning": 8, "Deep Learning": 8, "NLP": 5,
    "Computer Vision": 5, "Generative AI": 4, "MLOps": 5, "React": 5, "Node.js": 4, "Django": 4,
    "Spring Boot": 5, "Kubernetes": 5, "Linux": 4, "AWS": 5, "Azure": 5, "GCP": 5, "Network Security": 6,
    "Penetration Testing": 6, "Cryptography": 4, "Android": 6, "Flutter": 5, "Embedded C": 5,
    "Microcontrollers": 4, "RTOS": 4, "Figma": 2, "Git": 1, "Postman": 1, "Excel": 2, "JIRA": 1, "Nmap": 1,
    "Wireshark": 1, "PyTorch": 5, "TensorFlow": 4, "Apache Spark": 4, "Kali Linux": 1, "HTML": 2, "CSS": 3, "Selenium": 3, "Docker": 2, "Tableau": 2, "Power BI": 3,
}

TIPS = {
    "Python": "Solve 50+ beginner-to-medium problems and build 2 small scripts/apps (HackerRank or LeetCode Easy tier is enough to start).",
    "SQL": "Practise joins, GROUP BY, window functions and subqueries on a real dataset; aim for 50+ queries.",
    "Data Structures & Algorithms": "Follow one structured list (arrays, strings, hashing, trees, graphs, DP) and solve a few problems every day; consistency beats volume.",
    "Statistics": "Cover descriptive stats, distributions, hypothesis testing and regression; apply each on a Kaggle or open dataset.",
    "Machine Learning": "Complete an introductory ML course, then reproduce a full workflow (cleaning, features, model, evaluation) on a Kaggle dataset.",
    "Git": "Use Git for every project from today; push to GitHub with clear commits and a README.",
    "Docker": "Containerise one of your existing projects and write a Dockerfile plus docker-compose file.",
    "REST APIs": "Build a CRUD API with authentication and test it in Postman; publish the docs.",
    "System Design": "Study the basics (load balancing, caching, databases, queues) and practise designing 5 common systems.",
    "Generative AI": "Build a small RAG chatbot over your own documents and document its limitations.",
    "Excel": "Learn pivot tables, lookups and charts by cleaning and summarising a public dataset.",
    "Power BI": "Build one end-to-end dashboard from a public dataset and publish a screenshot or link.",
}


def tip_for(skill):
    return TIPS.get(skill, f"Take one structured course on {skill}, then apply it in a small project and list the project on your resume.")


def weeks_for(skill):
    return WEEKS.get(skill, 3)


# =============================================================================
# 2. ROLE CATALOG (editable). Entries in core/preferred may be a tuple = "any one of".
# =============================================================================
ROLES = {
    "Data Analyst": dict(
        aliases=["data analytics", "business intelligence analyst", "bi analyst", "reporting analyst", "analyst"],
        core=["SQL", "Excel", "Statistics", "Data Visualization", "Python", "Power BI"],
        preferred=["Tableau", "Pandas", "NumPy", "ETL", "R"],
        min_projects=2,
        certifications=["Google Data Analytics Certificate", "Microsoft PL-300 (Power BI Data Analyst)", "Tableau Desktop Specialist"],
        projects=[("Sales or HR dashboard with KPIs, filters and a written insight summary", ["Power BI", "SQL", "Excel", "Data Visualization"]),
                  ("Exploratory data analysis of a public dataset with a clear business recommendation", ["Python", "Pandas", "Statistics", "Data Visualization"]),
                  ("SQL case study: answer 15 business questions on a sample database", ["SQL"]),
                  ("Tableau story on a public-health or finance dataset", ["Tableau", "Data Visualization"])],
        interview=["SQL joins and window functions", "A/B testing and hypothesis testing basics", "Explaining a dashboard to a non-technical person", "Excel pivot tables and lookups"]),
    "Data Scientist": dict(
        aliases=["data science", "ds", "applied scientist", "junior data scientist"],
        core=["Python", "Statistics", "Machine Learning", "Pandas", "NumPy", "Scikit-learn", "SQL", "Data Visualization"],
        preferred=["Deep Learning", "PyTorch", "TensorFlow", "NLP", "Apache Spark", "Git", "AWS"],
        min_projects=3,
        certifications=["DeepLearning.AI Machine Learning Specialization (Coursera)", "IBM Data Science Professional Certificate", "Microsoft DP-100 (Azure Data Scientist)"],
        projects=[("End-to-end prediction project (churn, price or risk) with proper train/test split and error analysis", ["Python", "Pandas", "Scikit-learn", "Machine Learning", "Statistics"]),
                  ("Kaggle competition entry with feature engineering and a written write-up", ["Python", "Machine Learning", "Pandas", "NumPy"]),
                  ("NLP sentiment or topic analysis on a real text dataset", ["NLP", "Python", "Deep Learning"]),
                  ("Deploy a trained model behind a simple web app", ["Python", "Machine Learning", "Git"])],
        interview=["Bias-variance, overfitting and regularisation", "Evaluation metrics (precision/recall/ROC-AUC) and when to use them", "SQL and pandas data manipulation", "Walking through one of your projects end to end"]),
    "Machine Learning Engineer": dict(
        aliases=["ml", "ml engineer", "mle", "ai ml engineer", "ai/ml engineer", "artificial intelligence engineer", "ai engineer"],
        core=["Python", "Machine Learning", "Deep Learning", "Scikit-learn", "PyTorch", "Data Structures & Algorithms", "Git", "Docker"],
        preferred=["TensorFlow", "MLOps", "FastAPI", "Kubernetes", "AWS", "Apache Spark", "SQL"],
        min_projects=3,
        certifications=["DeepLearning.AI Deep Learning Specialization", "AWS Certified Machine Learning Engineer - Associate", "Google Cloud Professional ML Engineer (later stage)"],
        projects=[("Train a deep learning model and serve it as a containerised API", ["PyTorch", "Deep Learning", "Docker", "FastAPI"]),
                  ("Reproduce a paper or a Kaggle solution and compare against a baseline", ["Python", "Machine Learning", "Scikit-learn"]),
                  ("Experiment tracking and model versioning pipeline", ["MLOps", "Git", "Python"]),
                  ("Image or text classifier with a monitored prediction endpoint", ["Deep Learning", "Docker", "AWS"])],
        interview=["Coding rounds on arrays, strings and hashing", "How backpropagation and gradient descent work", "Model deployment and monitoring trade-offs", "Debugging an underperforming model"]),
    "Generative AI Engineer": dict(
        aliases=["gen ai engineer", "genai engineer", "llm engineer", "generative ai developer", "ai application developer", "prompt engineer"],
        core=["Python", "Generative AI", "Prompt Engineering", "LangChain", "Vector Databases", "NLP", "REST APIs", "FastAPI"],
        preferred=["PyTorch", "Deep Learning", "Docker", "Git", "MLOps", "AWS"],
        min_projects=3,
        certifications=["DeepLearning.AI short courses on LLMs, RAG and agents", "Microsoft AI-102 (Azure AI Engineer Associate)", "Cloud provider AI fundamentals (AWS / Azure / Google Cloud)"],
        projects=[("RAG question-answering bot over your own PDFs with source citations", ["Generative AI", "LangChain", "Vector Databases", "Python"]),
                  ("LLM-powered API service with prompt versioning and basic evaluation", ["FastAPI", "REST APIs", "Prompt Engineering"]),
                  ("Text summariser or classifier comparing a fine-tuned model with prompting", ["NLP", "PyTorch", "Deep Learning"]),
                  ("Containerised chatbot deployed to a cloud free tier", ["Docker", "AWS", "Git"])],
        interview=["How RAG works and where it fails", "Prompt design and evaluation methods", "Embeddings and vector search basics", "API design and latency/cost trade-offs"]),
    "Data Engineer": dict(
        aliases=["big data engineer", "etl developer", "data pipeline engineer", "analytics engineer"],
        core=["SQL", "Python", "ETL", "Data Warehousing", "Apache Spark", "Airflow", "Linux", "Git"],
        preferred=["Kafka", "AWS", "Docker", "PostgreSQL", "Kubernetes", "Azure"],
        min_projects=3,
        certifications=["Databricks Certified Data Engineer Associate", "Google Professional Data Engineer (later stage)", "Microsoft DP-700 (Fabric Data Engineer Associate)"],
        projects=[("Batch ETL pipeline from an API into a warehouse, scheduled with Airflow", ["ETL", "Airflow", "Python", "SQL", "Data Warehousing"]),
                  ("PySpark job processing a multi-GB public dataset", ["Apache Spark", "Python"]),
                  ("Streaming pipeline with Kafka and a simple dashboard", ["Kafka", "Python"]),
                  ("Dockerised data pipeline with tests and README", ["Docker", "Git", "Linux"])],
        interview=["Advanced SQL (windows, CTEs, query tuning)", "Star schema and data modelling", "Batch vs streaming trade-offs", "Spark partitioning and shuffles"]),
    "Software Developer": dict(
        aliases=["software engineer", "sde", "sde 1", "software development engineer", "programmer", "application developer", "software developer trainee", "associate software engineer"],
        core=["Data Structures & Algorithms", "OOP", ("Java", "Python", "C++"), "SQL", "DBMS", "Operating Systems", "Git"],
        preferred=["System Design", "Computer Networks", "REST APIs", "Docker", "Linux"],
        min_projects=2,
        certifications=["NPTEL Data Structures and Algorithms", "Oracle Java SE Programmer (if Java-focused)", "Cloud fundamentals (AWS Cloud Practitioner or Azure AZ-900)"],
        projects=[("Full application with login, CRUD and a database (for example a library or expense manager)", ["OOP", "SQL", "DBMS", "Git"]),
                  ("Implement core data structures from scratch with unit tests", ["Data Structures & Algorithms", "OOP"]),
                  ("Multi-threaded or file-system based tool that exercises OS concepts", ["Operating Systems", "OOP"]),
                  ("REST service containerised with Docker", ["REST APIs", "Docker", "Git"])],
        interview=["Arrays, strings, hashing, trees, graphs, DP", "OOP principles and SOLID", "DBMS normalisation, transactions and indexing", "OS: processes, threads, deadlocks, memory"]),
    "Backend Developer": dict(
        aliases=["backend engineer", "back end developer", "server side developer", "java developer", "python developer", "api developer", "node developer"],
        core=[("Java", "Python", "Node.js"), "Data Structures & Algorithms", "OOP", "REST APIs", "SQL", "Database Design", "Git"],
        preferred=["Spring Boot", "Django", "MongoDB", "Docker", "System Design", "AWS", "Operating Systems"],
        min_projects=3,
        certifications=["Oracle Java SE Programmer (Java track)", "AWS Cloud Practitioner / Solutions Architect Associate", "NPTEL Database Management Systems"],
        projects=[("REST API with JWT authentication, pagination, validation and tests", ["REST APIs", "SQL", "Database Design", "Git"]),
                  ("E-commerce or booking backend with relational schema and transactions", ["Database Design", "SQL", "Spring Boot", "Django"]),
                  ("Rate-limited or cached API using Redis-style caching concepts", ["System Design", "REST APIs"]),
                  ("Dockerised service deployed on a cloud free tier", ["Docker", "AWS", "Git"])],
        interview=["REST design and HTTP status codes", "SQL joins, indexes and transactions", "Authentication and authorisation flows", "Designing a URL shortener or similar small system"]),
    "Frontend Developer": dict(
        aliases=["front end developer", "front-end developer", "ui developer", "web developer", "react developer", "javascript developer"],
        core=["HTML", "CSS", "JavaScript", "React", "Responsive Design", "Git", "REST APIs"],
        preferred=["TypeScript", "Figma", "Node.js"],
        min_projects=3,
        certifications=["Meta Front-End Developer Professional Certificate (Coursera)", "freeCodeCamp Responsive Web Design / JavaScript certifications"],
        projects=[("Responsive portfolio site deployed on GitHub Pages or Netlify", ["HTML", "CSS", "Responsive Design", "Git"]),
                  ("React app that consumes a public API with loading and error states", ["React", "JavaScript", "REST APIs"]),
                  ("Clone of a real product page or dashboard with reusable components", ["React", "CSS"]),
                  ("Convert a Figma design to pixel-accurate code", ["Figma", "HTML", "CSS"])],
        interview=["JavaScript closures, promises and the event loop", "React hooks and state management", "CSS layout (flexbox/grid) and accessibility", "Browser rendering and performance basics"]),
    "Full Stack Developer": dict(
        aliases=["fullstack developer", "full-stack developer", "mern developer", "mean developer", "full stack engineer"],
        core=["HTML", "CSS", "JavaScript", "React", "Node.js", "REST APIs", ("SQL", "MongoDB"), "Git"],
        preferred=["TypeScript", "Docker", "AWS", "System Design", "Django"],
        min_projects=3,
        certifications=["freeCodeCamp Full Stack certifications", "Meta Full-Stack or Back-End Developer certificates (Coursera)", "AWS Cloud Practitioner"],
        projects=[("Full-stack app with auth, CRUD and a database, deployed publicly", ["React", "Node.js", "REST APIs", "MongoDB", "SQL"]),
                  ("Real-time chat or collaborative tool", ["Node.js", "JavaScript", "React"]),
                  ("Dockerised app with CI pipeline", ["Docker", "Git", "AWS"]),
                  ("Admin dashboard with role-based access", ["React", "REST APIs", "CSS"])],
        interview=["End-to-end request flow from browser to database", "JavaScript and React fundamentals", "SQL vs NoSQL choices", "Securing an API (auth, CORS, validation)"]),
    "DevOps Engineer": dict(
        aliases=["devops", "site reliability engineer", "sre", "build and release engineer", "platform engineer"],
        core=["Linux", "Bash/Shell", "Git", "Docker", "CI/CD", ("AWS", "Azure", "GCP"), "Kubernetes"],
        preferred=["Terraform", "Ansible", "Jenkins", "Monitoring", "Python", "Computer Networks"],
        min_projects=3,
        certifications=["AWS Cloud Practitioner then Solutions Architect Associate", "Certified Kubernetes Application Developer (CKAD)", "HashiCorp Terraform Associate"],
        projects=[("CI/CD pipeline that builds, tests and deploys a containerised app", ["CI/CD", "Docker", "Git", "Jenkins"]),
                  ("Deploy an app to Kubernetes (minikube or kind) with health checks", ["Kubernetes", "Docker"]),
                  ("Provision cloud infrastructure with Terraform", ["Terraform", "AWS", "Azure", "GCP"]),
                  ("Monitoring dashboard with alerts for a sample service", ["Monitoring", "Linux"])],
        interview=["Linux troubleshooting (processes, disk, networking)", "Docker image layers and networking", "CI/CD stages and rollback strategies", "Kubernetes pods, services and deployments"]),
    "Cloud Engineer": dict(
        aliases=["cloud architect", "cloud administrator", "cloud support engineer", "aws engineer", "azure engineer", "cloud developer"],
        core=[("AWS", "Azure", "GCP"), "Linux", "Computer Networks", "Docker", "Git", "Bash/Shell"],
        preferred=["Terraform", "Kubernetes", "CI/CD", "Python", "Monitoring", "Network Security"],
        min_projects=2,
        certifications=["AWS Cloud Practitioner -> Solutions Architect Associate", "Microsoft AZ-900 -> AZ-104", "Google Associate Cloud Engineer"],
        projects=[("Three-tier web app hosted on a cloud provider with a load balancer", ["AWS", "Azure", "GCP", "Computer Networks", "Linux"]),
                  ("Infrastructure as code for a VPC plus compute and storage", ["Terraform", "Computer Networks"]),
                  ("Serverless API with logging and alerts", ["AWS", "Monitoring", "Python"]),
                  ("Containerised app deployed to a managed container service", ["Docker", "Kubernetes", "CI/CD"])],
        interview=["Shared-responsibility model and IAM basics", "VPC, subnets, routing and security groups", "Storage, compute and cost trade-offs", "High availability and backup design"]),
    "Cybersecurity Analyst": dict(
        aliases=["cyber security analyst", "security analyst", "soc analyst", "information security analyst", "cybersecurity engineer", "ethical hacker", "penetration tester", "infosec"],
        core=["Network Security", "Computer Networks", "Linux", "Cryptography", "Vulnerability Assessment", "Incident Response"],
        preferred=["Penetration Testing", "OWASP", "SIEM", "Wireshark", "Kali Linux", "Nmap", "Python"],
        min_projects=2,
        certifications=["CompTIA Security+", "ISC2 Certified in Cybersecurity (CC)", "Google Cybersecurity Certificate", "CEH (later stage)"],
        projects=[("Home lab: scan, find and report vulnerabilities on an intentionally vulnerable VM", ["Vulnerability Assessment", "Nmap", "Kali Linux", "Penetration Testing"]),
                  ("Packet-capture analysis report of suspicious traffic", ["Wireshark", "Computer Networks", "Network Security"]),
                  ("Log analysis and alerting rules in a SIEM (free tier or open-source)", ["SIEM", "Incident Response", "Linux"]),
                  ("OWASP Top 10 walkthrough on a practice web app", ["OWASP", "Penetration Testing"])],
        interview=["TCP/IP, DNS, HTTP and common attacks", "CIA triad, encryption and hashing", "Walking through an incident-response lifecycle", "OWASP Top 10 examples"]),
    "QA / Test Automation Engineer": dict(
        aliases=["qa", "qa engineer", "quality assurance engineer", "software tester", "test engineer", "automation tester", "sdet", "qa analyst", "tester", "testing engineer"],
        core=["Manual Testing", "Test Case Design", "SDLC", "Agile/Scrum", "Selenium", ("Java", "Python"), "SQL"],
        preferred=["Test Automation", "Postman", "API Testing", "JUnit", "CI/CD", "Git", "JIRA"],
        min_projects=2,
        certifications=["ISTQB Foundation Level (CTFL)", "Selenium / Playwright course certificates", "Postman API fundamentals"],
        projects=[("Selenium framework with page-object model and HTML reports", ["Selenium", "Test Automation", "Java", "Python"]),
                  ("Full test plan, test cases and bug reports for a public web app", ["Test Case Design", "Manual Testing", "SDLC"]),
                  ("Postman collection with automated API tests", ["Postman", "API Testing"]),
                  ("CI job that runs the automation suite on every commit", ["CI/CD", "Git", "JUnit"])],
        interview=["Test-case design techniques (boundary values, equivalence classes)", "Bug life cycle and severity vs priority", "Locators, waits and flaky-test handling", "Basic SQL checks for data validation"]),
    "Android Developer": dict(
        aliases=["android app developer", "mobile developer", "mobile app developer", "kotlin developer", "android engineer"],
        core=[("Kotlin", "Java"), "Android", "OOP", "REST APIs", "Git", "Data Structures & Algorithms"],
        preferred=["Jetpack Compose", "Firebase", "SQL", "Flutter", "React Native"],
        min_projects=3,
        certifications=["Google's Android developer training courses (developer.android.com)", "Kotlin fundamentals course certificates"],
        projects=[("Notes or expense tracker with local database and clean architecture", ["Android", "Kotlin", "SQL", "OOP"]),
                  ("App consuming a public REST API with pagination and caching", ["REST APIs", "Android"]),
                  ("Chat or to-do app with Firebase authentication and sync", ["Firebase", "Android"]),
                  ("Rebuild one screen set in Jetpack Compose", ["Jetpack Compose", "Kotlin"])],
        interview=["Activity/fragment lifecycle", "Kotlin coroutines and null safety", "MVVM architecture", "Handling network calls and offline data"]),
    "Business Analyst": dict(
        aliases=["ba", "business systems analyst", "functional analyst", "product analyst", "associate business analyst", "it business analyst"],
        core=["Requirements Gathering", "SQL", "Excel", "Documentation", "Agile/Scrum", "Stakeholder Management"],
        preferred=["Power BI", "Tableau", "UML", "Process Modeling", "JIRA", "Statistics"],
        min_projects=2,
        certifications=["IIBA ECBA", "Scrum Master / Product Owner fundamentals (PSM I, CSPO)", "Microsoft PL-300 (Power BI)"],
        projects=[("Write a BRD and user stories for a real app idea, with acceptance criteria", ["Requirements Gathering", "Documentation", "Agile/Scrum"]),
                  ("Process-flow and gap analysis of an existing workflow (for example college admissions)", ["Process Modeling", "UML", "Stakeholder Management"]),
                  ("KPI dashboard answering 5 business questions from a dataset", ["Power BI", "SQL", "Excel"]),
                  ("Sprint plan and backlog in JIRA for a team project", ["JIRA", "Agile/Scrum"])],
        interview=["Requirements elicitation techniques", "User stories vs use cases", "SQL queries for business questions", "Handling conflicting stakeholder priorities"]),
    "Embedded Systems Engineer": dict(
        aliases=["embedded engineer", "firmware engineer", "embedded software engineer", "embedded developer", "iot engineer", "embedded"],
        core=[("Embedded C", "C"), "Microcontrollers", "Communication Protocols", "RTOS", "Circuit Design"],
        preferred=["C++", "Raspberry Pi", "IoT", "Python", "Git", "Linux"],
        min_projects=3,
        certifications=["NPTEL Embedded Systems courses", "Vendor trainings (STMicroelectronics, Arm, Espressif)"],
        projects=[("Sensor data logger on a microcontroller using I2C/SPI and UART output", ["Microcontrollers", "Communication Protocols", "Embedded C"]),
                  ("FreeRTOS multi-task application (for example sensor + display + alarm)", ["RTOS", "Embedded C", "C"]),
                  ("IoT node publishing data over MQTT to a dashboard", ["IoT", "Raspberry Pi", "Python"]),
                  ("Custom PCB or breadboard schematic with documentation", ["Circuit Design"])],
        interview=["Pointers, bit manipulation, volatile and memory layout in C", "Interrupts, timers and ISR rules", "I2C vs SPI vs UART", "RTOS tasks, semaphores and priority inversion"]),
    "UI/UX Designer": dict(
        aliases=["ux", "ui", "ux designer", "ui designer", "product designer", "ui ux designer", "user experience designer", "interaction designer"],
        core=["Figma", "Wireframing", "Prototyping", "User Research", "Design Systems"],
        preferred=["HTML", "CSS", "Responsive Design"],
        min_projects=3,
        certifications=["Google UX Design Certificate", "Interaction Design Foundation courses"],
        projects=[("Case study: research, personas, wireframes and tested prototype for one app", ["User Research", "Wireframing", "Prototyping", "Figma"]),
                  ("Redesign an existing app screen set with before/after reasoning", ["Figma", "Design Systems"]),
                  ("Reusable component library and style guide", ["Design Systems", "Figma"]),
                  ("Responsive landing page designed and coded", ["HTML", "CSS", "Responsive Design"])],
        interview=["Portfolio walkthrough: problem, process, outcome", "Usability heuristics and accessibility", "How you validate a design decision", "Design critique and handling feedback"]),
}

GENERAL_SOFT_SKILL_ADVICE = (
    "Communication and teamwork are assessed in almost every interview: practise explaining one project in 2 minutes, "
    "prepare 3 STAR-format stories (challenge, action, result), and join a group project, club or hackathon to show collaboration."
)


# =============================================================================
# 3. SKILL DETECTION (local, alias based)
# =============================================================================
def _alias_rx(alias):
    toks = [re.escape(t) for t in alias.split()]
    body = r"[\s\-]+".join(toks)
    flags = 0 if len(alias) <= 2 else re.I
    return re.compile(rf"(?<![A-Za-z0-9+#]){body}(?![A-Za-z0-9+#])", flags)


_RX_CACHE = {}


def _patterns(skill):
    if skill not in _RX_CACHE:
        aliases = [skill] + SKILL_DB.get(skill, ("", []))[1]
        _RX_CACHE[skill] = [(a, _alias_rx(a)) for a in dict.fromkeys(aliases)]
    return _RX_CACHE[skill]


def detect_local(text, skills=None):
    """{skill: [matched strings]} for every catalog skill found in text."""
    out = {}
    for s in (skills or SKILL_DB):
        ev = []
        for _, rx in _patterns(s):
            for m in rx.finditer(text or ""):
                if m.group(0) not in ev and len(ev) < 3:
                    ev.append(m.group(0))
        if ev:
            out[s] = ev
    return out


def registry_key(skill, ec):
    """Map a catalog skill to the model-registry key (or None) using employability_core's alias table."""
    reg = getattr(ec, "_EXACT", None) or {}
    name = skill.strip().lower()
    k = reg.get(name)
    if not k:
        return None
    # accept only if the registry key/display IS this skill (an alias such as mysql -> SQL must not count)
    disp = str((getattr(ec, "SKILLS", {}).get(k, {}) or {}).get("display", k)).strip().lower()
    return k if name in (disp, str(k).lower()) else None


def collect_skills(resume_text="", ex=None, profile=None, manual=(), not_have=(), ec=None):
    """
    The student's skills, with evidence. Sources: resume text, the extractor output, ticks in the
    StudentProfile (present/absent), and skills typed by hand. `not_have` removes false positives.
    """
    ex = ex or {}
    corpus = "\n".join([resume_text or "",
                        " , ".join(map(str, ex.get("technical_skills", []))),
                        ex.get("project_section", ""), ex.get("internship_section", ""), ex.get("certification_section", "")])
    have = {s: dict(source="resume text", evidence=ev) for s, ev in detect_local(corpus).items()}

    if ec is not None:
        detected_keys = set(ex.get("skill_detections", {}) or {})
        present = profile.present_skills() if profile is not None else set()
        absent = ({k for k, v in profile.skill_state.items() if v == "absent"} if profile is not None else set())
        for s in SKILL_DB:
            k = registry_key(s, ec)
            if not k:
                continue
            if k in present:
                have.setdefault(s, dict(source="confirmed in profile", evidence=[s]))
            elif k in detected_keys:
                have.setdefault(s, dict(source="resume extractor", evidence=[s]))
            if k in absent and s in have and have[s]["source"] != "confirmed in profile":
                del have[s]
    for s in manual:
        s = _canonical(s)
        have[s] = dict(source="added by you", evidence=[s])
    for s in not_have:
        have.pop(_canonical(s), None)
    return have


def _canonical(name):
    n = str(name).strip()
    for s in SKILL_DB:
        if s.lower() == n.lower():
            return s
    low = n.lower()
    for s, (_, aliases) in SKILL_DB.items():
        if low in [a.lower() for a in aliases]:
            return s
    return n


def skill_inventory(have, ex=None):
    """Group the skills the student has by category (catalog skills + extra names from the extractor)."""
    groups = {}
    for s in sorted(have):
        groups.setdefault(SKILL_DB.get(s, ("Other", []))[0], []).append(s)
    known = {s.lower() for s in have}
    extra = [n for n in (ex or {}).get("technical_skills", []) if str(n).lower() not in known and _canonical(n) not in have]
    if extra:
        groups.setdefault("Other (from resume extractor)", []).extend(sorted(set(map(str, extra))))
    return groups


# =============================================================================
# 4. ROLE RESOLUTION
# =============================================================================
def _norm(s):
    return re.sub(r"[^a-z0-9+# ]+", " ", str(s).lower()).split()


def list_roles():
    return sorted(ROLES)


def resolve_role(query, top=3):
    """Ranked [(role, score)] for free text such as 'ml engg', 'sde', 'react developer'."""
    q = " ".join(_norm(query))
    if not q:
        return []
    scores = {}
    for role, r in ROLES.items():
        best = 0.0
        for name in [role] + r["aliases"]:
            n = " ".join(_norm(name))
            if q == n:
                best = 1.0
                break
            if min(len(q), len(n)) >= 4 and (n in q or q in n):
                best = max(best, 0.9)
            best = max(best, difflib.SequenceMatcher(None, q, n).ratio())
            qt, nt = set(q.split()), set(n.split())
            if qt and nt:
                best = max(best, 0.85 * len(qt & nt) / len(qt | nt))
        scores[role] = best
    ranked = sorted(scores.items(), key=lambda kv: -kv[1])
    return [(r, round(s, 2)) for r, s in ranked[:top] if s >= 0.45]


def choose_role(query, interactive=True):
    """
    Returns (role_name, role_dict). Asks a short question when the text is ambiguous or unknown.
    Unknown roles can be defined on the spot by typing the skills they need.
    """
    cands = resolve_role(query)
    if cands and (cands[0][1] == 1.0 or len(cands) == 1 or cands[0][1] - cands[1][1] >= 0.1):
        return cands[0][0], ROLES[cands[0][0]]
    if not interactive:
        if cands:
            print(f"Ambiguous role '{query}'; using best match '{cands[0][0]}'. Other options: {[c[0] for c in cands[1:]]}")
            return cands[0][0], ROLES[cands[0][0]]
        raise ValueError(f"Role '{query}' is not in the catalog. Supported roles: {list_roles()}. "
                         "Use custom_role(name, core_skills) to define it.")
    if cands:
        print(f"'{query}' could mean several roles:")
        for i, (r, s) in enumerate(cands, 1):
            print(f"  {i}. {r}")
        print("  0. None of these (define my own role)")
        pick = input("Choose a number: ").strip()
        if pick.isdigit() and 1 <= int(pick) <= len(cands):
            return cands[int(pick) - 1][0], ROLES[cands[int(pick) - 1][0]]
    else:
        print(f"'{query}' is not in the built-in catalog. Built-in roles: {', '.join(list_roles())}")
    raw = input(f"Type the skills a '{query}' needs, comma-separated (or press Enter to stop): ").strip()
    if not raw:
        raise ValueError("No role selected.")
    return query.strip().title(), custom_role(query, [s.strip() for s in raw.split(",") if s.strip()])


def custom_role(name, core, preferred=(), min_projects=2):
    """Define your own role. Unknown skills are registered so they can be matched in resume text."""
    for s in list(core) + list(preferred):
        for x in (s if isinstance(s, (tuple, list)) else [s]):
            if _canonical(x) not in SKILL_DB:
                SKILL_DB[_canonical(x)] = ("Custom", [])
    fix = lambda items: [tuple(_canonical(x) for x in i) if isinstance(i, (tuple, list)) else _canonical(i) for i in items]
    return dict(aliases=[], core=fix(core), preferred=fix(preferred), min_projects=min_projects,
                certifications=[], projects=[], interview=[], custom=True)


# =============================================================================
# 5. GAP ANALYSIS
# =============================================================================
def _groups(items):
    return [tuple(i) if isinstance(i, (tuple, list)) else (i,) for i in items]


def analyze_gap(role, have):
    rows = []
    for importance, items, weight in (("Core", role["core"], 2), ("Preferred", role["preferred"], 1)):
        for g in _groups(items):
            hit = [s for s in g if s in have]
            if hit:
                suggest, weeks = None, 0
            else:
                suggest = min(g, key=lambda s: (weeks_for(s), g.index(s)))
                weeks = weeks_for(suggest)
            rows.append(dict(requirement=" / ".join(g), importance=importance, status="Have" if hit else "Missing",
                             matched=", ".join(hit), evidence=", ".join(have[hit[0]]["evidence"]) if hit else "",
                             learn_first=suggest, est_weeks=weeks, weight=weight))
    t = pd.DataFrame(rows)
    pct = lambda d: round(100 * (d["status"] == "Have").mean(), 1) if len(d) else None
    core_t, pref_t = t[t.importance == "Core"], t[t.importance == "Preferred"]
    score = round(100 * (t.weight * (t.status == "Have")).sum() / t.weight.sum(), 1)
    label = ("Strong match: ready to apply, focus on projects and interview prep" if score >= 75 else
             "Good foundation: a few gaps to close before applying widely" if score >= 50 else
             "Early stage: build core skills first (see the plan below)" if score >= 25 else
             "Beginner for this role: start with the fundamentals in the plan below")
    return dict(table=t, score=score, label=label, core_pct=pct(core_t), preferred_pct=pct(pref_t),
                missing_core=core_t[core_t.status == "Missing"], missing_preferred=pref_t[pref_t.status == "Missing"],
                have_rows=t[t.status == "Have"])


# =============================================================================
# 6. RECOMMENDATIONS
# =============================================================================
def build_recommendations(role_name, role, gap, profile_values=None, ex=None):
    pv = profile_values or {}
    ex = ex or {}
    recs = {}

    plan, mc, mp = [], gap["missing_core"], gap["missing_preferred"]
    ordered = list(mc.itertuples()) + list(mp.itertuples())
    phase = lambda i, r: ("Phase 1 (now)" if r.importance == "Core" and i < 3 else
                          "Phase 2" if r.importance == "Core" else "Phase 3 (differentiators)")
    for i, r in enumerate(ordered):
        plan.append(dict(phase=phase(i, r), skill=r.learn_first, requirement=r.requirement, importance=r.importance,
                         est_weeks=r.est_weeks, how=tip_for(r.learn_first)))
    recs["learning_plan"] = pd.DataFrame(plan, columns=["phase", "skill", "requirement", "importance", "est_weeks", "how"])
    recs["core_weeks"] = int(mc["est_weeks"].sum()) if len(mc) else 0
    recs["preferred_weeks"] = int(mp["est_weeks"].sum()) if len(mp) else 0

    missing_names = {r.learn_first for r in ordered}
    scored = sorted(role.get("projects", []), key=lambda p: -len(missing_names & set(p[1])))
    recs["projects"] = [dict(title=t, covers=sorted(missing_names & set(sk))) for t, sk in scored[:3]]
    recs["certifications"] = role.get("certifications", [])
    recs["interview_topics"] = role.get("interview", [])

    prof = []
    projects, rel_projects = pv.get("Project_Count"), pv.get("Relevant_Project_Count")
    if projects is None:
        projects = ex.get("project_count_estimate")
    need = role.get("min_projects", 2)
    if projects is not None and projects < need:
        prof.append(f"Projects: you list {int(projects)}; for {role_name} aim for at least {need}, with the newest ones using the missing core skills.")
    if rel_projects is not None and rel_projects < 1:
        prof.append(f"None of your projects is marked relevant to {role_name}: build or reframe one so it clearly targets this role.")
    if pv.get("Internship") == 0:
        prof.append("No internship: apply for internships or virtual internships, or contribute to an open-source project, and document the outcome.")
    certs = pv.get("Certification_Count")
    if certs is None:
        certs = ex.get("certification_count_estimate")
    if certs is not None and certs < 1 and role.get("certifications"):
        prof.append("No certification listed: one recognised, role-relevant certificate (see list) shows initiative.")
    if pv.get("Backlogs") not in (None, 0):
        prof.append("Backlogs: clear them as early as possible; many recruiters require zero active backlogs.")
    cg = pv.get("CGPA")
    if cg is not None and cg < 6.5:
        prof.append("CGPA is on the lower side: some recruiters apply eligibility cut-offs, so offset it with strong projects, certifications and a clear portfolio.")
    if not ex.get("hackathon_mention", True):
        prof.append("No hackathon or competition mentioned: one team event is a quick way to show applied skill and collaboration.")
    prof.append(GENERAL_SOFT_SKILL_ADVICE)
    recs["profile"] = prof

    resume = []
    if len(mc):
        resume.append("Do not list a skill you cannot demonstrate: add each missing core skill only after you have used it in a project.")
    resume.append(f"Mirror role keywords from real {role_name} job postings, but only for skills you have; put role skills near the top of the Skills section.")
    resume.append("Write each project with the stack used and one measurable result (accuracy, latency, users, time saved).")
    recs["resume"] = resume
    return recs


# =============================================================================
# 7. OPTIONAL: WHAT-IF WITH THE SAVED MODEL
# =============================================================================
def what_if_model(ec, model, pre, X_raw, gap):
    """
    Re-score the SAME student row after switching individual missing skills to 'present'.
    Only skills that are model input columns can be tested. Model-based and trained on synthetic data:
    an illustration of how the model responds, not a prediction of the real job market.
    """
    base = ec.predict_employability(model, pre, X_raw)["p_placed"]
    rows = []
    for r in gap["table"].query("status == 'Missing'").itertuples():
        key = registry_key(r.learn_first, ec)
        if key is None or key not in X_raw.columns or X_raw.iloc[0][key] == 1:
            continue
        X2 = X_raw.copy()
        X2.loc[X2.index[0], key] = 1.0
        try:
            p2 = ec.predict_employability(model, pre, X2)["p_placed"]
        except Exception:
            continue
        rows.append(dict(skill=r.learn_first, importance=r.importance, p_placed_now=base, p_placed_if_added=p2, change=p2 - base))
    out = pd.DataFrame(rows, columns=["skill", "importance", "p_placed_now", "p_placed_if_added", "change"])
    out = out.sort_values("change", ascending=False).reset_index(drop=True)
    combined = None
    keys = [registry_key(s, ec) for s in out["skill"]]
    keys = [k for k in keys if k]
    if keys:
        X3 = X_raw.copy()
        for k in keys:
            X3.loc[X3.index[0], k] = 1.0
        combined = ec.predict_employability(model, pre, X3)["p_placed"]
    return dict(base=base, table=out, all_added=combined)


# =============================================================================
# 8. ONE-CALL WRAPPER, PRINTING, CHART, REPORT
# =============================================================================
def run_skill_gap(role_query, ec=None, resume_text="", ex=None, profile=None, manual_skills=(), not_have=(),
                  interactive=True, profile_values=None):
    role_name, role = choose_role(role_query, interactive=interactive)
    have = collect_skills(resume_text, ex, profile, manual_skills, not_have, ec)
    gap = analyze_gap(role, have)
    pv = dict(profile_values or {})
    if profile is not None:
        for c in ("CGPA", "Backlogs", "Internship", "Project_Count", "Certification_Count", "Relevant_Project_Count"):
            if profile.value(c) is not None:
                pv.setdefault(c, profile.value(c))
    recs = build_recommendations(role_name, role, gap, pv, ex)
    return dict(role_name=role_name, role=role, have=have, inventory=skill_inventory(have, ex), gap=gap, recs=recs)


def print_report(res):
    g, r = res["gap"], res["recs"]
    bar = lambda p: "#" * int(round((p or 0) / 5)) + "-" * (20 - int(round((p or 0) / 5)))
    print("=" * 72)
    print(f"SKILL-GAP REPORT  |  Target role: {res['role_name']}")
    print("=" * 72)
    print(f"Role readiness score : {g['score']:.0f}/100  [{bar(g['score'])}]")
    print(f"  Core skills        : {g['core_pct']}% covered")
    print(f"  Preferred skills   : {g['preferred_pct']}% covered")
    print(f"  Verdict            : {g['label']}")
    print("\nWHAT THIS SCORE IS: share of this catalog's role skills found in your resume/confirmations "
          "(core counts double). It is a planning aid, not a hiring probability.")
    print("\n--- 1. SKILLS YOU HAVE (all detected, by category) ---")
    for cat, items in res["inventory"].items():
        print(f"  {cat}: {', '.join(items)}")
    print("\n--- 2. SKILLS YOU HAVE THAT THIS ROLE WANTS ---")
    for row in g["have_rows"].itertuples():
        print(f"  [OK] {row.requirement} ({row.importance})" + (f"  <- {row.evidence}" if row.evidence else ""))
    if g["have_rows"].empty:
        print("  (none found yet)")
    print("\n--- 3. SKILL GAPS ---")
    for title, df in (("Core (must-have)", g["missing_core"]), ("Preferred (nice-to-have)", g["missing_preferred"])):
        print(f"  {title}:")
        if df.empty:
            print("    none - fully covered")
        for row in df.itertuples():
            print(f"    [GAP] {row.requirement}" + (f"  (start with {row.learn_first})" if " / " in row.requirement else "") + f"  ~{row.est_weeks} wk")
    print("\n--- 4. LEARNING PLAN (priority order) ---")
    lp = r["learning_plan"]
    if lp.empty:
        print("  No gaps against this role's list: focus on projects, depth and interview practice.")
    for phase, d in lp.groupby("phase", sort=False):
        print(f"  {phase}")
        for row in d.itertuples():
            print(f"    - {row.skill} (~{row.est_weeks} wk): {row.how}")
    if len(lp):
        print(f"  Rough effort at 8-10 hrs/week: core gaps ~{r['core_weeks']} weeks, preferred ~{r['preferred_weeks']} more. "
              "These are estimates; they vary with your background.")
    if r["projects"]:
        print("\n--- 5. PROJECTS TO BUILD ---")
        for p in r["projects"]:
            print(f"  - {p['title']}" + (f"  [closes gaps: {', '.join(p['covers'])}]" if p["covers"] else ""))
    if r["certifications"]:
        print("\n--- 6. CERTIFICATIONS TO CONSIDER (check current availability and cost) ---")
        for c in r["certifications"]:
            print(f"  - {c}")
    print("\n--- 7. PROFILE IMPROVEMENTS ---")
    for x in r["profile"]:
        print(f"  - {x}")
    print("\n--- 8. RESUME TIPS ---")
    for x in r["resume"]:
        print(f"  - {x}")
    if r["interview_topics"]:
        print("\n--- 9. INTERVIEW PREPARATION TOPICS ---")
        for x in r["interview_topics"]:
            print(f"  - {x}")


def plot_gap(res):
    import matplotlib.pyplot as plt
    g = res["gap"]
    t = g["table"].copy()
    t["order"] = t["importance"].map({"Core": 0, "Preferred": 1})
    t = t.sort_values(["order", "status"], ascending=[True, True]).iloc[::-1]
    fig, ax = plt.subplots(1, 2, figsize=(11, max(3.5, 0.34 * len(t) + 1.2)), gridspec_kw=dict(width_ratios=[1, 2]))
    vals = [g["core_pct"] or 0, g["preferred_pct"] or 0, g["score"]]
    ax[0].barh(["Core", "Preferred", "Overall score"], vals, color=["#264653", "#8ab17d", "#e9c46a"])
    ax[0].set_xlim(0, 100)
    ax[0].set_xlabel("% covered")
    ax[0].set_title(f"Readiness for {res['role_name']}", fontsize=10)
    for i, v in enumerate(vals):
        ax[0].text(min(v + 2, 88), i, f"{v:.0f}%", va="center", fontsize=9)
    colors = ["#2a9d8f" if s == "Have" else "#e76f51" for s in t["status"]]
    ax[1].barh([f"{r.requirement} ({r.importance[0]})" for r in t.itertuples()], [1] * len(t), color=colors)
    ax[1].set_xticks([])
    ax[1].set_title("Green = you have it   Red = gap   (C = core, P = preferred)", fontsize=10)
    fig.tight_layout()
    return fig


def plot_what_if(wi):
    import matplotlib.pyplot as plt
    t = wi["table"].head(10).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 0.42 * len(t) + 1.3))
    ax.barh(t["skill"], t["change"] * 100, color=["#2a9d8f" if v >= 0 else "#e76f51" for v in t["change"]])
    ax.axvline(0, color="k", lw=0.8)
    ax.set_xlabel("Change in model P(Placed), percentage points")
    ax.set_title("What-if: adding one missing skill (saved model, synthetic data)")
    return fig


def to_markdown(res, what_if=None):
    g, r = res["gap"], res["recs"]
    L = [f"# Skill-gap report: {res['role_name']}", "",
         f"**Readiness score:** {g['score']:.0f}/100 (core {g['core_pct']}%, preferred {g['preferred_pct']}%)  ",
         f"**Verdict:** {g['label']}", "",
         "_The score is the share of this catalog's role skills found in your resume/confirmations (core counts double). "
         "It is a planning aid, not a hiring probability._", "", "## Skills you have"]
    for cat, items in res["inventory"].items():
        L.append(f"- **{cat}:** {', '.join(items)}")
    L += ["", "## Gaps"]
    for title, df in (("Core", g["missing_core"]), ("Preferred", g["missing_preferred"])):
        L.append(f"**{title}:** " + (", ".join(df["requirement"]) if len(df) else "none"))
    L += ["", "## Learning plan"]
    for row in r["learning_plan"].itertuples():
        L.append(f"- **{row.phase}: {row.skill}** (~{row.est_weeks} wk) - {row.how}")
    if r["projects"]:
        L += ["", "## Projects to build"] + [f"- {p['title']}" for p in r["projects"]]
    if r["certifications"]:
        L += ["", "## Certifications to consider (check current availability)"] + [f"- {c}" for c in r["certifications"]]
    L += ["", "## Profile improvements"] + [f"- {x}" for x in r["profile"]]
    L += ["", "## Resume tips"] + [f"- {x}" for x in r["resume"]]
    if r["interview_topics"]:
        L += ["", "## Interview topics"] + [f"- {x}" for x in r["interview_topics"]]
    if what_if is not None and len(what_if["table"]):
        L += ["", "## Model what-if (synthetic-data model; illustration only)",
              f"Current model P(Placed): {what_if['base']:.1%}"]
        for row in what_if["table"].itertuples():
            L.append(f"- Adding {row.skill}: {row.p_placed_if_added:.1%} ({row.change * 100:+.1f} pts)")
    return "\n".join(L)


# ---- self-check: every skill named by a role must exist in SKILL_DB ----------
def _validate_catalog():
    bad = []
    for role, r in ROLES.items():
        for items in (r["core"], r["preferred"]):
            for g in _groups(items):
                bad += [(role, s) for s in g if s not in SKILL_DB]
    return bad


assert not _validate_catalog(), _validate_catalog()
