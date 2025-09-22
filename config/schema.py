"""
Configuration schema definitions for DQ Service Calculator
"""
from typing import Dict, List, Union, Optional, Any
from dataclasses import dataclass
from enum import Enum


class QuestionType(Enum):
    """Supported question types"""
    NUMBER_INPUT = "number_input"
    SELECTBOX = "selectbox"
    RADIO = "radio"
    CHECKBOX = "checkbox"


class ComplexityLevel(Enum):
    """User complexity levels"""
    BASIC = "basic"
    ADVANCED = "advanced"


@dataclass
class QuestionConfig:
    """Configuration for a single question"""
    label: str
    type: str
    tooltip: str
    section: str
    complexity_level: str
    options: Optional[List[str]] = None
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    default: Optional[Union[str, int, bool]] = None
    optional: bool = False
    depends_on: Optional[str] = None
    depends_value: Optional[str] = None


@dataclass
class CalculationRules:
    """Configuration for calculation rules"""
    base_service_days: int
    minimum_project_days: int
    workflow_multipliers: Dict[str, float]
    integration_complexity: Dict[str, float]
    integration_complexity_legacy: Dict[str, float]
    data_volume_multipliers: Dict[str, float]
    rules_overhead: Dict[str, Union[int, float]]
    existing_rules_impact: Dict[str, float]
    tool_setup: Dict[str, float]
    datawash_installation: Dict[str, float]
    cloud_integration: Dict[str, float]
    additional_requirements: Dict[str, float]


@dataclass
class UISection:
    """Configuration for UI sections"""
    name: str
    icon: str
    description: str


@dataclass
class MethodologyPhase:
    """Configuration for methodology phases"""
    title: str
    description: str


@dataclass
class AppConfig:
    """Main application configuration"""
    title: str
    subtitle: str
    description: str
    page_icon: str
    layout: str


@dataclass
class ComplexityLevelConfig:
    """Configuration for complexity levels"""
    label: str
    description: str
    show_questions: Union[List[str], str]


@dataclass
class PricingConfig:
    """Configuration for pricing functionality"""
    default_price_per_day: float
    currency: str
    currency_symbol: str
    allow_admin_override: bool
    min_price_override: float
    max_price_override: float

@dataclass
class ExportConfig:
    """Configuration for export functionality"""
    formats: List[str]
    include_metadata: bool
    timestamp_format: str

@dataclass
class SecurityConfig:
    """Configuration for security features"""
    breakdown_password: str
    password_required: bool


@dataclass
class DQCalculatorConfig:
    """Complete configuration for DQ Calculator"""
    app_config: AppConfig
    complexity_levels: Dict[str, ComplexityLevelConfig]
    questions: Dict[str, QuestionConfig]
    calculation_rules: CalculationRules
    pricing_config: PricingConfig
    security_config: SecurityConfig
    export_config: ExportConfig
    ui_sections: List[UISection]
    methodology_phases: Dict[str, MethodologyPhase]


def validate_question_config(question_id: str, config: QuestionConfig) -> List[str]:
    """Validate a single question configuration"""
    errors = []

    # Validate question type
    try:
        QuestionType(config.type)
    except ValueError:
        errors.append(f"Question '{question_id}': Invalid question type '{config.type}'")

    # Validate complexity level
    try:
        ComplexityLevel(config.complexity_level)
    except ValueError:
        errors.append(f"Question '{question_id}': Invalid complexity level '{config.complexity_level}'")

    # Type-specific validations
    if config.type == QuestionType.NUMBER_INPUT.value:
        if config.min_value is None or config.max_value is None:
            errors.append(f"Question '{question_id}': Number input requires min_value and max_value")
        elif config.min_value >= config.max_value:
            errors.append(f"Question '{question_id}': min_value must be less than max_value")

    if config.type in [QuestionType.SELECTBOX.value, QuestionType.RADIO.value]:
        if not config.options or len(config.options) < 2:
            errors.append(f"Question '{question_id}': {config.type} requires at least 2 options")

    # Dependency validation
    if config.depends_on and not config.depends_value:
        errors.append(f"Question '{question_id}': depends_on requires depends_value")

    return errors


def validate_calculation_rules(rules: CalculationRules) -> List[str]:
    """Validate calculation rules"""
    errors = []

    if rules.base_service_days <= 0:
        errors.append("base_service_days must be positive")

    if rules.minimum_project_days <= 0:
        errors.append("minimum_project_days must be positive")

    if rules.base_service_days < rules.minimum_project_days:
        errors.append("base_service_days should be >= minimum_project_days")

    # Validate multipliers are non-negative
    for multiplier_dict in [
        rules.workflow_multipliers,
        rules.integration_complexity,
        rules.data_volume_multipliers,
        rules.existing_rules_impact,
        rules.tool_setup,
        rules.cloud_integration,
        rules.additional_requirements
    ]:
        for key, value in multiplier_dict.items():
            if value < 0:
                errors.append(f"Negative multiplier not allowed: {key} = {value}")

    return errors


def validate_config(config: DQCalculatorConfig) -> List[str]:
    """Validate the complete configuration"""
    errors = []

    # Validate questions
    for question_id, question_config in config.questions.items():
        errors.extend(validate_question_config(question_id, question_config))

    # Validate calculation rules
    errors.extend(validate_calculation_rules(config.calculation_rules))

    # Validate sections exist for all questions
    defined_sections = {section.name for section in config.ui_sections}
    question_sections = {q.section for q in config.questions.values()}
    missing_sections = question_sections - defined_sections
    if missing_sections:
        errors.extend([f"Missing UI section definition: {section}" for section in missing_sections])

    # Validate complexity levels
    for level_id, level_config in config.complexity_levels.items():
        if level_config.show_questions != "all":
            undefined_questions = set(level_config.show_questions) - set(config.questions.keys())
            if undefined_questions:
                errors.extend([
                    f"Complexity level '{level_id}' references undefined questions: {list(undefined_questions)}"
                ])

    # Validate dependencies
    for question_id, question_config in config.questions.items():
        if question_config.depends_on:
            if question_config.depends_on not in config.questions:
                errors.append(f"Question '{question_id}' depends on undefined question '{question_config.depends_on}'")
            else:
                dep_question = config.questions[question_config.depends_on]
                if question_config.depends_value not in (dep_question.options or []):
                    errors.append(
                        f"Question '{question_id}' depends on value '{question_config.depends_value}' "
                        f"not in options for '{question_config.depends_on}'"
                    )

    return errors