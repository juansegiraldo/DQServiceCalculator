"""
Results breakdown generator for DQ Service Calculator
"""
from typing import Dict, List, Any
import pandas as pd
from datetime import datetime
import json

from config.schema import DQCalculatorConfig


class BreakdownGenerator:
    """Generates detailed breakdowns and reports for calculation results"""

    def __init__(self, config: DQCalculatorConfig):
        """
        Initialize breakdown generator

        Args:
            config: DQ calculator configuration
        """
        self.config = config

    def generate_breakdown_dataframe(self, breakdown: Dict[str, float], total_days: int) -> pd.DataFrame:
        """
        Generate a pandas DataFrame for the cost breakdown

        Args:
            breakdown: Calculation breakdown dictionary
            total_days: Total calculated days

        Returns:
            DataFrame with component breakdown
        """
        breakdown_data = []
        for component, days in breakdown.items():
            if days > 0:
                breakdown_data.append({
                    "Component": component,
                    "Days": int(days),
                    "Percentage": f"{(days/total_days)*100:.1f}%",
                    "Raw_Days": days,
                    "Raw_Percentage": (days/total_days)*100
                })

        return pd.DataFrame(breakdown_data)

    def generate_export_data(self, responses: Dict[str, Any], total_days: int,
                           breakdown: Dict[str, float]) -> Dict[str, Any]:
        """
        Generate complete export data structure

        Args:
            responses: User responses
            total_days: Total calculated days
            breakdown: Calculation breakdown

        Returns:
            Dictionary with all export data
        """
        export_data = {
            "metadata": {
                "generated_date": datetime.now().strftime(self.config.export_config.timestamp_format),
                "calculator_version": "2.0",
                "configuration_file": "default_config.yaml"
            },
            "project_details": self._clean_responses_for_export(responses),
            "results": {
                "total_days": total_days,
                "breakdown": {k: round(v, 1) for k, v in breakdown.items() if v > 0}
            },
            "calculation_rules": {
                "base_service_days": self.config.calculation_rules.base_service_days,
                "minimum_project_days": self.config.calculation_rules.minimum_project_days
            }
        }

        if self.config.export_config.include_metadata:
            export_data["questions_config"] = self._generate_questions_metadata()

        return export_data

    def _clean_responses_for_export(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and format responses for export"""
        cleaned = {}
        for question_id, value in responses.items():
            if question_id in self.config.questions:
                question_config = self.config.questions[question_id]
                cleaned[question_id] = {
                    "question": question_config.label,
                    "value": value,
                    "section": question_config.section
                }
            else:
                # Handle legacy question IDs
                cleaned[question_id] = {
                    "question": question_id.replace('_', ' ').title(),
                    "value": value,
                    "section": "Legacy"
                }
        return cleaned

    def _generate_questions_metadata(self) -> Dict[str, Any]:
        """Generate metadata about questions for export"""
        metadata = {}
        for question_id, question_config in self.config.questions.items():
            metadata[question_id] = {
                "label": question_config.label,
                "type": question_config.type,
                "section": question_config.section,
                "complexity_level": question_config.complexity_level,
                "optional": question_config.optional
            }
        return metadata

    def generate_summary_report(self, responses: Dict[str, Any], total_days: int,
                              breakdown: Dict[str, float], price_per_day: float = 0) -> str:
        """
        Generate a human-readable summary report

        Args:
            responses: User responses
            total_days: Total calculated days
            breakdown: Calculation breakdown
            price_per_day: Daily rate for cost calculation

        Returns:
            Formatted summary report
        """
        report = []
        report.append("=" * 60)
        report.append("DATA QUALITY SERVICE ESTIMATION REPORT")
        report.append("=" * 60)
        report.append("")

        # Project overview
        report.append("PROJECT OVERVIEW")
        report.append("-" * 20)
        tables_count = responses.get('tables_count', responses.get('num_workflows', 1))
        report.append(f"Tables/Workflows: {tables_count}")

        if 'workflow_complexity' in responses:
            report.append(f"Complexity: {responses['workflow_complexity']}")

        if 'data_sources' in responses or 'integration_complexity' in responses:
            integration = responses.get('data_sources', responses.get('integration_complexity', ''))
            report.append(f"Integration: {integration}")

        report.append("")

        # Results summary
        report.append("ESTIMATION RESULTS")
        report.append("-" * 20)
        report.append(f"Total Working Days: {total_days}")

        if price_per_day > 0:
            total_cost = total_days * price_per_day
            report.append(f"Total Cost: €{total_cost:,.2f}")

        report.append("")

        # Breakdown
        report.append("COST BREAKDOWN")
        report.append("-" * 20)
        for component, days in breakdown.items():
            if days > 0:
                percentage = (days/total_days)*100
                report.append(f"{component}: {days:.1f} days ({percentage:.1f}%)")

        report.append("")

        # Methodology phases
        report.append("STRATESYS DQ METHODOLOGY")
        report.append("-" * 30)
        for phase_id, phase_config in self.config.methodology_phases.items():
            report.append(f"{phase_config.title}:")
            # Clean up description formatting
            description_lines = phase_config.description.strip().split('\n')
            for line in description_lines:
                if line.strip():
                    report.append(f"  {line.strip()}")
            report.append("")

        # Footer
        report.append("=" * 60)
        report.append("Generated by Stratesys DQ Service Calculator")
        report.append(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)

        return "\n".join(report)

    def generate_csv_breakdown(self, breakdown: Dict[str, float], total_days: int) -> str:
        """
        Generate CSV format breakdown

        Args:
            breakdown: Calculation breakdown
            total_days: Total calculated days

        Returns:
            CSV formatted string
        """
        df = self.generate_breakdown_dataframe(breakdown, total_days)
        return df.to_csv(index=False)

    def generate_json_export(self, responses: Dict[str, Any], total_days: int,
                           breakdown: Dict[str, float]) -> str:
        """
        Generate JSON format export

        Args:
            responses: User responses
            total_days: Total calculated days
            breakdown: Calculation breakdown

        Returns:
            JSON formatted string
        """
        export_data = self.generate_export_data(responses, total_days, breakdown)
        return json.dumps(export_data, indent=2, ensure_ascii=False)

    def get_phase_descriptions(self) -> Dict[str, str]:
        """Get methodology phase descriptions for UI display"""
        phases = {}
        for phase_id, phase_config in self.config.methodology_phases.items():
            phases[phase_id] = {
                "title": phase_config.title,
                "description": phase_config.description
            }
        return phases

    def calculate_project_timeline(self, total_days: int, team_size: int = 1) -> Dict[str, Any]:
        """
        Calculate project timeline based on days and team size

        Args:
            total_days: Total working days
            team_size: Number of team members

        Returns:
            Timeline information
        """
        working_days_per_week = 5
        weeks = total_days / working_days_per_week

        if team_size > 1:
            parallel_weeks = weeks / team_size
            timeline = {
                "sequential_weeks": round(weeks, 1),
                "parallel_weeks": round(parallel_weeks, 1),
                "team_size": team_size,
                "total_person_days": total_days
            }
        else:
            timeline = {
                "weeks": round(weeks, 1),
                "team_size": 1,
                "total_person_days": total_days
            }

        return timeline