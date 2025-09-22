"""
Calculation engine for DQ Service Calculator
"""
from typing import Dict, Any, Tuple, List
import math

from config.schema import DQCalculatorConfig, CalculationRules


class CalculationEngine:
    """Handles all calculation logic for DQ service estimation"""

    def __init__(self, config: DQCalculatorConfig):
        """
        Initialize calculation engine with configuration

        Args:
            config: Complete DQ calculator configuration
        """
        self.config = config
        self.rules = config.calculation_rules

    def calculate_working_days(self, responses: Dict[str, Any]) -> Tuple[int, Dict[str, float]]:
        """
        Calculate estimated working days based on user responses

        Args:
            responses: Dictionary of user responses to questions

        Returns:
            Tuple of (total_days, breakdown_dict)
        """
        breakdown = {}

        # Base service days (always included)
        base_days = self.rules.base_service_days
        breakdown['Base Service (Phases 0-3)'] = base_days

        # Calculate workflow complexity
        workflow_days = self._calculate_workflow_complexity(responses)
        if workflow_days > 0:
            breakdown['Workflow Complexity'] = workflow_days

        # Calculate data integration complexity
        integration_days = self._calculate_integration_complexity(responses)
        if integration_days > 0:
            breakdown['Data Integration'] = integration_days

        # Calculate DQ rules development
        rules_days = self._calculate_rules_development(responses)
        if rules_days > 0:
            breakdown['DQ Rules Development'] = rules_days

        # Calculate data volume impact
        volume_days = self._calculate_data_volume_impact(responses)
        if volume_days > 0:
            breakdown['Data Volume Impact'] = volume_days

        # Calculate tool setup requirements
        tool_days = self._calculate_tool_setup(responses)
        if tool_days > 0:
            breakdown['Tool Setup'] = tool_days

        # Calculate cloud integration
        cloud_days = self._calculate_cloud_integration(responses)
        if cloud_days > 0:
            breakdown['Cloud Integration'] = cloud_days

        # Calculate additional requirements
        additional_days = self._calculate_additional_requirements(responses)
        if additional_days > 0:
            breakdown['Additional Requirements'] = additional_days

        # Calculate total
        total_days = sum(breakdown.values())
        total_days = max(int(total_days), self.rules.minimum_project_days)

        return total_days, breakdown

    def _calculate_workflow_complexity(self, responses: Dict[str, Any]) -> float:
        """Calculate days based on workflow complexity"""
        tables_count = responses.get('tables_count', responses.get('num_workflows', 1))
        workflow_complexity = responses.get('workflow_complexity', 'Simple (single table/report)')

        multiplier = self.rules.workflow_multipliers.get(workflow_complexity, 2.0)
        return tables_count * multiplier

    def _calculate_integration_complexity(self, responses: Dict[str, Any]) -> float:
        """Calculate days based on data integration complexity"""
        tables_count = responses.get('tables_count', responses.get('num_workflows', 1))

        # Try new format first, then fall back to legacy format
        integration_complexity = responses.get('data_sources', responses.get('integration_complexity', ''))

        # Map new format to calculation values
        if integration_complexity in self.rules.integration_complexity:
            base_multiplier = self.rules.integration_complexity[integration_complexity]
        elif integration_complexity in self.rules.integration_complexity_legacy:
            base_multiplier = self.rules.integration_complexity_legacy[integration_complexity]
        else:
            base_multiplier = 0.0

        return tables_count * base_multiplier

    def _calculate_rules_development(self, responses: Dict[str, Any]) -> float:
        """Calculate days for DQ rules development"""
        existing_rules = responses.get('existing_rules', responses.get('dq_rules_status', 'Not documented'))

        base_rules_impact = self.rules.existing_rules_impact.get(existing_rules, 5.0)

        # Calculate rules overhead if rules_count is provided
        rules_overhead = 0.0
        if 'rules_count' in responses:
            tables_count = responses.get('tables_count', responses.get('num_workflows', 1))
            total_rules = responses['rules_count'] * tables_count
            base_included = self.rules.rules_overhead.get('base_rules_included', 20)

            if total_rules > base_included:
                extra_rules = total_rules - base_included
                extra_rule_groups = math.ceil(extra_rules / 5)  # Groups of 5 additional rules
                rules_overhead = extra_rule_groups * self.rules.rules_overhead.get('additional_rules_per_5', 0.5)

        return base_rules_impact + rules_overhead

    def _calculate_data_volume_impact(self, responses: Dict[str, Any]) -> float:
        """Calculate days based on data volume"""
        if 'data_volume' not in responses:
            return 0.0

        tables_count = responses.get('tables_count', responses.get('num_workflows', 1))
        data_volume = responses['data_volume']

        multiplier = self.rules.data_volume_multipliers.get(data_volume, 0.0)
        return tables_count * multiplier

    def _calculate_tool_setup(self, responses: Dict[str, Any]) -> float:
        """Calculate days for tool setup"""
        tool_setup_days = 0.0

        # Commercial DQ tool
        commercial_tool = responses.get('commercial_tool', responses.get('dq_tool_status', 'No commercial tool'))
        if commercial_tool in self.rules.tool_setup:
            tool_setup_days += self.rules.tool_setup[commercial_tool]
        elif commercial_tool in ['Have existing DQ tool', 'Need other tool']:
            # Legacy mapping
            if 'existing' in commercial_tool.lower():
                tool_setup_days += self.rules.tool_setup.get('Have existing DQ tool', 2.0)
            else:
                tool_setup_days += self.rules.tool_setup.get('Need tool acquisition', 3.0)

        # DataWash installation
        datawash_installation = responses.get('datawash_installation', 'No, not needed')
        datawash_days = self.rules.datawash_installation.get(datawash_installation, 0.0)
        tool_setup_days += datawash_days

        return tool_setup_days

    def _calculate_cloud_integration(self, responses: Dict[str, Any]) -> float:
        """Calculate days for cloud platform integration"""
        cloud_platform = responses.get('cloud_platform', 'Not applicable')
        return self.rules.cloud_integration.get(cloud_platform, 0.0)

    def _calculate_additional_requirements(self, responses: Dict[str, Any]) -> float:
        """Calculate days for additional requirements"""
        additional_days = 0.0

        # Governance maturity
        if not responses.get('governance_maturity', False):
            additional_days += self.rules.additional_requirements.get('governance_setup', 3.0)

        # Compliance requirements
        if responses.get('compliance_req', False):
            additional_days += self.rules.additional_requirements.get('compliance', 2.0)

        # Historical analysis
        if responses.get('historical_analysis', False):
            tables_count = responses.get('tables_count', responses.get('num_workflows', 1))
            per_workflow = self.rules.additional_requirements.get('historical_analysis_per_workflow', 2.0)
            additional_days += tables_count * per_workflow

        # System integration
        if responses.get('system_integration', False):
            additional_days += self.rules.additional_requirements.get('system_integration', 3.0)

        return additional_days

    def get_calculation_explanation(self, responses: Dict[str, Any], breakdown: Dict[str, float]) -> str:
        """
        Generate detailed explanation of how the calculation was performed

        Args:
            responses: User responses
            breakdown: Calculation breakdown

        Returns:
            Detailed explanation string
        """
        explanation = "**Calculation Breakdown:**\n\n"

        tables_count = responses.get('tables_count', responses.get('num_workflows', 1))
        explanation += f"📊 **Project Scope:** {tables_count} table(s)/workflow(s)\n\n"

        for component, days in breakdown.items():
            if days > 0:
                explanation += f"• **{component}:** {days:.1f} days\n"

                # Add specific explanations for each component
                if component == 'Base Service (Phases 0-3)':
                    explanation += "  - Core DQ methodology implementation\n"
                elif component == 'Workflow Complexity':
                    complexity = responses.get('workflow_complexity', 'Simple (single table/report)')
                    explanation += f"  - {complexity}: {tables_count} × {days/tables_count:.1f} days each\n"
                elif component == 'Data Integration':
                    integration = responses.get('data_sources', responses.get('integration_complexity', ''))
                    explanation += f"  - {integration}\n"
                elif component == 'DQ Rules Development':
                    rules_status = responses.get('existing_rules', responses.get('dq_rules_status', ''))
                    explanation += f"  - Rules status: {rules_status}\n"
                elif component == 'Tool Setup' and 'datawash_installation' in responses:
                    if responses['datawash_installation'] == 'Yes, please provide installation':
                        explanation += "  - Includes DataWash installation (~10 days)\n"

                explanation += "\n"

        total_days = sum(breakdown.values())
        explanation += f"**Total Estimated Days:** {int(total_days)} days\n"
        explanation += f"**Minimum Project Threshold:** {self.rules.minimum_project_days} days\n"

        return explanation

    def validate_responses(self, responses: Dict[str, Any], required_only: List[str] = None, complexity_level: str = "advanced") -> Dict[str, str]:
        """
        Validate user responses against configuration

        Args:
            responses: User responses to validate
            required_only: List of required question IDs. If None, validates all non-optional fields.
            complexity_level: Complexity level to determine which fields to validate

        Returns:
            Dictionary of validation errors (empty if valid)
        """
        errors = {}

        # If required_only is specified, only validate those fields
        if required_only:
            questions_to_validate = {qid: self.config.questions[qid]
                                   for qid in required_only
                                   if qid in self.config.questions}
        else:
            # Only validate questions that are shown for this complexity level
            from config.loader import get_config_loader
            config_loader = get_config_loader()
            shown_questions = config_loader.get_questions_for_complexity(complexity_level)
            questions_to_validate = {qid: self.config.questions[qid]
                                   for qid in shown_questions
                                   if qid in self.config.questions}

        for question_id, question_config in questions_to_validate.items():
            if question_id in responses:
                value = responses[question_id]

                # Type validations
                if question_config.type == "number_input":
                    if not isinstance(value, (int, float)) or value < 0:
                        errors[question_id] = "Must be a positive number"
                    elif (question_config.min_value is not None and
                          value < question_config.min_value):
                        errors[question_id] = f"Must be at least {question_config.min_value}"
                    elif (question_config.max_value is not None and
                          value > question_config.max_value):
                        errors[question_id] = f"Must be at most {question_config.max_value}"

                elif question_config.type in ["selectbox", "radio"]:
                    if question_config.options and value not in question_config.options:
                        errors[question_id] = f"Must be one of: {', '.join(question_config.options)}"

            elif not question_config.optional and (required_only is None or question_id in required_only):
                errors[question_id] = "This field is required"

        return errors

    def validate_quick_responses(self, responses: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate responses for quick estimate mode with minimal requirements

        Args:
            responses: User responses to validate

        Returns:
            Dictionary of validation errors (empty if valid)
        """
        # Only validate essential fields for quick estimate
        required_fields = ['tables_count', 'workflow_complexity', 'data_sources', 'existing_rules']
        return self.validate_responses(responses, required_fields)