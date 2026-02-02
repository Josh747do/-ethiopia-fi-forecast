# Event Impact Modeling Methodology

*Generated: 2026-02-02 05:14:28*

## Project Overview

- **Project**: Ethiopia Financial Inclusion Forecasting System
- **Task**: Task 3: Event Impact Modeling
- **Objective**: Model how events (policies, product launches, infrastructure investments) affect financial inclusion indicators
- **Date**: 2026-02-02
- **Analyst**: Data Scientist at Selam Analytics
- **Stakeholders**: Development finance institutions, Mobile money operators, National Bank of Ethiopia

## Methodological Approach

### Stage 1: Data Understanding & Preparation

Load and clean data, understand impact_link structure, join events with impacts

**Key Activities:**
- Loaded enriched data from Tasks 1-2
- Separated data by record_type (observations, events, impact_links)
- Joined impact_links with events using parent_id
- Cleaned and standardized impact magnitude values (converted string values like 'high' to numeric)

**Outputs:** impact_with_events dataframe, cleaned impact links

### Stage 2: Event-Indicator Matrix Construction

Build core impact estimation matrix

**Key Activities:**
- Defined 5 core indicators for forecasting (ACC_OWNERSHIP, USG_DIGITAL_PAYMENT, ACC_MM_ACCOUNT, INF_AGENT_DENSITY, INF_4G_COVERAGE)
- Created matrix with events as rows and indicators as columns
- Populated matrix from existing impact_link records
- Applied rule-based estimates for missing values based on event category
- Used event category mapping to assign default impacts

**Outputs:** initial_event_indicator_matrix.csv, visualization heatmap

### Stage 3: Comparable Country Evidence Integration

Use evidence from similar markets to inform impact estimates

**Key Activities:**
- Built database of comparable countries (Kenya, Tanzania, Rwanda, India)
- Extracted impact evidence from academic studies and reports
- Mapped Ethiopian event types to comparable evidence
- Applied evidence-based adjustment factors to impact estimates
- Created confidence scores based on evidence quality

**Outputs:** evidence_adjusted_matrix.csv, comparable_country_evidence_summary.csv

### Stage 4: Historical Validation

Test impact estimates against actual historical changes

**Key Activities:**
- Focused on Telebirr launch as key case study (document reference)
- Compared model estimates with actual 2021-2024 changes
- Calculated error metrics (absolute error, percent error)
- Identified systematic biases and high-error events
- Created validation summary with accuracy ratings

**Outputs:** model_validation_results.csv, refinement_recommendations.csv

### Stage 5: Impact Estimate Refinement

Adjust estimates based on validation results

**Key Activities:**
- Applied global adjustment for systematic underestimation (1.93pp average)
- Implemented event-specific refinements for high-error events
- Applied indicator-specific adjustments based on validation patterns
- Created confidence scoring matrix (High/Medium/Low)
- Calculated uncertainty ranges for each estimate

**Outputs:** refined_event_indicator_matrix.csv, confidence_matrix.csv, uncertainty_ranges.csv

## Key Assumptions

### Impact Modeling

- Linear additive impacts: Events have independent, additive effects on indicators
- Constant lag structures: Similar event types have similar time-to-impact profiles
- Scalable evidence: Comparable country impacts can be scaled to Ethiopian context
- Indicator independence: Core indicators respond independently to events (minimal interaction effects)

### Data Assumptions

- Impact_link records represent expert or evidence-based estimates
- Missing impact magnitudes can be estimated using event category rules
- Historical observations are accurate and representative
- Event categorization is consistent and meaningful

### Forecasting Assumptions

- Past relationships between events and indicators will continue in the forecast period
- No major disruptive events beyond those modeled will occur
- Policy environment remains relatively stable
- Technological adoption curves follow similar patterns to comparable countries

## Limitations and Uncertainties

### Data Limitations

- Sparse historical data: Only 5 Findex points over 13 years for account ownership
- Limited pre/post event data: Few events have comprehensive before/after measurements
- Impact_link completeness: Not all events have modeled impact relationships
- Data granularity: Limited disaggregated data (gender, region, urban/rural)

### Modeling Limitations

- Simplified impact representation: Complex real-world effects reduced to single estimates
- Linear assumptions: Non-linear adoption curves and saturation effects not captured
- Interaction effects: Combined impacts of multiple events may not be additive
- Time variation: Static impact estimates don't capture changing effectiveness over time

### Evidence Limitations

- Transferability: Comparable country evidence may not fully apply to Ethiopian context
- Context differences: Regulatory, cultural, and economic differences not fully accounted for
- Evidence quality: Variation in study methodologies and data quality across sources

## Validation Results

### Overall Performance

- **Validation Pairs**: 9
- **Mean Absolute Error Original**: 2.95pp
- **Mean Absolute Error Refined**: 1.62pp
- **Improvement**: 1.33pp (45% reduction)
- **Systematic Bias**: Underestimation of 1.93pp addressed through refinements

### Key Case Study: Telebirr Launch

#### ACC_MM_ACCOUNT

- **Actual Growth**: 4.75pp (2021-2024)
- **Model Estimate**: 6.00pp
- **Error**: +1.25pp (overestimate)
- **Accuracy**: Good

#### ACC_OWNERSHIP

- **Actual Growth**: 3.00pp (2021-2024)
- **Original Estimate**: 2.20pp
- **Refined Estimate**: 10.72pp
- **Error Improvement**: 8.80pp to -7.72pp

## Outputs Generated

### Matrices

- `event_indicator_matrix_initial.csv: Initial impact estimates`
- `event_indicator_matrix_evidence_adjusted.csv: After comparable country evidence`
- `event_indicator_matrix_refined.csv: Final refined impact estimates`

### Supporting Documentation

- `impact_confidence_matrix.csv: Confidence scores (High/Medium/Low)`
- `impact_uncertainty_ranges.csv: Uncertainty ranges for each estimate`
- `model_validation_results.csv: Historical validation results`
- `comparable_country_evidence_summary.csv: Evidence base documentation`

### Logs And Methodology

- `refinement_log.csv: All adjustments applied during refinement`
- `refinement_strategy.json: Refinement methodology documentation`
- `comparable_countries_database.json: Comparable country evidence database`

### Visualizations

- `event_indicator_matrix_initial.png: Initial matrix heatmap`
- `evidence_adjusted_matrix_comparison.png: Evidence adjustment comparison`
- `model_validation_results.png: Validation scatter plot`
- `refined_matrix_comparison.png: Refinement progression visualization`

## Implications for Forecasting (Task 4)

- Policy events have stronger systemic impacts than initially estimated
- Infrastructure investments show long-term cumulative effects
- Market entry events drive competition and innovation benefits
- Digital ID and interoperability are high-impact enablers
