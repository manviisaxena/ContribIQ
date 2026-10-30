ContribIQ
Built by contributors, for contributors.

ContribIQ is an open-source platform designed to help developers make informed decisions before contributing to GitHub repositories. It aims to bring repository insights, contribution opportunities, and personal contribution tracking together in one place.

Finding the right open-source project to contribute to is not always easy. Developers may struggle to identify actively maintained repositories, discover beginner-friendly issues, understand licensing requirements, and keep track of their pull requests. ContribIQ aims to make that process easier.
Project status: ContribIQ is under active development. The capabilities listed below describe the project's goals; not all features are implemented or available yet.

What ContribIQ aims to offer
- Repository health analysis — Understand repository activity and indicators of project health.
- Maintainer responsiveness — Get insights into how maintainers engage with issues and pull requests.
- Good first issue discovery — Find beginner-friendly issues and potential contribution opportunities.
- License compatibility — Review repository licensing information before contributing.
- Personal PR dashboard — Track pull requests and follow your open-source contributions.
Technology stack
The current codebase uses the following technologies:
Area	Technologies
Frontend	React, TypeScript, Vite
Backend	Python, FastAPI
Database and migrations	PostgreSQL, SQLAlchemy, Alembic
Authentication foundations	Passlib (bcrypt), JWT
GitHub integration	GitHub API client libraries


Additional infrastructure and AI-related dependencies are part of the planned development stack and will be documented as those components are implemented.
Project structure
ContribIQ/
├── backend/
│   ├── api/          # API routes
│   ├── core/         # Configuration and security utilities
│   ├── db/           # Database setup and session management
│   ├── models/       # SQLAlchemy models
│   └── schemas/      # Pydantic schemas
├── frontend/
│   └── src/
│       ├── api/      # Frontend API clients
│       ├── components/
│       ├── context/
│       ├── pages/
│       ├── styles/
│       └── utils/
├── alembic/          # Database migrations
├── docs/             # Development plan and project documentation
├── requirements.txt  # Backend dependencies
└── README.md

Getting started

Prerequisites
- Git
- Node.js and npm
- Python
- PostgreSQL

1. Clone the repository
git clone <repository-url>
cd ContribIQ
2. Set up the frontend
cd frontend
npm install
npm run dev
Vite will print the local development URL when the frontend server starts.
3. Set up the backend
From the repository root, create and activate a virtual environment:
python3 -m venv .venv
source .venv/bin/activate
Install the backend dependencies:
python -m pip install -r requirements.txt
Create your local environment file:
cp .env.example .env
Update the values in .env for your local PostgreSQL database and other required services. Never commit .env or real credentials.

Start the API from the repository root:
uvicorn backend.main:app --reload
The backend exposes its interactive API documentation at /docs when the application is running. The current application startup also checks the database connection, so PostgreSQL must be configured and available.
Development roadmap
ContribIQ is being developed incrementally. The roadmap includes:
1. Foundation — Frontend scaffold, backend setup, database foundation, user model, and authentication utilities.
2. Authentication and profile — Authentication endpoints, GitHub OAuth, frontend integration, and contributor profiles.
3. Repository analysis foundation — GitHub API integration, repository metadata, background processing, and analysis progress.
4. Repository overview — Repository insights, architecture visualization, and caching.
5. Contributor onboarding — Guided onboarding paths and contributor profiles.
6. Issue discovery and recommendations — Issue difficulty assessment, matching, and recommendations.
7. Issue deep dives — Detailed issue context and related codebase insights.
8. Q&A and release readiness — Codebase Q&A, contributor readiness scoring, quality improvements, and deployment.

Contributing
Contributions, suggestions, and feedback are welcome.

Before contributing:
1. Check the existing issues to see what needs work.
2. Look for issues labelled good first issue if you're new to the project.
3. Comment on an issue before starting substantial work so the approach can be discussed.
4. Open a pull request with a clear summary of the changes and relevant testing details.
Please keep changes focused and include tests or verification steps where appropriate. Contribution guidelines will be expanded as the project develops.
Project goal
Our goal is to make open-source contribution more accessible, transparent, and approachable for developers at every experience level.

Whether you're making your first contribution or working across multiple repositories, ContribIQ aims to help you discover meaningful opportunities and follow your open-source journey.

Built by contributors, for contributors.
License
ContribIQ is licensed under the Apache License 2.0.