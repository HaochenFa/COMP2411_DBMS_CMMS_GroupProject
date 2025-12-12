"""
PDF Report Generation Service for PolyU CMMS.

This module provides comprehensive PDF report generation with charts,
tables, and PolyU branding.
"""

import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, inch
from reportlab.platypus import (
    HRFlowable,
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# Try to import matplotlib for chart generation
try:
    import matplotlib

    matplotlib.use("Agg")  # Non-interactive backend
    import matplotlib.pyplot as plt

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# PolyU Brand Colors
POLYU_RED = colors.HexColor("#A6192E")
POLYU_GOLD = colors.HexColor("#B08E55")
POLYU_DARK_RED = colors.HexColor("#8C1526")
POLYU_GRAY = colors.HexColor("#5D5D5D")
POLYU_LIGHT_GRAY = colors.HexColor("#E8E8E8")


class ReportGenerator:
    """Generates comprehensive PDF reports for PolyU CMMS."""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles for PolyU branding."""
        # Title style
        self.styles.add(
            ParagraphStyle(
                name="PolyUTitle",
                parent=self.styles["Heading1"],
                fontSize=24,
                textColor=POLYU_RED,
                spaceAfter=20,
                alignment=TA_CENTER,
                fontName="Helvetica-Bold",
            )
        )

        # Section header style
        self.styles.add(
            ParagraphStyle(
                name="SectionHeader",
                parent=self.styles["Heading2"],
                fontSize=14,
                textColor=POLYU_RED,
                spaceBefore=15,
                spaceAfter=10,
                fontName="Helvetica-Bold",
            )
        )

        # Subtitle style
        self.styles.add(
            ParagraphStyle(
                name="Subtitle",
                parent=self.styles["Normal"],
                fontSize=12,
                textColor=POLYU_GRAY,
                alignment=TA_CENTER,
                spaceAfter=30,
            )
        )

        # KPI value style
        self.styles.add(
            ParagraphStyle(
                name="KPIValue",
                parent=self.styles["Normal"],
                fontSize=20,
                textColor=POLYU_RED,
                alignment=TA_CENTER,
                fontName="Helvetica-Bold",
            )
        )

        # KPI label style
        self.styles.add(
            ParagraphStyle(
                name="KPILabel",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=POLYU_GRAY,
                alignment=TA_CENTER,
            )
        )

    def _create_header(self, report_title):
        """Create report header with PolyU branding."""
        elements = []

        # Main title
        elements.append(Paragraph("PolyU CMMS", self.styles["PolyUTitle"]))
        elements.append(Paragraph(report_title, self.styles["SectionHeader"]))

        # Generation timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elements.append(Paragraph(f"Generated: {timestamp}", self.styles["Subtitle"]))

        # Horizontal line
        elements.append(
            HRFlowable(
                width="100%", thickness=2, color=POLYU_RED, spaceBefore=5, spaceAfter=20
            )
        )

        return elements

    def _create_kpi_table(self, kpis):
        """Create a KPI summary table.

        Args:
            kpis: List of dicts with 'label' and 'value' keys
        """
        # Create cells for each KPI
        kpi_data = []
        values_row = []
        labels_row = []

        for kpi in kpis:
            values_row.append(Paragraph(str(kpi["value"]), self.styles["KPIValue"]))
            labels_row.append(Paragraph(kpi["label"], self.styles["KPILabel"]))

        kpi_data.append(values_row)
        kpi_data.append(labels_row)

        # Calculate column widths
        num_cols = len(kpis)
        col_width = (A4[0] - 2 * inch) / num_cols

        table = Table(kpi_data, colWidths=[col_width] * num_cols)
        table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("BOX", (0, 0), (-1, -1), 1, POLYU_LIGHT_GRAY),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, POLYU_LIGHT_GRAY),
                    ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                    ("TOPPADDING", (0, 0), (-1, -1), 15),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 15),
                ]
            )
        )

        return table

    def _create_data_table(self, headers, data, title=None):
        """Create a styled data table.

        Args:
            headers: List of column headers
            data: List of rows (each row is a list of values)
            title: Optional table title
        """
        elements = []

        if title:
            elements.append(Paragraph(title, self.styles["SectionHeader"]))

        # Prepare table data with headers
        table_data = [headers] + data

        # Calculate column widths
        available_width = A4[0] - 2 * inch
        col_width = available_width / len(headers)

        table = Table(table_data, colWidths=[col_width] * len(headers))
        table.setStyle(
            TableStyle(
                [
                    # Header styling
                    ("BACKGROUND", (0, 0), (-1, 0), POLYU_RED),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                    # Body styling
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 1), (-1, -1), 9),
                    ("ALIGN", (0, 1), (-1, -1), "LEFT"),
                    # Alternating row colors
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, POLYU_LIGHT_GRAY],
                    ),
                    # Grid
                    ("GRID", (0, 0), (-1, -1), 0.5, POLYU_GRAY),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        elements.append(table)
        elements.append(Spacer(1, 20))

        return elements

    def _create_bar_chart(self, data, x_key, y_key, title, xlabel, ylabel):
        """Generate a bar chart image using matplotlib.

        Returns an Image flowable or None if matplotlib unavailable.
        """
        if not MATPLOTLIB_AVAILABLE or not data:
            return None

        fig, ax = plt.subplots(figsize=(7, 3.5))

        x_values = [
            str(item.get(x_key, ""))[:20] for item in data
        ]  # Truncate long labels
        y_values = [item.get(y_key, 0) for item in data]

        bars = ax.bar(x_values, y_values, color="#A6192E", edgecolor="#8C1526")

        ax.set_xlabel(xlabel, fontsize=10, color="#5D5D5D")
        ax.set_ylabel(ylabel, fontsize=10, color="#5D5D5D")
        ax.set_title(title, fontsize=12, fontweight="bold", color="#A6192E")

        # Rotate x labels if needed
        if len(x_values) > 5:
            plt.xticks(rotation=45, ha="right", fontsize=8)
        else:
            plt.xticks(fontsize=9)

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(colors="#5D5D5D")

        plt.tight_layout()

        # Save to buffer
        img_buffer = io.BytesIO()
        plt.savefig(
            img_buffer,
            format="png",
            dpi=150,
            bbox_inches="tight",
            facecolor="white",
            edgecolor="none",
        )
        plt.close(fig)
        img_buffer.seek(0)

        return Image(img_buffer, width=6.5 * inch, height=3 * inch)

    def _create_pie_chart(self, data, label_key, value_key, title):
        """Generate a pie chart image using matplotlib.

        Returns an Image flowable or None if matplotlib unavailable.
        """
        if not MATPLOTLIB_AVAILABLE or not data:
            return None

        fig, ax = plt.subplots(figsize=(6, 4))

        labels = [str(item.get(label_key, ""))[:15] for item in data]
        values = [item.get(value_key, 0) for item in data]

        # PolyU color palette
        chart_colors = [
            "#A6192E",
            "#B08E55",
            "#8C1526",
            "#5D5D5D",
            "#A0A0A0",
            "#D4D4D4",
            "#E8D4A0",
            "#6B3A3A",
        ]

        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            autopct="%1.1f%%",
            colors=chart_colors[: len(values)],
            startangle=90,
            pctdistance=0.75,
        )

        ax.set_title(title, fontsize=12, fontweight="bold", color="#A6192E")

        for autotext in autotexts:
            autotext.set_fontsize(8)
            autotext.set_color("white")

        plt.tight_layout()

        img_buffer = io.BytesIO()
        plt.savefig(
            img_buffer,
            format="png",
            dpi=150,
            bbox_inches="tight",
            facecolor="white",
            edgecolor="none",
        )
        plt.close(fig)
        img_buffer.seek(0)

        return Image(img_buffer, width=5 * inch, height=3.5 * inch)

    def _create_footer(self, canvas, doc):
        """Add footer to each page."""
        canvas.saveState()

        # Footer line
        canvas.setStrokeColor(POLYU_RED)
        canvas.setLineWidth(1)
        canvas.line(inch, 0.75 * inch, A4[0] - inch, 0.75 * inch)

        # Footer text
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(POLYU_GRAY)
        canvas.drawString(
            inch,
            0.5 * inch,
            f"PolyU CMMS Report | Generated {datetime.now().strftime('%Y-%m-%d')}",
        )
        canvas.drawRightString(A4[0] - inch, 0.5 * inch, f"Page {doc.page}")

        canvas.restoreState()

    def generate_comprehensive_report(self, report_data, sections=None):
        """Generate a comprehensive PDF report.

        Args:
            report_data: Dict containing all report data from the API
            sections: List of sections to include (default: all)

        Returns:
            BytesIO buffer containing the PDF
        """
        if sections is None:
            sections = [
                "executive_summary",
                "maintenance",
                "personnel",
                "activities",
                "schools",
                "safety",
            ]

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=inch,
            bottomMargin=inch,
        )

        elements = []

        # Header
        elements.extend(self._create_header("Comprehensive Management Report"))

        # Executive Summary Section
        if "executive_summary" in sections:
            elements.extend(self._build_executive_summary(report_data))

        # Maintenance Section
        if "maintenance" in sections:
            elements.extend(self._build_maintenance_section(report_data))

        # Personnel Section
        if "personnel" in sections:
            elements.extend(self._build_personnel_section(report_data))

        # Activities Section
        if "activities" in sections:
            elements.extend(self._build_activities_section(report_data))

        # Schools Section
        if "schools" in sections:
            elements.extend(self._build_schools_section(report_data))

        # Safety Section
        if "safety" in sections:
            elements.extend(self._build_safety_section(report_data))

        # Build the PDF
        doc.build(
            elements, onFirstPage=self._create_footer, onLaterPages=self._create_footer
        )

        buffer.seek(0)
        return buffer

    def _build_executive_summary(self, report_data):
        """Build executive summary section."""
        elements = []
        elements.append(Paragraph("Executive Summary", self.styles["SectionHeader"]))

        summary = report_data.get("summary", {})
        kpis = [
            {"label": "Total Personnel", "value": summary.get("total_persons", 0)},
            {"label": "Departments", "value": summary.get("total_schools", 0)},
            {"label": "Activities", "value": summary.get("total_activities", 0)},
            {
                "label": "Maintenance Tasks",
                "value": summary.get("total_maintenance", 0),
            },
        ]

        elements.append(self._create_kpi_table(kpis))
        elements.append(Spacer(1, 20))

        return elements

    def _build_maintenance_section(self, report_data):
        """Build maintenance analysis section."""
        elements = []
        elements.append(PageBreak())
        elements.append(Paragraph("Maintenance Analysis", self.styles["SectionHeader"]))

        maintenance_data = report_data.get("maintenance_summary", [])

        # Bar chart
        chart = self._create_bar_chart(
            maintenance_data,
            "building",
            "count",
            "Maintenance Tasks by Building",
            "Building",
            "Task Count",
        )
        if chart:
            elements.append(chart)
            elements.append(Spacer(1, 20))

        # Data table
        if maintenance_data:
            headers = ["Type", "Building", "Campus", "Count"]
            rows = [
                [
                    str(item.get("type", "")),
                    str(item.get("building", "")),
                    str(item.get("campus", "")),
                    str(item.get("count", 0)),
                ]
                for item in maintenance_data[:15]
            ]  # Limit to 15 rows

            elements.extend(
                self._create_data_table(headers, rows, "Maintenance Summary Table")
            )

        return elements

    def _build_personnel_section(self, report_data):
        """Build personnel overview section."""
        elements = []
        elements.append(PageBreak())
        elements.append(Paragraph("Personnel Overview", self.styles["SectionHeader"]))

        people_data = report_data.get("people_summary", [])

        # Pie chart
        chart = self._create_pie_chart(
            people_data, "job_role", "count", "Personnel Distribution by Role"
        )
        if chart:
            elements.append(chart)
            elements.append(Spacer(1, 20))

        # Data table
        if people_data:
            headers = ["Job Role", "Status", "Count"]
            rows = [
                [
                    str(item.get("job_role", "")),
                    str(item.get("status", "")),
                    str(item.get("count", 0)),
                ]
                for item in people_data
            ]

            elements.extend(
                self._create_data_table(headers, rows, "Personnel by Role and Status")
            )

        return elements

    def _build_activities_section(self, report_data):
        """Build activities statistics section."""
        elements = []
        elements.append(PageBreak())
        elements.append(
            Paragraph("Activities Statistics", self.styles["SectionHeader"])
        )

        activities_data = report_data.get("activities_summary", [])

        # Bar chart
        chart = self._create_bar_chart(
            activities_data,
            "type",
            "activity_count",
            "Activities by Type",
            "Activity Type",
            "Count",
        )
        if chart:
            elements.append(chart)
            elements.append(Spacer(1, 20))

        # Data table
        if activities_data:
            headers = ["Type", "Organiser", "Count"]
            rows = [
                [
                    str(item.get("type", "")),
                    str(item.get("organiser_name", ""))[:25],
                    str(item.get("activity_count", 0)),
                ]
                for item in activities_data[:15]
            ]

            elements.extend(
                self._create_data_table(headers, rows, "Activities Summary")
            )

        return elements

    def _build_schools_section(self, report_data):
        """Build schools/departments section."""
        elements = []
        elements.append(PageBreak())
        elements.append(
            Paragraph("Department Statistics", self.styles["SectionHeader"])
        )

        schools_data = report_data.get("school_stats", [])

        # Bar chart for affiliated people
        chart = self._create_bar_chart(
            schools_data,
            "school_name",
            "affiliated_people",
            "Affiliated Personnel by Department",
            "Department",
            "Personnel Count",
        )
        if chart:
            elements.append(chart)
            elements.append(Spacer(1, 20))

        # Data table
        if schools_data:
            headers = ["Department", "School Name", "Faculty", "Personnel", "Locations"]
            rows = [
                [
                    str(item.get("department", "")),
                    str(item.get("school_name", ""))[:20],
                    str(item.get("faculty", ""))[:20],
                    str(item.get("affiliated_people", 0)),
                    str(item.get("locations_count", 0)),
                ]
                for item in schools_data
            ]

            elements.extend(
                self._create_data_table(headers, rows, "Department Overview")
            )

        return elements

    def _build_safety_section(self, report_data):
        """Build safety/chemical hazard section."""
        elements = []
        elements.append(PageBreak())
        elements.append(
            Paragraph("Safety & Chemical Hazard Report", self.styles["SectionHeader"])
        )

        safety_data = report_data.get("safety_data", [])
        freq_data = report_data.get("maintenance_frequency", [])

        # Summary text
        hazard_count = sum(1 for item in safety_data if item.get("active_chemical"))
        elements.append(
            Paragraph(
                f"<b>Chemical Hazard Tasks:</b> {hazard_count} cleaning tasks involve "
                "active chemicals requiring special safety precautions.",
                self.styles["Normal"],
            )
        )
        elements.append(Spacer(1, 15))

        # Frequency table
        if freq_data:
            headers = ["Frequency", "Type", "Task Count"]
            rows = [
                [
                    str(item.get("frequency", "")),
                    str(item.get("type", "")),
                    str(item.get("task_count", 0)),
                ]
                for item in freq_data
            ]

            elements.extend(
                self._create_data_table(headers, rows, "Maintenance Frequency Analysis")
            )

        return elements


def generate_report(report_data, sections=None):
    """Convenience function to generate a PDF report.

    Args:
        report_data: Dict containing all report data
        sections: Optional list of sections to include

    Returns:
        BytesIO buffer containing the PDF
    """
    generator = ReportGenerator()
    return generator.generate_comprehensive_report(report_data, sections)
