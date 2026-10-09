from pathlib import Path
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(r"D:\Reggii\GLA\Mini Project")
OUTPUT = ROOT / "PROJECT_SYNOPSIS.docx"

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
    run.font.color.rgb = RGBColor.from_string(BLUE if level == 1 else DARK)
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
    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    header_run = header.add_run("IAMShield AI - Project Synopsis")
    header_run.italic = True
    header_run.font.name = "Times New Roman"
    header_run.font.size = Pt(9)
    header_run.font.color.rgb = RGBColor.from_string(GRAY)
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer_run = footer.add_run("GLA University | Page ")
    footer_run.font.name = "Times New Roman"
    footer_run.font.size = Pt(9)
    add_page_number(footer)


def build_document():
    doc = Document()
    setup_document(doc)

    # Cover page
    add_center(doc, "IAMSHIELD AI", 27, True, BLUE, 2)
    add_center(doc, "Assisted Least-Privilege IAM Policy Synthesis", 17, True, DARK, 20)
    add_center(doc, "A Project Synopsis submitted in partial fulfilment of the requirements for the award of the degree of", 12, False, DARK, 12)
    add_center(doc, "BACHELOR OF TECHNOLOGY", 18, True, BLUE, 2)
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
    add_center(doc, "GLA University, Mathura - 281406, India", 13, True, BLUE, 4)
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

    # Chapter 3
    add_heading(doc, "CHAPTER 3: SOFTWARE DESIGN")
    add_heading(doc, "3.1 Architecture Overview", 2)
    add_body(doc, "The system follows a simple three-layer architecture. The React client presents telemetry and policy findings. The FastAPI backend exposes endpoints and coordinates analysis. The database stores access patterns and generated policy drafts. The synthesis engine is deliberately rule-based so that its decisions can be explained and tested.")
    add_table(doc, ["Layer", "Responsibility", "Technology"], [["Presentation", "Dashboard, synthesis view, policy review", "React, Vite, CSS"], ["Application", "API routes, filtering, synthesis, validation", "Python, FastAPI"], ["Persistence", "Users, access patterns, policies, audit data", "SQLAlchemy, SQLite demo database" ]], [1.5, 3.2, 1.9])
    add_heading(doc, "3.2 Data Flow", 2)
    add_center(doc, "Access Events -> Pattern Analysis -> Policy Synthesis -> Validation -> Human Review", 12, True, TEAL, 15)
    add_body(doc, "The ingestion step receives normalized events. The analysis step removes denied or stale events and groups the remaining records. The synthesis step creates explicit statements. The validation step checks the policy structure and highlights wildcards. The final state is a reviewable draft rather than an automatic production change.")
    add_heading(doc, "3.3 Database Design", 2)
    add_table(doc, ["Entity", "Important fields", "Purpose"], [["AccessPattern", "resource, action, access_count, timestamps, status", "Stores observed access evidence"], ["Policy", "name, policy_document, status, timestamps", "Stores generated policy drafts"], ["AuditLog", "action, resource, details, timestamp", "Supports traceability"], ["User and Role", "identity and role fields", "Reserved for controlled access in the next iteration"]], [1.5, 3.1, 2.0])
    add_heading(doc, "3.4 Policy Synthesis Logic", 2)
    add_body(doc, "The current algorithm is intentionally deterministic. It selects recent allowed records, groups actions by resource, creates one Allow statement per resource, and produces recommendations when wildcard permissions are observed. This approach does not claim to understand every business intent; it gives the administrator a clear evidence-based starting point.")
    add_table(doc, ["Input", "Processing", "Output"], [["AccessPattern records", "Filter by time and status", "Recent allowed records"], ["Recent records", "Group action-resource pairs", "Minimal statement groups"], ["Statement groups", "Run structural and wildcard checks", "Policy plus findings"]], [1.8, 2.8, 2.0])

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
    code_run.font.color.rgb = RGBColor.from_string(BLUE)

    doc.save(OUTPUT)
    print(f"Saved {OUTPUT}")


if __name__ == "__main__":
    build_document()
