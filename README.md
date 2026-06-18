#  Predictive Logistics & Supply Chain Risk Engine (Anti-RTO System)

An end-to-end Data Engineering and Artificial Intelligence platform that identifies high-risk shipments and predicts **Return-to-Origin (RTO)** delivery failures before packages ever leave the warehouse floor.

---

##  The Business Problem & Financial Impact

In the e-commerce and retail logistics industries, **RTO (Return to Origin)**—where a package cannot be delivered and must be shipped back—is a multi-billion dollar leak. Every failed delivery results in:
* **Double Freight Expenses:** Wasted forward and reverse shipping costs.
* **Blocked Inventory:** Products float in transit for days, missing out on real buyers.
* **Operational Overhead:** Unnecessary warehouse repackaging, sorting, and manual handling fees.

###  Project Goal
This engine acts as an early-warning radar system. By analyzing historical shipping lanes, carrier trends, package traits, and real-time environmental factors, it flags high-risk orders ahead of time. This allows logistics managers to proactively intervene (e.g., call the customer to verify an address, change the shipping speed, or swap the courier partner) to protect profit margins.


##  Architectural Blueprint

The platform mimics real-world corporate enterprise architectures by cleanly decoupling ingestion, data-warehousing, business analytics, and predictive artificial intelligence into four separate pipeline stages:

### 🛡️ Layer 1: The Automated Data Guardrail (`src/bouncer.py`)
Raw shipping data coming from field operations is inherently chaotic. This programmatic gatekeeper ingests incoming records and runs immediate quality checks. 
* **Quarantine Staging:** Corrupt rows (e.g., negative package weights, invalid distances) are automatically blocked and routed to an isolated audit layer (`data/quarantined_errors.csv`).
* **Clean Ingestion:** Pristine records are mapped smoothly and batched straight into operational memory.

###  Layer 2: Optimized Enterprise Data Storage (MySQL Schema)
Instead of dumping data into a massive, slow, unstructured flat file, the engine structures information into an enterprise-grade **Star Schema** relational database.

By separating attributes into dedicated **Dimension Tables** and linking them to a central transaction ledger (**`fact_shipments`**), the architecture minimizes file storage space, eliminates textual redundancy, and maximizes data index lookup speeds.

```text
       [ dim_couriers ] (Carrier Metadata)
              |
       [ fact_shipments ] (Central Operational Ledger)
              |
        [ dim_routes ] (Geographic Distances)



###  Layer 3: Courier Performance Leaderboards (`src/lane_analysis.sql`)
Using advanced database analytics (**SQL Window Functions**), the system compiles live operational intelligence. It evaluates historical database logs to automatically calculate carrier failure percentages and rank courier performance (`DENSE_RANK()`) within specific regions, instantly highlighting territory-specific bottlenecks.

###  Layer 4: The Machine Learning Risk Predictor (`src/ml_pipeline.ipynb`)
In real supply chains, successful deliveries drastically outnumber failures, making failures incredibly rare and hard for basic AI to spot (a massive data science challenge called *Class Imbalance*).

The engine extracts clean features from the MySQL database and feeds them into an **XGBoost AI Tree Ensemble** configured with a dynamic **18.07x loss penalty**. This forces the AI to study the rare failure examples intensely, creating an ultra-sensitive risk detector.

---

##  Executive Metrics & Operational Impact

When deployed against a production block of **25,000 real logistics transactions**, the engine delivered the following results:

* **⚡ 77% Failure Capture (Recall):** The AI successfully intercepts nearly **8 out of every 10 real delivery failures** before dispatch.
* **🌲 Automated Class Correction:** Mathematically balances severe data distortions (where failures accounted for just 0.03% of the dataset) using cost-sensitive learning weights.
* **💼 Operational Actionability:** Transitions logistics teams from reactive damage control to proactive cost mitigation, stopping financial loss at the warehouse gate.

---

## 🛠️ Technology Stack
* **Core Language:** Python 3.13
* **Data Storage:** MySQL Server 8.0 (Relational Star Schema Warehouse)
* **Machine Learning Engine:** XGBoost Classifier, Scikit-Learn
* **Data Pipelines:** Pandas, Native DBAPI2 Database Connectors

---

## 💻 Technical Setup & Execution

### 1. Initialize the Relational Database
```bash
mysql -u root -p < src/database_setup.sql

### 2. Stream Data Through Ingestion Guardrail
```bash
python src/bouncer.py

### 3. Run the Machine Learning Pipeline
Open src/ml_pipeline.ipynb in your IDE, connect your environment kernel, and click "Run All" to train the prediction model.