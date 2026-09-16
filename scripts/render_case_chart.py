"""Render the invented forecast-review fixture; optional matplotlib dependency."""
import csv
from decimal import Decimal
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parents[1]
inputs = root / 'flagship/forecast-review/inputs'
def series(name, key, value):
    with (inputs / name).open() as f:
        return {r[key]: Decimal(r[value]) for r in csv.DictReader(f)}
actual = series('actual.csv', 'Month', 'Observed')
a = series('candidate-a.csv', 'period', 'Forecast')
b = series('candidate-b.csv', 'snapshot', 'prediction')
common = set(actual) & set(a) & set(b)
def mae(pred, keys):
    return float(sum(abs(pred[k]-actual[k]) for k in keys)/len(keys))
fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), facecolor='#f5f7fa')
fig.suptitle('The ranking changes when the sample is fair.', x=.055, y=.96, ha='left', fontsize=21, fontweight='bold', color='#132c42')
for ax, title, values, counts in zip(axes, ['BEFORE · Different available months', 'AFTER · Same seven months'], [[mae(a,set(a)),mae(b,set(b))],[mae(a,common),mae(b,common)]], [[9,10],[7,7]]):
    ax.set_facecolor('#f5f7fa')
    ax.barh([1,0],values,height=.40,color=['#597a96','#127b70'])
    for y,v,n in zip([1,0],values,counts):ax.text(v+.10,y,f'{v:.2f}  /  {n} months',va='center',fontsize=12,color='#132c42')
    ax.set_yticks([1,0],['Candidate A','Candidate B']);ax.set_xlim(0,6);ax.set_ylim(-.55,1.6)
    ax.set_title(title,loc='left',fontsize=12,pad=15,fontweight='bold',color='#132c42')
    ax.set_xlabel('Mean absolute error (USD) · lower is better',fontsize=10,color='#526775')
    ax.set_xticks([0,1,2,3,4,5]);ax.tick_params(axis='both',length=0,labelcolor='#526775')
    for spine in ax.spines.values():spine.set_visible(False)
    ax.set_axisbelow(True);ax.grid(axis='x',color='#e0e6eb')
fig.text(.055,.045,'Invented teaching data. Five of twelve months remain excluded: this is not full-year model approval.',fontsize=11,color='#526775')
fig.subplots_adjust(left=.13,right=.96,top=.73,bottom=.22,wspace=.45)
fig.savefig(root/'assets/forecast-ranking.png',dpi=180,facecolor=fig.get_facecolor())
plt.close(fig)
