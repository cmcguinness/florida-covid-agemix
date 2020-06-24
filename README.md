# Florida Covid Agemix

This is a simple (ish) utility that pulls down the case data from the Florida Department of Health, converts it to a pandas DataFrame, and then generates a chart showing how the relative comparison of age brackets in the positive results.

If you run it on the state as a whole, it presents a daily tracking chart of the mix.  If you run it on a single county, it presents a week by week tracking as daily results are way to noisy to use.

The DataFrame is written out to a csv file in the snapshots subdirectory for later comparisons or preservation in case of data deletion or modification by the DOH.

The chart generated is written out to the subdirectory images and is time and (if at the county level) name stamped to indicate what it represents.

Nb: the code quality isn't that great -- it's mostly been a scramble to work on this in my limited spare time, so working is "good enough".  I hope that these programs have no use very soon.

Charles McGuinness @SocialSeerCom on Twitter

