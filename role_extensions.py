"""
role_extensions.py
==================
Adds Civil, Mechanical, Production / Industrial, Electrical, Electronics & Communication and Aerospace
roles (and the skills they need) to skill_gap's catalog WITHOUT editing skill_gap.py.

Import this module right after `import skill_gap`; it extends SKILL_DB / ROLES / WEEKS / TIPS in place.

* Skills whose catalog name equals a registry display name (e.g. "AutoCAD", "STAAD.Pro", "PLC",
  "Primavera") are also model inputs, so the score "what-if" works for them.
* Other skills (e.g. "Thermodynamics", "Six Sigma") are matched from resume text and used for the gap plan only.
* To add a role: add a skill to SKILLS below if needed, then call _role(...) and list it in FAMILIES.
"""
import re

import skill_gap as sg

# ----------------------------------------------------------------------------- skills
# name: (category, [aliases matched in resume text])
SKILLS = {
    # ---- Civil
    "AutoCAD": ("Design & CAD", ["autocad", "auto cad"]),
    "Revit": ("Civil", ["revit"]),
    "STAAD.Pro": ("Civil", ["staad", "staad pro", "staad.pro"]),
    "ETABS": ("Civil", ["etabs", "sap2000"]),
    "Civil 3D": ("Civil", ["civil 3d", "civil3d"]),
    "Primavera": ("Civil", ["primavera", "primavera p6", "ms project", "microsoft project"]),
    "BIM": ("Civil", ["bim", "building information modeling", "building information modelling"]),
    "Structural Analysis": ("Civil", ["structural analysis", "structural design"]),
    "Surveying": ("Civil", ["surveying", "total station", "land surveying"]),
    "Construction Management": ("Civil", ["construction management", "construction planning", "project management"]),
    "Concrete & Steel Design": ("Civil", ["rcc design", "concrete design", "steel design", "reinforced concrete", "prestressed concrete"]),
    "Estimation & Costing": ("Civil", ["estimation", "costing", "quantity surveying", "bill of quantities", "boq", "rate analysis"]),
    "Geotechnical Engineering": ("Civil", ["geotechnical", "soil mechanics", "foundation engineering", "soil testing"]),
    "Transportation Engineering": ("Civil", ["highway engineering", "transportation engineering", "road design", "traffic engineering"]),
    "Building Codes & Standards": ("Civil", ["is codes", "bis codes", "is 456", "is 800", "building codes", "national building code", "irc codes"]),
    "Site Execution": ("Civil", ["site execution", "site supervision", "site work", "construction supervision"]),
    "GIS": ("Civil", ["gis", "arcgis", "qgis"]),
    "Water Resources": ("Civil", ["hydrology", "water resources", "environmental engineering", "wastewater"]),
    # ---- Mechanical
    "SolidWorks": ("Mechanical", ["solidworks", "solid works"]),
    "CATIA": ("Mechanical", ["catia"]),
    "Creo": ("Mechanical", ["creo", "pro/e", "pro-e"]),
    "ANSYS": ("Mechanical", ["ansys"]),
    "CAD": ("Design & CAD", ["cad", "computer aided design", "computer-aided design", "3d cad"]),
    "CAM": ("Mechanical", ["computer aided manufacturing", "computer-aided manufacturing", "mastercam", "cam programming"]),
    "CAE": ("Mechanical", ["cae", "finite element analysis", "finite element method", "fea"]),
    "CNC": ("Manufacturing & Quality", ["cnc", "cnc machining", "cnc programming", "g-code", "g code"]),
    "Robotics": ("Mechanical", ["robotics", "robotic arm", "robot operating system"]),
    "3D Modeling": ("Mechanical", ["3d modeling", "3d modelling", "3d printing", "additive manufacturing"]),
    "Manufacturing": ("Manufacturing & Quality", ["manufacturing", "manufacturing processes", "machining", "casting", "welding"]),
    "Thermodynamics": ("Mechanical", ["thermodynamics", "heat transfer", "thermal engineering", "thermal analysis"]),
    "Fluid Mechanics": ("Mechanical", ["fluid mechanics", "fluid dynamics", "cfd", "ansys fluent"]),
    "Machine Design": ("Mechanical", ["machine design", "design of machine elements", "mechanical design"]),
    "Strength of Materials": ("Mechanical", ["strength of materials", "mechanics of materials", "solid mechanics"]),
    "GD&T": ("Mechanical", ["gd&t", "gdt", "geometric dimensioning", "geometric dimensioning and tolerancing"]),
    "HVAC": ("Mechanical", ["hvac", "refrigeration and air conditioning", "air conditioning", "refrigeration"]),
    "Automotive Engineering": ("Mechanical", ["automotive engineering", "ic engines", "internal combustion", "vehicle dynamics", "ev powertrain"]),
    "Mechatronics": ("Mechanical", ["mechatronics"]),
    "Maintenance Engineering": ("Mechanical", ["maintenance engineering", "preventive maintenance", "predictive maintenance", "total productive maintenance", "tpm", "condition monitoring"]),
    "Hydraulics & Pneumatics": ("Mechanical", ["hydraulics", "pneumatics", "hydraulic systems"]),
    "Material Science": ("Mechanical", ["material science", "materials science", "metallurgy", "material selection"]),
    "Engineering Drawing": ("Design & CAD", ["engineering drawing", "technical drawing", "drafting"]),
    "Aerodynamics": ("Aerospace", ["aerodynamics", "aircraft design", "propulsion", "flight mechanics", "gas dynamics"]),
    "MATLAB": ("Tools", ["matlab"]),
    "Simulink": ("Tools", ["simulink"]),
    # ---- Production / industrial / quality
    "Lean Manufacturing": ("Manufacturing & Quality", ["lean manufacturing", "lean six sigma", "kaizen", "5s", "value stream mapping", "just in time"]),
    "Six Sigma": ("Manufacturing & Quality", ["six sigma", "lean six sigma", "dmaic", "green belt"]),
    "Quality Control": ("Manufacturing & Quality", ["quality control", "quality inspection", "spc", "statistical process control", "iso 9001", "quality management"]),
    "Production Planning": ("Manufacturing & Quality", ["production planning", "production scheduling", "production planning and control", "ppc", "capacity planning", "mrp"]),
    "Supply Chain & Inventory": ("Manufacturing & Quality", ["supply chain", "inventory management", "logistics", "procurement", "warehouse management"]),
    "Process Planning": ("Manufacturing & Quality", ["process planning", "process design", "work instruction", "process optimization", "process optimisation", "cycle time"]),
    "Industrial Engineering": ("Manufacturing & Quality", ["industrial engineering", "work study", "time study", "method study", "ergonomics"]),
    "Operations Research": ("Manufacturing & Quality", ["operations research", "linear programming", "simulation modeling", "queueing"]),
    "Tool & Die Design": ("Manufacturing & Quality", ["jigs and fixtures", "jig and fixture", "tool design", "die design", "press tools"]),
    "Industrial Safety": ("Manufacturing & Quality", ["industrial safety", "safety management", "hse", "ehs", "hazop", "risk assessment"]),
    "ERP / SAP": ("Manufacturing & Quality", ["erp", "sap", "sap pm", "sap mm"]),
    "Metrology": ("Manufacturing & Quality", ["metrology", "cmm", "coordinate measuring", "vernier", "micrometer"]),
    # ---- Electrical
    "PLC": ("Electrical", ["plc", "programmable logic controller", "ladder logic", "siemens s7", "allen-bradley", "allen bradley", "tia portal"]),
    "SCADA": ("Electrical", ["scada", "hmi", "wincc"]),
    "Power Systems": ("Electrical", ["power systems", "power system", "load flow", "power system analysis", "switchgear", "protection systems"]),
    "Control Systems": ("Electrical", ["control systems", "control system", "pid control", "pid", "state space"]),
    "Electrical Machines": ("Electrical", ["electrical machines", "electrical machine", "transformers", "motors and drives", "induction motor"]),
    "Power Electronics": ("Electrical", ["power electronics", "smps", "inverters", "dc-dc converters"]),
    "Electrical Design": ("Electrical", ["electrical design", "electrical drawings", "load calculation", "cable sizing", "earthing design", "lighting design", "etap", "dialux"]),
    "Industrial Automation": ("Electrical", ["industrial automation", "process automation", "vfd", "variable frequency drive", "factory automation"]),
    "Electrical Standards": ("Electrical", ["iec standards", "ieee standards", "national electrical code", "electrical safety", "is 732"]),
    "Instrumentation": ("Electrical", ["instrumentation", "sensors and transducers", "transmitters", "process instrumentation"]),
    "Renewable Energy": ("Electrical", ["renewable energy", "solar pv", "pv system design", "wind energy", "pvsyst"]),
    # ---- Electronics & communication
    "Digital Electronics": ("Electronics", ["digital electronics", "digital logic", "logic design", "combinational circuits"]),
    "Analog Electronics": ("Electronics", ["analog electronics", "analog circuits", "op-amp", "op amp", "operational amplifier"]),
    "Verilog": ("Electronics", ["verilog", "systemverilog"]),
    "VHDL": ("Electronics", ["vhdl"]),
    "FPGA": ("Electronics", ["fpga", "xilinx", "vivado", "altera", "quartus"]),
    "Signal Processing": ("Electronics", ["signal processing", "digital signal processing", "dsp", "fft"]),
    "VLSI Design": ("Electronics", ["vlsi", "cmos", "asic", "rtl design", "physical design", "cadence", "synopsys"]),
    "Communication Systems": ("Electronics", ["communication systems", "digital communication", "wireless communication", "modulation", "antenna", "rf design", "5g", "lte"]),
}

WEEKS = {
    "AutoCAD": 3, "Revit": 5, "STAAD.Pro": 4, "ETABS": 4, "Civil 3D": 5, "Primavera": 4, "BIM": 4,
    "Structural Analysis": 8, "Surveying": 3, "Construction Management": 5, "Concrete & Steel Design": 8,
    "Estimation & Costing": 4, "Geotechnical Engineering": 5, "Transportation Engineering": 5,
    "Building Codes & Standards": 3, "Site Execution": 4, "GIS": 3, "Water Resources": 5,
    "SolidWorks": 5, "CATIA": 6, "Creo": 5, "ANSYS": 6, "CAD": 4, "CAM": 4, "CAE": 6, "CNC": 5, "Robotics": 6,
    "Manufacturing": 5, "Thermodynamics": 5, "Fluid Mechanics": 5, "Machine Design": 6, "Strength of Materials": 5,
    "GD&T": 3, "HVAC": 5, "Automotive Engineering": 6, "Mechatronics": 5, "Aerodynamics": 6, "MATLAB": 3, "Simulink": 4,
    "Lean Manufacturing": 3, "Six Sigma": 5, "Quality Control": 4, "Production Planning": 4, "Process Planning": 4,
    "Industrial Engineering": 5, "Operations Research": 5, "Tool & Die Design": 5, "ERP / SAP": 4, "Metrology": 3,
    "PLC": 5, "SCADA": 4, "Power Systems": 7, "Control Systems": 6, "Electrical Machines": 5, "Power Electronics": 6,
    "Electrical Design": 5, "Industrial Automation": 5, "Instrumentation": 4, "Renewable Energy": 4,
    "Digital Electronics": 4, "Analog Electronics": 5, "Verilog": 5, "VHDL": 4, "FPGA": 5, "Signal Processing": 6,
    "VLSI Design": 8, "Communication Systems": 6,
}

TIPS = {
    "AutoCAD": "Redraw a full residential plan, section and elevation from scratch; practise layers, dimensioning and plotting to scale.",
    "Revit": "Model a small building (architecture + structure) from your AutoCAD plan and produce schedules and sheets.",
    "STAAD.Pro": "Model and analyse a G+3 framed building, then check the beam and column results by hand for one member.",
    "Primavera": "Create a schedule with WBS, durations, dependencies and a critical path for a small building project.",
    "Estimation & Costing": "Take off quantities for a residential building from drawings and prepare a priced BOQ in Excel.",
    "Surveying": "Do a levelling and total-station exercise, then plot the contours or layout in AutoCAD.",
    "SolidWorks": "Model 3 parts, assemble them, and produce a detailed drawing; aim for the CSWA exam.",
    "ANSYS": "Run a static-structural and a thermal case on a part you designed and validate the result against a hand calculation.",
    "CNC": "Write and simulate G-code for two parts (turning and milling); describe your tool and feed choices.",
    "GD&T": "Annotate one of your drawings using datums, flatness, position and fits, and explain each callout.",
    "Lean Manufacturing": "Map the value stream of any process (even a canteen or lab), list the wastes, and propose 5S/kaizen changes with numbers.",
    "Six Sigma": "Complete a Green Belt-level course and apply DMAIC to a small dataset (defects, cycle time).",
    "Quality Control": "Build control charts (X-bar/R) in Excel from sample data and interpret out-of-control signals.",
    "PLC": "Program ladder logic for a conveyor and a traffic-light sequence in a free simulator.",
    "Power Systems": "Solve a load-flow and fault-analysis case study by hand and in a simulation tool (MATLAB/ETAP/PowerWorld).",
    "Electrical Design": "Prepare a single-line diagram, load calculation and cable sizing for a small building.",
    "Verilog": "Code and simulate an adder, counter and FSM, then run them on an FPGA board or simulator with testbenches.",
    "Signal Processing": "Implement filtering and FFT on a recorded signal in MATLAB or Python and explain the results.",
    "Control Systems": "Design a PID controller for a motor or tank model in MATLAB/Simulink and show the step response.",
}


# ----------------------------------------------------------------------------- roles
ROLES = {}


def _role(name, aliases, core, preferred, certs, projects, interview, min_projects=2):
    ROLES[name] = dict(aliases=aliases, core=core, preferred=preferred, min_projects=min_projects,
                       certifications=certs, projects=projects, interview=interview)


# ---- CIVIL
_role("Site Engineer (Civil)",
      ["civil site engineer", "site engineer", "construction engineer", "civil engineer", "junior civil engineer", "execution engineer"],
      ["AutoCAD", "Site Execution", "Construction Management", "Estimation & Costing", "Surveying", "Building Codes & Standards"],
      ["Primavera", "Revit", "Structural Analysis", "Excel", "Documentation"],
      ["AutoCAD Certified User (Autodesk)", "NPTEL Construction Planning and Management", "Primavera P6 foundation course", "NEBOSH IGC or similar site-safety certificate (later stage)"],
      [("Quantity take-off and cost estimate for a small residential building", ["Estimation & Costing", "AutoCAD", "Excel"]),
       ("Construction schedule for a G+2 building in Primavera or MS Project", ["Primavera", "Construction Management"]),
       ("Total-station survey with a contour and layout drawing", ["Surveying", "AutoCAD"]),
       ("Quality and safety checklist for concreting and formwork based on IS codes", ["Building Codes & Standards", "Site Execution"])],
      ["Concrete grades, curing and slump test", "Reading structural and architectural drawings", "Quantity estimation of a slab or footing", "Site safety and handling contractors and labour"])

_role("Structural Design Engineer",
      ["structural engineer", "structural designer", "rcc designer", "structural design", "design engineer civil"],
      ["Structural Analysis", "STAAD.Pro", "Concrete & Steel Design", "AutoCAD", "Building Codes & Standards", "Strength of Materials"],
      ["ETABS", "Revit", "BIM", "Excel", "Geotechnical Engineering"],
      ["NPTEL Design of Reinforced Concrete and Steel Structures", "Vendor training for STAAD.Pro / ETABS", "Autodesk Revit certification (structural track, later stage)"],
      [("Analyse and design a G+3 RCC frame in STAAD.Pro or ETABS per IS 456 with a hand-check of one beam and column", ["STAAD.Pro", "ETABS", "Concrete & Steel Design", "Structural Analysis"]),
       ("Design a steel roof truss and connections per IS 800", ["Concrete & Steel Design", "Structural Analysis"]),
       ("Foundation design (isolated and combined footing) from soil data", ["Geotechnical Engineering", "Concrete & Steel Design"]),
       ("Structural model in Revit with reinforcement detailing drawings", ["Revit", "AutoCAD", "BIM"])],
      ["Limit state design basics and load combinations", "Bending moment and shear force diagrams", "Difference between one-way and two-way slabs", "Walk through one design you did end to end"],
      min_projects=3)

_role("Construction Planning Engineer",
      ["planning engineer", "project planner", "project engineer civil", "construction project engineer", "construction planner"],
      ["Construction Management", "Primavera", "Estimation & Costing", "Excel", "Site Execution", "Documentation"],
      ["BIM", "AutoCAD", "Stakeholder Management", "Building Codes & Standards", "Industrial Safety"],
      ["Primavera P6 course certificate", "NPTEL Construction Planning and Management", "CAPM (later stage)"],
      [("Baseline schedule with resource loading and a critical-path analysis", ["Primavera", "Construction Management"]),
       ("Cash-flow and cost-control sheet for a small project", ["Excel", "Estimation & Costing"]),
       ("Weekly progress report and delay analysis for a case study project", ["Documentation", "Site Execution"])],
      ["Critical path method and float", "Earned value basics", "Resource levelling", "How you would recover a delayed schedule"])

_role("Quantity Surveyor / Estimation Engineer",
      ["quantity surveyor", "estimation engineer", "cost engineer", "billing engineer", "qs", "estimator"],
      ["Estimation & Costing", "AutoCAD", "Excel", "Building Codes & Standards", "Documentation", "Construction Management"],
      ["Revit", "BIM", "Primavera", "Stakeholder Management"],
      ["NPTEL Construction Management / Estimation courses", "Excel for cost control course certificate"],
      [("Full BOQ with rate analysis for a G+1 building", ["Estimation & Costing", "Excel"]),
       ("Quantity take-off from a Revit or AutoCAD model", ["Revit", "AutoCAD", "BIM"]),
       ("Tender comparison statement for three contractor quotes", ["Documentation", "Excel"])],
      ["Rate analysis of brickwork or plastering", "Mode of measurement as per IS 1200", "Variation orders and running bills", "Excel formulas for quantity sheets"])

_role("BIM / CAD Engineer (Civil)",
      ["bim engineer", "bim modeler", "revit modeler", "cad engineer civil", "draftsman civil", "civil draftsman"],
      ["Revit", "BIM", "AutoCAD", "Engineering Drawing", "Documentation"],
      ["Civil 3D", "Structural Analysis", "Building Codes & Standards"],
      ["Autodesk Certified Professional in Revit (later stage)", "AutoCAD Certified User (Autodesk)"],
      [("Full architectural + structural model of a small building in Revit with sheets", ["Revit", "BIM"]),
       ("Convert 2D AutoCAD plans into a coordinated 3D model", ["AutoCAD", "Revit"]),
       ("Clash-detection report for two discipline models", ["BIM", "Documentation"])],
      ["Levels of development (LOD)", "Families and parametric components", "Clash detection workflow", "Sheet setup and annotation standards"])

_role("Highway / Transportation Engineer",
      ["highway engineer", "road engineer", "transportation engineer", "infrastructure engineer", "civil 3d engineer"],
      ["Transportation Engineering", "Civil 3D", "AutoCAD", "Surveying", "Geotechnical Engineering", "Estimation & Costing"],
      ["GIS", "Building Codes & Standards", "Primavera", "Construction Management"],
      ["NPTEL Highway Engineering / Transportation Systems", "Civil 3D vendor training"],
      [("Geometric design of 1 km of road (horizontal and vertical alignment) in Civil 3D", ["Civil 3D", "Transportation Engineering", "Surveying"]),
       ("Pavement design from CBR and traffic data per IRC", ["Geotechnical Engineering", "Transportation Engineering"]),
       ("Cost estimate and quantities for the road project", ["Estimation & Costing", "AutoCAD"])],
      ["Design speed, sight distance and curves", "Flexible vs rigid pavement", "CBR test and subgrade", "Traffic volume studies"])

_role("Water & Environmental Engineer",
      ["environmental engineer", "water resources engineer", "hydrology engineer", "wastewater engineer"],
      ["Water Resources", "GIS", "AutoCAD", "Excel", "Documentation"],
      ["Python", "Surveying", "Statistics", "Civil 3D"],
      ["NPTEL Water Resources / Environmental Engineering courses", "QGIS / ArcGIS introductory certificate"],
      [("Catchment delineation and runoff estimate for a small basin using QGIS", ["GIS", "Water Resources"]),
       ("Design a small water-supply or sewer network with calculations", ["Water Resources", "AutoCAD", "Excel"]),
       ("Rainfall-data statistical analysis in Excel or Python", ["Statistics", "Python", "Excel"])],
      ["Hydrologic cycle and design storms", "Water treatment unit processes", "BOD, COD and effluent standards", "GIS layers and projections"])

# ---- MECHANICAL
_role("Mechanical Design Engineer",
      ["mechanical engineer", "cad design engineer", "product design engineer", "mechanical design", "design engineer mechanical"],
      [("CAD", "SolidWorks", "CATIA", "Creo", "AutoCAD"), "Machine Design", "Strength of Materials", "GD&T", "Engineering Drawing", "Material Science"],
      ["ANSYS", "CAE", "Manufacturing", "3D Modeling", "Metrology"],
      ["Certified SolidWorks Associate (CSWA) then CSWP", "Autodesk certification (Inventor / AutoCAD)", "NPTEL Design of Machine Elements"],
      [("Design a gearbox or a pressure vessel with calculations, 3D model and detailed drawings", ["SolidWorks", "Machine Design", "Strength of Materials", "Engineering Drawing"]),
       ("Tolerance stack-up and GD&T drawing for an assembly", ["GD&T", "Engineering Drawing"]),
       ("Static FEA of a bracket with design optimisation", ["ANSYS", "CAE"]),
       ("3D-printed functional prototype with design rationale", ["3D Modeling", "CAD"])],
      ["Factor of safety and failure theories", "Bearing, gear and shaft design basics", "Reading and creating manufacturing drawings", "Walk through one of your design projects"],
      min_projects=3)

_role("CAE / Simulation Engineer",
      ["cae engineer", "fea engineer", "simulation engineer", "cfd engineer", "analysis engineer"],
      ["CAE", "ANSYS", "Strength of Materials", "Fluid Mechanics", "Thermodynamics", "CAD"],
      ["MATLAB", "Python", "Material Science", "Machine Design", "SolidWorks"],
      ["ANSYS learning-hub courses (free) and certificates", "NPTEL Finite Element Method / CFD"],
      [("Static structural and modal analysis of a component with mesh-convergence study", ["ANSYS", "CAE", "Strength of Materials"]),
       ("CFD of flow through a pipe bend or around an aerofoil validated against theory", ["Fluid Mechanics", "ANSYS"]),
       ("Transient thermal analysis of a heat sink", ["Thermodynamics", "CAE"])],
      ["Mesh quality and convergence", "Boundary conditions and how to validate", "Linear vs non-linear analysis", "Steady vs transient CFD"],
      min_projects=3)

_role("Manufacturing Engineer",
      ["manufacturing engineer", "process engineer manufacturing", "shop floor engineer", "machining engineer"],
      ["Manufacturing", "CNC", "Process Planning", "GD&T", "Metrology", "Engineering Drawing"],
      ["Lean Manufacturing", "CAM", "Quality Control", "Tool & Die Design", "Industrial Safety"],
      ["NPTEL Manufacturing Processes courses", "Lean / Six Sigma Yellow or Green Belt", "NSDC / SSC machining or CNC operator certificates"],
      [("Process plan, routing sheet and cycle-time estimate for a machined component", ["Process Planning", "Manufacturing", "Engineering Drawing"]),
       ("CNC program for a turned or milled part with simulation", ["CNC", "CAM"]),
       ("Inspection plan with a gauge and measurement data sheet", ["Metrology", "GD&T", "Quality Control"])],
      ["Machining parameters (speed, feed, depth)", "Casting, forging and welding defects", "Fits, tolerances and inspection tools", "How to reduce cycle time"])

_role("Thermal / HVAC Engineer",
      ["hvac engineer", "thermal engineer", "refrigeration engineer", "mep engineer", "mechanical mep engineer"],
      ["HVAC", "Thermodynamics", "Fluid Mechanics", "AutoCAD", "Excel"],
      ["Revit", "ANSYS", "Estimation & Costing", "Building Codes & Standards"],
      ["NPTEL Refrigeration and Air Conditioning", "ASHRAE learning-institute courses", "AutoCAD Certified User"],
      [("Cooling-load calculation and equipment selection for a small commercial space", ["HVAC", "Thermodynamics", "Excel"]),
       ("Duct layout and sizing drawing", ["AutoCAD", "Fluid Mechanics", "HVAC"]),
       ("Psychrometric analysis of an air-conditioning cycle", ["Thermodynamics", "HVAC"])],
      ["Psychrometric chart and processes", "Vapour-compression cycle and COP", "Duct sizing methods", "Heat load components"])

_role("Automotive Engineer",
      ["automotive engineer", "vehicle engineer", "ev engineer", "automobile engineer", "powertrain engineer"],
      ["Automotive Engineering", "CAD", "Machine Design", "Thermodynamics", "Strength of Materials"],
      ["CATIA", "ANSYS", "MATLAB", "Simulink", "GD&T"],
      ["NPTEL Automotive / IC Engine courses", "SAE collegiate design series participation (Formula / Baja)", "MATLAB Onramp (free)"],
      [("Design a suspension or chassis component and analyse it in FEA", ["CAD", "ANSYS", "Machine Design"]),
       ("Engine or EV powertrain performance model in MATLAB/Simulink", ["MATLAB", "Simulink", "Automotive Engineering"]),
       ("Team vehicle project (Baja / Formula / Supra) with documented contribution", ["Automotive Engineering", "CATIA"])],
      ["Four-stroke cycle and engine performance", "Braking, steering and suspension geometry", "EV battery and motor basics", "Your vehicle-team project"],
      min_projects=3)

_role("Robotics / Mechatronics Engineer",
      ["robotics engineer", "mechatronics engineer", "robotics", "mechatronics"],
      ["Robotics", "Mechatronics", "Microcontrollers", "Control Systems", "CAD", ("Python", "C++")],
      ["PLC", "Raspberry Pi", "MATLAB", "Simulink", "3D Modeling", "Embedded C"],
      ["NPTEL Robotics courses", "MATLAB Onramp and Simulink Onramp (free)", "ROS beginner course certificate"],
      [("Line-following or obstacle-avoiding robot with sensors and a microcontroller", ["Microcontrollers", "Robotics", "Embedded C"]),
       ("Robotic-arm kinematics simulation in MATLAB or Python", ["Robotics", "MATLAB", "Python"]),
       ("PID speed or position control of a motor with a plotted response", ["Control Systems", "Simulink"]),
       ("3D-printed chassis designed in CAD", ["CAD", "3D Modeling"])],
      ["Forward and inverse kinematics", "PID tuning", "Sensors and actuators selection", "Your robot build, end to end"],
      min_projects=3)

_role("Maintenance Engineer",
      ["plant maintenance engineer", "reliability engineer", "maintenance engineer", "service engineer", "maintenance engineer mechanical"],
      ["Maintenance Engineering", "Hydraulics & Pneumatics", "Thermodynamics", "Industrial Safety", "Engineering Drawing", "Documentation"],
      ["PLC", "Lean Manufacturing", "ERP / SAP", "Metrology"],
      ["NPTEL Maintenance Engineering / TPM courses", "NEBOSH IGC or similar safety certificate (later stage)", "Basic PLC / hydraulics vendor training"],
      [("Preventive-maintenance schedule and checklist for a set of machines", ["Maintenance Engineering", "Documentation"]),
       ("Root-cause analysis (5-Why / fishbone) of a failure case study", ["Maintenance Engineering", "Industrial Safety"]),
       ("Hydraulic or pneumatic circuit design and simulation", ["Hydraulics & Pneumatics"])],
      ["Preventive vs predictive maintenance", "Common causes of bearing and pump failures", "Reading hydraulic circuit symbols", "Lock-out tag-out and safety practices"])

_role("Aerospace / Aeronautical Engineer",
      ["aerospace engineer", "aeronautical engineer", "aircraft design engineer", "aerospace design engineer"],
      ["CAD", "CATIA", "Fluid Mechanics", "Thermodynamics", "Strength of Materials", "Aerodynamics"],
      ["ANSYS", "CAE", "MATLAB", "Simulink", "Material Science"],
      ["NPTEL Aerodynamics / Propulsion courses", "MATLAB Onramp (free)", "Aerodynamics or CFD short courses"],
      [("Airfoil CFD study comparing lift and drag at several angles of attack", ["Aerodynamics", "ANSYS", "Fluid Mechanics"]),
       ("Design and analysis of a wing rib or fuselage frame", ["CATIA", "CAE", "Strength of Materials"]),
       ("Flight-dynamics or rocket-trajectory simulation", ["MATLAB", "Simulink"])],
      ["Lift, drag and boundary layer", "Compressible-flow basics", "Jet engine cycles", "Aircraft structural components"],
      min_projects=3)

# ---- PRODUCTION / INDUSTRIAL
_role("Production Engineer",
      ["production engineer", "production planning engineer", "production supervisor", "manufacturing operations", "shop floor production engineer"],
      ["Production Planning", "Manufacturing", "Process Planning", "Lean Manufacturing", "Quality Control", "Industrial Safety"],
      ["Six Sigma", "ERP / SAP", "Excel", "Industrial Engineering", "CNC", "Statistics"],
      ["Lean Six Sigma Yellow or Green Belt", "NPTEL Production Planning and Control", "NSDC / SSC manufacturing certificates"],
      [("Production schedule and capacity plan for a multi-product line in Excel", ["Production Planning", "Excel"]),
       ("Line-balancing study with takt-time and cycle-time analysis", ["Lean Manufacturing", "Process Planning"]),
       ("Defect Pareto and corrective-action plan from sample data", ["Quality Control", "Statistics"]),
       ("5S and layout improvement proposal with before/after numbers", ["Lean Manufacturing", "Industrial Safety"])],
      ["Takt time, OEE and line balancing", "Push vs pull and kanban", "Common casting, welding and machining defects", "How you handle a missed production target"],
      min_projects=3)

_role("Quality Engineer",
      ["quality engineer", "quality control engineer", "qc engineer", "inspection engineer", "quality assurance engineer manufacturing"],
      ["Quality Control", "Statistics", "Metrology", "GD&T", "Six Sigma", "Engineering Drawing"],
      ["Lean Manufacturing", "Excel", "Documentation", "Manufacturing", "ERP / SAP"],
      ["Lean Six Sigma Green Belt", "ASQ Certified Quality Technician / Engineer (later stage)", "ISO 9001 internal-auditor course"],
      [("SPC study with X-bar/R charts and a process-capability (Cp/Cpk) report", ["Quality Control", "Statistics", "Excel"]),
       ("Inspection plan and measurement-system analysis for a part", ["Metrology", "GD&T"]),
       ("8D / corrective-action report for a defect case study", ["Quality Control", "Documentation"])],
      ["Cp, Cpk and control charts", "7 QC tools", "Difference between QA and QC", "Calibration and measurement uncertainty"])

_role("Industrial / Process Improvement Engineer",
      ["industrial engineer", "process improvement engineer", "lean engineer", "operations engineer", "continuous improvement engineer"],
      ["Industrial Engineering", "Lean Manufacturing", "Six Sigma", "Process Planning", "Statistics", "Excel"],
      ["Operations Research", "Supply Chain & Inventory", "ERP / SAP", "Python", "Power BI"],
      ["Lean Six Sigma Green Belt", "NPTEL Industrial Engineering / Operations Management", "Excel or Power BI course certificate"],
      [("Time-and-motion study with a standard-time calculation and layout redesign", ["Industrial Engineering", "Process Planning"]),
       ("DMAIC project on a real or sample process with measurable savings", ["Six Sigma", "Statistics"]),
       ("Linear-programming model for product mix solved with Excel Solver", ["Operations Research", "Excel"])],
      ["DMAIC phases", "Value-stream mapping and waste types", "Linear programming formulation", "How to measure improvement"],
      min_projects=3)

_role("Supply Chain / Operations Engineer",
      ["supply chain engineer", "logistics engineer", "materials engineer", "procurement engineer", "operations analyst"],
      ["Supply Chain & Inventory", "Production Planning", "Excel", "ERP / SAP", "Operations Research", "Documentation"],
      ["Power BI", "SQL", "Lean Manufacturing", "Statistics"],
      ["NPTEL Supply Chain Management", "APICS / ASCM CSCP (later stage)", "SAP MM or PP fundamentals course"],
      [("Inventory model (EOQ, reorder point, safety stock) with a sensitivity table", ["Supply Chain & Inventory", "Excel"]),
       ("Demand-forecast and material-requirements plan for a sample product", ["Production Planning", "Statistics"]),
       ("Supplier scorecard dashboard", ["Power BI", "Excel"])],
      ["EOQ, ABC analysis and safety stock", "MRP logic", "Bullwhip effect", "How you would cut lead time"])

_role("CNC Programmer / Tool Engineer",
      ["cnc programmer", "tool design engineer", "tool and die engineer", "cam programmer", "machining programmer"],
      ["CNC", "CAM", "Tool & Die Design", "GD&T", "Engineering Drawing", "Manufacturing"],
      ["SolidWorks", "Metrology", "Material Science", "Lean Manufacturing"],
      ["NSDC / SSC CNC programming certificates", "Mastercam / Fusion 360 CAM course certificate", "NPTEL Manufacturing Processes"],
      [("CAM toolpaths and G-code for a milled part, simulated and verified", ["CAM", "CNC"]),
       ("Jig or fixture design with a drawing and clamping-force reasoning", ["Tool & Die Design", "Engineering Drawing"]),
       ("Tool-life and cutting-parameter comparison on sample data", ["Manufacturing", "Material Science"])],
      ["G and M codes", "Work and tool offsets", "Fixture locating principles (3-2-1)", "Choosing speeds and feeds"])

# ---- ELECTRICAL
_role("Electrical Design Engineer",
      ["electrical engineer", "electrical design", "mep electrical engineer", "electrical drafter", "power distribution design"],
      ["Electrical Design", "AutoCAD", "Electrical Machines", "Power Systems", "Electrical Standards", "Circuit Design"],
      ["Renewable Energy", "Revit", "Excel", "Control Systems"],
      ["NPTEL Electrical Machines / Power Systems", "AutoCAD Electrical or AutoCAD Certified User", "Electrical-safety / wiring-code short course"],
      [("Single-line diagram, load calculation and cable sizing for a small building", ["Electrical Design", "AutoCAD", "Excel"]),
       ("Lighting design and layout for a commercial space", ["Electrical Design", "AutoCAD"]),
       ("Earthing and protection scheme write-up with calculations", ["Electrical Standards", "Power Systems"])],
      ["Cable selection and voltage drop", "Transformer and motor ratings", "MCB / MCCB / RCCB differences", "Earthing types"],
      min_projects=3)

_role("Power Systems Engineer",
      ["power engineer", "power system engineer", "transmission engineer", "substation engineer", "protection engineer"],
      ["Power Systems", "Electrical Machines", "Power Electronics", "MATLAB", "Electrical Standards", "Control Systems"],
      ["Simulink", "Python", "Renewable Energy", "Electrical Design"],
      ["NPTEL Power System Analysis / Protection", "MATLAB Onramp and Simscape Electrical tutorials (free)", "ETAP / PowerWorld student training"],
      [("Load-flow and short-circuit study of a 5-bus system", ["Power Systems", "MATLAB"]),
       ("Simulation of a grid-connected solar PV system", ["Renewable Energy", "Simulink", "Power Electronics"]),
       ("Relay-coordination case study", ["Power Systems", "Electrical Standards"])],
      ["Per-unit system", "Symmetrical and unsymmetrical faults", "Transformer connections", "Basics of protection relays"],
      min_projects=3)

_role("PLC / Automation Engineer",
      ["plc engineer", "automation engineer", "scada engineer", "controls engineer", "instrumentation engineer", "industrial automation engineer"],
      ["PLC", "SCADA", "Industrial Automation", "Control Systems", "Instrumentation", "Circuit Design"],
      ["Electrical Design", "Communication Protocols", "Robotics", "Python", "Microcontrollers"],
      ["Siemens / Allen-Bradley / Delta PLC vendor courses", "NPTEL Industrial Automation and Control", "NSDC / SSC electronics or automation certificates"],
      [("Conveyor and bottle-filling sequence in ladder logic, simulated", ["PLC", "Industrial Automation"]),
       ("SCADA / HMI screen for a tank-level process", ["SCADA", "Instrumentation"]),
       ("Motor control with a VFD and sensors, with a wiring diagram", ["Industrial Automation", "Circuit Design"]),
       ("PID loop tuning on a simulated process", ["Control Systems"])],
      ["Ladder logic basics (timers, counters, latches)", "Analog vs digital I/O", "Modbus and Profibus basics", "Sensor and transmitter selection"],
      min_projects=3)

# ---- ELECTRONICS & COMMUNICATION
_role("VLSI Design Engineer",
      ["vlsi engineer", "rtl design engineer", "asic engineer", "chip design engineer", "vlsi design", "verification engineer"],
      ["VLSI Design", "Verilog", "Digital Electronics", "FPGA", "Analog Electronics", "Circuit Design"],
      ["VHDL", "Linux", "Python", "Bash/Shell", "MATLAB"],
      ["NPTEL VLSI Design / Digital IC Design", "FPGA board vendor tutorials (Xilinx / Intel)", "Cadence or Synopsys academic training (if offered by your college)"],
      [("RTL design and testbench of an ALU, FIFO and UART in Verilog", ["Verilog", "Digital Electronics"]),
       ("Implement the design on an FPGA board with timing report", ["FPGA", "VLSI Design"]),
       ("CMOS inverter and gate-level simulation with a delay and power comparison", ["Circuit Design", "Analog Electronics", "VLSI Design"])],
      ["Blocking vs non-blocking assignments", "Setup and hold time", "FSM design styles", "CMOS inverter operation"],
      min_projects=3)

_role("Communication / DSP Engineer",
      ["communication engineer", "dsp engineer", "telecom engineer", "rf engineer", "wireless engineer", "signal processing engineer"],
      ["Communication Systems", "Signal Processing", "Digital Electronics", "Analog Electronics", "MATLAB", "Computer Networks"],
      ["Python", "Simulink", "FPGA", "Circuit Design", "Wireshark"],
      ["NPTEL Digital Communication / Signal Processing", "MATLAB Onramp and Communications Toolbox tutorials (free)", "Software-defined-radio beginner course"],
      [("Simulate BPSK/QPSK over an AWGN channel and plot bit-error rate in MATLAB or Python", ["Communication Systems", "MATLAB", "Python"]),
       ("Design and apply an FIR/IIR filter to a real audio or sensor signal", ["Signal Processing", "MATLAB"]),
       ("Microstrip antenna or RF-filter simulation", ["Communication Systems", "Circuit Design"])],
      ["Sampling and Nyquist", "Modulation schemes and BER", "FIR vs IIR filters", "Link-budget basics"],
      min_projects=3)


# ----------------------------------------------------------------------------- families (UI grouping)
FAMILIES = {
    "Software & IT": ["Software Developer", "Backend Developer", "Frontend Developer", "Full Stack Developer",
                      "Data Analyst", "Data Scientist", "Machine Learning Engineer", "Generative AI Engineer",
                      "Data Engineer", "DevOps Engineer", "Cloud Engineer", "Cybersecurity Analyst",
                      "QA / Test Automation Engineer", "Android Developer", "Business Analyst", "UI/UX Designer"],
    "Civil Engineering": ["Site Engineer (Civil)", "Structural Design Engineer", "Construction Planning Engineer",
                          "Quantity Surveyor / Estimation Engineer", "BIM / CAD Engineer (Civil)",
                          "Highway / Transportation Engineer", "Water & Environmental Engineer"],
    "Mechanical Engineering": ["Mechanical Design Engineer", "CAE / Simulation Engineer", "Manufacturing Engineer",
                               "Thermal / HVAC Engineer", "Automotive Engineer", "Robotics / Mechatronics Engineer",
                               "Maintenance Engineer"],
    "Production & Industrial": ["Production Engineer", "Quality Engineer", "Industrial / Process Improvement Engineer",
                                "Supply Chain / Operations Engineer", "CNC Programmer / Tool Engineer",
                                "Manufacturing Engineer", "Maintenance Engineer"],
    "Electrical Engineering": ["Electrical Design Engineer", "Power Systems Engineer", "PLC / Automation Engineer",
                               "Robotics / Mechatronics Engineer", "Embedded Systems Engineer"],
    "Electronics & Communication": ["Embedded Systems Engineer", "VLSI Design Engineer", "Communication / DSP Engineer",
                                    "PLC / Automation Engineer", "Software Developer"],
    "Aerospace Engineering": ["Aerospace / Aeronautical Engineer", "CAE / Simulation Engineer",
                              "Mechanical Design Engineer", "Robotics / Mechatronics Engineer"],
}

_BRANCH_TO_FAMILY = {"CSE": "Software & IT", "IT": "Software & IT", "ECE": "Electronics & Communication",
                     "EEE": "Electrical Engineering", "Mechanical": "Mechanical Engineering",
                     "Civil": "Civil Engineering", "Aerospace": "Aerospace Engineering"}
_PRODUCTION_RX = re.compile(r"production engineering|industrial engineering|manufacturing engineering|"
                            r"production and industrial|industrial and production", re.I)


# ----------------------------------------------------------------------------- apply
def _apply():
    for name, (cat, aliases) in SKILLS.items():
        sg.SKILL_DB.setdefault(name, (cat, aliases))
    for k, v in WEEKS.items():
        sg.WEEKS.setdefault(k, v)
    for k, v in TIPS.items():
        sg.TIPS.setdefault(k, v)
    for name, role in ROLES.items():
        sg.ROLES.setdefault(name, role)
    # safety net: every referenced skill must exist and every family role must exist
    bad = []
    for name in ROLES:
        r = sg.ROLES[name]
        for items in (r["core"], r["preferred"]):
            for g in items:
                for s in (g if isinstance(g, (tuple, list)) else (g,)):
                    if s not in sg.SKILL_DB:
                        bad.append((name, s))
    missing_roles = [(f, r) for f, rs in FAMILIES.items() for r in rs if r not in sg.ROLES]
    if bad or missing_roles:
        raise RuntimeError(f"role_extensions: unknown skills {bad} / roles {missing_roles}")


_apply()


# ----------------------------------------------------------------------------- UI helpers
def family_names():
    return list(FAMILIES)


def roles_in(family):
    return sorted(FAMILIES.get(family, sg.list_roles()))


def guess_family(ex, resume_text=""):
    """Best-effort field guess from the resume; None when unclear."""
    text = resume_text or ""
    if _PRODUCTION_RX.search(text):
        return "Production & Industrial"
    found = {_BRANCH_TO_FAMILY[b] for b in (ex or {}).get("education", {}).get("branch_candidates", [])
             if b in _BRANCH_TO_FAMILY}
    return next(iter(found)) if len(found) == 1 else None


def branch_guess(ex, resume_text=""):
    """Text to pre-select in the Branch dropdown (matched case-insensitively against its options)."""
    if _PRODUCTION_RX.search(resume_text or ""):
        return "Production" if re.search(r"production", resume_text, re.I) else "Industrial"
    cands = (ex or {}).get("education", {}).get("branch_candidates", [])
    return cands[0] if len(cands) == 1 else None