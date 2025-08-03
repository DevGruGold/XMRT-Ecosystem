"""
Document Generation Module for Enhanced Eliza
Provides comprehensive document creation capabilities
"""

import os
import json
import markdown
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import io
import base64


@dataclass
class DocumentTemplate:
    """Document template configuration"""

    name: str
    type: str  # 'report', 'analysis', 'presentation', 'memo'
    sections: List[str]
    style_config: Dict[str, Any]


class DocumentGenerator:
    """Advanced document generation with multiple formats and templates"""

    def __init__(self):
        self.templates = self._initialize_templates()
        self.output_formats = ["markdown", "pdf", "html", "json"]

    def _initialize_templates(self) -> Dict[str, DocumentTemplate]:
        """Initialize document templates"""
        return {
            "dao_report": DocumentTemplate(
                name="DAO Activity Report",
                type="report",
                sections=[
                    "executive_summary",
                    "metrics",
                    "analysis",
                    "recommendations",
                ],
                style_config={"theme": "professional", "include_charts": True},
            ),
            "technical_analysis": DocumentTemplate(
                name="Technical Analysis",
                type="analysis",
                sections=["overview", "methodology", "findings", "conclusions"],
                style_config={"theme": "technical", "include_code": True},
            ),
            "project_memo": DocumentTemplate(
                name="Project Memorandum",
                type="memo",
                sections=["purpose", "background", "proposal", "next_steps"],
                style_config={"theme": "business", "format": "concise"},
            ),
            "research_report": DocumentTemplate(
                name="Research Report",
                type="report",
                sections=[
                    "abstract",
                    "introduction",
                    "methodology",
                    "results",
                    "discussion",
                    "references",
                ],
                style_config={"theme": "academic", "include_citations": True},
            ),
        }

    def generate_document(
        self,
        template_name: str,
        content_data: Dict[str, Any],
        output_format: str = "markdown",
        custom_config: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Generate document using specified template and data"""
        try:
            if template_name not in self.templates:
                return {
                    "success": False,
                    "error": f"Template {template_name} not found",
                }

            if output_format not in self.output_formats:
                return {
                    "success": False,
                    "error": f"Output format {output_format} not supported",
                }

            template = self.templates[template_name]
            config = {**template.style_config, **(custom_config or {})}

            # Generate content based on template
            document_content = self._build_document_content(
                template, content_data, config
            )

            # Convert to requested format
            if output_format == "markdown":
                output = self._generate_markdown(document_content, config)
            elif output_format == "pdf":
                output = self._generate_pdf(document_content, config)
            elif output_format == "html":
                output = self._generate_html(document_content, config)
            elif output_format == "json":
                output = self._generate_json(document_content, config)

            return {
                "success": True,
                "template": template_name,
                "format": output_format,
                "content": output,
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "sections": len(template.sections),
                    "word_count": self._estimate_word_count(document_content),
                },
            }

        except Exception as e:
            return {"success": False, "error": f"Document generation failed: {str(e)}"}

    def _build_document_content(
        self, template: DocumentTemplate, data: Dict[str, Any], config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build structured document content"""
        content = {
            "title": data.get("title", template.name),
            "author": data.get("author", "Eliza AI Agent"),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "sections": {},
        }

        for section in template.sections:
            content["sections"][section] = self._generate_section_content(
                section, data, config
            )

        return content

    def _generate_section_content(
        self, section: str, data: Dict[str, Any], config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate content for a specific section"""
        section_data = data.get("sections", {}).get(section, {})

        if section == "executive_summary":
            return {
                "title": "Executive Summary",
                "content": section_data.get(
                    "content",
                    "This report provides a comprehensive analysis of current DAO activities and performance metrics.",
                ),
                "key_points": section_data.get(
                    "key_points",
                    [
                        "DAO activity has increased significantly",
                        "Key performance indicators show positive trends",
                        "Recommendations for continued growth",
                    ],
                ),
            }
        elif section == "metrics":
            return {
                "title": "Key Metrics",
                "content": section_data.get(
                    "content", "Performance metrics and statistical analysis."
                ),
                "data": section_data.get("data", {}),
                "charts": section_data.get("charts", []),
            }
        elif section == "analysis":
            return {
                "title": "Analysis",
                "content": section_data.get(
                    "content", "Detailed analysis of findings and trends."
                ),
                "findings": section_data.get("findings", []),
                "insights": section_data.get("insights", []),
            }
        elif section == "recommendations":
            return {
                "title": "Recommendations",
                "content": section_data.get(
                    "content", "Strategic recommendations based on analysis."
                ),
                "actions": section_data.get(
                    "actions",
                    [
                        "Continue monitoring key metrics",
                        "Implement suggested improvements",
                        "Schedule regular reviews",
                    ],
                ),
            }
        else:
            return {
                "title": section.replace("_", " ").title(),
                "content": section_data.get(
                    "content", f"Content for {section} section."
                ),
                "data": section_data.get("data", {}),
            }

    def _generate_markdown(
        self, content: Dict[str, Any], config: Dict[str, Any]
    ) -> str:
        """Generate Markdown format document"""
        md_content = []

        # Title and metadata
        md_content.append(f"# {content['title']}")
        md_content.append(f"**Author:** {content['author']}")
        md_content.append(f"**Date:** {content['date']}")
        md_content.append("")

        # Sections
        for section_key, section_data in content["sections"].items():
            md_content.append(f"## {section_data['title']}")
            md_content.append("")
            md_content.append(section_data["content"])
            md_content.append("")

            # Add key points if available
            if "key_points" in section_data:
                for point in section_data["key_points"]:
                    md_content.append(f"- {point}")
                md_content.append("")

            # Add actions if available
            if "actions" in section_data:
                md_content.append("### Action Items:")
                for action in section_data["actions"]:
                    md_content.append(f"1. {action}")
                md_content.append("")

            # Add findings if available
            if "findings" in section_data:
                md_content.append("### Key Findings:")
                for finding in section_data["findings"]:
                    md_content.append(f"- {finding}")
                md_content.append("")

        return "\n".join(md_content)

    def _generate_pdf(self, content: Dict[str, Any], config: Dict[str, Any]) -> str:
        """Generate PDF format document (returns base64 encoded)"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=18,
            spaceAfter=30,
            alignment=1,  # Center alignment
        )
        story.append(Paragraph(content["title"], title_style))
        story.append(Spacer(1, 12))

        # Metadata
        story.append(Paragraph(f"<b>Author:</b> {content['author']}", styles["Normal"]))
        story.append(Paragraph(f"<b>Date:</b> {content['date']}", styles["Normal"]))
        story.append(Spacer(1, 20))

        # Sections
        for section_key, section_data in content["sections"].items():
            # Section title
            story.append(Paragraph(section_data["title"], styles["Heading2"]))
            story.append(Spacer(1, 12))

            # Section content
            story.append(Paragraph(section_data["content"], styles["Normal"]))
            story.append(Spacer(1, 12))

            # Add lists if available
            if "key_points" in section_data:
                for point in section_data["key_points"]:
                    story.append(Paragraph(f"• {point}", styles["Normal"]))
                story.append(Spacer(1, 12))

        doc.build(story)
        pdf_data = buffer.getvalue()
        buffer.close()

        return base64.b64encode(pdf_data).decode("utf-8")

    def _generate_html(self, content: Dict[str, Any], config: Dict[str, Any]) -> str:
        """Generate HTML format document"""
        html_content = []

        # HTML header
        html_content.append("<!DOCTYPE html>")
        html_content.append("<html><head>")
        html_content.append(f"<title>{content['title']}</title>")
        html_content.append("<style>")
        html_content.append("body { font-family: Arial, sans-serif; margin: 40px; }")
        html_content.append("h1 { color: #333; border-bottom: 2px solid #333; }")
        html_content.append("h2 { color: #666; margin-top: 30px; }")
        html_content.append(".metadata { color: #888; margin-bottom: 20px; }")
        html_content.append("</style>")
        html_content.append("</head><body>")

        # Title and metadata
        html_content.append(f"<h1>{content['title']}</h1>")
        html_content.append(f"<div class='metadata'>")
        html_content.append(f"<strong>Author:</strong> {content['author']}<br>")
        html_content.append(f"<strong>Date:</strong> {content['date']}")
        html_content.append("</div>")

        # Sections
        for section_key, section_data in content["sections"].items():
            html_content.append(f"<h2>{section_data['title']}</h2>")
            html_content.append(f"<p>{section_data['content']}</p>")

            if "key_points" in section_data:
                html_content.append("<ul>")
                for point in section_data["key_points"]:
                    html_content.append(f"<li>{point}</li>")
                html_content.append("</ul>")

        html_content.append("</body></html>")
        return "\n".join(html_content)

    def _generate_json(self, content: Dict[str, Any], config: Dict[str, Any]) -> str:
        """Generate JSON format document"""
        return json.dumps(content, indent=2, default=str)

    def _estimate_word_count(self, content: Dict[str, Any]) -> int:
        """Estimate word count in document"""
        total_words = 0
        for section_data in content["sections"].values():
            if "content" in section_data:
                total_words += len(section_data["content"].split())
        return total_words

    def create_data_visualization(
        self, data: Dict[str, Any], chart_type: str = "line"
    ) -> str:
        """Create data visualization and return base64 encoded image"""
        try:
            plt.figure(figsize=(10, 6))

            if chart_type == "line":
                x_data = data.get("x", list(range(len(data.get("y", [])))))
                y_data = data.get("y", [1, 2, 3, 4, 5])
                plt.plot(x_data, y_data, marker="o")
                plt.title(data.get("title", "Line Chart"))
                plt.xlabel(data.get("xlabel", "X Axis"))
                plt.ylabel(data.get("ylabel", "Y Axis"))

            elif chart_type == "bar":
                categories = data.get("categories", ["A", "B", "C", "D"])
                values = data.get("values", [10, 20, 15, 25])
                plt.bar(categories, values)
                plt.title(data.get("title", "Bar Chart"))
                plt.xlabel(data.get("xlabel", "Categories"))
                plt.ylabel(data.get("ylabel", "Values"))

            elif chart_type == "pie":
                labels = data.get("labels", ["A", "B", "C", "D"])
                sizes = data.get("sizes", [25, 35, 20, 20])
                plt.pie(sizes, labels=labels, autopct="%1.1f%%")
                plt.title(data.get("title", "Pie Chart"))

            # Save to buffer
            buffer = io.BytesIO()
            plt.savefig(buffer, format="png", dpi=300, bbox_inches="tight")
            buffer.seek(0)

            # Encode to base64
            image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
            buffer.close()
            plt.close()

            return image_base64

        except Exception as e:
            return f"Error creating visualization: {str(e)}"

    def get_available_templates(self) -> List[Dict[str, Any]]:
        """Get list of available document templates"""
        return [
            {
                "name": name,
                "type": template.type,
                "sections": template.sections,
                "description": f"{template.name} - {template.type} format",
            }
            for name, template in self.templates.items()
        ]


# Example usage and testing
if __name__ == "__main__":
    doc_gen = DocumentGenerator()

    # Test document generation
    sample_data = {
        "title": "XMRT DAO Monthly Report",
        "author": "Eliza AI Agent",
        "sections": {
            "executive_summary": {
                "content": "This month showed significant growth in DAO participation and development activity.",
                "key_points": [
                    "Repository commits increased by 40%",
                    "New contributors joined the project",
                    "Community engagement reached all-time high",
                ],
            },
            "metrics": {
                "content": "Key performance indicators demonstrate positive trends across all areas.",
                "data": {"commits": 150, "contributors": 12, "issues_closed": 25},
            },
        },
    }

    # Generate markdown document
    result = doc_gen.generate_document("dao_report", sample_data, "markdown")
    if result["success"]:
        print("Document generated successfully!")
        print(f"Word count: {result['metadata']['word_count']}")
        print("First 200 characters:")
        print(result["content"][:200] + "...")
    else:
        print(f"Error: {result['error']}")
