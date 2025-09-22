# Data Quality Service Calculator - Stratesys

A configurable Streamlit web application to estimate working days and costs for Data Quality implementation projects based on the Stratesys methodology and DMBOK2 framework.

## 🚀 Features

### Configuration-Driven Architecture
- **YAML Configuration**: All questions, calculation rules, and UI settings are defined in `config/default_config.yaml`
- **Dynamic UI Generation**: Questions and forms are generated automatically from configuration
- **Validation**: Comprehensive configuration validation with helpful error messages
- **Hot Reload**: Admin users can reload configuration without restarting the app

### User Experience Levels
- **Basic Mode**: Essential questions only (suitable for data analysts)
- **Advanced Mode**: All questions visible (suitable for CDO/CTO level)
- **Quick Estimate**: 3-question rapid assessment mode

### Enhanced UX Features
- **Conditional Questions**: Questions appear/disappear based on previous answers
- **Progress Indicators**: Visual feedback for multi-step workflows
- **Interactive Visualizations**: Pie charts, resource allocation charts, risk matrices
- **Confidence Indicators**: AI-driven estimate confidence levels
- **Export Options**: JSON, CSV, and formatted text reports

### Professional UI Components
- **Custom Components**: Metric cards, info cards, expandable sections
- **Enhanced Visualizations**: Plotly charts for better data presentation
- **Responsive Design**: Mobile-friendly layout
- **Admin Panel**: Configuration management and debugging tools

## 📁 Project Structure

```
dq_calculator/
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
├── requirements.txt          # Dependencies
└── README.md                 # This file
```

## 🛠️ Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
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
  description: "Calculate estimated working days..."
  page_icon: "📊"
  layout: "wide"
```

#### User Complexity Levels
```yaml
complexity_levels:
  basic:
    label: "Basic (Essential questions only)"
    description: "Suitable for data analysts and quick estimates"
    show_questions: ["tables_count", "data_sources", "existing_rules", "commercial_tool"]

  advanced:
    label: "Advanced (All questions)"
    description: "Suitable for CDO/CTO level detailed planning"
    show_questions: "all"
```

## 🎯 Usage

### Basic Mode
1. Select "Basic (Essential questions only)"
2. Answer 4-6 core questions
3. Get quick estimate

### Advanced Mode
1. Select "Advanced (All questions)"
2. Fill out comprehensive questionnaire
3. Get detailed breakdown with all factors

### Quick Estimate Mode
1. Use sidebar to select "Quick Estimate"
2. Answer 3 essential questions
3. Get instant rough estimate

### Admin Mode
1. Enable "Admin Mode" in sidebar
2. Reload configuration files
3. View configuration summary
4. Debug calculation components

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
    complexity_level: "basic"  # or advanced
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

## 🔄 Methodology

Based on the Stratesys 4-phase Data Quality methodology:

- **Phase 0**: Data Exploration & Standard Rules Application
- **Phase 1**: Data Health Monitoring Setup
- **Phase 2**: Remediation Planning & Root Cause Analysis
- **Phase 3**: Implementation & Training

## 🧪 Testing

The application includes:
- Configuration validation
- Input validation
- Error handling
- Backward compatibility with original question format

## 🆘 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all files are in correct directory structure
2. **Configuration Errors**: Check YAML syntax and required fields
3. **Calculation Errors**: Verify all required questions have valid responses
4. **UI Issues**: Clear browser cache and restart Streamlit

## 📞 Support

For questions or issues:
1. Check the configuration file syntax
2. Review error messages in Streamlit
3. Contact your Stratesys representative
4. Submit issues to the development team

---

**Generated by Stratesys Technology Solutions**
*Professional Data Quality Services Calculator v2.0*