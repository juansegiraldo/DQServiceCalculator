"""
DQ Service Calculator - Streamlit Application
Modern, configurable implementation with dynamic UI generation
"""
import streamlit as st
import sys
import os
from pathlib import Path

# Add current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from config.loader import load_config, ConfigurationError
    from config.schema import DQCalculatorConfig
    from calculator.engine import CalculationEngine
    from calculator.breakdown import BreakdownGenerator
    from ui.generator import UIGenerator
    from ui.components import CustomComponents
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please ensure all required files are in the correct directory structure")
    st.stop()


class DQServiceCalculatorApp:
    """Main application class for the DQ Service Calculator"""

    def __init__(self):
        """Initialize the application"""
        self.config = None
        self.config_loader = None
        self.calculation_engine = None
        self.breakdown_generator = None
        self.ui_generator = None
        self.custom_components = CustomComponents()

        # Initialize session state
        self._init_session_state()

    def _init_session_state(self):
        """Initialize Streamlit session state"""
        if 'calculated' not in st.session_state:
            st.session_state.calculated = False
        if 'complexity_level' not in st.session_state:
            st.session_state.complexity_level = 'advanced'
        if 'responses' not in st.session_state:
            st.session_state.responses = {}
        if 'total_days' not in st.session_state:
            st.session_state.total_days = 0
        if 'breakdown' not in st.session_state:
            st.session_state.breakdown = {}

    def load_configuration(self, reload: bool = False) -> bool:
        """
        Load application configuration

        Args:
            reload: Force reload of configuration from file

        Returns:
            True if successful, False otherwise
        """
        try:
            from config.loader import get_config_loader
            self.config_loader = get_config_loader()
            self.config = self.config_loader.load_config(reload=reload)

            # Initialize components with configuration
            self.calculation_engine = CalculationEngine(self.config)
            self.breakdown_generator = BreakdownGenerator(self.config)
            self.ui_generator = UIGenerator(self.config, self.config_loader)

            # Always update price_per_day from configuration
            st.session_state.price_per_day = self.config.pricing_config.default_price_per_day

            return True

        except ConfigurationError as e:
            st.error(f"Configuration Error: {e}")
            return False
        except Exception as e:
            st.error(f"Unexpected error loading configuration: {e}")
            return False

    def setup_page(self):
        """Setup Streamlit page configuration"""
        st.set_page_config(
            page_title=f"{self.config.app_config.title} - {self.config.app_config.subtitle}",
            page_icon=self.config.app_config.page_icon,
            layout=self.config.app_config.layout
        )

    def render_header(self):
        """Render application header"""
        st.title(f"{self.config.app_config.page_icon} {self.config.app_config.title}")
        st.markdown(f"**{self.config.app_config.subtitle}**")
        st.markdown(self.config.app_config.description)
        st.divider()

    def render_complexity_selector(self) -> str:
        """
        Render complexity level selector

        Returns:
            Selected complexity level
        """
        complexity_level = self.ui_generator.render_complexity_selector()
        st.session_state.complexity_level = complexity_level
        return complexity_level

    def render_main_form(self, complexity_level: str) -> dict:
        """
        Render main calculator form

        Args:
            complexity_level: Selected complexity level

        Returns:
            User responses dictionary
        """
        return self.ui_generator.render_questions_form(complexity_level)

    def calculate_results(self, responses: dict, is_quick_estimate: bool = False, complexity_level: str = "advanced") -> tuple:
        """
        Calculate working days and breakdown

        Args:
            responses: User responses
            is_quick_estimate: Whether this is a quick estimate calculation
            complexity_level: Complexity level for validation

        Returns:
            Tuple of (total_days, breakdown, validation_errors)
        """
        # Validate responses
        if is_quick_estimate:
            validation_errors = self.calculation_engine.validate_quick_responses(responses)
        else:
            validation_errors = self.calculation_engine.validate_responses(responses, complexity_level=complexity_level)
        
        if validation_errors:
            return 0, {}, validation_errors

        # Calculate results
        total_days, breakdown = self.calculation_engine.calculate_working_days(responses)

        return total_days, breakdown, {}

    def render_results(self, total_days: int, breakdown: dict, responses: dict):
        """
        Render calculation results

        Args:
            total_days: Total calculated days
            breakdown: Cost breakdown
            responses: User responses
        """
        # Price input (outside form to prevent reset)
        price_per_day = self.ui_generator.render_price_display()

        # Results metrics
        self.ui_generator.render_results_section(total_days, breakdown, price_per_day)


    def _calculate_confidence(self, responses: dict, total_days: int) -> float:
        """
        Calculate confidence level for the estimate

        Args:
            responses: User responses
            total_days: Total calculated days

        Returns:
            Confidence level (0-1)
        """
        confidence = 0.7  # Base confidence

        # Increase confidence if more questions answered
        answered_questions = len([v for v in responses.values() if v is not None])
        total_questions = len(self.config.questions)
        completion_ratio = answered_questions / total_questions
        confidence += 0.2 * completion_ratio

        # Increase confidence if rules are documented
        if responses.get('existing_rules') == 'Fully documented and validated':
            confidence += 0.1

        # Decrease confidence for very large or very small projects
        if total_days > 50 or total_days < 5:
            confidence -= 0.1

        return min(max(confidence, 0.0), 1.0)



    def render_quick_estimate_mode(self):
        """Render quick estimate mode"""
        st.subheader("⚡ Quick Estimate Mode")
        st.info("Get a rapid estimate with just the essential questions")

        with st.form("quick_estimate_form"):
            col1, col2, col3 = st.columns(3)

            with col1:
                tables_count = st.number_input(
                    "Number of tables/reports",
                    min_value=1,
                    max_value=20,
                    value=1,
                    help="How many data sources to analyze"
                )

            with col2:
                complexity = st.selectbox(
                    "Project complexity",
                    ["Simple", "Moderate", "Complex"],
                    help="Overall project complexity level"
                )

            with col3:
                existing_rules = st.selectbox(
                    "Existing DQ rules",
                    ["None", "Some", "Complete"],
                    help="Current state of data quality documentation"
                )

            submitted = st.form_submit_button("🧮 Quick Calculate", type="primary")

        # Process submission outside the form to avoid rerun issues
        if submitted:
            try:
                # Map quick responses to full responses
                if complexity == 'Simple':
                    workflow_complexity = 'Simple (single table/report)'
                    data_sources = 'Single location (same database/schema)'
                    governance_maturity = False
                elif complexity == 'Moderate':
                    workflow_complexity = 'Simple (single table/report)'
                    data_sources = 'Multiple locations (2-3 sources)'
                    governance_maturity = False
                else:  # Complex
                    workflow_complexity = 'Complex (multiple tables/joins)'
                    data_sources = 'Complex integration (4+ sources)'
                    governance_maturity = True

                quick_responses = {
                    'tables_count': tables_count,
                    'workflow_complexity': workflow_complexity,
                    'data_sources': data_sources,
                    'existing_rules': {
                        'None': 'Not documented',
                        'Some': 'Partially documented',
                        'Complete': 'Fully documented and validated'
                    }[existing_rules],
                    'commercial_tool': 'No commercial tool',
                    'governance_maturity': governance_maturity,
                    # Add all required fields with sensible defaults for quick estimate
                    'data_volume': 'Small (<1M records)',  # Default to small for quick estimate
                    'datawash_installation': 'No, not needed',  # Default to no installation
                    'compliance_req': False,  # Default to no compliance requirements
                    'historical_analysis': False,  # Default to no historical analysis
                    'system_integration': False  # Default to no system integration
                }

                total_days, breakdown, errors = self.calculate_results(quick_responses, is_quick_estimate=True)

                if errors:
                    st.error("Validation errors:")
                    for field, error in errors.items():
                        st.error(f"- {field}: {error}")
                else:
                    st.session_state.calculated = True
                    st.session_state.total_days = total_days
                    st.session_state.breakdown = breakdown
                    st.session_state.responses = quick_responses

                    # Show quick results
                    st.success("Calculation completed!")
                    
                    # Show central KPI
                    from ui.components import CustomComponents
                    cost = total_days * st.session_state.price_per_day
                    CustomComponents.central_kpi_card(
                        value=f"€{cost:,.0f}",
                        label="Total Estimated Cost",
                        icon="💰"
                    )


            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.error("Please try again or contact support if the problem persists.")

    def render_sidebar_features(self):
        """Render sidebar with additional features"""
        st.sidebar.title("🔧 Options")

        # Mode selector
        mode = st.sidebar.radio(
            "Calculator Mode",
            ["Quick Estimate", "Full Calculator"],
            help="Choose between quick or detailed calculation"
        )

        # Configuration reload button
        st.sidebar.divider()
        st.sidebar.subheader("⚙️ Configuration")
        
        if st.sidebar.button("🔄 Reload Configuration", help="Reload configuration from file"):
            if self.load_configuration(reload=True):
                st.sidebar.success("Configuration reloaded successfully!")
                st.rerun()
            else:
                st.sidebar.error("Failed to reload configuration")

        # Help section
        with st.sidebar.expander("❓ Help & Information"):
            st.markdown("""
            **How to use this calculator:**
            1. Select calculator mode
            2. Fill out the relevant questions
            3. Click calculate to get your estimate
            """)

        return mode

    def run(self):
        """Main application entry point"""
        # Load configuration
        if not self.load_configuration():
            st.stop()

        # Setup page
        self.setup_page()

        # Render header
        self.render_header()

        # Render sidebar
        mode = self.render_sidebar_features()

        if mode == "Quick Estimate":
            # Quick estimate mode (now default)
            self.render_quick_estimate_mode()
        else:
            # Full calculator mode - now only shows advanced level
            # Show advanced calculator header
            complexity_level = self.render_complexity_selector()

            # Main form
            responses = self.render_main_form(complexity_level)

            # Process results if form was submitted
            if responses:
                total_days, breakdown, validation_errors = self.calculate_results(responses, complexity_level=complexity_level)

                if validation_errors:
                    st.error("Please correct the following errors:")
                    for field, error in validation_errors.items():
                        st.error(f"**{field}**: {error}")
                else:
                    # Store results in session state
                    st.session_state.calculated = True
                    st.session_state.total_days = total_days
                    st.session_state.breakdown = breakdown
                    st.session_state.responses = responses

                    # Render results
                    self.render_results(total_days, breakdown, responses)

        # Render footer
        self.ui_generator.render_footer()


def main():
    """Application entry point"""
    try:
        app = DQServiceCalculatorApp()
        app.run()
    except Exception as e:
        st.error(f"Application error: {e}")
        st.error("Please check the application configuration and try again")


if __name__ == "__main__":
    main()