# PHI Architecture Notes

## System Direction

PHI is being designed as an AcademicOS that combines academic data, schedules,
assessments, goals, and automation into a structured system.

## Core Layers

1. **Data Layer**
   - Student information
   - Courses
   - Assessments
   - Marks
   - Grades
   - Academic goals

2. **Integration Layer**
   - Academic portals
   - Email
   - Calendar
   - Learning-management systems

3. **Intelligence Layer**
   - Planning
   - Analysis
   - Recommendations
   - Academic performance projections

4. **Interface Layer**
   - CLI and development tools
   - Future user-facing interfaces

## Design Constraint

The intelligence layer should not silently invent missing academic information.
Unknown data must remain distinguishable from verified data.
