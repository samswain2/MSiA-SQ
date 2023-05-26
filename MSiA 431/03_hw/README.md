# ChatGPT Bias & Fairness Analysis

## Data

    1. Did chatGPT capture the required attributes? If not, which attributes did it miss? Were any attributes incorrectly identified? 

    **This was ChatGPT's response**:
    - Demographic Info: The use of demographic information like 'percent_white', 'percent_hispanic', 'percent_black', 'percent_asian', 'percent_mixed', 'percent_other', 'percent_bachelors', 'percent_high_school', 'percent_no_high_school', can lead to discriminatory bias in a model. If there are underlying societal biases that influence these variables (which is often the case), the model might learn and perpetuate these biases. For instance, a model might unfairly associate higher crime rates with areas that have a high percentage of a specific racial or educational group, which can reinforce harmful stereotypes.

    - Location Information: Location-based features like 'num_districts', 'num_wards', 'num_community_areas', 'num_location_descriptions', can be a proxy for demographic characteristics or socioeconomic status. If there are patterns in your data where certain areas (districts, wards, etc.) have more crimes due to socioeconomic factors, the model could unfairly associate those geographic locations with higher crime rates. This could lead to discrimination against people living in those areas.

    - Lag features: 'total_crimes_lag_1', 'total_arrests_lag_1', 'total_domestic_crimes_lag_1', etc., are features that describe past states of crime, arrests, and domestic crimes. These features could indirectly capture and perpetuate existing biases in the law enforcement and criminal justice systems. If historical data reflects unfair targeting or over-policing of certain demographic groups or areas, the model trained on this data may predict higher crime rates for those groups or areas in the future.


    - Add/remove protected (including proxy) attributes based on your evaluation of the outputs from chatGPT

    

    - Analyze the data. Do you detect bias in the data?
    - Present the results visually to show salient insights wrt to bias.
    - Based on the EDA and your project objective (predicting crime at the beat level), develop a hypothesis about where b/f issues could arise in the modeling.

## Modeling

    - Based on your hypothesis, assess the fairness of your model/analysis by applying the fairness-related metrics that are available in any of the R and Python packages for fairness analysis.
    - Explain the reasoning for the groups that you selected for the fairness metrics.
    - Compare the fairness metrics for the different groups.
    - If you developed multiple models compare the fairness metrics for the models.
    - Comment on the results.
    - Suggest how the bias/fairness issues could be mitigated.
    - Present the results visually to show salient insights.

