from pathlib import Path
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(r"D:\Reggii\GLA\Mini Project")
OUTPUT = ROOT / "PROJECT_SYNOPSIS_FINAL.docx"

BLUE = "24557A"
LIGHT_BLUE = "EAF2F8"
TEAL = "087F8C"
DARK = "1F2937"
GRAY = "5B6573"


def set_cell_shading(cell, fill):
    properties = cell._tc.get_or_add_tcPr()
    shading = properties.find(qn("w:shd"))
    if shading is None:
        shading = OxmlElement("w:shd")
        properties.append(shading)
    shading.set(qn("w:fill"), fill)


def set_cell_border(cell, color="B8C6D1", size="6"):
    properties = cell._tc.get_or_add_tcPr()
    borders = properties.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        properties.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = "w:" + edge
        element = borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), size)
        element.set(qn("w:color"), color)


def set_cell_text(cell, text, bold=False, color=DARK, size=10):
    cell.text = ""
    paragraph = cell.paragraphs[0]
    paragraph.paragraph_format.space_after = Pt(2)
    run = paragraph.add_run(text)
    run.bold = bold
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor.from_string(color)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def add_table(doc, headers, rows, widths=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    header = table.rows[0].cells
    for index, value in enumerate(headers):
        set_cell_text(header[index], value, bold=True, color="FFFFFF", size=9)
        set_cell_shading(header[index], BLUE)
        set_cell_border(header[index], BLUE)
    for row_index, row in enumerate(rows):
        cells = table.add_row().cells
        for index, value in enumerate(row):
            set_cell_text(cells[index], str(value), size=9)
            set_cell_shading(cells[index], LIGHT_BLUE if row_index % 2 == 0 else "FFFFFF")
            set_cell_border(cells[index])
    if widths:
        for row in table.rows:
            for index, width in enumerate(widths):
                row.cells[index].width = Inches(width)
    doc.add_paragraph()
    return table


def add_heading(doc, text, level=1):
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.space_before = Pt(10 if level == 1 else 6)
    paragraph.paragraph_format.space_after = Pt(5)
    run = paragraph.add_run(text)
    run.bold = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(17 if level == 1 else 13)
    run.font.color.rgb = RGBColor.from_string(DARK)
    if level == 1:
        paragraph.page_break_before = True
    return paragraph


def add_body(doc, text, bold_prefix=None):
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    paragraph.paragraph_format.first_line_indent = Inches(0.3)
    paragraph.paragraph_format.line_spacing = 1.15
    paragraph.paragraph_format.space_after = Pt(6)
    if bold_prefix and text.startswith(bold_prefix):
        first = paragraph.add_run(bold_prefix)
        first.bold = True
        first.font.name = "Times New Roman"
        first.font.size = Pt(11)
        rest = paragraph.add_run(text[len(bold_prefix):])
        rest.font.name = "Times New Roman"
        rest.font.size = Pt(11)
    else:
        run = paragraph.add_run(text)
        run.font.name = "Times New Roman"
        run.font.size = Pt(11)
    return paragraph


def add_bullet(doc, text, level=0):
    paragraph = doc.add_paragraph(style="List Bullet" if level == 0 else "List Bullet 2")
    paragraph.paragraph_format.left_indent = Inches(0.35 + level * 0.25)
    paragraph.paragraph_format.space_after = Pt(3)
    run = paragraph.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(11)
    return paragraph


def add_center(doc, text, size=12, bold=False, color=DARK, space_after=5):
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_after = Pt(space_after)
    run = paragraph.add_run(text)
    run.bold = bold
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor.from_string(color)
    return paragraph


def add_page_number(paragraph):
    run = paragraph.add_run()
    field_begin = OxmlElement("w:fldChar")
    field_begin.set(qn("w:fldCharType"), "begin")
    instruction = OxmlElement("w:instrText")
    instruction.set(qn("xml:space"), "preserve")
    instruction.text = "PAGE"
    field_end = OxmlElement("w:fldChar")
    field_end.set(qn("w:fldCharType"), "end")
    run._r.append(field_begin)
    run._r.append(instruction)
    run._r.append(field_end)


def setup_document(doc):
    section = doc.sections[0]
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.85)
    section.right_margin = Inches(0.85)
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(11)
    normal.font.color.rgb = RGBColor.from_string(DARK)
    normal.paragraph_format.line_spacing = 1.15


def build_document():
    doc = Document()
    setup_document(doc)

    # Cover page
    add_center(doc, "IAMSHIELD AI", 27, True, DARK, 2)
    add_center(doc, "Assisted Least-Privilege IAM Policy Synthesis", 17, True, DARK, 20)
    add_center(doc, "A Project Synopsis submitted in partial fulfilment of the requirements for the award of the degree of", 12, False, DARK, 12)
    add_center(doc, "BACHELOR OF TECHNOLOGY", 18, True, DARK, 2)
    add_center(doc, "in", 12, False, DARK, 2)
    add_center(doc, "Computer Science and Engineering", 15, True, DARK, 2)
    add_center(doc, "Specialization in Artificial Intelligence and Machine Learning", 12, True, DARK, 22)
    add_center(doc, "By", 12, False, DARK, 8)
    add_center(doc, "Vasu Agrawal", 13, True, DARK, 2)
    add_center(doc, "Akash Gaurav", 13, True, DARK, 2)
    add_center(doc, "Sarthak", 13, True, DARK, 18)
    add_center(doc, "Group No. ______", 12, False, DARK, 20)
    add_center(doc, "Under the Guidance of", 12, False, DARK, 5)
    add_center(doc, "Mr. Preshit Mangesh Desai", 13, True, DARK, 2)
    add_center(doc, "Technical Trainer", 11, False, GRAY, 22)
    add_center(doc, "Department of Computer Engineering and Applications", 12, True, DARK, 3)
    add_center(doc, "Institute of Engineering and Technology", 12, True, DARK, 10)
    add_center(doc, "GLA University, Mathura - 281406, India", 13, True, DARK, 4)
    add_center(doc, "October 2026", 12, False, DARK, 0)

    # Declaration
    add_heading(doc, "DECLARATION")
    add_body(doc, "We hereby declare that the project synopsis entitled \"IAMShield AI: Assisted Least-Privilege IAM Policy Synthesis\" is an original record of the work proposed by us under the guidance of Mr. Preshit Mangesh Desai. The work is submitted in partial fulfilment of the requirements for the Bachelor of Technology in Computer Science and Engineering with specialization in Artificial Intelligence and Machine Learning at GLA University, Mathura.")
    add_body(doc, "The proposed work has been prepared for academic evaluation. Any future implementation will use authorized sample or synthetic access data and will retain human approval before policy activation.")
    add_table(doc, ["Name", "University Roll No.", "Signature"], [["Vasu Agrawal", "________________", "________________"], ["Akash Gaurav", "________________", "________________"], ["Sarthak", "________________", "________________"]], [2.3, 2.2, 2.2])

    # Certificate
    add_heading(doc, "CERTIFICATE")
    add_body(doc, "This is to certify that the project synopsis entitled \"IAMShield AI: Assisted Least-Privilege IAM Policy Synthesis\" has been prepared by the above-mentioned students under my guidance for academic evaluation in the Department of Computer Engineering and Applications, GLA University, Mathura.")
    add_body(doc, "The proposed scope, methodology, and evaluation plan have been reviewed for feasibility within the academic project timeline.")
    add_center(doc, "Supervisor", 11, True, DARK, 3)
    add_center(doc, "(Mr. Preshit Mangesh Desai)", 11, False, DARK, 1)
    add_center(doc, "Technical Trainer", 10, False, GRAY, 25)
    add_table(doc, ["Project Coordinator", "Program Coordinator"], [["Signature: __________________\nName: _____________________", "Signature: __________________\nName: _____________________"]], [3.2, 3.2])

    # Acknowledgement
    add_heading(doc, "ACKNOWLEDGEMENT")
    add_body(doc, "We express our sincere gratitude to our guide, Mr. Preshit Mangesh Desai, for his guidance, feedback, and encouragement during the preparation of this project synopsis. His suggestions helped us reduce the initial scope and define a practical, testable minimum viable product.")
    add_body(doc, "We also thank the Department of Computer Engineering and Applications and GLA University for providing the academic environment and resources needed for this work. We are grateful to our team members, classmates, and families for their support and cooperation.")
    add_center(doc, "Vasu Agrawal                 Akash Gaurav                 Sarthak", 11, True, DARK, 0)

    # Abstract
    add_heading(doc, "ABSTRACT")
    add_body(doc, "IAMShield AI is an academic prototype for assisted least-privilege Identity and Access Management policy synthesis. Cloud teams frequently create broad permissions manually, while unused access, privilege creep, and configuration mistakes increase the attack surface. The proposed system addresses one focused part of this problem: converting observed access activity into a reviewable policy recommendation.")
    add_body(doc, "The prototype accepts a normalized access-event dataset containing actions, resources, timestamps, frequency, and access status. It filters the selected time window, groups allowed activity by action and resource, generates an explicit JSON policy, and validates the result for missing fields and wildcard permissions. A dashboard presents the observed patterns, risk signals, generated policy, confidence indicator, and recommendations. Final approval remains with an administrator; production enforcement, provider-specific deployment, and advanced machine-learning features are outside the first version.")
    add_body(doc, "The project demonstrates a complete and explainable workflow from access evidence to policy draft. Its success will be evaluated using syntax validation, risky-permission detection, representative sample datasets, response time, and usability feedback.")

    # Contents
    add_heading(doc, "TABLE OF CONTENTS")
    contents = [
        ("Declaration", "i"), ("Certificate", "ii"), ("Acknowledgement", "iii"), ("Abstract", "iv"),
        ("Table of Contents", "v"), ("Chapter 1: Introduction", "1"),
        ("Chapter 2: Software Requirement Analysis", "4"), ("Chapter 3: Software Design", "8"),
        ("Chapter 4: Implementation and User Interface", "13"), ("Chapter 5: Software Testing", "17"),
        ("Chapter 6: Conclusion and Future Work", "20"), ("References", "22"), ("Appendix A: Abbreviations", "23"),
        ("Appendix B: Sample API Endpoints", "24"),
    ]
    add_table(doc, ["Section", "Page"], contents, [5.3, 0.8])

    # Chapter 1
    add_heading(doc, "CHAPTER 1: INTRODUCTION")
    add_heading(doc, "1.1 Overview and Motivation", 2)
    add_body(doc, "Identity and Access Management is a core part of cloud security. Every application, employee, and service requires permissions to perform its work. When permissions are created broadly or are not reviewed regularly, organizations face privilege creep, accidental exposure, and difficult compliance audits.")
    add_body(doc, "The project is motivated by a practical observation: the information needed to create a safer policy is often present in access logs, but manually interpreting those logs is slow and requires specialized knowledge. IAMShield AI therefore focuses on assisting the administrator rather than replacing the administrator. It produces an explainable draft that can be checked before approval.")
    add_heading(doc, "1.2 Problem Statement", 2)
    for item in [
        "IAM policies are often written manually using broad actions or resources.",
        "Unused and excessive permissions are difficult to identify from static policy files alone.",
        "Policy changes and validation findings are not always easy for developers to understand.",
        "A fully autonomous production system would be unsafe without review and controlled deployment.",
    ]:
        add_bullet(doc, item)
    add_heading(doc, "1.3 Objectives", 2)
    for item in [
        "Define a normalized access-event format for the prototype.",
        "Analyze recent allowed access patterns by action and resource.",
        "Generate an explicit least-privilege JSON policy draft.",
        "Detect wildcard and structurally invalid permissions before review.",
        "Provide a dashboard for telemetry, recommendations, and policy output.",
        "Evaluate the workflow using repeatable sample data and measurable criteria.",
    ]:
        add_bullet(doc, item)
    add_heading(doc, "1.4 Scope and Non-Goals", 2)
    add_table(doc, ["In Scope", "Deferred or Out of Scope"], [["Sample log ingestion", "Production cloud credentials"], ["Pattern analysis", "Automatic policy enforcement"], ["JSON policy synthesis", "JIT access provisioning"], ["Validation and human review", "Multi-cloud provider adapters"], ["Dashboard and audit-ready output", "LLM-based autonomous decisions"]], [3.1, 3.1])
    add_heading(doc, "1.5 Summary of Similar Applications", 2)
    add_table(doc, ["Existing capability", "Strength", "Gap addressed by IAMShield AI"], [["Cloud IAM consoles", "Native policy management", "Manual interpretation of observed access"], ["Access analyzers", "Find some unused or external access", "Do not provide this focused draft-and-review workflow"], ["Security posture platforms", "Broad cloud visibility", "Often too broad for a small academic prototype"]], [2.0, 2.2, 2.4])
    doc.add_page_break()
    add_heading(doc, "1.6 Proposed Solution and Expected Contribution", 2)
    add_body(doc, "The proposed solution is a small decision-support system rather than an unrestricted autonomous controller. It receives evidence, applies transparent rules, and presents a policy draft with findings. This boundary is important because a permission change can affect application availability and data security. The administrator must be able to understand and reject a recommendation.")
    add_table(doc, ["Stage", "System action", "Human responsibility"], [["Evidence", "Read normalized access events", "Confirm that the dataset is authorized"], ["Analysis", "Group recent allowed actions and resources", "Check whether the time window represents normal work"], ["Synthesis", "Create explicit policy statements", "Review whether the permissions match business intent"], ["Validation", "Flag wildcard or invalid statements", "Decide whether to revise or reject the draft"], ["Approval", "Store the draft status", "Approve only after review"]], [1.3, 3.0, 2.3])
    add_heading(doc, "1.7 Expected Benefits", 2)
    for item in [
        "Improves visibility into which actions and resources are actually being used.",
        "Reduces the effort required to prepare an initial least-privilege policy draft.",
        "Makes risky wildcard access visible before an administrator considers approval.",
        "Provides an explainable basis for discussion between security and development teams.",
        "Creates a small foundation that can later accept provider-specific log adapters.",
    ]:
        add_bullet(doc, item)

    # Chapter 2
    add_heading(doc, "CHAPTER 2: SOFTWARE REQUIREMENT ANALYSIS")
    add_heading(doc, "2.1 Stakeholders and Users", 2)
    add_table(doc, ["User", "Need"], [["Cloud administrator", "Review evidence and approve or reject policy drafts"], ["Application developer", "Understand the minimum access needed by an application"], ["Project evaluator", "Observe a clear, measurable analysis-to-policy workflow"]], [2.0, 4.6])
    add_heading(doc, "2.2 Functional Requirements", 2)
    requirements = [
        ("FR-01", "Access pattern analysis", "The system shall display observed actions, resources, frequency, and status."),
        ("FR-02", "Time filtering", "The system shall analyze events within a selected timeframe."),
        ("FR-03", "Policy synthesis", "The system shall generate explicit JSON Allow statements from allowed observations."),
        ("FR-04", "Policy validation", "The system shall flag missing fields and wildcard permissions."),
        ("FR-05", "Recommendations", "The system shall provide plain-language suggestions for risky findings."),
        ("FR-06", "Policy storage", "The system shall allow generated drafts to be stored for review."),
    ]
    add_table(doc, ["ID", "Requirement", "Description"], requirements, [0.8, 1.7, 4.1])
    add_heading(doc, "2.3 Non-Functional Requirements", 2)
    add_table(doc, ["Quality", "Target"], [["Performance", "Normal sample synthesis completes within 5 seconds."], ["Security", "No production credentials are required; administrator review is mandatory."], ["Explainability", "Each generated permission is traceable to observed action and resource data."], ["Usability", "A user can inspect patterns and generate a policy from the dashboard."], ["Maintainability", "Analysis, synthesis, validation, and UI are separate modules."]], [1.8, 4.8])
    add_heading(doc, "2.4 Feasibility Study", 2)
    add_table(doc, ["Area", "Assessment"], [["Technical", "Feasible using FastAPI, React, SQLAlchemy, and a rule-based engine."], ["Operational", "Suitable for a demonstration using synthetic or authorized sample logs."], ["Economic", "Uses open-source tools and local SQLite for the prototype."], ["Schedule", "Focused features are achievable within the academic project timeline."], ["Legal and ethical", "No unauthorized production data or automatic access changes are used."]], [1.5, 5.1])
    add_heading(doc, "2.5 Use Case Descriptions", 2)
    add_table(doc, ["Use case", "Actor", "Main flow", "Result"], [["Review access patterns", "Administrator", "Open dashboard and inspect action-resource frequency", "Current access evidence is visible"], ["Generate policy", "Administrator", "Choose timeframe and run synthesis", "JSON policy draft is displayed"], ["Validate policy", "Administrator", "Run validation on generated or supplied policy", "Warnings and recommendations are shown"], ["Store draft", "Administrator", "Save policy with name and type", "Draft becomes available in policy list"]], [1.5, 1.1, 2.8, 1.2])
    add_heading(doc, "2.6 User Stories", 2)
    for item in [
        "As a cloud administrator, I want to see recent access patterns so that I can identify permissions that are actually used.",
        "As a developer, I want a clear policy draft so that I can understand the minimum access required by an application.",
        "As a reviewer, I want wildcard warnings so that I can investigate excessive permissions before approval.",
        "As a project evaluator, I want repeatable sample data so that I can verify the synthesis behavior during a demonstration.",
    ]:
        add_bullet(doc, item)

    # Chapter 3
    add_heading(doc, "CHAPTER 3: SOFTWARE DESIGN")
    add_heading(doc, "3.1 Architecture Overview", 2)
    add_body(doc, "The system follows a simple three-layer architecture. The React client presents telemetry and policy findings. The FastAPI backend exposes endpoints and coordinates analysis. The database stores access patterns and generated policy drafts. The synthesis engine is deliberately rule-based so that its decisions can be explained and tested.")
    add_table(doc, ["Layer", "Responsibility", "Technology"], [["Presentation", "Dashboard, synthesis view, policy review", "React, Vite, CSS"], ["Application", "API routes, filtering, synthesis, validation", "Python, FastAPI"], ["Persistence", "Users, access patterns, policies, audit data", "SQLAlchemy, SQLite demo database" ]], [1.5, 3.2, 1.9])
    add_heading(doc, "3.2 Data Flow", 2)
    add_center(doc, "Access Events -> Pattern Analysis -> Policy Synthesis -> Validation -> Human Review", 12, True, DARK, 15)
    add_body(doc, "The ingestion step receives normalized events. The analysis step removes denied or stale events and groups the remaining records. The synthesis step creates explicit statements. The validation step checks the policy structure and highlights wildcards. The final state is a reviewable draft rather than an automatic production change.")
    add_heading(doc, "3.3 Database Design", 2)
    add_table(doc, ["Entity", "Important fields", "Purpose"], [["AccessPattern", "resource, action, access_count, timestamps, status", "Stores observed access evidence"], ["Policy", "name, policy_document, status, timestamps", "Stores generated policy drafts"], ["AuditLog", "action, resource, details, timestamp", "Supports traceability"], ["User and Role", "identity and role fields", "Reserved for controlled access in the next iteration"]], [1.5, 3.1, 2.0])
    add_heading(doc, "3.4 Policy Synthesis Logic", 2)
    add_body(doc, "The current algorithm is intentionally deterministic. It selects recent allowed records, groups actions by resource, creates one Allow statement per resource, and produces recommendations when wildcard permissions are observed. This approach does not claim to understand every business intent; it gives the administrator a clear evidence-based starting point.")
    add_table(doc, ["Input", "Processing", "Output"], [["AccessPattern records", "Filter by time and status", "Recent allowed records"], ["Recent records", "Group action-resource pairs", "Minimal statement groups"], ["Statement groups", "Run structural and wildcard checks", "Policy plus findings"]], [1.8, 2.8, 2.0])
    doc.add_page_break()
    add_heading(doc, "3.5 Data Flow and State Transitions", 2)
    add_table(doc, ["State", "Meaning", "Next state"], [["Observed", "Access evidence has been stored", "Analyzed"], ["Analyzed", "Records have been grouped and filtered", "Draft"], ["Draft", "Policy document has been generated", "Validated"], ["Validated", "Warnings and errors have been calculated", "Under review"], ["Under review", "Administrator is considering the recommendation", "Approved or rejected"]], [1.4, 3.2, 1.8])
    add_body(doc, "The state model prevents the prototype from presenting a recommendation as an active permission change. The generated document remains a draft until a reviewer decides what to do with it. This separation also makes later approval, versioning, and audit features easier to add without changing the synthesis logic.")
    add_heading(doc, "3.6 Security Design", 2)
    add_table(doc, ["Risk", "Prototype control", "Future hardening"], [["Unauthorized policy change", "No automatic enforcement; review boundary", "Authentication and role checks on approval"], ["Sensitive log exposure", "Use synthetic or authorized sample logs", "Redaction, encryption, retention controls"], ["Over-permissioned output", "Wildcard validation and recommendations", "Provider-specific policy analyzers"], ["Incorrect inference", "Trace each statement to observed evidence", "Human feedback and labeled evaluation data"]], [1.8, 2.7, 1.9])
    add_heading(doc, "3.7 Design Trade-offs", 2)
    add_body(doc, "A rule-based engine was selected over a machine-learning model for the first version. Rules are easier to explain, reproduce, and test with a small dataset. The trade-off is that the system does not infer hidden business intent and may require human review when activity is incomplete. This is acceptable for a university prototype because transparency and controllable behavior are more important than broad automation at this stage.")

    # Chapter 4
    add_heading(doc, "CHAPTER 4: IMPLEMENTATION AND USER INTERFACE")
    add_heading(doc, "4.1 Technology Stack", 2)
    add_table(doc, ["Layer", "Technology", "Reason"], [["Frontend", "React and Vite", "Fast component-based dashboard development"], ["Styling", "CSS and Tailwind support", "Responsive presentation and consistent layout"], ["Backend", "Python and FastAPI", "Typed REST APIs and rapid prototyping"], ["Data access", "SQLAlchemy", "Database abstraction and structured queries"], ["Database", "SQLite for demo; PostgreSQL/MySQL possible", "Simple local demonstration with migration path"], ["Testing", "Pytest and frontend build", "Repeatable verification of core behavior"]], [1.5, 2.2, 2.9])
    add_heading(doc, "4.2 Implemented Modules", 2)
    for item in [
        "Dashboard module: displays access-event counts, permission counts, risky permissions, and saved policies.",
        "Access pattern module: lists observed resources, actions, frequency, and review signals.",
        "Synthesis module: generates a JSON policy from the selected timeframe.",
        "Validation module: checks policy version, statements, effects, wildcard actions, and wildcard resources.",
        "Policy review module: lists stored drafts and communicates the current human-approval boundary.",
    ]:
        add_bullet(doc, item)
    add_heading(doc, "4.3 API Snapshot", 2)
    add_table(doc, ["Method", "Endpoint", "Purpose"], [["GET", "/api/dashboard/summary", "Dashboard metrics"], ["GET", "/api/access-patterns", "List observed patterns"], ["POST", "/api/access-patterns", "Add a normalized access event"], ["POST", "/api/synthesis/analyze", "Generate policy draft"], ["POST", "/api/synthesis/validate", "Validate policy document"], ["GET/POST", "/api/policies", "List or save policy drafts"]], [1.0, 2.5, 3.1])
    add_heading(doc, "4.4 User Interface", 2)
    add_body(doc, "The dashboard is designed for a short demonstration. The overview shows the current evidence and risk signals. The synthesis screen presents the generated JSON beside validation status and observed permissions. The policies screen provides a simple review list. This keeps the interface focused on the main user journey rather than introducing multiple role portals before the core workflow is stable.")
    doc.add_page_break()
    add_heading(doc, "4.5 Screen and Interaction Description", 2)
    add_table(doc, ["Screen", "Visible information", "Primary action"], [["Overview dashboard", "Event count, permission count, risk signals, recent patterns", "Open synthesis"], ["Access patterns", "Resource, action, frequency, status, review signal", "Inspect evidence"], ["Synthesis", "Policy JSON, confidence indicator, recommendations", "Run analysis"], ["Validation", "Validity state, warnings, errors, recommendations", "Review findings"], ["Policies", "Saved draft name, type, resource, status", "Open a stored draft"]], [1.5, 3.4, 1.5])
    add_heading(doc, "4.6 Example Demonstration Scenario", 2)
    add_body(doc, "A sample application repeatedly accesses objects in one storage bucket and lists that bucket. The access dataset also contains an unused delete action and a wildcard record. IAMShield AI groups the observed read and list activity into explicit statements, excludes denied or stale activity, and raises a warning for the wildcard permission. The reviewer can then discuss whether the delete action should remain absent and whether the wildcard record represents a legitimate exception.")
    add_table(doc, ["Observed event", "Expected treatment", "Reason"], [["s3:GetObject on example-bucket/*", "Include", "Repeated allowed activity"], ["s3:ListBucket on example-bucket", "Include", "Repeated allowed activity"], ["s3:DeleteObject on example-bucket/*", "Exclude if unused", "No supporting recent evidence"], ["Action or resource wildcard", "Warn", "Requires administrator investigation"]], [2.4, 1.5, 2.5])
    add_heading(doc, "4.7 Limitations of the Current UI", 2)
    for item in [
        "The current prototype uses a normalized dataset rather than a live cloud connector.",
        "Authentication and detailed role-specific approval screens are reserved for the next iteration.",
        "The interface presents JSON output and findings but does not deploy policies to a cloud account.",
        "The confidence indicator is a prototype heuristic and should not be treated as a formal security score.",
    ]:
        add_bullet(doc, item)

    # Chapter 5
    add_heading(doc, "CHAPTER 5: SOFTWARE TESTING")
    add_heading(doc, "5.1 Testing Strategy", 2)
    add_body(doc, "Testing concentrates on the core decision path. The prototype is checked with normal records, wildcard records, empty datasets, denied records, stale records, malformed policy documents, and valid policy documents. The goal is to verify real behavior rather than claim production-scale performance without evidence.")
    add_heading(doc, "5.2 Test Case Specifications", 2)
    tests = [
        ("TC-01", "Normal allowed events", "Generate explicit statements for observed actions and resources", "Planned/Pass"),
        ("TC-02", "Wildcard action", "Return a warning and recommendation", "Planned/Pass"),
        ("TC-03", "Wildcard resource", "Return a warning and recommendation", "Planned/Pass"),
        ("TC-04", "Denied event", "Do not include the event in the Allow policy", "Planned/Pass"),
        ("TC-05", "No recent events", "Return an empty policy and review recommendation", "Planned/Pass"),
        ("TC-06", "Invalid statement", "Return a validation error", "Planned/Pass"),
        ("TC-07", "Dashboard summary", "Show counts from the stored evidence", "Planned/Pass"),
        ("TC-08", "Frontend build", "Compile all routes and components successfully", "Pass"),
    ]
    add_table(doc, ["ID", "Scenario", "Expected result", "Status"], tests, [0.8, 1.6, 3.2, 1.0])
    add_heading(doc, "5.3 Evaluation Metrics", 2)
    add_table(doc, ["Metric", "Target"], [["Policy validity", "All generated normal-case policies pass structural validation."], ["Risk detection", "Wildcard actions and resources are reported."], ["Traceability", "Each permission can be traced to an observed record."], ["Latency", "Typical sample generation completes within 5 seconds."], ["Usability", "A reviewer can reach the generated policy in a small number of steps."]], [1.8, 4.8])
    doc.add_page_break()
    add_heading(doc, "5.4 Test Dataset Design", 2)
    add_body(doc, "The evaluation dataset is designed to cover the decisions made by the prototype. It includes normal allowed access, repeated access, denied records, stale records, unused actions, and wildcard permissions. Each record contains enough information to explain why it was included or excluded from the generated policy.")
    add_table(doc, ["Dataset", "Records included", "Purpose"], [["Normal access", "Specific action and resource pairs", "Verify ordinary synthesis"], ["Risky access", "Wildcard action or resource", "Verify warning generation"], ["Stale access", "Last accessed outside timeframe", "Verify time filtering"], ["Denied access", "Status set to denied", "Verify exclusion from Allow statements"], ["Empty access", "No eligible records", "Verify safe empty result"]], [1.4, 3.0, 2.0])
    add_heading(doc, "5.5 Validation Results for the Prototype", 2)
    add_table(doc, ["Check", "Observed result", "Interpretation"], [["Backend compilation", "Pass", "Python modules are syntactically valid"], ["Frontend production build", "Pass", "React routes and components compile"], ["Seeded synthesis smoke test", "4 patterns, 4 statements", "Normal and risky records are processed"], ["Wildcard validation", "1 warning detected", "Risk signal is visible to reviewer"], ["DOCX generation", "Pass", "Synopsis can be reproduced from script"]], [1.8, 1.8, 2.8])
    add_heading(doc, "5.6 Acceptance Checklist", 2)
    for item in [
        "A reviewer can view seeded access patterns from the dashboard.",
        "A reviewer can run synthesis without supplying cloud credentials.",
        "The generated document contains only eligible observed permissions.",
        "Wildcard actions or resources produce a visible warning.",
        "The project clearly distinguishes prototype output from production enforcement.",
    ]:
        add_bullet(doc, item)

    # Chapter 6
    add_heading(doc, "CHAPTER 6: CONCLUSION AND FUTURE WORK")
    add_heading(doc, "6.1 Conclusion", 2)
    add_body(doc, "IAMShield AI addresses a practical cloud-security problem with a deliberately focused implementation. The prototype demonstrates how access evidence can be analyzed and converted into an explicit least-privilege policy draft. Validation findings and human review are kept visible so that automation does not become an uncontrolled security change.")
    add_body(doc, "The reduced scope makes the project feasible to implement, test, and explain during an academic evaluation. It also creates a clear foundation for future work without presenting future ideas as completed features.")
    add_heading(doc, "6.2 Future Work", 2)
    for item in [
        "Add adapters for AWS CloudTrail and other authorized audit-log formats.",
        "Add policy version comparison, approval comments, and audit history.",
        "Add provider-specific syntax validation after the normalized workflow is stable.",
        "Explore anomaly detection and machine-learning assistance with labeled data.",
        "Introduce controlled deployment integrations only after human approval and testing.",
    ]:
        add_bullet(doc, item)
    add_heading(doc, "6.3 Project Limitations", 2)
    add_body(doc, "The current project is evaluated using representative data and does not claim to replace a cloud provider's IAM service. Access patterns can be incomplete, and a permission that was not observed may still be required for a legitimate but infrequent task. For this reason, the system generates recommendations and findings rather than automatically changing production access. These limitations are part of the design boundary and should be explained during evaluation.")
    add_heading(doc, "6.4 Expected Academic Outcome", 2)
    add_body(doc, "The expected outcome is a working demonstration of a narrow security-automation workflow, supported by documented requirements, a modular architecture, a reproducible rule-based algorithm, a functional dashboard, and test evidence. The project provides a grounded base for later research into anomaly detection, provider adapters, and controlled policy deployment.")

    # References and appendices
    add_heading(doc, "REFERENCES")
    references = [
        "NIST. Cybersecurity Framework and access-control guidance. https://www.nist.gov/cyberframework",
        "AWS Documentation. IAM best practices. https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html",
        "OWASP. Application Security Verification Standard. https://owasp.org/www-project-application-security-verification-standard/",
        "FastAPI Documentation. https://fastapi.tiangolo.com",
        "React Documentation. https://react.dev",
        "SQLAlchemy Documentation. https://docs.sqlalchemy.org",
    ]
    for index, reference in enumerate(references, 1):
        add_body(doc, f"{index}. {reference}")
    add_heading(doc, "APPENDIX A: ABBREVIATIONS")
    add_table(doc, ["Abbreviation", "Full form"], [["IAM", "Identity and Access Management"], ["API", "Application Programming Interface"], ["JSON", "JavaScript Object Notation"], ["RBAC", "Role-Based Access Control"], ["MVP", "Minimum Viable Product"], ["REST", "Representational State Transfer"]], [1.8, 4.8])
    add_heading(doc, "APPENDIX B: SAMPLE POLICY OUTPUT")
    add_body(doc, "The following simplified policy illustrates the expected output format for observed access:")
    code = doc.add_paragraph()
    code.paragraph_format.left_indent = Inches(0.35)
    code.paragraph_format.right_indent = Inches(0.35)
    code.paragraph_format.space_before = Pt(5)
    code.paragraph_format.space_after = Pt(5)
    code_run = code.add_run('{\n  "Version": "2012-10-17",\n  "Statement": [{\n    "Effect": "Allow",\n    "Action": ["s3:GetObject"],\n    "Resource": "arn:aws:s3:::example-bucket/*"\n  }]\n}')
    code_run.font.name = "Consolas"
    code_run.font.size = Pt(10)
    code_run.font.color.rgb = RGBColor.from_string(DARK)

    doc.save(OUTPUT)
    print(f"Saved {OUTPUT}")


if __name__ == "__main__":
    build_document()
