"""
Dynamic UI generator for DQ Service Calculator
"""
import streamlit as st
from typing import Dict, Any, List, Optional, Tuple

from config.schema import DQCalculatorConfig, QuestionConfig
from config.loader import ConfigLoader


class UIGenerator:
    """Generates Streamlit UI components from configuration"""

    def __init__(self, config: DQCalculatorConfig, config_loader: ConfigLoader):
        """
        Initialize UI generator

        Args:
            config: DQ calculator configuration
            config_loader: Configuration loader instance
        """
        self.config = config
        self.config_loader = config_loader

    def render_complexity_selector(self) -> str:
        """
        Render complexity level selector (now always returns 'advanced')

        Returns:
            Selected complexity level (always 'advanced')
        """
        # Since we only have 'advanced' level now, we don't need to show the selector
        # Just show the header for the advanced level
        st.subheader("Advanced Calculator")

        return 'advanced'

    def render_questions_form(self, complexity_level: str = "advanced") -> Dict[str, Any]:
        """
        Render form with questions based on complexity level

        Args:
            complexity_level: Selected complexity level

        Returns:
            Dictionary of user responses
        """
        responses = {}

        # Get questions grouped by section
        sections = self.config_loader.get_questions_by_section(complexity_level)

        # Create form
        with st.form("dq_calculator_form"):
            # Render sections
            for section_config in self.config.ui_sections:
                section_name = section_config.name
                if section_name not in sections:
                    continue

                question_ids = sections[section_name]
                if not question_ids:
                    continue

                # Section header
                st.subheader(f"{section_config.icon} {section_name}")
                if section_config.description:
                    st.markdown(f"*{section_config.description}*")

                # Render questions in this section
                section_responses = self._render_section_questions(
                    question_ids, responses, complexity_level
                )
                responses.update(section_responses)

                # Add spacing between sections
                st.markdown("---")

            # Submit button
            submitted = st.form_submit_button(
                "🧮 Calculate Estimated Working Days",
                type="primary",
                use_container_width=True
            )

        return responses if submitted else {}

    def _render_section_questions(self, question_ids: List[str], current_responses: Dict[str, Any],
                                complexity_level: str) -> Dict[str, Any]:
        """
        Render questions for a specific section

        Args:
            question_ids: List of question IDs to render
            current_responses: Current user responses
            complexity_level: Selected complexity level

        Returns:
            Dictionary of responses for this section
        """
        responses = {}

        for question_id in question_ids:
            if question_id not in self.config.questions:
                continue

            question_config = self.config.questions[question_id]

            # Check if question should be shown based on dependencies
            if not self.config_loader.should_show_question(question_id, current_responses):
                continue

            # Render the question
            response = self._render_question(question_id, question_config)
            if response is not None:
                responses[question_id] = response
                current_responses[question_id] = response  # Update for dependency checking

        return responses

    def _render_question(self, question_id: str, question_config: QuestionConfig) -> Any:
        """
        Render a single question component

        Args:
            question_id: Question identifier
            question_config: Question configuration

        Returns:
            User response value
        """
        # Create unique key for the component
        key = f"q_{question_id}"

        # Add optional indicator to label
        label = question_config.label
        if question_config.optional:
            label += " (Optional)"

        if question_config.type == "number_input":
            return st.number_input(
                label,
                min_value=question_config.min_value or 1,
                max_value=question_config.max_value or 100,
                value=question_config.default or 1,
                help=question_config.tooltip,
                key=key
            )

        elif question_config.type == "selectbox":
            options = question_config.options or []
            default_index = 0
            if question_config.default and question_config.default in options:
                default_index = options.index(question_config.default)

            return st.selectbox(
                label,
                options,
                index=default_index,
                help=question_config.tooltip,
                key=key
            )

        elif question_config.type == "radio":
            options = question_config.options or []
            default_index = 0
            if question_config.default and question_config.default in options:
                default_index = options.index(question_config.default)

            return st.radio(
                label,
                options,
                index=default_index,
                help=question_config.tooltip,
                key=key
            )

        elif question_config.type == "checkbox":
            return st.checkbox(
                label,
                value=question_config.default or False,
                help=question_config.tooltip,
                key=key
            )

        else:
            st.error(f"Unknown question type: {question_config.type}")
            return None

    def render_results_section(self, total_days: int, breakdown: Dict[str, float],
                             price_per_day: float = 0) -> None:
        """
        Render results section with central KPI for total estimated cost

        Args:
            total_days: Total calculated days
            breakdown: Calculation breakdown
            price_per_day: Daily rate for cost calculation
        """
        from ui.components import CustomComponents
        
        st.divider()

        # Show central KPI for total estimated cost
        if price_per_day > 0:
            total_cost = total_days * price_per_day
            CustomComponents.central_kpi_card(
                value=f"€{total_cost:,.0f}",
                label="Total Estimated Cost",
                icon="💰"
            )
        else:
            CustomComponents.central_kpi_card(
                value="Set price above",
                label="Total Estimated Cost",
                icon="⚠️"
            )

    def render_breakdown_section(self, breakdown: Dict[str, float], total_days: int) -> None:
        """
        Render detailed cost breakdown

        Args:
            breakdown: Calculation breakdown
            total_days: Total calculated days
        """
        st.subheader("📊 Cost Breakdown")

        # Create breakdown dataframe
        breakdown_data = []
        for component, days in breakdown.items():
            if days > 0:
                breakdown_data.append({
                    "Component": component,
                    "Days": int(days),
                    "Percentage": f"{(days/total_days)*100:.1f}%"
                })

        if breakdown_data:
            import pandas as pd
            breakdown_df = pd.DataFrame(breakdown_data)

            col1, col2 = st.columns([2, 1])

            with col1:
                st.dataframe(breakdown_df, use_container_width=True, hide_index=True)

            with col2:
                st.bar_chart(breakdown_df.set_index('Component')['Days'])

    def render_methodology_section(self) -> None:
        """Render methodology phases explanation"""
        st.subheader("🔄 Stratesys DQ Methodology")

        # Split phases into two columns
        phase_items = list(self.config.methodology_phases.items())
        mid_point = len(phase_items) // 2

        col1, col2 = st.columns(2)

        with col1:
            for phase_id, phase_config in phase_items[:mid_point]:
                self._render_methodology_phase(phase_config)

        with col2:
            for phase_id, phase_config in phase_items[mid_point:]:
                self._render_methodology_phase(phase_config)

    def _render_methodology_phase(self, phase_config) -> None:
        """Render a single methodology phase"""
        st.markdown(f"**{phase_config.title}**")
        st.markdown(phase_config.description)
        st.markdown("")

    def render_export_section(self, export_data: Dict[str, Any]) -> None:
        """
        Render export functionality

        Args:
            export_data: Data to export
        """
        st.subheader("📄 Export Results")

        col1, col2, col3 = st.columns(3)

        # JSON export
        with col1:
            import json
            json_data = json.dumps(export_data, indent=2, ensure_ascii=False)
            st.download_button(
                "📋 Download Summary (JSON)",
                data=json_data,
                file_name=f"dq_estimate_{export_data['metadata']['generated_date'][:10]}.json",
                mime="application/json",
                use_container_width=True
            )

        # CSV export
        with col2:
            if 'results' in export_data and 'breakdown' in export_data['results']:
                import pandas as pd
                breakdown = export_data['results']['breakdown']
                total_days = export_data['results']['total_days']

                breakdown_data = []
                for component, days in breakdown.items():
                    breakdown_data.append({
                        "Component": component,
                        "Days": days,
                        "Percentage": f"{(days/total_days)*100:.1f}%"
                    })

                breakdown_df = pd.DataFrame(breakdown_data)
                csv_data = breakdown_df.to_csv(index=False)

                st.download_button(
                    "📊 Download Breakdown (CSV)",
                    data=csv_data,
                    file_name=f"dq_breakdown_{export_data['metadata']['generated_date'][:10]}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        # Text report export
        with col3:
            from calculator.breakdown import BreakdownGenerator
            generator = BreakdownGenerator(self.config)

            responses = {k: v['value'] for k, v in export_data['project_details'].items()}
            total_days = export_data['results']['total_days']
            breakdown = export_data['results']['breakdown']

            report = generator.generate_summary_report(responses, total_days, breakdown)

            st.download_button(
                "📄 Download Report (TXT)",
                data=report,
                file_name=f"dq_report_{export_data['metadata']['generated_date'][:10]}.txt",
                mime="text/plain",
                use_container_width=True
            )

    def render_price_display(self, allow_admin_override: bool = False) -> float:
        """
        Get configured price per day with optional admin override (no display)

        Args:
            allow_admin_override: Whether to show admin override option

        Returns:
            Price per day value
        """
        # Get price from configuration
        default_price = self.config.pricing_config.default_price_per_day
        currency_symbol = self.config.pricing_config.currency_symbol
        currency = self.config.pricing_config.currency

        # Always use the configuration value, but maintain session state for admin overrides
        if 'price_per_day' not in st.session_state:
            st.session_state.price_per_day = default_price
        elif not allow_admin_override:
            # If not in admin mode, always use the configuration value
            st.session_state.price_per_day = default_price

        current_price = st.session_state.price_per_day

        # Admin override option (only if explicitly requested)
        if allow_admin_override and self.config.pricing_config.allow_admin_override:
            with st.expander("Admin: Override Daily Rate"):
                st.warning("⚠️ Admin Override - Use with caution")

                override_price = st.number_input(
                    f"Override price ({currency})",
                    min_value=self.config.pricing_config.min_price_override,
                    max_value=self.config.pricing_config.max_price_override,
                    value=current_price,
                    format="%.2f",
                    help=f"Override daily rate (range: {currency_symbol}{self.config.pricing_config.min_price_override:,.0f} - {currency_symbol}{self.config.pricing_config.max_price_override:,.0f})",
                    key="admin_price_override"
                )

                if st.button("Apply Override", type="secondary"):
                    st.session_state.price_per_day = override_price
                    st.success(f"Daily rate updated to {currency_symbol}{override_price:,.2f}")
                    st.rerun()

                if st.button("Reset to Default", type="secondary"):
                    st.session_state.price_per_day = default_price
                    st.success(f"Daily rate reset to default ({currency_symbol}{default_price:,.2f})")
                    st.rerun()

        return st.session_state.price_per_day


    def render_footer(self) -> None:
        """Render application footer"""
        st.divider()
        st.markdown(f"""
        <div style='text-align: center; color: #666; font-size: 14px;'>
            <p>🏢 <strong>{self.config.app_config.subtitle}</strong> - {self.config.app_config.title}</p>
            <p>Based on DataGov Framework by Stratesys</p>
            <p>For more information, contact your Stratesys representative</p>
        </div>
        """, unsafe_allow_html=True)