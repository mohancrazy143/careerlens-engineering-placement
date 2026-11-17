"""
skills_registry.py
==================
Data module: canonical skills, aliases, role reference profiles and learning kits.

* Canonical keys for skills that exist in the trained model are IDENTICAL to the
  model's raw column names (e.g. 'Cpp', 'NodeJS', 'CI_CD'). Skills that are not
  model inputs (e.g. 'Unit_Testing') exist only for role analysis.
* ROLE_PROFILES are a CURATED FALLBACK, NOT derived from specific job postings.
  They are labelled `verified=False` everywhere they are displayed. A user-supplied
  job description always takes priority (see role_analysis.py).
"""

# --------------------------------------------------------------------------
# 1. SKILL REGISTRY      Key|Domain|Display|aliases (;-separated)|flags
#    flag 'A' = ambiguous token: matched CASE-SENSITIVELY and reported with
#    LOW confidence so the user must confirm it.
# --------------------------------------------------------------------------
_REGISTRY_TEXT = """
C|Programming|C|C|A
Cpp|Programming|C++|c++;cpp|
Java|Programming|Java|java|
Python|Programming|Python|python|
JavaScript|Programming|JavaScript|javascript;ecmascript;es6|
TypeScript|Programming|TypeScript|typescript|
CSharp|Programming|C#|c#;csharp;c sharp|
R|Programming|R|R|A
Go|Programming|Go|Go;golang|A
Kotlin|Programming|Kotlin|kotlin|
PHP|Programming|PHP|php|
Ruby|Programming|Ruby|Ruby|A
Swift|Programming|Swift|Swift|A
Dart|Programming|Dart|Dart|A
MATLAB|Programming|MATLAB|matlab|
DSA|CS Fundamentals|Data Structures & Algorithms|dsa;data structures;data structures and algorithms;algorithms|
OOP|CS Fundamentals|Object-Oriented Programming|oop;oops;object oriented;object-oriented programming|
DBMS|CS Fundamentals|DBMS|dbms;database management system;database management systems|
Operating_Systems|CS Fundamentals|Operating Systems|operating systems;operating system|
Computer_Networks|CS Fundamentals|Computer Networks|computer networks;computer networking|
Computer_Architecture|CS Fundamentals|Computer Architecture|computer architecture;computer organization|
Software_Engineering|CS Fundamentals|Software Engineering|software engineering;sdlc|
Computer_Security|Security|Computer / Network Security|computer security;cybersecurity;cyber security;information security;network security|
Cloud_Computing|Cloud DevOps Tools|Cloud Computing|cloud computing;cloud|
Distributed_Systems|CS Fundamentals|Distributed Systems|distributed systems|
Compiler_Design|CS Fundamentals|Compiler Design|compiler design|
Theory_of_Computation|CS Fundamentals|Theory of Computation|theory of computation;automata theory|
HTML|Web Development|HTML|html;html5|
CSS|Web Development|CSS|css;css3|
React|Web Development|React|react;reactjs;react.js|
Angular|Web Development|Angular|angular;angularjs|
Vue|Web Development|Vue|vue;vuejs;vue.js|
NodeJS|Web Development|Node.js|node.js;nodejs;node js|
ExpressJS|Web Development|Express.js|express.js;expressjs;express js|
NextJS|Web Development|Next.js|next.js;nextjs|
Spring_Boot|Web Development|Spring Boot|spring boot;springboot|
Django|Web Development|Django|django|
Flask|Web Development|Flask|flask|
REST_API|Web Development|REST APIs|rest api;rest apis;restful;restful api;restful apis|
GraphQL|Web Development|GraphQL|graphql|
Web_Development|Web Development|Web Development|web development;web developer;full stack;full-stack|
SQL|Database|SQL|sql;t-sql;pl/sql|
MySQL|Database|MySQL|mysql;mysql workbench|
PostgreSQL|Database|PostgreSQL|postgresql;postgres|
Oracle|Database|Oracle DB|oracle;oracle db;oracle database|
MongoDB|Database|MongoDB|mongodb;mongo db|
Redis|Database|Redis|redis|
Firebase|Database|Firebase|firebase;firestore|
NumPy|AI ML Data|NumPy|numpy|
Pandas|AI ML Data|Pandas|pandas|
Matplotlib|AI ML Data|Matplotlib|matplotlib;seaborn|
Scikit_Learn|AI ML Data|scikit-learn|scikit-learn;scikit learn;sklearn|
TensorFlow|AI ML Data|TensorFlow|tensorflow;keras|
PyTorch|AI ML Data|PyTorch|pytorch;torch|
Machine_Learning|AI ML Data|Machine Learning|machine learning;ml|
Deep_Learning|AI ML Data|Deep Learning|deep learning;neural networks;cnn;rnn;lstm|
NLP|AI ML Data|NLP|nlp;natural language processing|
Computer_Vision|AI ML Data|Computer Vision|computer vision;opencv|
Generative_AI|AI ML Data|Generative AI|generative ai;genai;gen ai;llm;llms;large language models|
Data_Analysis|AI ML Data|Data Analysis|data analysis;data analytics;exploratory data analysis|
Data_Visualization|AI ML Data|Data Visualization|data visualization;data visualisation;dashboards|
Statistics|AI ML Data|Statistics|statistics;statistical analysis;hypothesis testing;probability and statistics|
AWS|Cloud DevOps Tools|AWS|aws;amazon web services;ec2;s3|
Azure|Cloud DevOps Tools|Azure|azure;microsoft azure|
Google_Cloud|Cloud DevOps Tools|Google Cloud|google cloud;gcp;google cloud platform|
Git|Cloud DevOps Tools|Git|git;version control|
GitHub|Cloud DevOps Tools|GitHub|github|
GitLab|Cloud DevOps Tools|GitLab|gitlab|
Docker|Cloud DevOps Tools|Docker|docker;containerization;containers|
Kubernetes|Cloud DevOps Tools|Kubernetes|kubernetes;k8s|
Jenkins|Cloud DevOps Tools|Jenkins|jenkins|
CI_CD|Cloud DevOps Tools|CI/CD|ci/cd;ci-cd;cicd;continuous integration;github actions|
Linux|Cloud DevOps Tools|Linux|linux;ubuntu;unix|
Terraform|Cloud DevOps Tools|Terraform|terraform;infrastructure as code|
VS_Code|Cloud DevOps Tools|VS Code|vs code;vscode;visual studio code|
Jupyter|Cloud DevOps Tools|Jupyter|jupyter;jupyter notebook;google colab;colab|
Postman|Cloud DevOps Tools|Postman|postman|
Figma|Cloud DevOps Tools|Figma|figma|
PowerBI|Cloud DevOps Tools|Power BI|power bi;powerbi|
Tableau|Cloud DevOps Tools|Tableau|tableau|
Excel|Cloud DevOps Tools|Excel|Excel;ms excel;microsoft excel;advanced excel|A
Android_Studio|Cloud DevOps Tools|Android Studio|android studio;android development|
Embedded_C|Embedded & Electronics|Embedded C|embedded c|
Arduino|Embedded & Electronics|Arduino|arduino|
Raspberry_Pi|Embedded & Electronics|Raspberry Pi|raspberry pi|
Verilog|Embedded & Electronics|Verilog|verilog|
VHDL|Embedded & Electronics|VHDL|vhdl|
FPGA|Embedded & Electronics|FPGA|fpga|
Microcontrollers|Embedded & Electronics|Microcontrollers|microcontroller;microcontrollers;8051;stm32|
IoT|Embedded & Electronics|IoT|iot;internet of things|
PCB_Design|Embedded & Electronics|PCB Design|pcb design;pcb;altium;kicad|
Simulink|Embedded & Electronics|Simulink|simulink|
Signal_Processing|Embedded & Electronics|Signal Processing|signal processing;dsp|
Digital_Electronics|Embedded & Electronics|Digital Electronics|digital electronics;digital logic|
Analog_Electronics|Embedded & Electronics|Analog Electronics|analog electronics;analog circuits|
Embedded_Systems|Embedded & Electronics|Embedded Systems|embedded systems;embedded system|
PLC|Electrical|PLC|plc;programmable logic controller|
SCADA|Electrical|SCADA|scada|
Power_Systems|Electrical|Power Systems|power systems;power system|
Control_Systems|Electrical|Control Systems|control systems;control system|
Electrical_Machines|Electrical|Electrical Machines|electrical machines;electrical machine|
Power_Electronics|Electrical|Power Electronics|power electronics|
Circuit_Design|Electrical|Circuit Design|circuit design;circuit analysis|
Electrical_Design|Electrical|Electrical Design|electrical design|
Industrial_Automation|Electrical|Industrial Automation|industrial automation|
AutoCAD|Mechanical|AutoCAD|autocad|
SolidWorks|Mechanical|SolidWorks|solidworks;solid works|
CATIA|Mechanical|CATIA|catia|
Creo|Mechanical|Creo|creo;pro/e|
ANSYS|Mechanical|ANSYS|ansys|
CAD|Mechanical|CAD|cad;computer aided design;computer-aided design|
CAM|Mechanical|CAM|cam;computer aided manufacturing|
CAE|Mechanical|CAE|cae|
CNC|Mechanical|CNC|cnc;cnc machining;g-code|
Robotics|Mechanical|Robotics|robotics|
3D_Modeling|Mechanical|3D Modeling|3d modeling;3d modelling;3d printing|
Manufacturing|Mechanical|Manufacturing|manufacturing|
Revit|Civil|Revit|revit|
STAAD_Pro|Civil|STAAD.Pro|staad pro;staad.pro;staad|
ETABS|Civil|ETABS|etabs|
Civil_3D|Civil|Civil 3D|civil 3d;civil3d|
Primavera|Civil|Primavera|primavera|
BIM|Civil|BIM|bim;building information modeling|
Structural_Analysis|Civil|Structural Analysis|structural analysis|
Surveying|Civil|Surveying|surveying;total station|
Construction_Management|Civil|Construction Management|construction management|
Unit_Testing|Software Practices|Unit Testing|unit testing;unit tests;pytest;unittest;test driven development;tdd|
Maven|Software Practices|Maven|maven;gradle|
JUnit|Software Practices|JUnit|junit;mockito|
Hibernate|Web Development|Hibernate / JPA|hibernate;jpa|
Microservices|Software Practices|Microservices|microservices;microservice architecture|
System_Design|Software Practices|System Design|system design;software architecture;design patterns|
Agile|Software Practices|Agile|agile;scrum|
Authentication|Security|Authentication & Authorization|authentication;authorization;oauth;jwt|
Message_Queues|Software Practices|Message Queues|kafka;rabbitmq;message queue;message queues|
Feature_Engineering|AI ML Data|Feature Engineering|feature engineering;feature selection|
Model_Deployment|AI ML Data|Model Deployment|model deployment;model serving;fastapi;streamlit|
MLOps|AI ML Data|MLOps|mlops;mlflow;kubeflow|
Prompt_Engineering|AI ML Data|Prompt Engineering|prompt engineering;prompt design|
Vector_Databases|AI ML Data|Vector Databases|vector database;vector databases;faiss;pinecone;chromadb;embeddings|
LangChain|AI ML Data|LangChain|langchain;llamaindex;rag;retrieval augmented generation|
Shell_Scripting|Cloud DevOps Tools|Shell Scripting|shell scripting;bash;shell script;bash scripting|
Monitoring|Cloud DevOps Tools|Monitoring & Observability|prometheus;grafana;observability|
Ansible|Cloud DevOps Tools|Ansible|ansible;configuration management|
SIEM|Security|SIEM|siem;splunk;qradar;elk stack|
Vulnerability_Assessment|Security|Vulnerability Assessment|vulnerability assessment;penetration testing;pentesting;owasp zap;nessus;burp suite|
Wireshark|Security|Wireshark / Packet Analysis|wireshark;packet analysis;tcpdump|
Cryptography|Security|Cryptography|cryptography;encryption;pki|
OWASP|Security|OWASP Top 10|owasp;owasp top 10|
Incident_Response|Security|Incident Response|incident response;digital forensics;soc analyst|
Backup_Recovery|Database|Backup & Recovery|backup and recovery;database backup;disaster recovery|
Performance_Tuning|Database|Performance Tuning|performance tuning;query optimization;query optimisation;indexing|
Data_Modeling|Database|Data Modeling|data modeling;data modelling;er diagram;normalization|
Responsive_Design|Web Development|Responsive Design|responsive design;responsive web design;media queries;bootstrap;tailwind|
Web_Accessibility|Web Development|Web Accessibility|web accessibility;wcag|
Jest|Software Practices|Frontend Testing (Jest)|jest;react testing library;cypress;selenium|
""".strip()

SOFT_SKILL_COLUMNS = ["Communication", "Teamwork", "Leadership",
                      "Problem_Solving", "Presentation", "Time_Management"]


def _parse_registry(text):
    reg = {}
    for line in text.splitlines():
        key, domain, display, aliases, flags = line.split("|")
        reg[key] = dict(key=key, domain=domain, display=display,
                        aliases=[a for a in aliases.split(";") if a],
                        ambiguous="A" in flags)
    return reg


SKILLS = _parse_registry(_REGISTRY_TEXT)

# Skills known to be model input columns (from the notebook's printed schema).
# Validated against preprocessor.feature_names_in_ at run time (see core.audit).
MODEL_TECH_SKILL_KEYS = [k for k in SKILLS if k in {
    "C", "Cpp", "Java", "Python", "JavaScript", "TypeScript", "CSharp", "R", "Go", "Kotlin", "PHP", "Ruby",
    "Swift", "Dart", "MATLAB", "DSA", "OOP", "DBMS", "Operating_Systems", "Computer_Networks",
    "Computer_Architecture", "Software_Engineering", "Computer_Security", "Cloud_Computing",
    "Distributed_Systems", "Compiler_Design", "Theory_of_Computation", "HTML", "CSS", "React", "Angular",
    "Vue", "NodeJS", "ExpressJS", "NextJS", "Spring_Boot", "Django", "Flask", "REST_API", "GraphQL",
    "Web_Development", "SQL", "MySQL", "PostgreSQL", "Oracle", "MongoDB", "Redis", "Firebase", "NumPy",
    "Pandas", "Matplotlib", "Scikit_Learn", "TensorFlow", "PyTorch", "Machine_Learning", "Deep_Learning",
    "NLP", "Computer_Vision", "Generative_AI", "Data_Analysis", "Data_Visualization", "Statistics", "AWS",
    "Azure", "Google_Cloud", "Git", "GitHub", "GitLab", "Docker", "Kubernetes", "Jenkins", "CI_CD", "Linux",
    "Terraform", "VS_Code", "Jupyter", "Postman", "Figma", "PowerBI", "Tableau", "Excel", "Android_Studio",
    "Embedded_C", "Arduino", "Raspberry_Pi", "Verilog", "VHDL", "FPGA", "Microcontrollers", "IoT",
    "PCB_Design", "Simulink", "Signal_Processing", "Digital_Electronics", "Analog_Electronics",
    "Embedded_Systems", "PLC", "SCADA", "Power_Systems", "Control_Systems", "Electrical_Machines",
    "Power_Electronics", "Circuit_Design", "Electrical_Design", "Industrial_Automation", "AutoCAD",
    "SolidWorks", "CATIA", "Creo", "ANSYS", "CAD", "CAM", "CAE", "CNC", "Robotics", "3D_Modeling",
    "Manufacturing", "Revit", "STAAD_Pro", "ETABS", "Civil_3D", "Primavera", "BIM",
    "Structural_Analysis", "Surveying", "Construction_Management"}]

# Model input columns that are NOT technical skills (profile / experience / academic).
MODEL_PROFILE_FIELDS = {
    "categorical": ["Education_Level", "UG_Degree", "PG_Specialization", "Branch"],
    "academic": ["Year", "CGPA", "Attendance_Percentage", "Backlogs",
                 "Core_Subject_Score", "Technical_Subject_Score", "Aptitude_Score"],
    "role_context": ["PG_Required_For_Target_Role", "Relevant_Degree_Required"],
    "experience": ["Project_Count", "Relevant_Project_Count", "Internship",
                   "Internship_Duration_Months", "Hackathon_Participation",
                   "Certification_Count", "Relevant_Certification_Count",
                   "Open_Source_Contribution"],
    "soft": SOFT_SKILL_COLUMNS,
}


def display_name(key):
    return SKILLS[key]["display"] if key in SKILLS else key.replace("_", " ")


def domain_of(key):
    return SKILLS[key]["domain"] if key in SKILLS else "Other"


# --------------------------------------------------------------------------
# 2. CURATED ROLE PROFILES  (FALLBACK; unverified; NOT derived from postings)
#    tiers: core / important / complementary
#    An item is a skill key, or (label, [option keys]) meaning "any one of".
# --------------------------------------------------------------------------
_CLOUDS = ("A major cloud platform (AWS / Azure / Google Cloud)", ["AWS", "Azure", "Google_Cloud"])
_DL_FW = ("A deep-learning framework (PyTorch / TensorFlow)", ["PyTorch", "TensorFlow"])
_RDB = ("A relational database (MySQL / PostgreSQL / Oracle)", ["MySQL", "PostgreSQL", "Oracle"])
_FRONT = ("A frontend framework (React / Angular / Vue)", ["React", "Angular", "Vue"])
_LANG = ("A general-purpose language (Java / Python / C++ / C# / JavaScript)",
         ["Java", "Python", "Cpp", "CSharp", "JavaScript"])
_BLANG = ("A backend language (Java / Python / Node.js / C# / Go)",
          ["Java", "Python", "NodeJS", "CSharp", "Go"])

ROLE_PROFILES = {
    "python_developer": dict(title="Python Developer", aliases=["python developer", "python engineer", "python programmer"],
        core=["Python", "OOP", "Git", "SQL", "REST_API"], important=[("Flask or Django", ["Flask", "Django"]), "Unit_Testing", "DSA", "Linux"],
        complementary=["Docker", "PostgreSQL", "CI_CD"]),
    "software_developer": dict(title="Software Developer", aliases=["software developer", "software engineer", "sde", "software development engineer", "programmer analyst"],
        core=[_LANG, "DSA", "OOP", "Git", "DBMS", "SQL"], important=["Software_Engineering", "Unit_Testing", "REST_API", "Operating_Systems", "Computer_Networks"],
        complementary=["Docker", "CI_CD", "Agile"]),
    "full_stack_developer": dict(title="Full Stack Developer", aliases=["full stack developer", "fullstack developer", "full-stack developer", "full stack engineer", "mern developer"],
        core=["HTML", "CSS", "JavaScript", _FRONT, "NodeJS", "REST_API", ("A database (SQL or MongoDB)", ["SQL", "MySQL", "PostgreSQL", "MongoDB"]), "Git"],
        important=["TypeScript", "ExpressJS", "Authentication", "Responsive_Design"], complementary=["Docker", "CI_CD", "Jest"]),
    "java_developer": dict(title="Java Developer", aliases=["java developer", "java engineer", "java programmer", "j2ee developer"],
        core=["Java", "OOP", "DSA", "Spring_Boot", "SQL", "REST_API", "Git"], important=["Maven", "JUnit", "Hibernate", _RDB],
        complementary=["Microservices", "Docker", "CI_CD"]),
    "data_analyst": dict(title="Data Analyst", aliases=["data analyst", "business analyst data", "bi analyst", "business intelligence analyst", "analytics engineer"],
        core=["SQL", "Excel", "Data_Analysis", "Data_Visualization", "Statistics"], important=["Python", "Pandas", ("A BI tool (Power BI / Tableau)", ["PowerBI", "Tableau"]), "Matplotlib"],
        complementary=["NumPy", "Jupyter", "Git"]),
    "data_scientist": dict(title="Data Scientist", aliases=["data scientist", "applied scientist", "junior data scientist"],
        core=["Python", "Statistics", "Pandas", "NumPy", "Machine_Learning", "Scikit_Learn", "SQL"],
        important=["Data_Visualization", "Feature_Engineering", "Deep_Learning", "Matplotlib", "Git"], complementary=[_DL_FW, "Jupyter", "Model_Deployment"]),
    "machine_learning_engineer": dict(title="Machine Learning Engineer", aliases=["machine learning engineer", "ml engineer", "mle", "machine learning developer"],
        core=["Python", "Machine_Learning", "Deep_Learning", "Scikit_Learn", _DL_FW, "Git", "DSA"],
        important=["Model_Deployment", "Docker", "SQL", "Linux", "Statistics"], complementary=["MLOps", _CLOUDS, "Feature_Engineering"]),
    "ai_engineer": dict(title="AI Engineer", aliases=["ai engineer", "artificial intelligence engineer", "generative ai engineer", "llm engineer", "ai developer"],
        core=["Python", "Machine_Learning", "Deep_Learning", "NLP", "Generative_AI", _DL_FW],
        important=["Prompt_Engineering", "REST_API", "Git", "Docker", "Model_Deployment"], complementary=["LangChain", "Vector_Databases", _CLOUDS]),
    "cloud_engineer": dict(title="Cloud Engineer", aliases=["cloud engineer", "cloud administrator", "cloud support engineer", "cloud architect junior"],
        core=["Cloud_Computing", _CLOUDS, "Linux", "Computer_Networks", "Git"], important=["Docker", "Kubernetes", "Terraform", "CI_CD", "Shell_Scripting"],
        complementary=["Python", "Computer_Security", "Monitoring"]),
    "devops_engineer": dict(title="DevOps Engineer", aliases=["devops engineer", "devops", "site reliability engineer", "sre", "platform engineer"],
        core=["Linux", "Git", "CI_CD", "Docker", "Shell_Scripting", _CLOUDS], important=["Kubernetes", "Terraform", ("A CI server (Jenkins / GitLab CI)", ["Jenkins", "GitLab"]), "Monitoring", "Computer_Networks"],
        complementary=["Ansible", "Python"]),
    "cybersecurity_analyst": dict(title="Cybersecurity Analyst", aliases=["cybersecurity analyst", "cyber security analyst", "security analyst", "soc analyst", "information security analyst", "cybersecurity engineer"],
        core=["Computer_Security", "Computer_Networks", "Linux", "Operating_Systems", "SIEM", "Vulnerability_Assessment"],
        important=["Wireshark", "Cryptography", "OWASP", "Incident_Response"], complementary=["Python", "Shell_Scripting", "Cloud_Computing"]),
    "database_administrator": dict(title="Database Administrator", aliases=["database administrator", "dba", "database engineer", "sql dba"],
        core=["SQL", "DBMS", _RDB, "Backup_Recovery", "Performance_Tuning"], important=["Data_Modeling", "Linux", "Shell_Scripting"],
        complementary=["Computer_Security", "Cloud_Computing", "Python"]),
    "frontend_developer": dict(title="Frontend Developer", aliases=["frontend developer", "front end developer", "front-end developer", "ui developer", "react developer", "web developer frontend"],
        core=["HTML", "CSS", "JavaScript", _FRONT, "Git", "Responsive_Design"], important=["TypeScript", "REST_API", "Web_Accessibility", "Jest"],
        complementary=["Figma", "NextJS", "CI_CD"]),
    "backend_developer": dict(title="Backend Developer", aliases=["backend developer", "back end developer", "back-end developer", "backend engineer", "server side developer"],
        core=[_BLANG, "REST_API", "SQL", "DBMS", "Git"], important=["Authentication", "Unit_Testing", "Docker", "Redis"],
        complementary=["Microservices", "System_Design", "Message_Queues", "CI_CD"]),
}

# Titles that are too generic to pick one role -> ask the user to clarify.
AMBIGUOUS_TITLES = {
    "developer": ["software_developer", "full_stack_developer", "backend_developer", "frontend_developer"],
    "engineer": ["software_developer", "cloud_engineer", "devops_engineer", "machine_learning_engineer"],
    "analyst": ["data_analyst", "cybersecurity_analyst"],
    "web developer": ["frontend_developer", "full_stack_developer", "backend_developer"],
    "data engineer": ["data_analyst", "data_scientist", "backend_developer"],
}

# --------------------------------------------------------------------------
# 3. LEARNING KITS   Key|prerequisites;|practical project|resource|url|milestone|resume wording
#    url '-' = no URL given (the app then says "search the official documentation").
# --------------------------------------------------------------------------
_KIT_TEXT = """
Python||Build a CLI expense tracker that stores data in SQLite and has unit tests|Python Tutorial (official)|https://docs.python.org/3/tutorial/|Complete the tutorial and push a tested CLI project with a README to GitHub|Developed a tested Python CLI application (SQLite, argparse)
OOP|Python|Model a library-management system with inheritance, interfaces and 5+ classes|Python Classes (official)|https://docs.python.org/3/tutorial/classes.html|Design a 5-class system with at least one abstract base class and unit tests|Applied object-oriented design (inheritance, polymorphism) in a library-management system
Git||Contribute a feature branch via pull request to a personal repo and resolve one merge conflict|Pro Git book|https://git-scm.com/book/en/v2|Own a repo with 20+ meaningful commits, branches and one reviewed pull request|Used Git/GitHub with branching and pull-request workflow
SQL||Design a 5-table schema and write 15 queries (joins, aggregates, window functions)|PostgreSQL Tutorial (official)|https://www.postgresql.org/docs/current/tutorial.html|Solve 15 queries on your own schema including 3 window-function queries|Wrote analytical SQL (joins, aggregations, window functions) on a 5-table schema
REST_API|Python;SQL|Build a CRUD REST API with validation, status codes and Postman collection|MDN HTTP documentation|https://developer.mozilla.org/en-US/docs/Web/HTTP|Deploy an API with 5+ endpoints and a documented Postman collection|Built a RESTful CRUD API with input validation and documented endpoints
Flask|Python;REST_API|Build a notes API with Flask, SQLAlchemy and token login|Flask Tutorial (official)|https://flask.palletsprojects.com/en/stable/tutorial/|Finish the official tutorial app and add one custom feature|Developed a Flask web application with database and authentication
Django|Python;SQL|Build a blog with user accounts and an admin dashboard|Django Tutorial (official)|https://docs.djangoproject.com/en/stable/intro/tutorial01/|Complete tutorial parts 1-7 and add user registration|Built a Django web app with ORM models and admin dashboard
Unit_Testing|Python|Add a pytest suite (10+ tests, fixtures, mocks) to an existing project|pytest Getting Started (official)|https://docs.pytest.org/en/stable/getting-started.html|Reach 80% coverage on one project and run tests in CI|Wrote automated unit tests (pytest) achieving 80% coverage
DSA||Implement stack, queue, hash map, BST, graph BFS/DFS from scratch with tests|MIT OCW 6.006 Introduction to Algorithms|https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/|Solve 60 problems across arrays, trees, graphs and DP in a public repo|Implemented core data structures and solved 60+ algorithm problems
Linux||Set up an Ubuntu VM, write a cron-backed log-rotation script and manage users/permissions|Ubuntu command-line tutorial|https://ubuntu.com/tutorials/command-line-for-beginners|Complete 20 shell tasks (permissions, processes, networking, cron) in a lab notebook|Administered Linux systems (permissions, processes, cron, SSH)
PostgreSQL|SQL|Migrate a project database to PostgreSQL and add indexes with EXPLAIN evidence|PostgreSQL Docs (official)|https://www.postgresql.org/docs/current/|Show query time before/after adding one index|Used PostgreSQL with indexing and query-plan analysis
Docker|Linux|Containerise a web app + database with docker-compose|Docker Get Started (official)|https://docs.docker.com/get-started/|Publish an image and a working docker-compose.yml in your repo|Containerised a multi-service application with Docker Compose
CI_CD|Git;Unit_Testing|Add a GitHub Actions workflow that lints, tests and builds on every push|GitHub Actions docs|https://docs.github.com/en/actions|A repo with a green pipeline badge on main|Configured CI/CD pipeline (GitHub Actions) for automated test and build
Java||Build a console banking app with exceptions, collections and file persistence|Dev.java / Oracle Java tutorials|https://docs.oracle.com/javase/tutorial/|Complete the 'Learning the Java Language' trail and ship a tested project|Developed Java applications using collections, exceptions and OOP
DBMS|SQL|Normalise a messy dataset to 3NF and write transactions demonstrating ACID|CS186 Berkeley course notes|https://cs186berkeley.net/|ER diagram + 3NF schema + 3 transaction scripts|Designed normalised relational schemas (3NF) and transaction scripts
Software_Engineering||Write requirements, UML and a test plan for one existing project|Agile Manifesto and project documentation practice|-|Produce an SRS, class diagram and test plan for a project|Documented requirements, UML design and test plans
Operating_Systems||Simulate CPU scheduling (FCFS/SJF/RR) and page replacement in code|OSTEP (free textbook)|https://pages.cs.wisc.edu/~remzi/OSTEP/|Implement 3 scheduling and 3 page-replacement algorithms with output comparison|Implemented OS scheduling and memory-management simulations
Computer_Networks||Capture and explain a TCP handshake and DNS lookup; build a socket chat|Computer Networking: A Top-Down Approach resources|https://gaia.cs.umass.edu/kurose_ross/|Annotated packet-capture report + working socket chat|Built socket-based network applications and analysed packet traces
HTML||Hand-code a 3-page accessible portfolio site|MDN Learn Web Development|https://developer.mozilla.org/en-US/docs/Learn_web_development|3 semantic, validator-clean pages deployed publicly|Built semantic, accessible HTML pages
CSS|HTML|Rebuild a landing page with Flexbox/Grid, mobile-first|MDN Learn Web Development|https://developer.mozilla.org/en-US/docs/Learn_web_development|Responsive layout that passes at 360px, 768px and 1280px|Styled responsive interfaces with Flexbox and Grid
JavaScript|HTML;CSS|Build a to-do app with fetch() to a public API and DOM events|MDN JavaScript Guide|https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide|Ship an app using async/await, modules and local storage|Developed interactive web apps in JavaScript (ES6+, fetch/async)
React|JavaScript|Build a multi-page app with hooks, routing and an API call|React Learn (official)|https://react.dev/learn|Complete the tic-tac-toe + 'Thinking in React' tutorials, then deploy one app|Built single-page applications in React with hooks and routing
Angular|JavaScript;TypeScript|Build a task board with services and routing|Angular tutorials (official)|https://angular.dev/tutorials|Finish the official tutorial and deploy one app|Developed Angular components, services and routing
Vue|JavaScript|Build a weather dashboard with components and an API|Vue Tutorial (official)|https://vuejs.org/tutorial/|Finish the interactive tutorial and deploy one app|Developed Vue single-page applications
TypeScript|JavaScript|Convert a JavaScript project to strict TypeScript|TypeScript Handbook (official)|https://www.typescriptlang.org/docs/handbook/intro.html|Zero 'any' in the converted project under strict mode|Migrated a JavaScript codebase to strict TypeScript
NodeJS|JavaScript|Build a REST service with file upload and request logging|Node.js Learn (official)|https://nodejs.org/en/learn|Service with 5+ endpoints and error-handling middleware|Built Node.js backend services
ExpressJS|NodeJS|Create an Express API with JWT login and MongoDB|Express docs (official)|https://expressjs.com/en/starter/installing.html|API with auth middleware and 5+ routes tested in Postman|Developed Express.js APIs with JWT authentication
MongoDB||Model a blog with embedded vs referenced documents and add an aggregation pipeline|MongoDB Manual (official)|https://www.mongodb.com/docs/manual/tutorial/getting-started/|Write 5 aggregation queries on a seeded database|Designed MongoDB schemas and aggregation pipelines
MySQL|SQL|Build an inventory DB with stored procedures and indexes|MySQL Tutorial (official)|https://dev.mysql.com/doc/refman/8.0/en/tutorial.html|Schema + 3 stored procedures + index comparison|Implemented MySQL schemas with stored procedures and indexes
Oracle|SQL|Practice PL/SQL procedures and triggers on a sample schema|Oracle Database documentation|-|Write 3 PL/SQL procedures and 1 trigger|Wrote PL/SQL procedures and triggers
Spring_Boot|Java;REST_API|Build a REST service with JPA, validation and exception handling|Spring Boot guide (official)|https://spring.io/guides/gs/spring-boot|Service with CRUD, DTO validation and integration tests|Developed Spring Boot REST services with JPA
Maven|Java|Convert a project to Maven with dependency management and a test phase|Maven Getting Started (official)|https://maven.apache.org/guides/getting-started/|Project builds and tests with 'mvn verify'|Managed Java builds and dependencies with Maven
JUnit|Java|Add JUnit 5 tests with Mockito to a Spring or Java project|JUnit 5 User Guide (official)|https://junit.org/junit5/docs/current/user-guide/|20+ tests incl. mocks, 80% coverage|Wrote JUnit 5/Mockito tests
Hibernate|Java;SQL|Map 4 related entities with JPA and avoid N+1 queries|Hibernate ORM documentation|https://hibernate.org/orm/documentation/|Demonstrate lazy vs eager loading with SQL logs|Used Hibernate/JPA for ORM mapping
Microservices|REST_API;Docker|Split a monolith into 3 services with docker-compose|microservices.io patterns|https://microservices.io/patterns/|Three services communicating over REST with one shared gateway|Designed a containerised microservice architecture
Excel||Build a sales dashboard with PivotTables, XLOOKUP and charts|Microsoft Excel training|-|One workbook with 3 PivotTables and a dashboard sheet|Built Excel dashboards using PivotTables and lookup formulas
Data_Analysis|SQL;Python|Analyse a public dataset end-to-end and write 5 business insights|pandas 10-minute guide (official)|https://pandas.pydata.org/docs/user_guide/10min.html|Notebook with cleaning, EDA and a 1-page insight summary|Performed exploratory data analysis and presented actionable insights
Data_Visualization|Data_Analysis|Design a 3-chart story from a public dataset|Matplotlib tutorials|https://matplotlib.org/stable/tutorials/index.html|Three annotated charts with a written takeaway each|Created data visualisations communicating key insights
Statistics||Run a hypothesis test and confidence-interval analysis on real data|Khan Academy Statistics & Probability|https://www.khanacademy.org/math/statistics-probability|Written analysis with a t-test, CI and interpretation|Applied hypothesis testing and confidence intervals
Pandas|Python|Clean and merge two messy CSVs and publish the notebook|pandas 10-minute guide (official)|https://pandas.pydata.org/docs/user_guide/10min.html|Notebook with groupby, merge, missing-value handling|Wrangled data with pandas (merge, groupby, cleaning)
PowerBI|Excel;SQL|Build a 3-page sales report with DAX measures|Power BI documentation (Microsoft)|https://learn.microsoft.com/en-us/power-bi/fundamentals/|Published report with 5 DAX measures|Built Power BI dashboards with DAX measures
Tableau|Excel|Build an interactive dashboard with filters and parameters|Tableau Training|https://www.tableau.com/learn/training|Public Tableau dashboard with 3 linked views|Built interactive Tableau dashboards
NumPy|Python|Implement linear regression with NumPy only|NumPy Absolute Beginners (official)|https://numpy.org/doc/stable/user/absolute_beginners.html|Vectorised implementation matching scikit-learn within 1e-6|Used NumPy for vectorised numerical computation
Matplotlib|Python|Reproduce 4 chart types with labelled axes|Matplotlib tutorials|https://matplotlib.org/stable/tutorials/index.html|Four publication-ready plots|Produced Matplotlib visualisations
Jupyter|Python|Publish a documented analysis notebook|Jupyter documentation|https://docs.jupyter.org/en/latest/|Notebook runs top-to-bottom with explanations|Documented analyses in Jupyter notebooks
Machine_Learning|Python;Statistics|Train and compare 3 classifiers with cross-validation on a public dataset|Google ML Crash Course|https://developers.google.com/machine-learning/crash-course|Report with CV metrics, confusion matrix and error analysis|Built and evaluated ML classifiers using cross-validation
Scikit_Learn|Python;Pandas|Build a leakage-free sklearn Pipeline with grid search|scikit-learn User Guide (official)|https://scikit-learn.org/stable/user_guide.html|Pipeline + CV results + saved model|Developed scikit-learn pipelines with hyperparameter tuning
Deep_Learning|Machine_Learning;NumPy|Train a CNN on an image dataset and analyse failure cases|Dive into Deep Learning|https://d2l.ai/|Model beating a baseline with documented training curves|Trained and evaluated deep neural networks
Feature_Engineering|Pandas;Machine_Learning|Engineer 10 features for a tabular problem and measure each one's effect|scikit-learn preprocessing guide|https://scikit-learn.org/stable/modules/preprocessing.html|Ablation table showing metric change per feature group|Engineered and validated features for tabular models
PyTorch|Python;Deep_Learning|Implement a training loop and fine-tune a pretrained model|PyTorch Tutorials (official)|https://pytorch.org/tutorials/|Fine-tuned model with saved checkpoints and metrics|Built PyTorch training pipelines
TensorFlow|Python;Deep_Learning|Train an image/text classifier with Keras and export it|TensorFlow Tutorials (official)|https://www.tensorflow.org/tutorials|Exported SavedModel with evaluation report|Built TensorFlow/Keras models
Model_Deployment|Python;REST_API;Docker|Serve a trained model via FastAPI in a container with a /predict endpoint|MLflow documentation|https://mlflow.org/docs/latest/index.html|Container answering /predict with schema validation|Deployed an ML model as a containerised REST service
MLOps|Model_Deployment;Git|Track experiments and register a model with MLflow|MLflow documentation|https://mlflow.org/docs/latest/index.html|Reproducible run history for 5 experiments|Tracked experiments and versioned models with MLflow
NLP|Python;Machine_Learning|Build a text classifier and compare TF-IDF vs transformer embeddings|Hugging Face NLP Course|https://huggingface.co/learn/nlp-course|Comparison report with metrics|Developed NLP text-classification pipelines
Generative_AI|Python;Deep_Learning|Build a retrieval-augmented Q&A app over your own documents|Hugging Face NLP Course|https://huggingface.co/learn/nlp-course|Working app with an evaluation set of 20 questions|Built generative-AI applications with retrieval
Prompt_Engineering|Generative_AI|Create and evaluate 3 prompt variants on a 30-example task|Anthropic prompt engineering docs|https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview|Evaluation table comparing prompt variants|Designed and evaluated LLM prompts
Vector_Databases|Python;Generative_AI|Index 500 document chunks and compare retrieval quality|FAISS documentation|-|Retrieval hit-rate table for 20 queries|Implemented vector-search retrieval
LangChain|Python;Generative_AI|Build a tool-using agent with logging|LangChain docs|https://python.langchain.com/docs/introduction/|Agent completing 5 scripted tasks|Built LLM applications with LangChain
Cloud_Computing||Deploy a static site and a small API to a free tier and document costs|Choose one provider's getting-started guide|-|Two deployed services with an architecture diagram|Deployed applications on cloud infrastructure
AWS|Linux;Computer_Networks|Host a web app on EC2 behind a security group with an S3 bucket|AWS Getting Started|https://aws.amazon.com/getting-started/|Deployed app + IAM least-privilege policy|Deployed workloads on AWS (EC2, S3, IAM)
Azure|Linux|Deploy an App Service with Azure SQL|Microsoft Learn Azure training|https://learn.microsoft.com/en-us/training/|Deployed app with documented resource group|Deployed workloads on Microsoft Azure
Google_Cloud|Linux|Deploy a container to Cloud Run|Google Cloud documentation|https://cloud.google.com/docs|Live Cloud Run service|Deployed workloads on Google Cloud
Kubernetes|Docker;Linux|Deploy a 2-service app with a Deployment, Service and ConfigMap on a local cluster|Kubernetes Basics (official)|https://kubernetes.io/docs/tutorials/kubernetes-basics/|App surviving a deliberate pod deletion|Deployed containerised apps on Kubernetes
Terraform|Linux;Git|Provision a VPC and VM entirely from code|Terraform tutorials (HashiCorp)|https://developer.hashicorp.com/terraform/tutorials|Reproducible 'apply' and 'destroy' from a clean state|Provisioned infrastructure as code with Terraform
Jenkins|Git;Linux|Create a pipeline from a Jenkinsfile that tests and builds|Jenkins tutorials (official)|https://www.jenkins.io/doc/tutorials/|Green multi-stage pipeline|Built Jenkins CI pipelines
GitLab|Git|Create a .gitlab-ci.yml pipeline with test and build stages|GitLab CI docs|https://docs.gitlab.com/ee/ci/|Green pipeline on main|Configured GitLab CI/CD pipelines
Shell_Scripting|Linux|Write a backup + log-cleanup script with error handling|GNU Bash Manual|https://www.gnu.org/software/bash/manual/bash.html|3 scripts with exit-code handling|Automated tasks with Bash scripts
Monitoring|Linux;Docker|Instrument an app with Prometheus metrics and a Grafana dashboard|Prometheus docs|https://prometheus.io/docs/introduction/overview/|Dashboard with 1 alert rule firing|Implemented monitoring with Prometheus/Grafana
Ansible|Linux;Shell_Scripting|Write a playbook configuring a web server on 2 VMs|Ansible Getting Started|https://docs.ansible.com/ansible/latest/getting_started/index.html|Idempotent playbook (second run changes nothing)|Automated configuration with Ansible
Computer_Security|Computer_Networks;Linux|Harden a Linux VM against a checklist and document each control|OWASP Top 10|https://owasp.org/www-project-top-ten/|Hardening report with before/after scan|Applied security hardening and documented controls
SIEM|Linux;Computer_Networks|Ingest logs into a free SIEM/ELK stack and write 3 detection rules|Elastic / Splunk free training|-|3 working detections with test events|Built log-based detections in a SIEM
Vulnerability_Assessment|Computer_Networks;Linux|Scan an intentionally vulnerable lab app and write a prioritised report|OWASP ZAP getting started|https://www.zaproxy.org/getting-started/|Report with 5 findings, severity and remediation|Performed vulnerability assessments on a lab environment
Wireshark|Computer_Networks|Analyse a capture to identify an anomaly|Wireshark documentation|https://www.wireshark.org/docs/|Annotated capture analysis|Analysed network traffic with Wireshark
Cryptography|Computer_Security|Implement and attack a toy cipher; use a vetted library for AES-GCM|Choose one university or NIST resource|-|Short write-up with attack demo and correct library use|Applied cryptographic primitives correctly
OWASP|Web_Development|Fix 5 OWASP Top 10 issues in a deliberately vulnerable app|OWASP Top 10|https://owasp.org/www-project-top-ten/|5 issues reproduced and fixed with tests|Remediated OWASP Top 10 vulnerabilities
Incident_Response|Computer_Security|Run a tabletop exercise and write an incident timeline|NIST SP 800-61|https://csrc.nist.gov/pubs/sp/800/61/r2/final|Written IR playbook and one timeline|Documented incident-response procedures
Backup_Recovery|SQL;Linux|Run a full backup and a point-in-time restore and time it|PostgreSQL backup docs|https://www.postgresql.org/docs/current/backup.html|Documented restore test with recovery time|Implemented and tested database backup/restore
Performance_Tuning|SQL|Tune 5 slow queries using indexes and query plans|PostgreSQL performance tips|https://www.postgresql.org/docs/current/performance-tips.html|Before/after timing for 5 queries|Optimised SQL queries via indexing and query plans
Data_Modeling|SQL|Create ER and physical models for a domain and justify 3 design choices|CS186 Berkeley notes|https://cs186berkeley.net/|Reviewed ER diagram and DDL|Designed relational data models
Responsive_Design|CSS|Make a site usable from 320px to 1440px|MDN media queries|https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_media_queries/Using_media_queries|No horizontal scroll at 320px; Lighthouse mobile pass|Delivered mobile-first responsive layouts
Web_Accessibility|HTML;CSS|Audit and fix a page against WCAG basics|W3C WAI introduction|https://www.w3.org/WAI/fundamentals/accessibility-intro/|Zero critical axe/Lighthouse accessibility errors|Improved web accessibility (WCAG)
Jest|JavaScript|Write component and unit tests with coverage|Jest documentation|https://jestjs.io/docs/getting-started|15+ tests, 80% coverage|Wrote Jest tests for frontend code
Figma||Prototype a 3-screen flow with components|Figma Help Center|https://help.figma.com/hc/en-us|Clickable prototype|Prototyped UI flows in Figma
NextJS|React|Build a server-rendered blog with dynamic routes|Next.js Learn (official)|https://nextjs.org/learn|Deployed app with SSR pages|Built Next.js applications
Authentication|REST_API|Implement password hashing, sessions/JWT and role checks|OWASP Authentication Cheat Sheet|https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html|Auth flow with tests for forbidden access|Implemented secure authentication and role-based access
Redis|REST_API|Add caching to an API and measure latency|Redis documentation|https://redis.io/docs/latest/|Latency before/after with hit ratio|Used Redis caching to reduce latency
System_Design|REST_API;DBMS|Draft a design doc for a URL shortener with trade-offs|Write a design doc (no single official source)|-|Reviewed 2-page design doc|Authored system design documents
Message_Queues|REST_API|Add an async worker fed by a queue|Apache Kafka quickstart|https://kafka.apache.org/documentation/#quickstart|Worker processing 1000 queued jobs|Used message queues for async processing
CSharp|OOP|Build a console + minimal API app|C# documentation (Microsoft)|https://learn.microsoft.com/en-us/dotnet/csharp/|Tested app on GitHub|Developed C# applications
Go|Git|Build a concurrent URL checker|A Tour of Go (official)|https://go.dev/tour/|Finish the tour and ship the tool|Built Go command-line services
Cpp|DSA|Implement an STL-style container with templates|Choose one reputable university C++ course|-|Tested container with iterators|Implemented data structures in C++
Agile||Run a 2-week sprint on a team project with a board|Scrum Guide|https://scrumguides.org/|Sprint board + retrospective notes|Worked in Agile/Scrum sprints
""".strip()


def _parse_kits(text):
    kits = {}
    for line in text.splitlines():
        key, pre, proj, rname, url, ms, resume = line.split("|")
        kits[key] = dict(prereq=[p for p in pre.split(";") if p], project=proj,
                         resource=(rname, None if url == "-" else url),
                         milestone=ms, resume=resume)
    return kits


KITS = _parse_kits(_KIT_TEXT)
