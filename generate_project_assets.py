from pathlib import Path
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor as DocRGBColor
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_AUTO_SIZE
from pptx.util import Inches, Pt as PptPt
from pptx.dml.color import RGBColor as PptRGBColor

ROOT = Path('d:/Reggii/GLA/Mini Project')
DOCX_PATH = ROOT / 'PROJECT_SYNOPSIS.docx'
PPTX_PATH = ROOT / 'IAMShield_AI_Presentation.pptx'
SYNOPSIS_PATH = ROOT / 'PROJECT_SYNOPSIS.md'
OUTLINE_PATH = ROOT / 'PRESENTATION_OUTLINE.md'

DOC_BLUE = DocRGBColor(59, 130, 246)
DOC_TEAL = DocRGBColor(20, 184, 166)
DOC_DARK = DocRGBColor(17, 24, 39)
DOC_LIGHT = DocRGBColor(239, 246, 255)
DOC_WHITE = DocRGBColor(255, 255, 255)
DOC_TEXT = DocRGBColor(31, 41, 55)

PPT_BLUE = PptRGBColor(59, 130, 246)
PPT_TEAL = PptRGBColor(20, 184, 166)
PPT_DARK = PptRGBColor(17, 24, 39)
PPT_LIGHT = PptRGBColor(239, 246, 255)
PPT_WHITE = PptRGBColor(255, 255, 255)
PPT_TEXT = PptRGBColor(31, 41, 55)


def add_docx_title(doc, title):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(title)
    run.bold = True
    run.font.size = Pt(24)
    run.font.name = 'Calibri'
    run.font.color.rgb = DOC_BLUE
    doc.add_paragraph()


def add_docx_section_heading(doc, heading, page_break=False):
    if page_break:
        doc.add_page_break()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(heading)
    run.bold = True
    run.font.size = Pt(16)
    run.font.name = 'Calibri'
    run.font.color.rgb = DOC_DARK


def add_docx_text(doc, text):
    if not text.strip():
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(text)
    run.font.size = Pt(11)
    run.font.name = 'Calibri'
    run.font.color.rgb = DOC_TEXT


def add_docx_bullets(doc, bullets):
    for item in bullets:
        p = doc.add_paragraph(style='List Bullet')
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.left_indent = Inches(0.3)
        p.paragraph_format.space_after = Pt(4)
        p.text = item
        run = p.runs[0]
        run.font.size = Pt(11)
        run.font.name = 'Calibri'
        run.font.color.rgb = DOC_TEXT
        if item.startswith('**') and item.endswith('**'):
            run.bold = True


def add_docx_table_like_lines(doc, lines):
    for line in lines:
        if line.strip():
            doc.add_paragraph(line)


def generate_docx_from_markdown():
    md_text = SYNOPSIS_PATH.read_text(encoding='utf-8')
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.75)
    section.left_margin = Inches(0.9)
    section.right_margin = Inches(0.9)
    section.start_type = None

    add_docx_title(doc, 'IAMShield AI: Project Synopsis')

    current_section = None
    current_bullets = []
    previous_was_table = False

    for raw_line in md_text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped:
            continue

        if line.startswith('---'):
            doc.add_paragraph()
            continue

        if line.startswith('## '):
            if current_section is not None:
                doc.add_paragraph()
            current_section = stripped[3:]
            add_docx_section_heading(doc, current_section, page_break=True)
            continue

        if line.startswith('### '):
            if current_section is not None:
                doc.add_paragraph()
            add_docx_section_heading(doc, stripped[4:], page_break=False)
            continue

        if line.startswith('#### '):
            doc.add_paragraph()
            p = doc.add_paragraph()
            run = p.add_run(stripped[5:])
            run.bold = True
            run.font.size = Pt(12)
            run.font.name = 'Calibri'
            continue

        if line.startswith('|') and '|' in line[1:]:
            add_docx_table_like_lines(doc, [line])
            previous_was_table = True
            continue

        if line.startswith('- ') or line.startswith('* '):
            current_bullets.append(stripped[2:].strip())
            continue

        if line.startswith('1. ') or line.startswith('2. ') or line.startswith('3. ') or line.startswith('4. ') or line.startswith('5. '):
            current_bullets.append(stripped)
            continue

        if line.startswith('**') and line.endswith('**'):
            add_docx_text(doc, line)
            continue

        if line.startswith('```'):
            continue

        if line.startswith('[') and line.endswith(']'):
            add_docx_text(doc, line)
            continue

        if current_bullets:
            add_docx_bullets(doc, current_bullets)
            current_bullets = []

        if line.startswith('**'):
            p = doc.add_paragraph()
            run = p.add_run(line.strip('*'))
            run.bold = True
            run.font.size = Pt(11)
            run.font.name = 'Calibri'
            continue

        add_docx_text(doc, line)

    if current_bullets:
        add_docx_bullets(doc, current_bullets)

    doc.save(DOCX_PATH)
    print(f'Saved DOCX: {DOCX_PATH}')


def build_slide_title(slide, title, color=PPT_BLUE):
    title_box = slide.shapes.add_textbox(Inches(0.6), Inches(0.3), Inches(11.5), Inches(0.7))
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = title
    run.font.bold = True
    run.font.size = PptPt(24)
    run.font.name = 'Aptos'
    run.font.color.rgb = color
    p.alignment = PP_ALIGN.LEFT

    accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(1.0), Inches(12.0), Inches(0.08))
    accent.fill.solid()
    accent.fill.fore_color.rgb = color
    accent.line.fill.background()


def add_bullets(slide, lines, left=Inches(0.8), top=Inches(1.5), width=Inches(11.0), height=Inches(4.8), font_size=20):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.level = 0
        p.bullet = True
        p.alignment = PP_ALIGN.LEFT
        p.space_after = 8
        for run in p.runs:
            run.font.size = PptPt(font_size)
            run.font.name = 'Aptos'
            run.font.color.rgb = PPT_TEXT


def add_stat_box(slide, title, value, x, y, w, h, color=PPT_TEAL):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    shape.adjustments[0] = 0.2
    tf = shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.alignment = PP_ALIGN.CENTER
    p.runs[0].font.bold = True
    p.runs[0].font.size = PptPt(12)
    p.runs[0].font.name = 'Aptos'
    p.runs[0].font.color.rgb = PPT_WHITE
    p2 = tf.add_paragraph()
    p2.text = value
    p2.alignment = PP_ALIGN.CENTER
    p2.runs[0].font.bold = True
    p2.runs[0].font.size = PptPt(20)
    p2.runs[0].font.name = 'Aptos'
    p2.runs[0].font.color.rgb = PPT_WHITE


def add_footer(slide, slide_index, total):
    footer = slide.shapes.add_textbox(Inches(10.7), Inches(7.0), Inches(1.5), Inches(0.25))
    tf = footer.text_frame
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = f'{slide_index}/{total}'
    run.font.size = PptPt(10)
    run.font.name = 'Aptos'
    run.font.color.rgb = PptRGBColor(100, 116, 139)
    p.alignment = PP_ALIGN.RIGHT


def add_note(slide, text):
    try:
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        if tf is not None:
            tf.text = text
    except Exception:
        pass


def generate_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blue = PPT_BLUE
    teal = PPT_TEAL

    slides = [
        {
            'title': 'IAMShield AI',
            'subtitle': 'Assisted Least-Privilege IAM Policy Synthesis',
            'bullets': [
                'Team: Vasu Agrawal, Akash Gaurav, Sarthak',
                'Date: October 23, 2026',
                'Mentor: Sir Preshit Desai',
                'University: GLA University'
            ],
            'stats': [],
            'note': 'Good morning/afternoon. This presentation introduces IAMShield AI, an approval-controlled prototype for assisted least-privilege IAM policy synthesis. State the team, mentor, and the central idea: access evidence is converted into an explainable policy draft, but the administrator remains responsible for approval.'
        },
        {
            'title': 'The IAM Policy Challenge',
            'subtitle': 'Manual, Error-Prone, and Unscalable',
            'bullets': [
                'Manual policy creation takes 20+ hours per policy and requires deep expertise.',
                'Privilege creep causes users to accumulate 2-3x more permissions than required.',
                'Compliance and audit cycles remain slow, costly, and difficult to prove.',
                '80% of cloud breaches are caused by misconfigurations; security risk increases with scale.'
            ],
            'stats': [('80%', 'cloud breaches linked to misconfigurations'), ('71%', 'organizations struggle with privilege management'), ('$4.24M', 'average breach cost')],
            'note': 'Explain that IAM policy management is a major operational risk in cloud environments and a growing compliance burden for organizations.'
        },
        {
            'title': 'IAMShield AI: Assisted Policy Synthesis',
            'subtitle': 'From Access Logs to Reviewable Least-Privilege Policies',
            'bullets': [
                'Accepts a small, structured access-log dataset for the prototype.',
                'Analyzes observed actions, resources, frequency, and recent activity.',
                'Generates a minimal JSON policy for administrator review.',
                'Validates syntax and flags wildcard or excessive permissions before approval.'
            ],
            'stats': [('MVP', 'single focused workflow'), ('JSON', 'reviewable output'), ('Human', 'approval remains required')],
            'note': 'Frame the solution as an academic decision-support prototype. It recommends a policy; an administrator remains responsible for review and approval.'
        },
        {
            'title': 'The IAMShield AI Process',
            'subtitle': 'Ingest → Analyze → Synthesize → Validate → Review',
            'bullets': [
                'Step 1: Load representative access events into the prototype.',
                'Step 2: Group events by action and resource and discard stale or denied events.',
                'Step 3: Generate explicit Allow statements only for observed access.',
                'Step 4: Validate the draft and send wildcard findings to human review.'
            ],
            'stats': [],
            'note': 'Walk through the end-to-end process and show how the system converts observed usage into a safer IAM policy.'
        },
        {
            'title': 'Project Approach & Methodology',
            'subtitle': 'Focused MVP with Human Approval',
            'bullets': [
                'Phase 1: Define a simple access-event schema and seed safe demo data.',
                'Phase 2: Implement pattern analysis, synthesis, and validation rules.',
                'Phase 3: Add a dashboard for telemetry, policy output, and findings.',
                'Phase 4: Test normal, wildcard, empty, and stale-access scenarios.'
            ],
            'stats': [('Must', 'analysis + synthesis'), ('Must', 'validation'), ('Should', 'approval + audit')],
            'note': 'Explain that reducing the feature set makes the project testable within the academic timeline and keeps the security claims defensible.'
        },
        {
            'title': 'Core Technologies & Algorithms',
            'subtitle': 'Smart Engine with Proven Stack',
            'bullets': [
                'Backend: Python + FastAPI exposes dashboard, access-pattern, synthesis, validation, and policy endpoints.',
                'Frontend: React + Vite presents telemetry, risk signals, JSON output, and policy review screens.',
                'Persistence: SQLAlchemy with SQLite for the demonstration; PostgreSQL/MySQL remain migration options.',
                'Algorithm: filter recent allowed events, group action-resource pairs, generate statements, then validate.'
            ],
            'stats': [('Rule-based', 'explainable decisions'), ('JSON', 'reviewable output'), ('SQLite', 'local demo storage')],
            'note': 'Explain the technology choices in practical terms. FastAPI supports a small typed API, React makes the workflow visible, SQLAlchemy keeps persistence replaceable, and the rule-based engine is easier to explain than an unverified black-box model.'
        },
        {
            'title': 'Market & Competition Analysis',
            'subtitle': 'A Focused Gap in IAM Policy Review',
            'bullets': [
                'Cloud providers offer strong IAM primitives, but teams still interpret access logs manually.',
                'AWS Access Analyzer and Entra PIM support analysis or privileged access, not this complete student workflow.',
                'IAMShield AI focuses on one narrow gap: explainable policy drafts from observed behavior.',
                'The prototype is a decision-support tool, not a replacement for cloud IAM services.'
            ],
            'stats': [('Gap', 'manual interpretation'), ('Focus', 'policy drafts'), ('Position', 'approval-controlled')],
            'note': 'Avoid claiming that the project replaces major vendors. Present it as a focused academic prototype that improves the review step.'
        },
        {
            'title': 'Ground-Level Research Validation',
            'subtitle': 'Problem, Compliance, and Feasibility Confirmed',
            'bullets': [
                'NIST and cloud IAM guidance support least privilege, explicit access, and reviewable controls.',
                'The research identifies manual interpretation, privilege creep, and broad permissions as the focused problem.',
                'The prototype was tested with seeded normal, wildcard, and recent access patterns.',
                'The result is presented as an evaluation target and academic prototype, not a production security guarantee.'
            ],
            'stats': [('4', 'seeded access patterns'), ('4', 'generated statements'), ('1', 'wildcard warning')],
            'note': 'Describe the evidence honestly. Ground-level validation currently means representative sample data, successful backend compilation, frontend build validation, policy generation, and wildcard-risk detection. Future evaluation will use larger authorized datasets.'
        },
        {
            'title': 'Technical Architecture Overview',
            'subtitle': 'Robust, Modular, and Secure by Design',
            'bullets': [
                'Presentation layer: React dashboard shows access patterns, counts, risk signals, and policy output.',
                'Application layer: FastAPI coordinates filtering, synthesis, validation, and policy storage.',
                'Data layer: SQLAlchemy models access patterns and policy drafts in a local SQLite demonstration store.',
                'Control boundary: no automatic production enforcement; every recommendation is intended for human review.'
            ],
            'stats': [('3', 'architecture layers'), ('5', 'main API workflows'), ('0', 'production changes')],
            'note': 'Walk through the architecture from left to right: the dashboard calls the FastAPI routes, the routes use the synthesis service and SQLAlchemy session, and the database stores the evidence and drafts. Emphasize that the prototype deliberately stops before production enforcement.'
        },
        {
            'title': 'Implementation Timeline & Milestones',
            'subtitle': 'Clear Roadmap to an MVP',
            'bullets': [
                'Completed foundation: project structure, SQLAlchemy models, SQLite fallback, and FastAPI application.',
                'Completed core workflow: demo data, access-pattern analysis, JSON synthesis, and validation warnings.',
                'Completed interface: dashboard, synthesis view, policy list, and responsive styling.',
                'Next hardening step: authentication, approval comments, version history, and larger test fixtures.'
            ],
            'stats': [('Now', 'working MVP'), ('Next', 'approval workflow'), ('Later', 'cloud adapters')],
            'note': 'Present this as progress and next steps rather than a commercial delivery promise. The core analysis-to-policy demonstration is working; authentication, approval history, and live cloud adapters are the next controlled increments.'
        },
        {
            'title': 'Success Metrics & Validation',
            'subtitle': 'Measurable Criteria for Quality',
            'bullets': [
                'Build quality: backend compilation and frontend production build complete successfully.',
                'Functional quality: normal, wildcard, empty, denied, and stale-event scenarios are defined for testing.',
                'Policy quality: generated permissions must trace back to eligible observed action-resource pairs.',
                'Safety quality: warnings are shown before approval, and production enforcement is intentionally absent.'
            ],
            'stats': [('Build', 'passed'), ('Smoke test', '4 patterns'), ('Warning', 'wildcard detected')],
            'note': 'These are the metrics that can be defended in the current presentation. Avoid claiming 95% production accuracy or commercial KPIs before a larger controlled evaluation is completed.'
        },
        {
            'title': 'Conclusion & Call to Action',
            'subtitle': 'A Practical First Step Toward Safer IAM Reviews',
            'bullets': [
                'The problem is clear: broad IAM permissions are difficult to review manually.',
                'The MVP analyzes sample access behavior and creates explainable policy drafts.',
                'Validation flags risky wildcards before an administrator approves anything.',
                'Advanced integrations and autonomous enforcement remain future work.'
            ],
            'stats': [('Core', 'analyze + synthesize'), ('Control', 'human approval'), ('Next', 'real log adapters')],
            'note': 'Close with a credible claim: the MVP proves the analysis-to-policy workflow while leaving production enforcement and provider integrations for later phases.'
        }
    ]

    for index, slide_data in enumerate(slides, start=1):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = PptRGBColor(248, 250, 252)

        top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.3))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = blue
        top_bar.line.fill.background()

        if index == 1:
            title_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.2), Inches(11.0), Inches(1.2))
            tf = title_box.text_frame
            p = tf.paragraphs[0]
            p.text = slide_data['title']
            p.alignment = PP_ALIGN.LEFT
            p.runs[0].font.bold = True
            p.runs[0].font.size = PptPt(30)
            p.runs[0].font.name = 'Aptos'
            p.runs[0].font.color.rgb = blue
            p2 = tf.add_paragraph()
            p2.text = slide_data['subtitle']
            p2.alignment = PP_ALIGN.LEFT
            p2.runs[0].font.size = PptPt(18)
            p2.runs[0].font.name = 'Aptos'
            p2.runs[0].font.color.rgb = PptRGBColor(71, 85, 105)

            accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(2.5), Inches(11.8), Inches(0.08))
            accent.fill.solid(); accent.fill.fore_color.rgb = teal; accent.line.fill.background()

            bullet_box = slide.shapes.add_textbox(Inches(0.8), Inches(2.9), Inches(8.0), Inches(2.7))
            btf = bullet_box.text_frame
            for bullet in slide_data['bullets']:
                p = btf.paragraphs[0] if not btf.paragraphs[0].text else btf.add_paragraph()
                p.text = bullet
                p.level = 0
                p.bullet = True
                p.alignment = PP_ALIGN.LEFT
                for run in p.runs:
                    run.font.size = PptPt(18)
                    run.font.name = 'Aptos'
                    run.font.color.rgb = PPT_TEXT

            right_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.5), Inches(2.8), Inches(3.0), Inches(2.7))
            right_box.fill.solid(); right_box.fill.fore_color.rgb = PptRGBColor(219, 234, 254); right_box.line.fill.background(); right_box.adjustments[0] = 0.2
            rf = right_box.text_frame
            rf.text = 'IAMShield AI\nSecurity\nAutomation\nCompliance'
            for idx, paragraph in enumerate(rf.paragraphs):
                paragraph.alignment = PP_ALIGN.CENTER
                for run in paragraph.runs:
                    run.font.size = PptPt(20 if idx == 0 else 16)
                    run.font.bold = idx == 0
                    run.font.name = 'Aptos'
                    run.font.color.rgb = blue
        else:
            build_slide_title(slide, slide_data['title'], blue)
            bullet_size = 16 if index in {6, 7, 8, 9, 10, 11} else 18
            add_bullets(slide, slide_data['bullets'], left=Inches(0.8), top=Inches(1.4), width=Inches(7.8), height=Inches(4.7), font_size=bullet_size)
            if slide_data['stats']:
                # stat cards on right
                x = Inches(8.9)
                y = Inches(1.7)
                for idx, (label, value) in enumerate(slide_data['stats'][:3]):
                    add_stat_box(slide, label, value, x, y + idx * Inches(1.4), Inches(2.8), Inches(1.2), color=teal if idx % 2 == 0 else blue)

        if index == 1:
            add_footer(slide, 1, len(slides))
        else:
            add_footer(slide, index, len(slides))

        add_note(slide, slide_data['note'])

    prs.save(PPTX_PATH)
    print(f'Saved PowerPoint: {PPTX_PATH}')


if __name__ == '__main__':
    generate_docx_from_markdown()
    generate_presentation()
