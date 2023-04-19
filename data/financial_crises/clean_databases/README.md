# Models 
Contains three programs allowing the construction of a chronology of systemic banking, currency and sovereign debt crises, either totally (1 for crisis years, 0 otherwise) or partially (construction of indicators needed for dating, completed by a narrative).

- *banking_crises.py*    : Dating systemic banking crises based on the criterion of Baron M., Verner E. and Xiong W. (2020). This criterion is still insufficient to date banking crises, but it does help to identify vulnerable countries. 
			 The final dating includes a manual part.
- *currency_crises.py*   : Dating of currency crises based on the Frankel J. and Rose A. criterion using the Laeven L. and Valencia F. (2020) thresholds of 30% and 10 percentage points. 
			 The final dating includes a manual part concerning crises that took place in a close window and borderline crises (tolerance at 28% for the first threshold or 9 percentage points for the second threshold).
- *debt_crises.py*       : Dating of sovereign debt crises based on the criterion of Nguyen T.C., Castro V. and Wood J. (2022). 
			 The final dating includes a manual part for borderline crises.
- *banking_crises.xlsx*  : Output of the programm banking_crises.py.
- *currency_crises.xlsx* : Output of the programm currency_crises.py.
- *debt_crises.xlsx*     : Output of the programm debt_crises.py.

The final dating is available in *../data/financial_crises/clean_databases/Barthelemy_Gautier_Rondeau_2023.xlsx*.
