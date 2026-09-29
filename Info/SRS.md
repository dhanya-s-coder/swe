# Factory Adjuster Simulation

## 1. Functional requirements

- **FR-1 Scenario setup (implemented with UI guard):** The system shall accept machine groups with category, positive machine count, positive MTTF, and positive fixed repair time through `/simulate`. The dashboard disables running when machine groups are absent; the API itself does not currently reject an empty machine list.
- **FR-2 Adjuster setup:** The system shall accept adjusters with one or more machine-category skills. The API requires each adjuster to have a skill; unique IDs are checked by the UI only and should also be validated by the API.
- **FR-3 Timeline and reproducibility:** The system shall accept a positive simulation duration, warm-up period shorter than duration, and random seed. Identical valid inputs and seed should reproduce the same sampled run, subject to implementation/runtime consistency.
- **FR-4 Failure scheduling:** The simulation shall schedule each machine's first failure and subsequent failures from positive Gaussian intervals centered on that machine's MTTF.
- **FR-5 Failure handling:** On failure, the machine shall stop accumulating running time and become assigned for repair if a compatible idle adjuster exists; otherwise it shall wait.
- **FR-6 Dispatch:** The system shall dispatch waiting compatible machines to idle skilled adjusters. Selection shall favor the adjuster with the fewest skills, then adjuster ID. Compatible waiting work shall be considered in waiting order.
- **FR-7 Repair completion:** On repair completion, the adjuster shall become idle, the machine shall resume operation, and a new failure shall be scheduled.
- **FR-8 Results:** `/simulate` shall return overall and per-category machine utilization, adjuster utilization, counts, failures, waiting machines/queue length, downtime, and per-machine status/efficiency.
- **FR-9 Persistence:** When `save=true`, the service shall attempt to save input and results in MongoDB. A persistence failure shall not discard the computed result and shall be reported as a warning.
- **FR-10 Experiments:** `/experiment` shall evaluate the requested combinations of machine-count multiplier, MTTF multiplier, and adjuster count, summarize repeated runs, and report an optimum using configured selection criteria.
- **FR-11 Dashboard:** The UI shall let a user add/remove machine groups and adjusters, set simulation duration and seed, run a simulation, and view aggregate/category/machine metrics.
- **FR-12 Validation (partial):** The API rejects warm-up greater than or equal to duration, an empty adjuster list, and adjusters without skills. Pydantic validates positive machine count, MTTF, and repair time. Empty machine lists, duplicate IDs, and category/skill mismatches are not currently rejected by the API.

## 2. Non-functional requirements

- **NFR-1 Performance:** Simulation time shall depend on the number of events and scenario size rather than waiting for virtual time to pass; the timeline is simulated computationally.
- **NFR-2 Reproducibility:** A seed shall initialize the pseudo-random generator for repeatable experiments.
- **NFR-3 Separation of concerns:** UI, API validation/orchestration, simulation logic, and persistence shall remain separate modules.
- **NFR-4 Data protection:** Database credentials shall be supplied through environment configuration and excluded from version control.
- **NFR-5 Interpretability:** Returned measures shall define their observation interval and denominator; experiment outputs shall retain scenario factors and uncertainty summaries.
