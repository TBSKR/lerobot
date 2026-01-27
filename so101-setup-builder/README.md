# SO-101 Setup Builder

A full-stack web application to help users design and configure SO-101 robot arm setups with intelligent recommendations, component comparison, and real-time pricing.

## Features

- **Guided Setup Wizard**: 5-step wizard to capture user preferences (experience, budget, use case, compute platform, camera)
- **Component Database**: Browse all SO-101 compatible components with specifications and pricing
- **Side-by-Side Comparison**: Compare up to 5 components
- **AI Recommendations**: Gemini-powered intelligent component suggestions
- **Multi-Vendor Pricing**: Prices from AliExpress, Amazon, Waveshare, RobotShop
- **Export Options**: PDF, JSON, and shopping list generation

## Tech Stack

- **Backend**: Python/FastAPI with async SQLAlchemy
- **Frontend**: React/TypeScript with Vite, TailwindCSS, Zustand
- **Database**: PostgreSQL
- **Cache**: Redis
- **AI**: Google Gemini API

## Quick Start

### Prerequisites

- Docker and Docker Compose
- (Optional) Gemini API key for AI recommendations
- (Optional) Tavily API key for web price search

### Setup

1. Clone the repository and navigate to the project:
   ```bash
   cd so101-setup-builder
   ```

2. Copy the environment file and add your API keys:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. Start all services:
   ```bash
   make up
   # or
   docker-compose up -d
   ```

4. Run database migrations:
   ```bash
   make migrate
   ```

5. Seed the database with initial data:
   ```bash
   make seed
   ```

6. Access the application:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Database Admin: http://localhost:8080

## Development

### Backend

The backend is a FastAPI application located in `/backend`.

```bash
# Enter backend container
make shell-backend

# Run tests
pytest

# Create a new migration
make migrate-create msg="Add new table"
```

### Frontend

The frontend is a React/TypeScript application located in `/frontend`.

```bash
# Enter frontend container
make shell-frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## API Endpoints

### Wizard
- `POST /api/v1/wizard/start` - Start a new setup session
- `PUT /api/v1/wizard/{setup_id}/step/{n}` - Save step answer
- `GET /api/v1/wizard/{setup_id}/summary` - Get full profile

### Components
- `GET /api/v1/components` - List components with filters
- `GET /api/v1/components/{id}` - Get component details
- `GET /api/v1/components/so101-defaults` - Get default SO-101 BOM

### Recommendations
- `POST /api/v1/recommendations/generate` - Generate AI recommendations
- `POST /api/v1/recommendations/chat` - Interactive Q&A

### Pricing
- `GET /api/v1/pricing/component/{id}` - Get vendor prices
- `GET /api/v1/pricing/setup/{setup_id}` - Get total cost breakdown

### Comparison
- `POST /api/v1/comparison/compare` - Compare 2-5 components

### Export
- `POST /api/v1/export/pdf` - Generate PDF
- `POST /api/v1/export/json` - Export as JSON
- `POST /api/v1/export/shopping-list` - Generate shopping list

## SO-101 Component Reference

### Motors (Feetech STS3215)

| Arm Type | Joint | Gear Ratio | Quantity |
|----------|-------|------------|----------|
| Follower | All   | 1/345      | 6        |
| Leader   | 1, 3  | 1/191      | 2        |
| Leader   | 2     | 1/345      | 1        |
| Leader   | 4,5,6 | 1/147      | 3        |

### Essential Components
- Waveshare Serial Bus Servo Driver Board
- 12V 5A DC Power Supply
- 3-Pin TTL Servo Cables
- USB-C Cable

## License

This project is part of the LeRobot ecosystem. See the main LeRobot repository for license information.

## Resources

- [LeRobot Documentation](https://huggingface.co/docs/lerobot)
- [SO-ARM100 GitHub](https://github.com/TheRobotStudio/SO-ARM100)
- [LeRobot GitHub](https://github.com/huggingface/lerobot)
