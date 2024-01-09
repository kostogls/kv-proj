-- query 1 --
SELECT 
	pss.pid,
	pd.plan_descr,
	pss.total_planned_sales,
	tf.total_forecast
FROM
	-- subquery to find the total_planned_sales per pid
	(SELECT ps.pid, ROUND(SUM(ps.planned_sales),2) AS total_planned_sales
	FROM plansales ps
	GROUP BY ps.pid) pss
JOIN
	(-- subquery to get total_forecast per pid of only forecast table, but we need to join it with plansales to get the right dates to compare. 
	 -- we use join to compare only same dates and not different ones of a table (eg left join) 
	SELECT ps.pid, SUM(f.forecast) AS total_forecast
	FROM forecast f
	JOIN plansales ps ON ps.date = f.date AND ps.item_id = f.item_id AND ps.store_id = f.store_id
	GROUP BY ps.pid) tf
ON pss.pid = tf.pid
-- join the final table with total sales and forecast with plandigest to get the plan_descr in the output as well for better readability
-- the join here is more efficient because the final total table has in general the least rows we can get in comparasion with joining inside the query 
JOIN plandigest pd
ON pd.pid = pss.pid


-- query 2 --
SELECT 
	tps.pid,
	pd.plan_descr,
	tps.cluster_descr,
	tps.total_planned_sales,
	tf.total_forecast 
FROM
	( -- subquery to find total_planned_sales per cluster for each pid only from plansales table
	SELECT ps.pid, pc.cluster_descr, ROUND(SUM(ps.planned_sales), 2) as total_planned_sales
	FROM plansales ps 
	JOIN plancluster pc ON pc.pid = ps.pid AND pc.store_id = ps.store_id
	GROUP BY ps.pid, pc.cluster_descr
	ORDER BY ps.pid, pc.cluster_descr
	) tps
JOIN
	(-- subquery to find total_forecast per cluster for each pid only from plansales table
	 -- we need to join with plan sales and then cluster to get cluster info about forecast dates 
	SELECT ps.pid, pc.cluster_descr, SUM(forecast) AS total_forecast
	FROM forecast f
	JOIN plansales ps ON ps.date = f.date AND ps.item_id = f.item_id AND ps.store_id = f.store_id
	JOIN plancluster pc ON pc.pid = ps.pid AND pc.store_id = ps.store_id
	GROUP BY ps.pid, pc.cluster_descr) tf
ON tps.pid = tf.pid and tps.cluster_descr = tf.cluster_descr
-- join the final table with total sales and forecast with plandigest to get the plan_descr in the output as well for better readability
JOIN plandigest pd
ON pd.pid = tps.pid


-- pre query 3 --
-- view to return table containing the joined plansales and sales on same week id, store id, item id (because we use it in 2 queries)
CREATE OR REPLACE VIEW ps_s_per_planweeks_combined AS
(
	SELECT *
	FROM
		( -- subquery to join plansales with calendar table and take the corresponding week of the plansale date
		SELECT ps.pid, ps.date as planned_sales_date, ps.item_id as ps_item_id, ps.store_id as ps_store_id, ps.planned_sales, c.year_week, c.weekid
		FROM plansales ps
		JOIN calendar c ON ps.date = c.date
		 ) psweeks
	JOIN 
		( -- subquery to join sales with calendar table and take the corresponding week of the sale date
		SELECT s.date as sales_date, s.item_id as s_item_id, s.store_id as s_store_id, s.sales, c.year_week as s_year_week
		FROM sales s
		JOIN calendar c ON s.date = c.date
		) sweeks
	ON psweeks.year_week = sweeks.s_year_week AND psweeks.ps_item_id = sweeks.s_item_id AND psweeks.ps_store_id = sweeks.s_store_id
)

-- query 3 --

-- join the plansales and sales table on same weeks of year that there is plan information
SELECT ps_s_per_planweeks_combined.pid, pd.plan_descr, pc.cluster_descr, ROUND(SUM(ps_s_per_planweeks_combined.planned_sales), 2) AS total_planned_sales, SUM(ps_s_per_planweeks_combined.sales) AS total_sales
FROM ps_s_per_planweeks_combined
JOIN plancluster pc ON pc.pid = ps_s_per_planweeks_combined.pid and pc.store_id = ps_s_per_planweeks_combined.s_store_id
JOIN plandigest pd ON ps_s_per_planweeks_combined.pid = pd.pid
GROUP BY ps_s_per_planweeks_combined.pid, pd.plan_descr,  pc.cluster_descr
ORDER BY ps_s_per_planweeks_combined.pid, pc.cluster_descr
-- result planned sales are less because not all the dates of weeks are present in the sales data
-- also, i checked if total sales this query outputs are equal to the total sales for a plan in the original file, but they are ~100 less
-- because it seems that some item - stores ids from plan sales do not correspond to the sales file. (they're missing from sales)

	
-- pre query 4  --

-- create a view with tha table that has all the differences of items sales between plan sales and last year sales per item id and per cluster
-- we need that view to keep the max difference (growth) and keep the item id as well
CREATE OR REPLACE VIEW cluster_item_growth_view AS 
(
	SELECT cl_st_item_sales.cluster_descr, cl_st_item_sales.s_item_id, (cl_st_item_sales.total_planned_sales - cl_st_item_sales.total_sales) as growth
	FROM
		(
			SELECT  pc.cluster_descr, ps_s_per_planweeks_combined.s_item_id, ROUND(SUM(ps_s_per_planweeks_combined.planned_sales), 2) AS total_planned_sales, SUM(ps_s_per_planweeks_combined.sales) AS total_sales
			FROM ps_s_per_planweeks_combined
			JOIN plancluster pc ON pc.pid = ps_s_per_planweeks_combined.pid and pc.store_id = ps_s_per_planweeks_combined.s_store_id
			GROUP BY pc.cluster_descr, ps_s_per_planweeks_combined.s_item_id
			ORDER BY pc.cluster_descr, ps_s_per_planweeks_combined.s_item_id
		) cl_st_item_sales
	ORDER BY cl_st_item_sales.cluster_descr, growth desc
)


-- query 4  --
SELECT cigv.cluster_descr, cigv.s_item_id, cigv.growth as max_growth
FROM
	cluster_item_growth_view cigv
WHERE cigv.growth IN 
	(
		SELECT MAX(cigv.growth) as max_growth
		FROM
			cluster_item_growth_view cigv
		GROUP BY cigv.cluster_descr
	)

