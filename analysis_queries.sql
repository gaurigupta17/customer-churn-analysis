-- sql/analysis_queries.sql
-- Comments explain the purpose of each query block.

-- ==========================================
-- 1. OVERALL CHURN & REVENUE IMPACT
-- ==========================================
-- This query calculates total customers, churned count, churn rate, and monthly revenue metrics.
-- It establishes the baseline business problem.
SELECT
    COUNT(*) as total_customers,
    SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) as churned_customers,
    ROUND(SUM(CASE WHEN churn = 'Yes' THEN 1.0 ELSE 0.0 END) / COUNT(*) * 100, 2) as churn_rate_pct,
    ROUND(SUM(monthly_charges), 2) as total_monthly_charges,
    ROUND(SUM(CASE WHEN churn = 'Yes' THEN monthly_charges ELSE 0 END), 2) as lost_monthly_revenue,
    ROUND(AVG(monthly_charges), 2) as avg_monthly_charges_overall,
    ROUND(AVG(CASE WHEN churn = 'Yes' THEN monthly_charges ELSE NULL END), 2) as avg_monthly_charges_churned,
    ROUND(AVG(CASE WHEN churn = 'No' THEN monthly_charges ELSE NULL END), 2) as avg_monthly_charges_retained
FROM customer_churn;


-- ==========================================
-- 2. CONTRACT TYPE & PAYMENT METHOD CORRELATION
-- ==========================================
-- Traditional Telecom relies heavily on long-term contracts.
-- This query checks if month-to-month contracts have substantially higher churn.
SELECT
    contract,
    COUNT(*) as total_customers,
    SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) as churned_customers,
    ROUND(SUM(CASE WHEN churn = 'Yes' THEN 1.0 ELSE 0.0 END) / COUNT(*) * 100, 2) as churn_rate_pct,
    ROUND(SUM(monthly_charges), 2) as total_charges
FROM customer_churn
GROUP BY contract
ORDER BY churn_rate_pct DESC;

-- Analysis by payment method to find billing issues
SELECT
    payment_method,
    COUNT(*) as total_customers,
    SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) as churned_customers,
    ROUND(SUM(CASE WHEN churn = 'Yes' THEN 1.0 ELSE 0.0 END) / COUNT(*) * 100, 2) as churn_rate_pct
FROM customer_churn
GROUP BY payment_method
ORDER BY churn_rate_pct DESC;


-- ==========================================
-- 3. TENURE COHORT ANALYSIS
-- ==========================================
-- This query segments customers into cohorts based on their tenure (months) to identify when churn is highest.
-- Typically, the first 6-12 months are high-risk.
SELECT
    CASE 
        WHEN tenure <= 6 THEN '01: 0 - 6 Months'
        WHEN tenure <= 12 THEN '02: 7 - 12 Months'
        WHEN tenure <= 24 THEN '03: 1 - 2 Years'
        WHEN tenure <= 36 THEN '04: 2 - 3 Years'
        WHEN tenure <= 48 THEN '05: 3 - 4 Years'
        WHEN tenure <= 60 THEN '06: 4 - 5 Years'
        ELSE '07: 5+ Years'
    END as tenure_cohort,
    COUNT(*) as total_customers,
    SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) as churned_customers,
    ROUND(SUM(CASE WHEN churn = 'Yes' THEN 1.0 ELSE 0.0 END) / COUNT(*) * 100, 2) as churn_rate_pct
FROM customer_churn
GROUP BY tenure_cohort
ORDER BY tenure_cohort ASC;


-- ==========================================
-- 4. SERVICE TYPE & TECH SUPPORT IMPACT
-- ==========================================
-- In traditional telecom, service quality and customer support are primary drivers of retention.
-- This query analyzes churn rates across internet service packages and tech support subscriptions.
SELECT
    internet_service,
    COUNT(*) as total_customers,
    SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) as churned_customers,
    ROUND(SUM(CASE WHEN churn = 'Yes' THEN 1.0 ELSE 0.0 END) / COUNT(*) * 100, 2) as churn_rate_pct
FROM customer_churn
GROUP BY internet_service
ORDER BY churn_rate_pct DESC;

-- Churn rate for customers with and without Tech Support (among those who have internet service)
SELECT
    tech_support,
    COUNT(*) as total_customers,
    SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) as churned_customers,
    ROUND(SUM(CASE WHEN churn = 'Yes' THEN 1.0 ELSE 0.0 END) / COUNT(*) * 100, 2) as churn_rate_pct
FROM customer_churn
WHERE internet_service <> 'No'
GROUP BY tech_support
ORDER BY churn_rate_pct DESC;


-- ==========================================
-- 5. PROFILE RISKS: SENIOR CITIZENS, PARTNERS & DEPENDENTS
-- ==========================================
-- Investigates churn difference among customer profiles.
SELECT
    senior_citizen,
    COUNT(*) as total_customers,
    SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) as churned_customers,
    ROUND(SUM(CASE WHEN churn = 'Yes' THEN 1.0 ELSE 0.0 END) / COUNT(*) * 100, 2) as churn_rate_pct
FROM customer_churn
GROUP BY senior_citizen;
