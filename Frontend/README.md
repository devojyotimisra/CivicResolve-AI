# CivicResolve AI — Frontend

A modern, responsive web application for municipal administration, civic issue reporting, and public facility management. Built with **React 19**, **Vite**, and **Tailwind CSS v4**.

---

## Features & Portals

### Citizen Portal
* **Single Sign-On (SSO):** Quick and secure authentication using Google Login.
* **Grievance Reporting:** File civic hazard reports (potholes, street lights, waste accumulation) either anonymously or with an authenticated citizen account.
* **Live Token Tracking:** Track issue resolution progress in real-time using unique 12-character tracking codes.
* **Civic Facilities & Reservations:** Explore municipal venues (community halls, public parks), check real-time availability calendars, and book reservations online.
* **Utility Billing:** View and pay municipal taxes, water bills, and maintenance fees.
* **Progressive Web App (PWA):** Install the application on desktop or mobile devices for a native-like experience.

### Field Officer Portal
* **Task Management:** View assigned maintenance tickets and hazard reports with location landmarks and citizen-submitted photos.
* **Live Status Advancement:** Update task statuses on the go (*En Route*, *On Site*, *In Progress*).
* **Photographic Proof:** Upload engineering notes and resolution photos/videos to mark tickets as *Resolved*.

### Commissioner Portal
* **Executive Dashboard:** Oversee city-wide resolution KPIs, department efficiency, and revenue analytics via interactive charts.
* **Administration:** Manage field officers, municipal departments, civic facilities, and citizen accounts from a centralized control panel.

---

## Tech Stack

* **Core Framework:** [React 19](https://react.dev/) + [Vite 8](https://vitejs.dev/) (with PWA capabilities)
* **Styling:** [Tailwind CSS v4](https://tailwindcss.com/) + [Radix UI](https://www.radix-ui.com/) / shadcn components
* **Icons & Visualization:** [Lucide React](https://lucide.dev/) + [Recharts](https://recharts.org/)
* **Routing & State:** [React Router v7](https://reactrouter.com/) + React Context API
* **Authentication:** Google OAuth 2.0 integration for seamless login
* **Notifications & Modals:** [Sonner](https://sonner.emilkowal.ski/) toasts + custom confirmation modals

---

## Getting Started

### Prerequisites
* [Node.js](https://nodejs.org/) (v18 or higher recommended)
* `npm` or `pnpm`

### Installation & Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd Frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```
   The application will be available at `http://localhost:5173`.

---

## Available Scripts

| Command | Description |
| :--- | :--- |
| `npm run dev` | Starts the local development server with Hot Module Replacement (HMR). |
| `npm run build` | Compiles and optimizes the application for production into the `dist/` folder. |
| `npm run preview` | Previews the locally built production bundle. |
| `npm run lint` | Runs the linter (`oxlint`) to check for code quality and syntax issues. |
| `npm run format` | Auto-formats code with Prettier, fixes ESLint issues, and runs Knip to find unused files/dependencies. |

---
