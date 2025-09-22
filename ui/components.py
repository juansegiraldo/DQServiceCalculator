"""
Custom UI components for DQ Service Calculator
"""
import streamlit as st
from typing import Dict, Any, List, Optional, Callable
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


class CustomComponents:
    """Custom Streamlit components for enhanced UX"""

    @staticmethod
    def progress_indicator(current_step: int, total_steps: int, labels: List[str] = None) -> None:
        """
        Render a progress indicator for multi-step workflows

        Args:
            current_step: Current step (1-based)
            total_steps: Total number of steps
            labels: Optional labels for each step
        """
        if labels is None:
            labels = [f"Step {i+1}" for i in range(total_steps)]

        progress_value = current_step / total_steps
        st.progress(progress_value)

        # Step indicators
        cols = st.columns(total_steps)
        for i, (col, label) in enumerate(zip(cols, labels)):
            with col:
                if i + 1 < current_step:
                    st.markdown(f"✅ **{label}**")
                elif i + 1 == current_step:
                    st.markdown(f"🔄 **{label}**")
                else:
                    st.markdown(f"⏸️ {label}")

    @staticmethod
    def info_card(title: str, content: str, icon: str = "ℹ️", type: str = "info") -> None:
        """
        Render an information card

        Args:
            title: Card title
            content: Card content
            icon: Icon to display
            type: Card type (info, success, warning, error)
        """
        color_map = {
            "info": "#e7f3ff",
            "success": "#d4edda",
            "warning": "#fff3cd",
            "error": "#f8d7da"
        }

        border_color_map = {
            "info": "#b3d7ff",
            "success": "#c3e6cb",
            "warning": "#ffeaa7",
            "error": "#f5c6cb"
        }

        bg_color = color_map.get(type, "#e7f3ff")
        border_color = border_color_map.get(type, "#b3d7ff")

        st.markdown(f"""
        <div style="
            background-color: {bg_color};
            border: 1px solid {border_color};
            border-radius: 8px;
            padding: 16px;
            margin: 8px 0;
        ">
            <h4 style="margin: 0 0 8px 0; color: #333;">
                {icon} {title}
            </h4>
            <p style="margin: 0; color: #555;">
                {content}
            </p>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def metric_card(value: str, label: str, delta: str = None, icon: str = "📊") -> None:
        """
        Render a metric card with optional delta

        Args:
            value: Primary metric value
            label: Metric label
            delta: Optional delta value
            icon: Icon to display
        """
        delta_html = f"<small style='color: #666;'>{delta}</small>" if delta else ""

        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin: 10px 0;
        ">
            <div style="font-size: 24px; margin-bottom: 5px;">{icon}</div>
            <div style="font-size: 36px; font-weight: bold; margin-bottom: 5px;">{value}</div>
            <div style="font-size: 16px; opacity: 0.9;">{label}</div>
            {delta_html}
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def central_kpi_card(value: str, label: str, subtitle: str = None, icon: str = "💰") -> None:
        """
        Render a subtle centered KPI card for the main result

        Args:
            value: Primary metric value (e.g., "€13,300")
            label: Metric label (e.g., "Total Estimated Cost")
            subtitle: Optional subtitle
            icon: Icon to display (not used in this version)
        """
        st.markdown(f"""
        <div style="
            display: flex;
            justify-content: center;
            margin: 40px 0;
        ">
            <div style="
                background: #f8f9fa;
                color: #2c3e50;
                padding: 30px 40px;
                border-radius: 12px;
                text-align: center;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                border: 1px solid #e9ecef;
                max-width: 400px;
                width: 100%;
            ">
                <div style="font-size: 16px; font-weight: 500; margin-bottom: 12px; color: #6c757d;">{label}</div>
                <div style="font-size: 48px; font-weight: 700; color: #2c3e50;">{value}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def comparison_table(data: Dict[str, Dict[str, Any]], title: str = "Comparison") -> None:
        """
        Render a comparison table

        Args:
            data: Dictionary with comparison data
            title: Table title
        """
        st.subheader(title)

        df = pd.DataFrame(data).T
        st.dataframe(df, use_container_width=True)

    @staticmethod
    def timeline_chart(milestones: List[Dict[str, Any]]) -> None:
        """
        Render a project timeline chart

        Args:
            milestones: List of milestone dictionaries with 'name', 'start', 'duration'
        """
        if not milestones:
            return

        # Create Gantt-like chart
        fig = go.Figure()

        for i, milestone in enumerate(milestones):
            fig.add_trace(go.Scatter(
                x=[milestone['start'], milestone['start'] + milestone['duration']],
                y=[i, i],
                mode='lines+markers',
                name=milestone['name'],
                line=dict(width=10),
                marker=dict(size=8)
            ))

        fig.update_layout(
            title="Project Timeline",
            xaxis_title="Days",
            yaxis_title="Milestones",
            yaxis=dict(
                tickmode='array',
                tickvals=list(range(len(milestones))),
                ticktext=[m['name'] for m in milestones]
            ),
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def breakdown_pie_chart(breakdown: Dict[str, float], title: str = "Cost Breakdown") -> None:
        """
        Render a pie chart for cost breakdown

        Args:
            breakdown: Dictionary with breakdown data
            title: Chart title
        """
        if not breakdown:
            return

        # Filter out zero values
        filtered_breakdown = {k: v for k, v in breakdown.items() if v > 0}

        if not filtered_breakdown:
            return

        fig = px.pie(
            values=list(filtered_breakdown.values()),
            names=list(filtered_breakdown.keys()),
            title=title,
            hole=0.3  # Donut chart style
        )

        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            textfont_size=12
        )

        fig.update_layout(
            showlegend=True,
            height=500,
            font=dict(size=14)
        )

        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def expandable_section(title: str, content: Callable, expanded: bool = False,
                          icon: str = "📋") -> None:
        """
        Render an expandable section

        Args:
            title: Section title
            content: Function that renders the content
            expanded: Whether section is expanded by default
            icon: Icon to display
        """
        with st.expander(f"{icon} {title}", expanded=expanded):
            content()

    @staticmethod
    def cost_calculator_widget(base_cost: float, multipliers: Dict[str, float]) -> float:
        """
        Render an interactive cost calculator widget

        Args:
            base_cost: Base cost value
            multipliers: Dictionary of multiplier options

        Returns:
            Calculated total cost
        """
        st.subheader("💰 Interactive Cost Calculator")

        total_cost = base_cost

        cols = st.columns(2)

        with cols[0]:
            st.write("**Base Cost:**")
            st.write(f"€{base_cost:,.2f}")

        with cols[1]:
            st.write("**Multipliers:**")
            for name, multiplier in multipliers.items():
                if st.checkbox(f"{name} (+{multiplier:.1%})", key=f"mult_{name}"):
                    total_cost += base_cost * multiplier

        st.divider()
        st.metric("Total Estimated Cost", f"€{total_cost:,.2f}")

        return total_cost

    @staticmethod
    def risk_assessment_matrix(risks: List[Dict[str, Any]]) -> None:
        """
        Render a risk assessment matrix

        Args:
            risks: List of risk dictionaries with 'name', 'probability', 'impact'
        """
        if not risks:
            return

        st.subheader("🎯 Risk Assessment Matrix")

        # Create scatter plot for risk matrix
        df = pd.DataFrame(risks)

        fig = px.scatter(
            df,
            x='probability',
            y='impact',
            text='name',
            title="Risk Assessment Matrix",
            labels={'probability': 'Probability', 'impact': 'Impact'},
            range_x=[0, 10],
            range_y=[0, 10]
        )

        fig.update_traces(
            textposition="top center",
            marker=dict(size=15, opacity=0.7)
        )

        fig.update_layout(
            height=500,
            xaxis_title="Probability (1-10)",
            yaxis_title="Impact (1-10)"
        )

        # Add quadrant lines
        fig.add_hline(y=5, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_vline(x=5, line_dash="dash", line_color="gray", opacity=0.5)

        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def resource_allocation_chart(resources: Dict[str, int]) -> None:
        """
        Render a resource allocation chart

        Args:
            resources: Dictionary mapping resource types to quantities
        """
        if not resources:
            return

        st.subheader("👥 Resource Allocation")

        # Create horizontal bar chart
        fig = go.Figure(go.Bar(
            x=list(resources.values()),
            y=list(resources.keys()),
            orientation='h',
            marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'][:len(resources)]
        ))

        fig.update_layout(
            title="Resource Allocation by Role",
            xaxis_title="Days",
            yaxis_title="Role",
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def confidence_indicator(confidence: float, label: str = "Estimate Confidence") -> None:
        """
        Render a confidence indicator

        Args:
            confidence: Confidence level (0-1)
            label: Indicator label
        """
        color = "green" if confidence >= 0.8 else "orange" if confidence >= 0.6 else "red"
        confidence_pct = int(confidence * 100)

        st.markdown(f"""
        <div style="
            display: flex;
            align-items: center;
            padding: 10px;
            background-color: #f0f2f6;
            border-radius: 5px;
            margin: 10px 0;
        ">
            <div style="
                width: 20px;
                height: 20px;
                border-radius: 50%;
                background-color: {color};
                margin-right: 10px;
            "></div>
            <span style="font-weight: bold;">{label}: {confidence_pct}%</span>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def quick_estimate_mode(questions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render a quick estimate mode with minimal questions

        Args:
            questions: Available questions configuration

        Returns:
            Quick estimate responses
        """
        st.subheader("⚡ Quick Estimate Mode")
        st.info("Get a rapid estimate with just 3 essential questions")

        responses = {}

        col1, col2, col3 = st.columns(3)

        with col1:
            responses['tables_count'] = st.number_input(
                "Number of tables",
                min_value=1,
                max_value=20,
                value=1,
                key="quick_tables"
            )

        with col2:
            responses['data_sources'] = st.selectbox(
                "Data complexity",
                ["Single location", "Multiple locations", "Complex integration"],
                key="quick_sources"
            )

        with col3:
            responses['existing_rules'] = st.radio(
                "Existing rules",
                ["None", "Some", "Complete"],
                key="quick_rules"
            )

        return responses

    @staticmethod
    def help_section_card(title: str, content: str, icon: str = "ℹ️", 
                         bg_color: str = "#f8f9fa", border_color: str = "#dee2e6") -> None:
        """
        Render a styled help section card

        Args:
            title: Card title
            content: Card content (markdown supported)
            icon: Icon to display
            bg_color: Background color
            border_color: Border color
        """
        st.markdown(f"""
        <div style="
            background-color: {bg_color};
            border: 1px solid {border_color};
            border-radius: 8px;
            padding: 16px;
            margin: 12px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <h4 style="margin: 0 0 12px 0; color: #2c3e50; display: flex; align-items: center;">
                <span style="margin-right: 8px; font-size: 18px;">{icon}</span>
                {title}
            </h4>
            <div style="color: #495057; line-height: 1.5;">
                {content}
            </div>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def feature_highlight(feature: str, description: str, icon: str = "✨") -> None:
        """
        Render a feature highlight with icon and description

        Args:
            feature: Feature name
            description: Feature description
            icon: Icon to display
        """
        st.markdown(f"""
        <div style="
            display: flex;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
        ">
            <span style="
                font-size: 16px;
                margin-right: 12px;
                color: #007bff;
            ">{icon}</span>
            <div>
                <strong style="color: #2c3e50;">{feature}</strong>
                <div style="color: #6c757d; font-size: 14px;">{description}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def step_indicator(step: int, total_steps: int, title: str, description: str = "") -> None:
        """
        Render a step indicator for help instructions

        Args:
            step: Current step number
            total_steps: Total number of steps
            title: Step title
            description: Optional step description
        """
        progress = step / total_steps
        color = "#28a745" if step == total_steps else "#007bff"
        
        st.markdown(f"""
        <div style="
            display: flex;
            align-items: center;
            padding: 12px;
            background: linear-gradient(90deg, {color}20 0%, {color}10 100%);
            border-left: 4px solid {color};
            border-radius: 4px;
            margin: 8px 0;
        ">
            <div style="
                background-color: {color};
                color: white;
                border-radius: 50%;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                font-size: 12px;
                margin-right: 12px;
            ">{step}</div>
            <div>
                <strong style="color: #2c3e50;">{title}</strong>
                {f'<div style="color: #6c757d; font-size: 14px; margin-top: 2px;">{description}</div>' if description else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)