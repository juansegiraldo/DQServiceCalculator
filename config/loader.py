"""
Configuration loader with validation for DQ Service Calculator
"""
import yaml
import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path

from .schema import (
    DQCalculatorConfig, AppConfig, ComplexityLevelConfig, QuestionConfig,
    CalculationRules, PricingConfig, SecurityConfig, ExportConfig, ReportConfig, CompanyInfo,
    UISection, MethodologyPhase, QuickEstimateConfig, QuickEstimateDefaults,
    validate_config
)


class ConfigurationError(Exception):
    """Raised when configuration is invalid"""
    pass


class ConfigLoader:
    """Loads and validates DQ Calculator configuration"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize config loader

        Args:
            config_path: Path to configuration file. If None, uses default config.
        """
        self.config_path = config_path or self._get_default_config_path()
        self._config: Optional[DQCalculatorConfig] = None

    def _get_default_config_path(self) -> str:
        """Get path to default configuration file"""
        current_dir = Path(__file__).parent
        return str(current_dir / "default_config.yaml")

    def load_config(self, reload: bool = False) -> DQCalculatorConfig:
        """
        Load configuration from file with validation

        Args:
            reload: Force reload even if config is cached

        Returns:
            Validated configuration object

        Raises:
            ConfigurationError: If configuration is invalid or file cannot be loaded
        """
        if self._config is not None and not reload:
            return self._config

        try:
            config_data = self._load_config_file()
            self._config = self._parse_config(config_data)
            self._validate_config()
            return self._config
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {str(e)}") from e

    def _load_config_file(self) -> Dict[str, Any]:
        """Load configuration file (YAML or JSON)"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        file_ext = Path(self.config_path).suffix.lower()

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                if file_ext in ['.yml', '.yaml']:
                    return yaml.safe_load(f)
                elif file_ext == '.json':
                    return json.load(f)
                else:
                    raise ValueError(f"Unsupported configuration file format: {file_ext}")
        except (yaml.YAMLError, json.JSONDecodeError) as e:
            raise ValueError(f"Invalid configuration file format: {str(e)}") from e

    def _parse_config(self, config_data: Dict[str, Any]) -> DQCalculatorConfig:
        """Parse configuration data into structured objects"""

        # Parse app config
        app_config_data = config_data.get('app_config', {})
        app_config = AppConfig(
            title=app_config_data.get('title', 'DQ Service Calculator'),
            subtitle=app_config_data.get('subtitle', 'Stratesys Technology Solutions'),
            description=app_config_data.get('description', ''),
            page_icon=app_config_data.get('page_icon', '📊'),
            layout=app_config_data.get('layout', 'wide'),
            sidebar_title=app_config_data.get('sidebar_title', '🔧 Options')
        )

        # Parse complexity levels
        complexity_levels = {}
        for level_id, level_data in config_data.get('complexity_levels', {}).items():
            complexity_levels[level_id] = ComplexityLevelConfig(
                title=level_data.get('title', level_data.get('label', '')),
                label=level_data.get('label', ''),
                description=level_data.get('description', ''),
                show_questions=level_data.get('show_questions', [])
            )

        # Parse quick estimate config
        quick_estimate_data = config_data.get('quick_estimate_config', {})
        defaults_data = quick_estimate_data.get('defaults', {})
        
        quick_estimate_config = QuickEstimateConfig(
            title=quick_estimate_data.get('title', '⚡ Quick Estimate Mode'),
            core_questions=quick_estimate_data.get('core_questions', ['tables_count']),
            defaults=QuickEstimateDefaults(
                workflow_complexity=defaults_data.get('workflow_complexity', 'Simple (single table/report)'),
                data_sources=defaults_data.get('data_sources', 'Single location (same database/schema)'),
                existing_rules=defaults_data.get('existing_rules', 'Not documented'),
                commercial_tool=defaults_data.get('commercial_tool', 'No commercial tool'),
                data_volume=defaults_data.get('data_volume', 'Small (<1M records)'),
                datawash_installation=defaults_data.get('datawash_installation', 'No, not needed'),
                compliance_req=defaults_data.get('compliance_req', False),
                historical_analysis=defaults_data.get('historical_analysis', False),
                system_integration=defaults_data.get('system_integration', False),
                governance_maturity=defaults_data.get('governance_maturity', False),
                rules_count=defaults_data.get('rules_count', 15),
                cloud_platform=defaults_data.get('cloud_platform', 'Not applicable')
            )
        )

        # Parse questions
        questions = {}
        for question_id, question_data in config_data.get('questions', {}).items():
            questions[question_id] = QuestionConfig(
                label=question_data.get('label', ''),
                type=question_data.get('type', 'text'),
                tooltip=question_data.get('tooltip', ''),
                section=question_data.get('section', 'General'),
                complexity_level=question_data.get('complexity_level', 'basic'),
                options=question_data.get('options'),
                min_value=question_data.get('min_value'),
                max_value=question_data.get('max_value'),
                default=question_data.get('default'),
                optional=question_data.get('optional', False),
                depends_on=question_data.get('depends_on'),
                depends_value=question_data.get('depends_value')
            )

        # Parse calculation rules
        calc_rules_data = config_data.get('calculation_rules', {})
        calculation_rules = CalculationRules(
            base_service_days=calc_rules_data.get('base_service_days', 9),
            additional_service_days=calc_rules_data.get('additional_service_days', 5),
            minimum_project_days=calc_rules_data.get('minimum_project_days', 5),
            workflow_multipliers=calc_rules_data.get('workflow_multipliers', {}),
            integration_complexity=calc_rules_data.get('integration_complexity', {}),
            integration_complexity_legacy=calc_rules_data.get('integration_complexity_legacy', {}),
            data_volume_multipliers=calc_rules_data.get('data_volume_multipliers', {}),
            rules_overhead=calc_rules_data.get('rules_overhead', {}),
            existing_rules_impact=calc_rules_data.get('existing_rules_impact', {}),
            tool_setup=calc_rules_data.get('tool_setup', {}),
            datawash_installation=calc_rules_data.get('datawash_installation', {}),
            cloud_integration=calc_rules_data.get('cloud_integration', {}),
            additional_requirements=calc_rules_data.get('additional_requirements', {})
        )

        # Parse pricing config
        pricing_config_data = config_data.get('pricing_config', {})
        pricing_config = PricingConfig(
            default_price_per_day=pricing_config_data.get('default_price_per_day', 700.0),
            currency=pricing_config_data.get('currency', 'EUR'),
            currency_symbol=pricing_config_data.get('currency_symbol', '€'),
            allow_admin_override=pricing_config_data.get('allow_admin_override', True),
            min_price_override=pricing_config_data.get('min_price_override', 500.0),
            max_price_override=pricing_config_data.get('max_price_override', 5000.0)
        )

        # Parse security config
        security_config_data = config_data.get('security_config', {})
        security_config = SecurityConfig(
            breakdown_password=security_config_data.get('breakdown_password', 'stratesys2024'),
            password_required=security_config_data.get('password_required', True)
        )

        # Parse export config
        export_config_data = config_data.get('export_config', {})
        export_config = ExportConfig(
            formats=export_config_data.get('formats', ['json']),
            include_metadata=export_config_data.get('include_metadata', True),
            timestamp_format=export_config_data.get('timestamp_format', '%Y-%m-%d %H:%M:%S')
        )

        # Parse report config
        report_config_data = config_data.get('report_config', {})
        company_info_data = report_config_data.get('company_info', {})
        company_info = CompanyInfo(
            name=company_info_data.get('name', 'Stratesys Technology Solutions'),
            logo_url=company_info_data.get('logo_url', ''),
            contact_email=company_info_data.get('contact_email', 'info@stratesys.com')
        )
        report_config = ReportConfig(
            include_executive_summary=report_config_data.get('include_executive_summary', True),
            include_calculation_explanation=report_config_data.get('include_calculation_explanation', True),
            include_methodology=report_config_data.get('include_methodology', True),
            include_risk_assessment=report_config_data.get('include_risk_assessment', True),
            include_company_branding=report_config_data.get('include_company_branding', True),
            default_language=report_config_data.get('default_language', 'es'),
            company_info=company_info
        )

        # Parse UI sections
        ui_sections = []
        for section_data in config_data.get('ui_sections', []):
            ui_sections.append(UISection(
                name=section_data.get('name', ''),
                icon=section_data.get('icon', ''),
                description=section_data.get('description', '')
            ))

        # Parse methodology phases
        methodology_phases = {}
        for phase_id, phase_data in config_data.get('methodology_phases', {}).items():
            methodology_phases[phase_id] = MethodologyPhase(
                title=phase_data.get('title', ''),
                description=phase_data.get('description', '')
            )

        return DQCalculatorConfig(
            app_config=app_config,
            complexity_levels=complexity_levels,
            quick_estimate_config=quick_estimate_config,
            questions=questions,
            calculation_rules=calculation_rules,
            pricing_config=pricing_config,
            security_config=security_config,
            export_config=export_config,
            report_config=report_config,
            ui_sections=ui_sections,
            methodology_phases=methodology_phases
        )

    def _validate_config(self) -> None:
        """Validate the loaded configuration"""
        if self._config is None:
            raise ConfigurationError("No configuration loaded")

        errors = validate_config(self._config)
        if errors:
            error_msg = "Configuration validation errors:\n" + "\n".join(f"- {error}" for error in errors)
            raise ConfigurationError(error_msg)

    def get_questions_for_complexity(self, complexity_level: str) -> List[str]:
        """Get list of question IDs for a specific complexity level"""
        if self._config is None:
            raise ConfigurationError("Configuration not loaded")

        if complexity_level not in self._config.complexity_levels:
            raise ValueError(f"Unknown complexity level: {complexity_level}")

        level_config = self._config.complexity_levels[complexity_level]
        if level_config.show_questions == "all":
            return list(self._config.questions.keys())
        else:
            return level_config.show_questions

    def get_questions_by_section(self, complexity_level: str = "advanced") -> Dict[str, List[str]]:
        """Get questions grouped by section for a specific complexity level"""
        if self._config is None:
            raise ConfigurationError("Configuration not loaded")

        allowed_questions = set(self.get_questions_for_complexity(complexity_level))
        sections = {}

        for question_id, question_config in self._config.questions.items():
            if question_id in allowed_questions:
                section = question_config.section
                if section not in sections:
                    sections[section] = []
                sections[section].append(question_id)

        return sections

    def should_show_question(self, question_id: str, responses: Dict[str, Any]) -> bool:
        """Check if a question should be shown based on dependencies"""
        if self._config is None:
            raise ConfigurationError("Configuration not loaded")

        if question_id not in self._config.questions:
            return False

        question_config = self._config.questions[question_id]

        # Check dependency
        if question_config.depends_on:
            if question_config.depends_on not in responses:
                return False
            if responses[question_config.depends_on] != question_config.depends_value:
                return False

        return True

    def export_config(self, output_path: str, format: str = "yaml") -> None:
        """Export current configuration to file"""
        if self._config is None:
            raise ConfigurationError("Configuration not loaded")

        # Convert config back to dict for export
        # This is a simplified implementation - you might want to add more complete serialization
        config_dict = {
            "app_config": {
                "title": self._config.app_config.title,
                "subtitle": self._config.app_config.subtitle,
                "description": self._config.app_config.description,
                "page_icon": self._config.app_config.page_icon,
                "layout": self._config.app_config.layout
            }
            # Add other sections as needed
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            if format.lower() in ['yml', 'yaml']:
                yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
            else:
                json.dump(config_dict, f, indent=2)


# Global config loader instance
_config_loader: Optional[ConfigLoader] = None


def get_config_loader(config_path: Optional[str] = None) -> ConfigLoader:
    """Get global config loader instance"""
    global _config_loader
    if _config_loader is None or config_path is not None:
        _config_loader = ConfigLoader(config_path)
    return _config_loader


def load_config(config_path: Optional[str] = None, reload: bool = False) -> DQCalculatorConfig:
    """Convenience function to load configuration"""
    loader = get_config_loader(config_path)
    return loader.load_config(reload)