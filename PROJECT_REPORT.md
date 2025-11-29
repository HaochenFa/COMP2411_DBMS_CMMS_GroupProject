# PolyU CMMS - Comprehensive Project Report

## Campus Maintenance and Management System

**Report Generated**: November 29, 2025
**Project Repository**: `HaochenFa/COMP2411_DBMS_CMMS_GroupProject`
**Current Branch**: `haochenfa/tests`

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [System Analysis](#2-system-analysis)
3. [Strengths & Weaknesses](#3-strengths--weaknesses)
4. [Areas for Improvement](#4-areas-for-improvement)
5. [Tech Stack & Implementation Details](#5-tech-stack--implementation-details)
6. [Functionalities](#6-functionalities)
7. [Conclusion](#7-conclusion)

---

## 1. System Overview

### 1.1 Project Purpose

The **PolyU CMMS** is a database-driven Campus Maintenance and Management System designed for **The Hong Kong Polytechnic University (PolyU)**. It serves as a centralized platform to manage campus maintenance activities, personnel, facilities, schools, and events.

### 1.2 Core Objectives

- Provide real-time visibility into campus maintenance operations
- Enable efficient personnel and school affiliation management
- Track activities and events across campus locations
- Ensure safety awareness through chemical hazard tracking
- Offer data-driven insights through an executive dashboard

### 1.3 Target Users

- Campus administrators and facility managers
- Maintenance supervisors and workers
- Academic staff and department heads
- System developers (via Dev Console)

### 1.4 Development Timeline

```mermaid
gantt
    title PolyU CMMS Development Timeline
    dateFormat  YYYY-MM-DD
    section Phase 1
    Project Initialization     :done, init, 2025-11-17, 1d
    section Phase 2
    Backend Setup (Flask/DB)   :done, backend1, 2025-11-26, 1d
    UI Development (React)     :done, ui1, 2025-11-26, 1d
    section Phase 3
    Docker Integration         :done, docker, 2025-11-27, 1d
    Electron Wrapper           :done, electron, 2025-11-27, 1d
    UI Refinement (PolyU Theme):done, ui2, 2025-11-27, 1d
    section Phase 4
    Feature Addition           :done, features, 2025-11-28, 1d
    Documentation              :done, docs, 2025-11-28, 1d
    section Phase 5
    Test Suite Implementation  :done, testing, 2025-11-29, 1d
    section Phase 6
    PDF Report Generation      :done, reports, 2025-11-29, 1d
```

| Phase | Date | Milestone |
|-------|------|-----------|
| Initialization | Nov 17 | Project setup, .gitignore configuration |
| Backend Setup | Nov 26 | Flask API, database schema, initial CRUD |
| UI Development | Nov 26 | React frontend, dark theme, Recharts integration |
| Docker Integration | Nov 27 | Containerization, docker-compose setup |
| Electron Wrapper | Nov 27 | Desktop application packaging |
| UI Refinement | Nov 27 | PolyU branding, red wine theme |
| Feature Addition | Nov 28 | Safety Search, Dev Console, cascading dropdowns |
| Documentation | Nov 28 | Comprehensive README update |
| Testing | Nov 29 | Comprehensive test suites (pytest, Vitest) |
| Report Generation | Nov 29 | PDF report generation with data analysis |

---

## 2. System Analysis

### 2.1 Architecture Overview

```mermaid
flowchart TB
    subgraph Desktop["Desktop Layer"]
        E[Electron App<br/>Cross-platform Wrapper]
    end
    
    subgraph Frontend["Frontend Layer"]
        R[React + Vite<br/>Port 5173]
        RC[Recharts<br/>Data Visualization]
        AX[Axios<br/>HTTP Client]
    end
    
    subgraph Backend["Backend Layer"]
        F[Flask REST API<br/>Port 5050]
        CORS[Flask-CORS]
    end
    
    subgraph Database["Database Layer"]
        M[(MySQL 8.0<br/>cmms_db)]
    end
    
    subgraph Docker["Docker Compose"]
        DC[Container Orchestration]
    end
    
    E --> R
    R --> RC
    R --> AX
    AX -->|HTTP/JSON| F
    F --> CORS
    F -->|mysql-connector| M
    
    DC -.->|manages| R
    DC -.->|manages| F
    DC -.->|manages| M
```

### 2.2 Database Entity-Relationship Model

```mermaid
erDiagram
    Person ||--o| Profile : "has"
    Person ||--o{ Activity : "organizes"
    Person }o--o{ Activity : "participates in"
    Person }o--o{ School : "affiliated with"
    Person ||--o{ Person : "supervises"
    
    School ||--o{ Location : "contains"
    Location ||--o{ Activity : "hosts"
    Location ||--o{ Maintenance : "requires"
    
    ExternalCompany ||--o{ Maintenance : "contracts"
    
    Person {
        varchar personal_id PK
        varchar name
        varchar gender
        date date_of_birth
        date entry_date
        varchar supervisor_id FK
    }
    
    Profile {
        int profile_id PK
        varchar personal_id FK
        varchar job_role
        varchar status
    }
    
    School {
        varchar school_name PK
        varchar department
        varchar faculty
        varchar hq_building
    }
    
    Location {
        int location_id PK
        varchar room
        varchar floor
        varchar building
        varchar type
        varchar campus
        varchar school_name FK
    }
    
    Activity {
        varchar activity_id PK
        varchar type
        datetime time
        varchar organiser_id FK
        int location_id FK
    }
    
    Maintenance {
        int maintenance_id PK
        varchar type
        varchar frequency
        int location_id FK
        boolean active_chemical
        int contracted_company_id FK
    }
    
    ExternalCompany {
        int company_id PK
        varchar name
        varchar contact_info
    }
    
    Participation {
        varchar personal_id PK
        varchar activity_id PK
    }
    
    Affiliation {
        varchar personal_id PK
        varchar school_name PK
    }
```

### 2.3 Data Flow Diagram

```mermaid
flowchart LR
    subgraph Users["User Interface"]
        U1[Admin]
        U2[Manager]
        U3[Staff]
    end

    subgraph Frontend["React Frontend"]
        D[Dashboard]
        EM[Entity Manager]
        RM[Relationship Manager]
        SS[Safety Search]
        RG[Report Generator]
        DC[Dev Console]
    end

    subgraph API["Flask API"]
        CRUD[CRUD Endpoints]
        RPT[Report Endpoints]
        QRY[Query Endpoint]
        IMP[Import Endpoint]
    end

    subgraph DB["MySQL Database"]
        T1[(Person)]
        T2[(School)]
        T3[(Location)]
        T4[(Activity)]
        T5[(Maintenance)]
    end

    U1 & U2 & U3 --> D & EM & RM & SS & RG & DC
    D --> RPT
    EM & RM --> CRUD
    SS --> CRUD
    RG --> RPT
    DC --> QRY
    EM --> IMP

    CRUD & RPT & QRY & IMP --> T1 & T2 & T3 & T4 & T5
```

---

## 3. Strengths & Weaknesses

### 3.1 Strengths ✅

```mermaid
mindmap
  root((Strengths))
    Architecture
      Clean 3-tier separation
      RESTful API design
      Reusable components
    Deployment
      Docker containerization
      Single-command startup
      Cross-platform Electron
    User Experience
      PolyU branded theme
      Interactive dashboards
      Cascading dropdowns
    Access Control
      Role-based permissions
      Three user roles
      UI permission enforcement
    Developer Tools
      Dev Console SQL interface
      Query history persistence
      Bulk CSV import
    Safety Features
      Chemical hazard tracking
      Warning flag system
    Business Rules
      Profile limits enforcement
      Referential integrity
    Testing
      139 automated tests
      Backend pytest suite
      Frontend Vitest suite
```

| Category | Strength | Details |
|----------|----------|---------|
| **Architecture** | Clean 3-tier separation | Frontend, Backend API, Database are fully decoupled |
| **Deployment** | Docker containerization | Single-command deployment via `docker-compose` |
| **Cross-platform** | Electron desktop app | Native-like experience on Windows/macOS/Linux |
| **UX Design** | PolyU-branded theme | Professional red wine and white color scheme |
| **Access Control** | Role-based permissions | Admin, Executive, Staff roles with granular permissions |
| **Data Visualization** | Recharts integration | Interactive bar charts, pie charts for analytics |
| **Developer Tools** | Dev Console | Raw SQL execution with query history persistence |
| **Safety Features** | Chemical hazard tracking | Safety Search with warning flags for hazardous tasks |
| **Data Management** | Bulk CSV import | Efficient batch data loading capability |
| **Dynamic Forms** | Cascading dropdowns | Smart Building → Room selection with filtering |
| **Business Rules** | Profile limits | Enforced limits: 10 Mid-level Managers, 50 Base-level Workers |
| **Code Quality** | Reusable components | Generic `EntityManager` and `RelationshipManager` |
| **API Design** | RESTful endpoints | Consistent CRUD patterns across all entities |
| **Error Handling** | Comprehensive error responses | JSON error messages with MySQL error codes |
| **Data Persistence** | localStorage for Dev Console | Query history survives browser refresh |
| **PDF Reports** | ReportLab + Matplotlib | Professional PDF generation with charts |
| **Report Customization** | Selectable sections | Users choose which data to include |
| **Testing** | Comprehensive test suites | 139 automated tests across backend, frontend, desktop |
| **Test Coverage** | Multi-layer testing | Unit tests, integration tests, API tests |

### 3.2 Weaknesses ⚠️

```mermaid
mindmap
  root((Weaknesses))
    Security
      Frontend-only RBAC
      Hardcoded credentials
      No backend auth
    Validation
      Limited server-side
      SQL injection risk
    Performance
      No pagination
      No caching
      N+1 queries
    Audit
      No logging
      No backup strategy
```

| Category | Weakness | Impact |
|----------|----------|--------|
| **Backend Authentication** | Frontend-only role-based access control | API endpoints not protected at backend level |
| **API Security** | Dev Console allows all SQL queries | Vulnerable to data manipulation/deletion |
| **Database Security** | Hardcoded credentials in docker-compose | Security risk in production |
| **Input Validation** | Limited server-side validation | Potential for invalid data entry |
| **Pagination** | No pagination for large datasets | Performance degradation with data growth |
| **Caching** | No caching mechanism | Repeated database queries for same data |
| **Transactions** | Limited transaction management | Partial failures possible in bulk operations |
| **Audit Trail** | No audit logging | Cannot track who changed what |
| **Backup Strategy** | No documented backup procedures | Data loss risk |
| **API Rate Limiting** | No rate limiting | Vulnerable to abuse/DoS |
| **Frontend State** | No global state management | Prop drilling, potential inconsistencies |

---

## 4. Areas for Improvement

### 4.1 Priority Matrix

```mermaid
quadrantChart
    title Improvement Priority Matrix
    x-axis Low Effort --> High Effort
    y-axis Low Impact --> High Impact
    quadrant-1 Plan Carefully
    quadrant-2 Implement First
    quadrant-3 Consider Later
    quadrant-4 Quick Wins

    Backend Auth: [0.7, 0.95]
    Input Validation: [0.4, 0.8]
    Pagination: [0.3, 0.6]
    Audit Logging: [0.5, 0.7]
    Caching: [0.6, 0.5]
    Mobile UI: [0.7, 0.4]
    PDF Export: [0.5, 0.3]
    E2E Testing: [0.6, 0.6]
```

### 4.2 High Priority 🔴

1. **Implement Backend Authentication** ⚠️ (Partially Done)
   - ✅ Frontend role-based access control implemented (Admin, Executive, Staff)
   - ✅ UI permission enforcement for CRUD operations
   - ⏳ Add JWT-based backend authentication
   - ⏳ Protect API endpoints with role verification

2. **Secure the Dev Console**
   - ✅ Restricted to Admin role only via frontend permissions
   - ⏳ Add backend role verification
   - ⏳ Add query whitelist/blacklist
   - ⏳ Implement query auditing

3. **Environment Configuration**
   - Use environment variables for all secrets
   - Separate configs for dev/staging/production

4. **Add End-to-End Testing**
   - E2E tests for critical workflows (Playwright/Cypress)
   - Automated browser testing for UI flows

### 4.3 Medium Priority 🟡

1. **Implement Pagination**
   - Add pagination to all list endpoints
   - Frontend table pagination with page size options

2. **Add Input Validation**
   - Server-side schema validation (marshmallow/pydantic)
   - Client-side form validation with error messages

3. **Implement Audit Logging**
   - Track create/update/delete operations
   - Store user, timestamp, and changes

4. **Add Global State Management**
   - Implement Redux or Zustand for React state
   - Centralized data fetching with React Query

### 4.4 Lower Priority 🟢

1. **Performance Optimizations**
   - Add database indexing on frequently queried columns
   - Implement caching layer (Redis)
   - Optimize N+1 queries

2. **Enhanced Reporting** ✅ (Partially Implemented)
   - ~~Export reports to PDF~~ ✅ Completed
   - Custom date range filtering
   - Scheduled report generation
   - Excel export option

3. **Mobile Responsiveness**
   - Improve mobile UI for tablets/phones
   - Progressive Web App (PWA) support

---

## 5. Tech Stack & Implementation Details

### 5.1 Technology Stack

```mermaid
flowchart TB
    subgraph Frontend["Frontend Stack"]
        direction TB
        React[React 18]
        Vite[Vite Build Tool]
        RR[React Router DOM]
        Axios[Axios HTTP]
        Recharts[Recharts]
        Lucide[Lucide Icons]
    end

    subgraph Backend["Backend Stack"]
        direction TB
        Flask[Flask]
        FlaskCORS[Flask-CORS]
        MySQL_Conn[mysql-connector-python]
        Dotenv[python-dotenv]
    end

    subgraph Database["Database"]
        MySQL[(MySQL 8.0)]
    end

    subgraph DevOps["DevOps Stack"]
        Docker[Docker]
        Compose[Docker Compose]
        Electron[Electron]
    end

    Frontend --> Backend
    Backend --> Database
    DevOps --> Frontend
    DevOps --> Backend
    DevOps --> Database
```

| Layer | Technology | Version/Details |
|-------|------------|-----------------|
| **Frontend** | React | Functional components with Hooks |
| **Build Tool** | Vite | Fast HMR, ESBuild bundling |
| **UI Icons** | lucide-react | Modern icon library |
| **Charts** | Recharts | React charting library |
| **HTTP Client** | Axios | Promise-based HTTP |
| **Routing** | react-router-dom | SPA navigation |
| **Backend** | Flask | Python web framework |
| **CORS** | flask-cors | Cross-origin resource sharing |
| **Database Driver** | mysql-connector-python | MySQL connectivity |
| **Environment** | python-dotenv | .env file support |
| **Database** | MySQL 8.0 | Relational database |
| **Desktop** | Electron | Cross-platform app |
| **Container** | Docker | Application containerization |
| **Orchestration** | Docker Compose | Multi-container management |

### 5.2 API Endpoint Summary

#### Entity CRUD Endpoints

| Endpoint | Methods | Description |
|----------|---------|-------------|
| `/api/persons` | GET, POST | List/create persons |
| `/api/persons/<id>` | PUT, DELETE | Update/delete person |
| `/api/profiles` | GET, POST | List/create profiles |
| `/api/schools` | GET, POST | List/create schools |
| `/api/schools/<id>` | PUT, DELETE | Update/delete school |
| `/api/locations` | GET, POST | List/create locations |
| `/api/locations/<id>` | PUT, DELETE | Update/delete location |
| `/api/activities` | GET, POST | List/create activities |
| `/api/activities/<id>` | PUT, DELETE | Update/delete activity |
| `/api/maintenance` | GET, POST | List/create maintenance tasks |
| `/api/maintenance/<id>` | PUT, DELETE | Update/delete maintenance |
| `/api/external-companies` | GET, POST | List/create companies |

#### Relationship Endpoints

| Endpoint | Methods | Description |
|----------|---------|-------------|
| `/api/participations` | GET, POST | Person-Activity links |
| `/api/affiliations` | GET, POST | Person-School links |

#### Report Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/reports/maintenance-summary` | Maintenance by location/type |
| `/api/reports/people-summary` | People by role/status |
| `/api/reports/activities-summary` | Activities by type/organizer |
| `/api/reports/school-stats` | School statistics |
| `/api/reports/maintenance-frequency` | Frequency analysis |

#### Special Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/health` | Health check |
| `/api/query` | Execute SQL (Dev Console) |
| `/api/search/safety` | Chemical hazard search |
| `/api/import` | Bulk CSV import |

#### PDF Report Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/reports/comprehensive-data` | Get all report data (JSON) |
| `/api/reports/generate-pdf` | Generate comprehensive PDF report |

### 5.3 Frontend Component Architecture

```mermaid
flowchart TB
    subgraph App["App.jsx"]
        Layout["Layout.jsx<br/>(Sidebar Navigation)"]
    end

    subgraph Pages["Page Components"]
        Dashboard["Dashboard.jsx<br/>Executive Overview"]

        subgraph EntityMgmt["Entity Management"]
            EM["EntityManager.jsx<br/>(Generic CRUD)"]
            PM["Person Management"]
            SM["School Management"]
            AM["Activity Management"]
            MM["Maintenance Management"]
        end

        subgraph RelMgmt["Relationship Management"]
            RM["RelationshipManager.jsx"]
            Part["Participations"]
            Aff["Affiliations"]
        end

        SS["SafetySearch.jsx<br/>Chemical Hazard Search"]
        DC["DevConsole.jsx<br/>SQL Query Interface"]
    end

    Layout --> Dashboard
    Layout --> EM
    EM --> PM & SM & AM & MM
    Layout --> RM
    RM --> Part & Aff
    Layout --> SS
    Layout --> DC
```

### 5.4 Database Schema Highlights

**Key Design Decisions:**

| Decision | Implementation | Rationale |
|----------|----------------|-----------|
| **Dynamic Age Calculation** | `TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE())` | Avoids stale data, always current |
| **Building Denormalization** | VARCHAR attribute in Location | Simplified schema, reduced joins |
| **Profile Limits** | API-level enforcement | 10 Mid-level Managers, 50 Base-level Workers |
| **Chemical Tracking** | Boolean `active_chemical` flag | Simple safety search implementation |
| **Self-referencing FK** | `supervisor_id` → `personal_id` | Hierarchical supervisor relationships |

---

## 6. Functionalities

### 6.1 Feature Overview

```mermaid
flowchart LR
    subgraph Core["Core Features"]
        D[📊 Dashboard]
        CRUD[📝 Entity CRUD]
        REL[🔗 Relationships]
    end

    subgraph Access["Access Control"]
        RBAC[🔐 Role-Based Access]
        PERM[👤 User Permissions]
    end

    subgraph Safety["Safety Features"]
        SS[⚠️ Safety Search]
        CH[🧪 Chemical Tracking]
    end

    subgraph DevTools["Developer Tools"]
        DC[💻 Dev Console]
        IMP[📥 CSV Import]
    end

    subgraph Reports["Analytics & Export"]
        MS[Maintenance Summary]
        PS[People Summary]
        AS[Activity Summary]
        SchS[School Stats]
        PDF[📄 PDF Reports]
    end

    RBAC --> D & CRUD & REL & DC
    D --> MS & PS & AS & SchS
    PDF --> MS & PS & AS & SchS
```

### 6.2 Role-Based Access Control

**Purpose**: Control user access to features based on their role

```mermaid
flowchart TB
    subgraph Roles["User Roles"]
        Admin[🔑 Admin<br/>Full Access]
        Exec[📊 Executive<br/>View + Reports]
        Staff[👷 Staff<br/>Limited Access]
    end

    subgraph Permissions["Permission Matrix"]
        P1[canViewDashboard]
        P2[canViewReports]
        P3[canViewSafetySearch]
        P4[canViewDevConsole]
        P5[canCreate]
        P6[canUpdate]
        P7[canDelete]
        P8[canViewEntities]
    end

    Admin --> P1 & P2 & P3 & P4 & P5 & P6 & P7 & P8
    Exec --> P1 & P2 & P3 & P8
    Staff --> P3 & P8
```

**Role Permissions**:

| Permission | Admin | Executive | Staff |
|------------|-------|-----------|-------|
| View Dashboard | ✅ | ✅ | ❌ |
| View Reports | ✅ | ✅ | ❌ |
| View Safety Search | ✅ | ✅ | ✅ |
| View Dev Console | ✅ | ❌ | ❌ |
| View Building Supervision | ✅ | ✅ | ❌ |
| Create Records | ✅ | ❌ | ❌ |
| Update Records | ✅ | ❌ | ❌ |
| Delete Records | ✅ | ❌ | ❌ |
| View Entities | ✅ | ✅ | ✅ |

**Implementation**:

- `RoleContext.jsx` - React Context for role state management
- `useRole()` hook - Access role and permissions in components
- `hasPermission()` - Check specific permission for current user
- UI components conditionally render based on permissions
- Login page for role selection with localStorage persistence

### 6.3 Executive Dashboard

**Purpose**: Provide real-time insights into campus management metrics

**Visualizations**:

- **Maintenance by Location**: Bar chart showing task distribution across buildings
- **People by Role**: Pie chart visualizing personnel distribution
- **Activities by Type**: Horizontal bar chart of activity counts
- **School Statistics**: Grouped bar chart (people + locations per school)
- **Maintenance Frequency**: Table view (Daily, Weekly, Monthly)

### 6.4 Entity Management

**Supported Entities & Fields**:

| Entity | Key Fields |
|--------|------------|
| **People** | Personal ID, Name, Gender, DOB, Entry Date, Supervisor |
| **Schools** | Name, Department, Faculty, HQ Building |
| **Activities** | ID, Type, Time, Organizer, Location |
| **Maintenance** | Type, Frequency, Location, Chemical Usage, Contractor |

**CRUD Features**:

- ✅ Create new records with form validation (Admin only)
- ✅ Edit existing records inline (Admin only)
- ✅ Delete with confirmation dialog (Admin only)
- ✅ Dynamic dropdown options from related tables
- ✅ Cascading selects (Building → Room)
- ✅ CSV bulk import (Admin only)
- ✅ Role-based UI - buttons hidden for non-Admin users

### 6.5 Relationship Management

```mermaid
flowchart LR
    subgraph Participations["Participations (M:N)"]
        P1[Person] <-->|participates in| A1[Activity]
    end

    subgraph Affiliations["Affiliations (M:N)"]
        P2[Person] <-->|affiliated with| S1[School]
    end
```

### 6.6 Safety Search

**Purpose**: Identify cleaning activities that may use hazardous chemicals

**Features**:

- Building-based search filter
- Displays cleaning maintenance tasks
- **Warning Flags**: Red alert with ⚠️ icon for `active_chemical = true`
- Shows location details (building, room, floor) and frequency

### 6.7 PDF Report Generation

**Purpose**: Generate professional PDF reports with comprehensive data analysis

**Features**:

- **Section Selection**: Choose which sections to include in the report
  - Executive Summary (KPI metrics and overview)
  - Maintenance Analysis (tasks by location/type with charts)
  - Personnel Overview (staff by role and status)
  - Activities Statistics (events summary with organizers)
  - Department Statistics (school/faculty data)
  - Safety Report (chemical hazard analysis)
- **PolyU Branding**: Professional styling with university colors (#A6192E, #B08E55)
- **Data Visualization**: Bar charts and pie charts embedded in PDF
- **Automatic Download**: One-click PDF generation and download

**Technical Implementation**:

- Backend: ReportLab for PDF generation, Matplotlib for charts
- Frontend: React component with section checkboxes
- API: `/api/reports/generate-pdf` returns PDF binary

### 6.8 Developer Console

**Purpose**: Direct database access for debugging and advanced queries

**Access**: Admin role only (hidden from Executive and Staff users)

**Features**:

- SQL query editor with monospace font
- Execute any SQL query (SELECT, INSERT, UPDATE, DELETE)
- Query result table with scrollable display
- **Query History**: Last 10 queries with success/fail status
- **LocalStorage Persistence**: Survives page refresh
- Error display with MySQL error messages
- **Danger Zone Warning**: Alerts users to potential data risks

### 6.9 Business Rule Enforcement

```mermaid
flowchart TD
    subgraph Rules["Business Rules"]
        R1[Mid-level Manager Limit: 10]
        R2[Base-level Worker Limit: 50]
        R3[One Profile per Person]
        R4[Cascade Delete Person]
        R5[Protect Location with Maintenance]
    end

    R1 -->|Checked on| ProfileCreate[Profile Creation]
    R2 -->|Checked on| ProfileCreate
    R3 -->|Enforced by| UniqueConstraint[UNIQUE Constraint]
    R4 -->|Deletes| Dependencies[Participation, Affiliation, Profile]
    R5 -->|Blocks| LocationDelete[Location Deletion]
```

### 6.10 Automated Testing

**Purpose**: Ensure code quality and prevent regressions through comprehensive test suites

```mermaid
flowchart TB
    subgraph Backend["Backend Tests (pytest)"]
        BU[Unit Tests<br/>85 tests]
        BI[Integration Tests<br/>11 tests]
    end

    subgraph Frontend["Frontend Tests (Vitest)"]
        FC[Component Tests<br/>34 tests]
        FI[API Integration<br/>5 tests]
    end

    subgraph Desktop["Desktop Tests (Vitest)"]
        DU[Utility Tests<br/>4 tests]
    end

    BU --> API[API Endpoints]
    BU --> DB[Database Utils]
    BI --> MySQL[(MySQL)]
    FC --> Components[React Components]
    FI --> MockAPI[Mocked API]
    DU --> Electron[Electron Utils]
```

**Test Coverage**:

| Component | Framework | Tests | Coverage |
|-----------|-----------|-------|----------|
| Backend | pytest + pytest-cov | 96 | API endpoints, DB utilities |
| Frontend | Vitest + React Testing Library | 39 | Components, API integration |
| Desktop | Vitest | 4 | Electron utilities |
| **Total** | - | **139** | - |

**Backend Test Categories**:

- `test_api_persons.py` - Person CRUD operations
- `test_api_schools.py` - School CRUD operations
- `test_api_locations.py` - Location CRUD operations
- `test_api_activities.py` - Activity CRUD operations
- `test_api_maintenance.py` - Maintenance CRUD operations
- `test_api_profiles.py` - Profile CRUD with business rule validation
- `test_api_relationships.py` - Participation/Affiliation operations
- `test_api_reports.py` - Dashboard report endpoints
- `test_api_special.py` - Safety search and raw query endpoints
- `test_db.py` - Database connection utilities
- `integration/` - Full database integration tests

**Frontend Test Categories**:

- `Dashboard.test.jsx` - Dashboard rendering and chart display
- `DevConsole.test.jsx` - SQL console functionality
- `EntityManager.test.jsx` - Generic CRUD component
- `RelationshipManager.test.jsx` - Relationship management
- `SafetySearch.test.jsx` - Chemical hazard search
- `api.test.jsx` - Frontend-backend API integration

---

## 7. Conclusion

The **PolyU CMMS** is a well-structured, functional Campus Maintenance and Management System that successfully demonstrates a modern full-stack architecture with comprehensive testing.

### Key Achievements ✅

- **Solid technical foundations** with React, Flask, and MySQL
- **Clean separation of concerns** across frontend, backend, and database layers
- **User-friendly features** including dashboards, CRUD operations, and safety search
- **Professional PDF report generation** with PolyU branding and data visualization
- **Developer productivity tools** like the Dev Console and bulk import
- **Comprehensive test suites** with 139 automated tests covering all layers:
  - Backend: 96 pytest tests (unit + integration)
  - Frontend: 39 Vitest tests (components + API integration)
  - Desktop: 4 Vitest tests (Electron utilities)
- **Quality assurance infrastructure** with pytest-cov for coverage and mocked database connections

### Priority Improvements 🎯

1. **Security**: Authentication, input validation, secure Dev Console
2. **End-to-End Testing**: Browser automation with Playwright/Cypress
3. **Performance**: Pagination, caching, query optimization

### Test Execution Summary

```bash
# Backend: 96 tests (85 passed, 11 skipped - integration tests require DB)
cd backend && pytest tests/ -v

# Frontend: 39 tests passed
cd frontend && npm test -- --run

# Desktop: 4 tests passed
cd desktop && npm test -- --run
```

---

> Report prepared for COMP2411 Database Systems Group Project
