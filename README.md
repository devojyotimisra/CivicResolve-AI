# CivicResolve AI

**AI-Powered Unified Civic Services Platform**

CivicResolve AI is a comprehensive solution for municipal administration, civic issue reporting, and public facility management. It bridges the gap between citizens, field officers, and city commissioners through an intelligent, unified digital platform.

---

## Team (MAY2026-TEAM 17)

| Team Member | Roll Number | Role |
| :--- | :--- | :--- |
| **Devojyoti Misra** | DS24F1002239 | Backend, AI, Frontend, Tester, Scrum Master, Code Reviewer |
| **Tathagata Banerjee** | DS23F3002603 | Backend, AI, Tester, Code Reviewer |
| **Bhabani Sankar Samal** | DS23F2005717 | Frontend, Tester, Code Reviewer |
| **Saurao Madhukar Upare** | DS21F1000355 | Frontend, Tester, Code Reviewer |
| **Vinshi Jain** | DS23F2004001 | Product Manager, Scrum Master |

**Shared IITM Folder Link:** [Google Drive](https://drive.google.com/drive/folders/18miwvXZWbhcpNJ9WMbTfdF_UoTOGp3nx)

---

## Key Features

### AI-Powered Intelligence
* **Spam & Fraud Detection:** Automated filtering of abusive, irrelevant, or non-civic complaint submissions using LLM evaluation.
* **Auto-Routing:** Smart classification of civic issues to automatically assign complaints to the appropriate municipal department.
* **Image Analysis:** Automated generation of detailed descriptions based on user-uploaded hazard photos.

### Three-Tier Portal System
1. **Citizen Portal:** Single Sign-On (SSO) via Google, anonymous or authenticated grievance reporting, live token tracking, utility billing, and civic facility reservations.
2. **Field Officer Portal:** Mobile-friendly task management, live status updates (*En Route*, *On Site*, *In Progress*), and resolution via photographic proof uploads.
3. **Commissioner Portal:** Executive dashboard with city-wide resolution KPIs, revenue analytics, and centralized administration for users, departments, and facilities.

---

## Technology Stack

### Frontend
* **Core:** React 19, Vite 8 (PWA enabled)
* **Styling & UI:** Tailwind CSS v4, Radix UI, shadcn components
* **Icons & Charts:** Lucide React, Recharts
* **State Management & Routing:** React Router v7, React Context API

### Backend
* **Core:** Python 3.12+, FastAPI
* **Database & ORM:** SQLite, SQLAlchemy 2.0+
* **Authentication:** JWT (JSON Web Tokens), Role-Based Access Control (RBAC)
* **AI Integration:** LLM-powered pipelines for automated routing and spam detection

---

## Repository Structure

* [`/Frontend`](./Frontend/) - Contains the React Progressive Web Application. See the [Frontend README](./Frontend/README.md) for local setup and development instructions.
* [`/Backend`](./Backend/) - Contains the FastAPI REST server and automated test suite. See the [Backend README](./Backend/README.md) for API setup, dependencies, and testing documentation.

---

## Getting Started

To run this project locally, you will need to set up both the backend server and the frontend development environment.

1. **Backend Setup:** Follow the instructions in [`Backend/README.md`](./Backend/README.md) to install dependencies via `uv`, run the test suite, and start the FastAPI server.
2. **Frontend Setup:** Follow the instructions in [`Frontend/README.md`](./Frontend/README.md) to install Node.js dependencies and start the Vite development server.