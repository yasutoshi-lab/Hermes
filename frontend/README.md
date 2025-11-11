# Hermes Frontend

Modern React + TypeScript frontend for the Hermes document summarization and analysis agent.

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling with dark mode support
- **React Router** - Client-side routing
- **Zustand** - State management
- **i18next** - Internationalization (Japanese/English)
- **Axios** - HTTP client

## Features

- 🌓 Dark mode support
- 🌍 Japanese/English i18n
- 🔐 Authentication (login/register)
- 💬 Chat interface for document analysis
- 📁 File upload support
- 🎨 Modern, responsive design
- 🔌 WebSocket support for real-time updates

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env

# Start development server
npm run dev
```

The application will be available at `http://localhost:3000`.

### Environment Variables

See `.env.example` for required environment variables:

- `VITE_API_URL` - Backend API URL
- `VITE_WS_URL` - WebSocket URL
- `VITE_APP_NAME` - Application name
- `VITE_DEFAULT_LOCALE` - Default language (ja/en)

## Development

```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## Docker

```bash
# Build image
docker build -t hermes-frontend .

# Run container
docker run -p 80:80 hermes-frontend
```

## Project Structure

```
src/
├── api/              # API client and endpoints
├── components/       # Reusable components
├── i18n/            # Internationalization config
├── layouts/         # Layout components
├── pages/           # Page components
├── stores/          # Zustand stores
├── App.tsx          # Main app component
├── main.tsx         # Entry point
└── index.css        # Global styles
```

## License

Apache 2.0
