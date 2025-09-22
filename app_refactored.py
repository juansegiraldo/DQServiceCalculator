"""
DQ Service Calculator - Streamlit Application
Modern, configurable implementation with dynamic UI generation
"""
import streamlit as st
import sys
import os
from pathlib import Path
from datetime import datetime

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
    from reports.generator import ReportGenerator
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
        self.report_generator = None
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
            self.report_generator = ReportGenerator(self.config)

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
        
        # Report download section
        self.render_report_download_section(responses, total_days, breakdown, price_per_day)


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

    def render_report_download_section(self, responses: dict, total_days: int, 
                                     breakdown: dict, price_per_day: float):
        """
        Render report download section

        Args:
            responses: User responses
            total_days: Total calculated days
            breakdown: Cost breakdown
            price_per_day: Daily rate
        """
        st.divider()
        st.subheader("📊 Descargar Reporte Ejecutivo")
        st.markdown("Descarga un reporte detallado que explica la lógica detrás de los cálculos para presentar a tu jefe.")
        
        # Get available formats
        available_formats = self.report_generator.get_available_formats()
        
        # Create columns for download buttons
        cols = st.columns(len(available_formats))
        
        for i, format_type in enumerate(available_formats):
            with cols[i]:
                if format_type == 'pdf':
                    if st.button(f"📄 Descargar PDF", key=f"download_{format_type}", 
                               help="Reporte completo en formato PDF"):
                        try:
                            pdf_content = self.report_generator.generate_pdf_report(
                                responses, total_days, breakdown, price_per_day
                            )
                            st.download_button(
                                label="💾 Descargar PDF",
                                data=pdf_content,
                                file_name=f"dq_estimation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                mime="application/pdf",
                                key=f"download_btn_{format_type}"
                            )
                        except Exception as e:
                            st.error(f"Error generando PDF: {str(e)}")
                
                elif format_type == 'excel':
                    if st.button(f"📊 Descargar Excel", key=f"download_{format_type}",
                               help="Reporte completo en formato Excel con múltiples hojas"):
                        try:
                            excel_content = self.report_generator.generate_excel_report(
                                responses, total_days, breakdown, price_per_day
                            )
                            st.download_button(
                                label="💾 Descargar Excel",
                                data=excel_content,
                                file_name=f"dq_estimation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key=f"download_btn_{format_type}"
                            )
                        except Exception as e:
                            st.error(f"Error generando Excel: {str(e)}")
                
                elif format_type == 'json':
                    if st.button(f"📋 Descargar JSON", key=f"download_{format_type}",
                               help="Datos estructurados en formato JSON"):
                        try:
                            json_content = self.breakdown_generator.generate_json_export(
                                responses, total_days, breakdown
                            )
                            st.download_button(
                                label="💾 Descargar JSON",
                                data=json_content,
                                file_name=f"dq_estimation_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json",
                                key=f"download_btn_{format_type}"
                            )
                        except Exception as e:
                            st.error(f"Error generando JSON: {str(e)}")
                
                elif format_type == 'csv':
                    if st.button(f"📈 Descargar CSV", key=f"download_{format_type}",
                               help="Desglose de costos en formato CSV"):
                        try:
                            csv_content = self.breakdown_generator.generate_csv_breakdown(
                                breakdown, total_days
                            )
                            st.download_button(
                                label="💾 Descargar CSV",
                                data=csv_content,
                                file_name=f"dq_breakdown_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv",
                                key=f"download_btn_{format_type}"
                            )
                        except Exception as e:
                            st.error(f"Error generando CSV: {str(e)}")
                
                elif format_type == 'txt':
                    if st.button(f"📝 Descargar Texto", key=f"download_{format_type}",
                               help="Reporte en formato de texto plano"):
                        try:
                            txt_content = self.breakdown_generator.generate_summary_report(
                                responses, total_days, breakdown, price_per_day
                            )
                            st.download_button(
                                label="💾 Descargar TXT",
                                data=txt_content,
                                file_name=f"dq_summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                mime="text/plain",
                                key=f"download_btn_{format_type}"
                            )
                        except Exception as e:
                            st.error(f"Error generando TXT: {str(e)}")
        
        # Show report preview
        with st.expander("👁️ Vista Previa del Reporte"):
            st.markdown("### Resumen Ejecutivo")
            exec_summary = self.report_generator.generate_executive_summary(
                responses, total_days, breakdown, price_per_day
            )
            st.markdown(exec_summary)
            
            st.markdown("### Explicación de Cálculos")
            calc_explanation = self.report_generator.generate_detailed_calculation_explanation(
                responses, breakdown
            )
            st.markdown(calc_explanation)

    def render_quick_estimate_mode(self):
        """Render quick estimate mode - shows core questions that most impact calculation"""
        st.subheader(self.config.quick_estimate_config.title)

        with st.form("quick_estimate_form"):
            # Show core questions that most impact the calculation
            # First row: tables_count and workflow_complexity
            col1, col2 = st.columns(2)
            
            with col1:
                # Tables count question
                tables_config = self.config.questions.get('tables_count')
                if tables_config:
                    tables_count = st.number_input(
                        tables_config.label,
                        min_value=tables_config.min_value or 1,
                        max_value=tables_config.max_value or 100,
                        value=tables_config.default or 1,
                        help=tables_config.tooltip
                    )
                else:
                    tables_count = st.number_input(
                        "Number of tables/reports",
                        min_value=1,
                        max_value=100,
                        value=1,
                        help="How many data sources to analyze"
                    )
            
            with col2:
                # Workflow complexity question
                workflow_config = self.config.questions.get('workflow_complexity')
                if workflow_config:
                    workflow_complexity = st.radio(
                        workflow_config.label,
                        workflow_config.options,
                        help=workflow_config.tooltip
                    )
                else:
                    workflow_complexity = st.radio(
                        "Workflow complexity",
                        ["Simple (single table/report)", "Complex (multiple tables/joins)"],
                        help="Simple: single data source, Complex: requires joining multiple tables"
                    )
            
            # Second row: rules_count and data_sources
            col3, col4 = st.columns(2)
            
            with col3:
                # Rules count question
                rules_config = self.config.questions.get('rules_count')
                if rules_config:
                    rules_count = st.number_input(
                        rules_config.label,
                        min_value=rules_config.min_value or 1,
                        max_value=rules_config.max_value or 100,
                        value=rules_config.default or 15,
                        help=rules_config.tooltip
                    )
                else:
                    rules_count = st.number_input(
                        "How many quality rules do you expect per table?",
                        min_value=1,
                        max_value=100,
                        value=15,
                        help="Standard workstreams include up to 15-20 rules. Additional rules require extra time."
                    )
            
            with col4:
                # Data sources question
                data_sources_config = self.config.questions.get('data_sources')
                if data_sources_config:
                    data_sources = st.selectbox(
                        data_sources_config.label,
                        data_sources_config.options,
                        help=data_sources_config.tooltip
                    )
                else:
                    data_sources = st.selectbox(
                        "Data source integration complexity",
                        ["Single location (same database/schema)", "Multiple locations (2-3 sources)", "Complex integration (4+ sources)"],
                        help="More data sources require additional integration work"
                    )

            submitted = st.form_submit_button("🧠 Calculate", type="primary", use_container_width=False)

        # Process submission outside the form to avoid rerun issues
        if submitted:
            try:
                # Use Quick Estimate configuration defaults
                quick_config = self.config.quick_estimate_config
                
                # Create responses using user selections for core questions and defaults for everything else
                quick_responses = {
                    'tables_count': tables_count,
                    'workflow_complexity': workflow_complexity,  # User selection
                    'rules_count': rules_count,  # User selection
                    'data_sources': data_sources,  # User selection
                    'existing_rules': quick_config.defaults.existing_rules,
                    'commercial_tool': quick_config.defaults.commercial_tool,
                    'governance_maturity': quick_config.defaults.governance_maturity,
                    'data_volume': quick_config.defaults.data_volume,
                    'datawash_installation': quick_config.defaults.datawash_installation,
                    'compliance_req': quick_config.defaults.compliance_req,
                    'historical_analysis': quick_config.defaults.historical_analysis,
                    'system_integration': quick_config.defaults.system_integration,
                    'cloud_platform': quick_config.defaults.cloud_platform
                }

                # Use the same calculation engine as advanced mode
                total_days, breakdown, errors = self.calculate_results(quick_responses, is_quick_estimate=False)

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
                    
                    # Show central KPI
                    from ui.components import CustomComponents
                    cost = total_days * st.session_state.price_per_day
                    CustomComponents.central_kpi_card(
                        value=f"€{cost:,.0f}",
                        label="Total Estimated Cost",
                        icon="💰"
                    )
                    
                    # Show report download section for quick estimate
                    self.render_report_download_section(quick_responses, total_days, breakdown, st.session_state.price_per_day)

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.error("Please try again or contact support if the problem persists.")

    def render_sidebar_features(self):
        """Render sidebar with additional features"""
       

        # Mode selector
        mode = st.sidebar.radio(
            "Calculator mode",
            ["Quick", "Advanced"],
            help='Choose between quick or detailed calculation'
        )

        # Configuration reload button
        # st.sidebar.divider()
        # st.sidebar.subheader("⚙️ Configuration")
        
        # if st.sidebar.button("🔄 Reload Configuration", help="Reload configuration from file"):
        #     if self.load_configuration(reload=True):
        #         st.sidebar.success("Configuration reloaded successfully!")
        #         st.rerun()
        #     else:
        #         st.sidebar.error("Failed to reload configuration")

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

        if mode == "Quick":
            # Quick estimate mode (now default)
            self.render_quick_estimate_mode()
        else:
            # Advanced calculator mode - now only shows advanced level
            # Show advanced calculator header
            complexity_level = self.render_complexity_selector()
            
            # Display advanced mode title
            advanced_config = self.config.complexity_levels.get(complexity_level)
            if advanced_config:
                st.subheader(advanced_config.title)

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