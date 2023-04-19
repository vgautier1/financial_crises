# Motivations

The objective of this directory is to gather the dating of crises (banking, currency and sovereign debt) existing in the literature in order to facilitate comparison and to propose the most up-to-date dating (January 2023) by making available the python programs allowing to build it.
This dating is part of the study of financial crises and continues the work started in my paper ***"Early Warning System for Currency Crises Using Long Short-Term Memory and Gated Recurrent Unit Neural Networks"*** available in the *doc* directory (Barthelemy_Gautier_Rondeau_2022).



# Path description
| *Path* | Description |
|---|---|

- | *data/financial_crises/clean_databases* | Dates of the three types of crises in Excel format (banking, foreign exchange and debt) from the literature in an identical format (panel). Contains a file specific to each dating and a global file allowing comparisons between the different papers. | <br>
- | *data/financial_crises/raw_databases*   | Dates of the three types of crises in Excel format (banking, foreign exchange and debt) from the literature without standardising the files (file as exported).  |<br>
- | *doc*    | Paper related to crisis dating in previous directories. |<br>
- | *models* | Program to build the dating (one program for each type of crisis and an associated Excel file of results). |<br>
- | *utils*  | Support functions for the three python crisis dating programs. |<br>
- | *graphs* | Graphic analysis of the proposed dating. |<br>



# Crisis criteria
Definition of the crises retained in order to construct the dating.
<br>
## Systemic banking crises
*Baron M., Verner E. and Xiong W. (2020)*.

A widespread bank failure occurs when one of these two conditions is met:
- failure of a top 5 bank (in terms of assets),
- more than five total bank failures above the normal bank failure rate (broadly defined to include forced mergers, restructurings, government equity injections, and near-collapse bank nationalizations).
<br>
Bank equity crisis refers to a widespread bank failure combined with a cumulative 30% decline in bank equity. The 30% criterion helps identify countries potentially vulnerable to banking crises, but the final verdict must be based on a narrative.


## Currency crises
*Frankel J. and Rose A. (1996)* with *Laeven L. and Valencia F. (2020)* thresholds. 
<br>
A currency crisis refers to a sharp nominal depreciation of the currency vis-a-vis the U.S. dollar that meets the following two conditions:
-	a year-on-year depreciation of at least 30 percent,
-	a year-on-year depreciation at least 10 percentage points higher than the rate of depreciation observed in the previous year.


## Debt crises
*Nguyen T. C., Castro V. and Wood J. (2022)*.
<br>
 A sovereign default occurs if one of the following conditions is met:
- the country does not pay its interest and/or principal obligations on the due date,
- the country defers its obligations by rescheduling or restructuring its debts on less favourable terms than the original ones.


A sovereign debt crisis occurs if one of the following conditions is met:
- total sovereign defaults exceed 1% of GDP for at least three consecutive years, 
- total sovereign defaults exceed 7% of GDP. 


The first year in which either of these conditions is met marks the beginning of a sovereign debt crisis. A debt crisis ends when total sovereign defaults, including debt restructuring or rescheduling, are below 1% of GDP.

# Some results
<p align="center">
  <img width="600" height="450" src="graphs/BGR_cumulative_crises.PNG">
</p>

*The previous graph includes all crisis episodes that could be identified by our criteria. The sample may contain countries for which some criteria are not available simultaneously or not available over the entire period.*
<br>
<p align="center">
  <img width="550" height="500" src="graphs/BGR_twin_triple_same_year.PNG">
</p>
<br>
<p align="center">
  <img width="550" height="500" src="graphs/BGR_twin_triple_one_year_apart.PNG">
</p>

*The Venn diagrams present the results only for the countries for which the three crisis criteria can be calculated and therefore only for the periods for which the three dates are available (this period may differ from one country to another). Twin or triple crises correspond to crises of different types that occur simultaneously or one year apart in **the same country/currency area.***
