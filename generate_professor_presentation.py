from pathlib import Path

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

import generate_project_assets as base

OUTPUT = Path(r"D:\Reggii\GLA\Mini Project\IAMShield_AI_Presentation_CORRECTED.pptx")
BLUE = base.PPT_BLUE
TEAL = base.PPT_TEAL
TEXT = base.PPT_TEXT
WHITE = base.PPT_WHITE
LIGHT_BACKGROUND = RGBColor(248, 250, 252)


def add_title(slide, title, subtitle):
    box = slide.shapes.add_textbox(Inches(0.8), Inches(1.15), Inches(7.75), Inches(1.35))
    frame = box.text_frame
    frame.word_wrap = True
    first = frame.paragraphs[0]
    first.text = title
    first.runs[0].font.name = "Aptos Display"
    first.runs[0].font.bold = True
    first.runs[0].font.size = Pt(30)
    first.runs[0].font.color.rgb = BLUE
    second = frame.add_paragraph()
    second.text = subtitle
    second.runs[0].font.name = "Aptos"
    second.runs[0].font.size = Pt(18)
    second.runs[0].font.color.rgb = RGBColor(71, 85, 105)


def add_slide_top(slide):
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.3))
    bar.fill.solid()
    bar.fill.fore_color.rgb = BLUE
    bar.line.fill.background()


def add_bullet_list(slide, bullets, dense=False):
    box = slide.shapes.add_textbox(Inches(0.8), Inches(2.65), Inches(7.75), Inches(3.85))
    frame = box.text_frame
    frame.word_wrap = True
    frame.margin_left = 0
    frame.margin_right = 0
    for index, text in enumerate(bullets):
        paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        paragraph.text = text
        paragraph.bullet = True
        paragraph.space_after = 9 if not dense else 7
        for run in paragraph.runs:
            run.font.name = "Aptos"
            run.font.size = Pt(16 if dense else 18)
            run.font.color.rgb = TEXT


def add_stat_cards(slide, cards):
    for index, (label, value) in enumerate(cards):
        base.add_stat_box(
            slide,
            label,
            value,
            Inches(8.9),
            Inches(1.7 + (index * 1.4)),
            Inches(2.8),
            Inches(1.2),
            color=TEAL if index % 2 == 0 else BLUE,
        )


def add_notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def build_deck():
    presentation = Presentation()
    presentation.slide_width = Inches(13.333)
    presentation.slide_height = Inches(7.5)

    slides = [
        ("IAMShield AI", "Turning Access Evidence into Safer IAM Reviews", [
            "Team: Vasu Agrawal, Akash Gaurav, Sarthak",
            "Mentor: Mr. Preshit Mangesh Desai",
            "GLA University | October 23, 2026",
            "Phase: working academic MVP",
        ], [], "Introduce the project in your own words. IAMShield AI asks whether access activity can help an administrator create a narrower IAM policy. Clarify that this is an academic prototype and the final decision remains with a human.", True),
        ("Why IAM Reviews Need Better Evidence", "Static policies do not show the whole story", [
            "A policy file shows what is allowed, but not always what an application actually uses.",
            "Unused permissions remain difficult to notice when reviews depend only on manual inspection.",
            "Broad permissions increase the impact of a compromised identity or service.",
            "The focused problem is comparing granted access with observed access.",
            "A useful review should show both the permission and the evidence behind it.",
        ], [("Input", "access activity"), ("Risk", "unused privilege"), ("Need", "clear evidence")], "Explain the problem without overclaiming statistics. Administrators need evidence about actual usage, and manual comparison is slow and easy to miss.", False),
        ("Our Focused Solution", "A recommendation engine for the IAM review step", [
            "Load normalized access events into a small demonstration dataset.",
            "Separate recent allowed activity from denied or stale records.",
            "Turn eligible evidence into explicit JSON Allow statements.",
            "Show warnings before a reviewer considers saving or approving the draft.",
            "The result is a recommendation, not an automatic production change.",
        ], [("1", "focused workflow"), ("JSON", "policy format"), ("Human", "final reviewer")], "Describe IAMShield AI as decision support. It produces a draft and findings; it does not silently change a cloud account.", False),
        ("One Example from Input to Output", "The algorithm stays intentionally explainable", [
            "Input: repeated GetObject and ListBucket activity for one storage bucket.",
            "Filter: ignore denied activity and events outside the selected time window.",
            "Output: explicit Allow statements for the observed actions and resources.",
            "Finding: wildcard action or resource access is shown as a review warning.",
            "The reviewer can connect each statement back to the source event.",
        ], [], "Use this as the main algorithm explanation. Every generated permission should be traceable to the evidence that produced it.", False),
        ("What the Generated Policy Contains", "A small output that a reviewer can inspect", [
            "Version: identifies the policy document format used by the prototype.",
            "Effect: uses explicit Allow statements for eligible observed activity.",
            "Action: lists the API operation found in the access evidence.",
            "Resource: narrows the permission to the resource seen in the event.",
        ], [("Version", "2012-10-17"), ("Effect", "explicit Allow"), ("Review", "before use")], "Explain the output field by field. The generated document is intentionally simple so a student, developer, or professor can inspect why each permission appears.", True),
        ("How We Reduced the Project Scope", "A smaller system is easier to test honestly", [
            "Kept: access-pattern analysis, policy generation, validation, and dashboard review.",
            "Deferred: live cloud connectors, automatic deployment, and advanced AI models.",
            "Reason: the core security decision should be testable before adding integrations.",
            "Result: a smaller prototype with a clear demonstration path.",
            "This makes the project easier to explain, reproduce, and evaluate.",
        ], [("Keep", "core workflow"), ("Defer", "cloud adapters"), ("Control", "human review")], "Explain that reducing the scope was deliberate. A smaller validated workflow is stronger than many unimplemented features.", False),
        ("Implementation Choices", "Simple components with clear ownership", [
            "FastAPI owns the REST endpoints and coordinates the workflow.",
            "The synthesis service contains filtering, grouping, and statement-generation rules.",
            "SQLAlchemy separates application logic from the SQLite demonstration database.",
            "React displays the evidence and makes the generated result easy to inspect.",
            "The modular boundary leaves room for later authentication and approval features.",
        ], [("Backend", "FastAPI"), ("Frontend", "React"), ("Storage", "SQLite demo")], "Connect each tool to a responsibility. The rule-based engine is used because its decisions can be explained and repeated with a small dataset.", True),
        ("What We Validated So Far", "Evidence from research and the working prototype", [
            "Standards research supports least privilege and controlled access review.",
            "The prototype starts with four seeded patterns, including one risky wildcard case.",
            "The synthesis smoke test produced four policy statements from eligible records.",
            "Validation detected the wildcard risk instead of silently treating it as safe.",
            "The frontend production build and backend compilation also passed.",
        ], [("4", "demo patterns"), ("4", "statements"), ("1", "warning")], "State exactly what has been validated: representative data, successful builds, policy generation, and wildcard-risk detection. Larger authorized datasets are future evaluation work.", True),
        ("Architecture of the Prototype", "Three layers and one explicit safety boundary", [
            "Presentation layer: dashboard and synthesis views show evidence and results.",
            "Application layer: API routes call the analysis and validation service.",
            "Data layer: access patterns and policy drafts are stored through SQLAlchemy.",
            "Safety boundary: the system stops at recommendation and review.",
            "This separation keeps policy logic independent from the interface.",
        ], [("3", "layers"), ("5", "API workflows"), ("0", "automatic changes")], "Walk through the dashboard, API, service, and database. Emphasize that the architecture intentionally stops before production enforcement.", True),
        ("Progress and Next Steps", "What is working and what remains", [
            "Working now: seeded telemetry, summary metrics, pattern listing, synthesis, and validation.",
            "Working now: React dashboard, synthesis result view, and policy review list.",
            "Next: add authentication and an explicit approve/reject record.",
            "Later: authorized cloud-log adapters and provider-specific validators.",
            "Each future feature will be added only after the core workflow is stable.",
        ], [("Done", "core workflow"), ("Next", "approval record"), ("Later", "log adapters")], "Present this as honest progress. The core demonstration works; authentication, approval history, and live integrations are controlled next steps.", True),
        ("How We Will Judge the Prototype", "Quality means correctness, traceability, and control", [
            "Correctness: normal records become explicit actions and resources in the draft.",
            "Safety: denied and stale records are excluded from the normal Allow output.",
            "Traceability: every statement can be explained from the source access pattern.",
            "Control: wildcard findings appear before a reviewer decides what to do.",
            "The same test cases can be repeated when new integrations are introduced.",
        ], [("Build", "passed"), ("Traceability", "required"), ("Control", "human review")], "For a security prototype, correctness and traceability matter more than unsupported accuracy numbers. Explain how each criterion can be checked.", True),
        ("Conclusion", "A small, explainable step toward safer IAM reviews", [
            "IAMShield AI connects observed access behavior with a policy-review workflow.",
            "The MVP demonstrates analysis, synthesis, validation, and dashboard presentation.",
            "The rule-based approach keeps the result explainable for a reviewer.",
            "The next step is controlled approval and larger authorized datasets.",
            "This gives the project a realistic path from academic prototype to future research.",
        ], [("Core", "evidence to draft"), ("Control", "human review"), ("Next", "approval + data")], "Close with this sentence: IAMShield AI demonstrates an explainable way to turn access evidence into a least-privilege policy draft without removing human control. Invite questions.", False),
    ]

    for index, (title, subtitle, bullets, stats, notes, is_title) in enumerate(slides, 1):
        slide = presentation.slides.add_slide(presentation.slide_layouts[6])
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = LIGHT_BACKGROUND
        add_slide_top(slide)
        if is_title:
            add_title(slide, title, subtitle)
            base.add_bullets(slide, bullets, left=Inches(0.8), top=Inches(2.9), width=Inches(8.0), height=Inches(2.7), font_size=18)
            shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.5), Inches(2.8), Inches(3.0), Inches(2.7))
            shape.fill.solid()
            shape.fill.fore_color.rgb = RGBColor(219, 234, 254)
            shape.line.fill.background()
            shape.text_frame.text = "IAMShield AI\nEvidence\nSynthesis\nReview"
            for paragraph_index, paragraph in enumerate(shape.text_frame.paragraphs):
                paragraph.alignment = PP_ALIGN.CENTER
                for run in paragraph.runs:
                    run.font.name = "Aptos"
                    run.font.size = Pt(20 if paragraph_index == 0 else 16)
                    run.font.bold = paragraph_index == 0
                    run.font.color.rgb = BLUE
        else:
            add_title(slide, title, subtitle)
            add_bullet_list(slide, bullets, dense=len(bullets) > 3)
            add_stat_cards(slide, stats)
        base.add_footer(slide, index, len(slides))
        add_notes(slide, notes)

    presentation.save(OUTPUT)
    print(f"Saved {OUTPUT}")


if __name__ == "__main__":
    build_deck()
