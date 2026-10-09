# IAMShield AI: Autonomous Least-Privilege IAM Policy Synthesizer

## Project Overview

**IAMShield AI** is an intelligent system designed to autonomously analyze user access patterns and automatically synthesize least-privilege Identity and Access Management (IAM) policies. The system combines rule-based logic with AI-driven insights to generate secure, minimal-permission policies that reduce security risks and improve compliance.

## Key Features

- **Autonomous Policy Synthesis**: Automatically generate least-privilege IAM policies based on user activity patterns
- **Access Pattern Analysis**: Analyze logs and access behaviors to identify required permissions
- **Policy Recommendation Engine**: Suggest optimal policies with explanations
- **Policy Validation**: Validate policies against security best practices and compliance requirements
- **Role-Based Access Control (RBAC)**: Manage users, roles, and permissions
- **Audit Logging**: Track all policy changes and access events
- **Multi-Cloud Support**: Generic policy format (AWS, Azure, GCP compatible)
- **Interactive Dashboard**: User-friendly web interface for policy management

## Domain
**Cybersecurity | Identity Defense & Cloud Security**

## Technology Stack

### Frontend
- **React** 18+ - UI framework
- **Tailwind CSS** - Styling
- **Vite** - Build tool (fast development)
- **Axios** - HTTP client
- **React Router** - Navigation

### Backend
- **Python 3.10+** - Programming language
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation
- **PyJWT** - JWT authentication
- **Uvicorn** - ASGI server

### Database
- **MySQL 8.0+** - Primary database
- **PostgreSQL 13+** - Alternative/Analytics database

### DevOps & Tools
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Git** - Version control
- **GitHub Actions** - CI/CD

## Project Structure

```
IAMShield-AI/
├── frontend/                 # React web application
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API integration
│   │   ├── hooks/           # Custom React hooks
│   │   ├── context/         # Context API for state
│   │   ├── utils/           # Utility functions
│   │   └── App.jsx          # Main app component
│   ├── public/              # Static assets
│   ├── package.json         # Dependencies
│   ├── vite.config.js       # Vite configuration
│   └── tailwind.config.js   # Tailwind configuration
│
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── main.py         # Entry point
│   │   ├── core/           # Configuration & constants
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas (DTOs)
│   │   ├── routes/         # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── middleware/     # Custom middleware
│   │   ├── utils/          # Utility functions
│   │   └── auth/           # Authentication logic
│   ├── tests/              # Unit & integration tests
│   ├── requirements.txt    # Python dependencies
│   ├── .env.example        # Environment variables template
│   └── Dockerfile          # Docker image configuration
│
├── database/               # Database schemas & migrations
│   ├── schemas/
│   │   ├── users.sql       # User tables
│   │   ├── policies.sql    # Policy tables
│   │   ├── logs.sql        # Audit log tables
│   │   └── init.sql        # Initial setup
│   └── migrations/         # Migration scripts
│
├── docs/                   # Documentation
│   ├── API.md             # API documentation
│   ├── DATABASE.md        # Database schema docs
│   ├── ARCHITECTURE.md    # System architecture
│   ├── SETUP.md           # Setup instructions
│   └── USAGE.md           # Usage guide
│
├── configs/               # Configuration files
│   ├── docker-compose.yml # Docker compose setup
│   ├── nginx.conf         # Nginx configuration (optional)
│   └── env.example        # Example environment variables
│
├── .github/               # GitHub specific files
│   └── workflows/         # CI/CD workflows
│       └── ci.yml         # GitHub Actions CI/CD
│
├── .gitignore            # Git ignore patterns
├── LICENSE               # MIT License
└── docker-compose.yml    # Docker composition
```

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.10+
- MySQL 8.0+ or PostgreSQL 13+
- Docker & Docker Compose (optional)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/Regginear/IAMShield-AI.git
   cd IAMShield-AI
   ```

2. **Setup Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Setup Backend**
   ```bash
   cd ../backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python -m uvicorn app.main:app --reload
   ```

4. **Setup Database**
   - Create MySQL/PostgreSQL database
   - Run migration scripts in `database/schemas/`
   - Update `.env` with database credentials

5. **Docker Setup (Alternative)**
   ```bash
   docker-compose up -d
   ```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh JWT token
- `POST /api/auth/logout` - User logout

### Users & Roles
- `GET /api/users` - List all users
- `POST /api/users` - Create new user
- `GET /api/roles` - List all roles
- `POST /api/roles` - Create new role

### Policies
- `GET /api/policies` - List all policies
- `POST /api/policies` - Create new policy
- `GET /api/policies/{id}` - Get policy details
- `PUT /api/policies/{id}` - Update policy
- `DELETE /api/policies/{id}` - Delete policy

### Policy Synthesis
- `POST /api/synthesis/analyze` - Analyze access patterns
- `POST /api/synthesis/generate` - Generate policy recommendations
- `POST /api/synthesis/validate` - Validate policy

### Audit & Logs
- `GET /api/logs` - Get audit logs
- `GET /api/logs/user/{user_id}` - Get user-specific logs

## Core Algorithms

### Least-Privilege Synthesis
The system uses a rule-based algorithm to identify the minimum required permissions:
1. **Input Analysis**: Parse access logs and activity patterns
2. **Permission Extraction**: Identify required resources and actions
3. **Conflict Resolution**: Handle overlapping or contradictory patterns
4. **Policy Optimization**: Minimize redundant permissions
5. **Output Generation**: Generate IAM policies in standard formats

### Access Pattern Classification
- **Resource Access**: Which resources are accessed
- **Action Frequency**: How often each action is performed
- **Time-based Patterns**: When access occurs
- **Anomaly Detection**: Identify unusual access patterns

## Security Features

- ✅ JWT-based authentication
- ✅ Role-Based Access Control (RBAC)
- ✅ Password hashing (bcrypt)
- ✅ CORS protection
- ✅ Input validation & sanitization
- ✅ Audit logging
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ Rate limiting

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

- **Vasu Agrawal** - Project Lead
- **Akash Gaurav** - Frontend and Design
- **Sarthak** - QA and Documentation

## Acknowledgments

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- AWS, Azure, and GCP IAM Policy Specifications

## Contact

For questions or feedback, please reach out via:
- GitHub Issues: [IAMShield-AI Issues](https://github.com/Regginear/IAMShield-AI/issues)
- Email: project team contact

---

**Last Updated**: 2026-09-02
**Status**: 🚀 In Development
