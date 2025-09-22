# Data Quality Service Calculator - Stratesys

A configurable Streamlit web application to estimate working days and costs for Data Quality implementation projects based on the Stratesys methodology and DMBOK2 framework.

## 🚀 Features

### Configuration-Driven Architecture
- **YAML Configuration**: All questions, calculation rules, and UI settings are defined in `config/default_config.yaml`
- **Dynamic UI Generation**: Questions and forms are generated automatically from configuration
- **Validation**: Comprehensive configuration validation with helpful error messages
- **Hot Reload**: Admin users can reload configuration without restarting the app

### User Experience Levels
- **Quick Estimate Mode**: 3-question rapid assessment mode (default)
- **Advanced Mode**: All questions visible (suitable for CDO/CTO level)

### Enhanced UX Features
- **Conditional Questions**: Questions appear/disappear based on previous answers
- **Interactive Visualizations**: Charts and breakdown displays
- **Export Options**: JSON, CSV, and formatted text reports
- **Configuration Management**: Hot reload of configuration without restart

### 📊 Executive Report Generation
- **PDF Reports**: Professional PDF reports with executive summary and detailed calculations
- **Excel Reports**: Multi-sheet Excel workbooks with breakdowns and methodology
- **Multiple Formats**: JSON, CSV, TXT, PDF, and Excel export options
- **Calculation Explanations**: Detailed explanations of how estimates are calculated
- **Risk Assessment**: Built-in risk evaluation and mitigation strategies
- **Methodology Documentation**: Complete Stratesys DQ methodology explanation

### Professional UI Components
- **Custom Components**: Metric cards, info cards, expandable sections
- **Enhanced Visualizations**: Charts for better data presentation
- **Responsive Design**: Mobile-friendly layout
- **Configuration Management**: Reload configuration without restarting the app

## 📁 Project Structure

```
DQServiceCalculator/
├── app_refactored.py          # Main application
├── config/
│   ├── __init__.py
│   ├── default_config.yaml    # Main configuration file
│   ├── schema.py             # Configuration schema definitions
│   └── loader.py             # Configuration loading and validation
├── calculator/
│   ├── __init__.py
│   ├── engine.py             # Calculation engine
│   └── breakdown.py          # Results breakdown generator
├── ui/
│   ├── __init__.py
│   ├── generator.py          # Dynamic UI generation
│   └── components.py         # Custom UI components
├── reports/
│   ├── __init__.py
│   └── generator.py          # Executive report generation
├── requirements.txt          # Dependencies
└── README.md                 # This file
```

## 🛠️ Installation

1. Install the required dependencies:
```powershell
pip install -r requirements.txt
```

**Note**: The application now includes report generation capabilities that require additional dependencies:
- `reportlab` for PDF generation
- `openpyxl` for Excel report generation

These are automatically included in the requirements.txt file.

2. Run the application:
```powershell
streamlit run app_refactored.py
```

## 📝 Configuration

### Main Configuration File: `config/default_config.yaml`

The configuration file contains:

#### Application Settings
```yaml
app_config:
  title: "Data Quality Service Calculator"
  subtitle: "Stratesys Technology Solutions"
  description: "Calculate estimated cost for your Data Quality implementation"
  page_icon: ""
  layout: "wide"
```

#### User Complexity Levels
```yaml
complexity_levels:
  advanced:
    label: "Advanced (All questions)"
    description: "Suitable for CDO/CTO level detailed planning"
    show_questions: "all"
```

## 🎯 Usage

### Quick Estimate Mode (Default)
1. The app opens in Quick Estimate mode by default
2. Answer 3 essential questions:
   - Number of tables/reports
   - Project complexity (Simple/Moderate/Complex)
   - Existing DQ rules status
3. Get instant cost estimate

### Advanced Mode
1. Use sidebar to select "Full Calculator"
2. Fill out comprehensive questionnaire with all sections
3. Get detailed breakdown with all factors
4. Download comprehensive executive reports

### 📊 Executive Report Generation
After completing any calculation (Quick Estimate or Advanced), you can download professional reports:

1. **PDF Reports**: Professional executive summaries with detailed calculations
2. **Excel Workbooks**: Multi-sheet workbooks with breakdowns, methodology, and risk assessment
3. **JSON Data**: Structured data for integration with other systems
4. **CSV Files**: Cost breakdowns for spreadsheet analysis
5. **Text Reports**: Human-readable summary reports

#### Report Contents Include:
- **Executive Summary**: High-level overview for management
- **Detailed Calculations**: Step-by-step explanation of how estimates are calculated
- **Methodology Documentation**: Complete Stratesys DQ methodology explanation
- **Risk Assessment**: Identified risks and mitigation strategies
- **Cost Breakdown**: Detailed component-by-component analysis
- **Project Timeline**: Estimated duration and resource requirements

#### Perfect for Presentations
The generated reports are specifically designed to help you explain the logic behind the calculations to your boss or stakeholders, including:
- Clear methodology explanation
- Transparent calculation breakdown
- Risk assessment and mitigation strategies
- Professional formatting suitable for executive presentations

### Configuration Management
1. Use sidebar "Reload Configuration" button to refresh settings
2. Configuration changes take effect immediately
3. No need to restart the application

## 🔧 Customization

### Adding New Questions

1. Edit `config/default_config.yaml`:
```yaml
questions:
  new_question_id:
    label: "Your question text"
    type: "selectbox"  # or number_input, radio, checkbox
    options: ["Option 1", "Option 2"]
    section: "Your Section"
    complexity_level: "advanced"
    tooltip: "Help text for users"
```

2. Update calculation rules if needed:
```yaml
calculation_rules:
  your_new_rule:
    "Option 1": 2.0
    "Option 2": 5.0
```

### Modifying Calculation Logic

Edit the `CalculationEngine` class in `calculator/engine.py` to add new calculation methods and reference your new configuration rules.

## 📊 Export Formats

The application supports multiple export formats:
- **JSON**: Complete project data and metadata
- **CSV**: Breakdown table for spreadsheet analysis
- **TXT**: Formatted report for presentations
- **PDF**: Professional report format (if configured)

## 🔄 Methodology

Based on the Stratesys 4-phase Data Quality methodology:

- **Phase 0**: Data Exploration & Standard Rules Application
- **Phase 1**: Data Health Monitoring Setup
- **Phase 2**: Remediation Planning & Root Cause Analysis
- **Phase 3**: Implementation & Training

## 🧪 Testing

The application includes:
- Configuration validation with detailed error messages
- Input validation for all question types
- Comprehensive error handling
- Session state management for user experience
- Hot reload capability for configuration changes

## 🆘 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all files are in correct directory structure and Python path is set correctly
2. **Configuration Errors**: Check YAML syntax and required fields in `config/default_config.yaml`
3. **Calculation Errors**: Verify all required questions have valid responses
4. **UI Issues**: Clear browser cache and restart Streamlit
5. **Configuration Not Loading**: Use the "Reload Configuration" button in the sidebar

## 📞 Support

For questions or issues:
1. Check the configuration file syntax
2. Review error messages in Streamlit
3. Contact your Stratesys representative
4. Submit issues to the development team

---

**Generated by Stratesys Technology Solutions**
*Professional Data Quality Services Calculator v2.0*

---

## 🔧 Technical Details

### Dependencies
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **PyYAML**: Configuration file parsing
- **Plotly**: Interactive visualizations

### Key Features
- **Modular Architecture**: Separated concerns with dedicated modules for configuration, calculation, and UI
- **Configuration-Driven**: All questions and rules defined in YAML for easy customization
- **Session Management**: Maintains user state across interactions
- **Error Handling**: Comprehensive validation and error reporting
- **Hot Reload**: Configuration changes without application restart