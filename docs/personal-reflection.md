# RD1 personal reflection

The passage-splitting result made me think about how easily a clause can lose its meaning. For 6.47% of annotated clauses, no single passage contained at least 90% of the clause. A highlight could show the main obligation while leaving its exception in the next passage. I would check the surrounding text before relying on a highlight.

The dashboard showed me that the API was healthy and returning results. Seeing about 88% red-flag recall on regular contracts could have made me confident in the tool overall, but recall fell to about 53% on franchise agreements. I would report the two results separately and route franchise agreements to full manual review. I would use lawyer-verified results and actual franchise review volumes to decide whether retraining was worth the cost.

I would start with the online API because it returned review packs quickly in the workload we tested. If a test at realistic peak demand repeatedly exceeded our proposed one-second p95 target, I would trial a tiered service. The entry tier would include a quota of immediate reviews, with additional contracts queued for quieter periods. The higher tier would get priority. I would adopt the change if the trial restored online response times and batch packs arrived within the promised window.
