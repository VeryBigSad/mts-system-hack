# Frontend Application

This is a React + TypeScript frontend application built with Vite and TailwindCSS.

## Prerequisites

- Node.js 18.x or higher
- npm or yarn
- Docker (optional, for containerized deployment)

## Local Development

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Building for Production

To build the application for production:

```bash
npm run build
```

The built files will be available in the `dist` directory.

## Docker Deployment

1. Build the Docker image:
```bash
docker compose build
```

2. Run the container:
```bash
docker compose up
```

The application will be available at `http://localhost:3000`

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint

## Technologies Used

- React 18
- TypeScript
- Vite
- TailwindCSS
- MediaPipe
- React Webcam 